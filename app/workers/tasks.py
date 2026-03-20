from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models.analysis_job import AnalysisJob
from app.db.models.analysis_snapshot import AnalysisSnapshot
from app.db.models.finding import Finding
from app.db.models.metric import Metric
from app.db.models.repository import Repository
from app.analyzers.structure_analyzer import analyze_structure
from app.analyzers.activity_analyzer import analyze_activity
from app.analyzers.contributor_analyzer import analyze_contributors
from app.analyzers.python_analyzer import analyze_python_code
from app.analyzers.scoring import compute_overall_score
from app.services.github_service import GitHubService
import uuid
from datetime import datetime, timezone


@celery_app.task(bind=True)
def run_analysis_job(self, job_id: str):
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == uuid.UUID(job_id)).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        repo = db.query(Repository).filter(Repository.id == job.repository_id).first()
        if not repo:
            raise ValueError("Repository not found")

        github_service = GitHubService(token=settings.GITHUB_TOKEN)
        headers = github_service.headers
        owner = repo.github_owner
        name = repo.github_name

        # Fetch repo metadata (for activity analysis)
        repo_metadata = github_service.fetch_repo_metadata(owner, name)

        # Run all analyzers
        structure_result = analyze_structure(owner, name, headers)
        activity_result = analyze_activity(owner, name, headers, repo_metadata)
        contributor_result = analyze_contributors(owner, name, headers)

        # Run python analyzer only for python repos (or try it anyway)
        python_result = None
        if repo.primary_language and repo.primary_language.lower() == "python":
            python_result = analyze_python_code(repo.clone_url, repo.default_branch)

        # Compute overall scores
        py_score = python_result["score"] if python_result and python_result.get("is_python") else None
        score_summary = compute_overall_score(
            structure_score=structure_result["score"],
            activity_score=activity_result["score"],
            contributor_score=contributor_result["score"],
            python_score=py_score,
        )

        # Persist snapshot
        snapshot = AnalysisSnapshot(
            analysis_job_id=job.id,
            overall_score=score_summary["overall_score"],
            overall_risk_level=score_summary["overall_risk_level"],
            maintainability_score=score_summary["maintainability_score"],
            security_score=score_summary["security_score"],
            activity_score=score_summary["activity_score"],
            collaboration_score=score_summary["collaboration_score"],
            sustainability_score=score_summary["sustainability_score"],
        )
        db.add(snapshot)
        db.flush()

        # Persist metrics
        all_metrics: dict = {}
        all_metrics.update(activity_result.get("metrics", {}))
        all_metrics.update(contributor_result.get("metrics", {}))
        if python_result:
            all_metrics.update(python_result.get("metrics", {}))

        for key, value in all_metrics.items():
            if value is None:
                continue
            m = Metric(
                snapshot_id=snapshot.id,
                key=key,
                value_numeric=float(value) if isinstance(value, (int, float)) else None,
                value_text=str(value) if not isinstance(value, (int, float)) else None,
            )
            db.add(m)

        # Persist findings
        all_findings = []
        all_findings.extend(structure_result.get("findings", []))
        all_findings.extend(activity_result.get("findings", []))
        all_findings.extend(contributor_result.get("findings", []))
        if python_result:
            all_findings.extend(python_result.get("findings", []))

        for f in all_findings:
            finding = Finding(
                snapshot_id=snapshot.id,
                category=f.get("category", "general"),
                severity=f.get("severity", "info"),
                title=f.get("title", ""),
                description=f.get("description", ""),
                recommendation=f.get("recommendation"),
            )
            db.add(finding)

        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(AnalysisJob).filter(AnalysisJob.id == uuid.UUID(job_id)).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)[:1000]
            job.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()

