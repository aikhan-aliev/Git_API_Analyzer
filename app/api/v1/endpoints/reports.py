import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.analysis_job import AnalysisJob
from app.db.models.analysis_snapshot import AnalysisSnapshot
from app.db.models.repository import Repository, RepositoryRegistration
from app.schemas.report import SnapshotResponse, FindingResponse

router = APIRouter()


def _check_repo_access(db: Session, repository_id: uuid.UUID, user: User):
    """Verify the user has a registration for this repository."""
    reg = db.query(RepositoryRegistration).filter(
        RepositoryRegistration.repository_id == repository_id,
        RepositoryRegistration.user_id == user.id
    ).first()
    if not reg:
        raise HTTPException(status_code=403, detail="Not authorized to access this repository")


@router.get("/repositories/{repository_id}/report/latest", response_model=SnapshotResponse)
def get_latest_report(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest analysis snapshot for a repository."""
    _check_repo_access(db, repository_id, current_user)

    # Get latest completed job
    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.repository_id == repository_id, AnalysisJob.status == "completed")
        .order_by(AnalysisJob.finished_at.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="No completed analysis found for this repository")

    snapshot = db.query(AnalysisSnapshot).filter(
        AnalysisSnapshot.analysis_job_id == job.id
    ).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found for this job")

    return snapshot


@router.get("/repositories/{repository_id}/reports", response_model=List[SnapshotResponse])
def list_reports(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all analysis snapshots for a repository."""
    _check_repo_access(db, repository_id, current_user)

    snapshots = (
        db.query(AnalysisSnapshot)
        .join(AnalysisJob)
        .filter(AnalysisJob.repository_id == repository_id)
        .order_by(AnalysisSnapshot.generated_at.desc())
        .all()
    )
    return snapshots


@router.get("/repositories/{repository_id}/findings", response_model=List[FindingResponse])
def get_findings(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the findings from the latest completed analysis."""
    _check_repo_access(db, repository_id, current_user)

    job = (
        db.query(AnalysisJob)
        .filter(AnalysisJob.repository_id == repository_id, AnalysisJob.status == "completed")
        .order_by(AnalysisJob.finished_at.desc())
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="No completed analysis found")

    snapshot = db.query(AnalysisSnapshot).filter(
        AnalysisSnapshot.analysis_job_id == job.id
    ).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found")

    return snapshot.findings
