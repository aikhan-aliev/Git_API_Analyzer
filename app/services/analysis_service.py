from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.repository import Repository
from app.db.models.analysis_job import AnalysisJob
from app.db.models.user import User
from app.workers.tasks import run_analysis_job
import uuid

def create_analysis_job(db: Session, repository_id: uuid.UUID, current_user: User) -> AnalysisJob:
    # Verify user has access to repo via registrations
    has_access = any(reg.repository_id == repository_id for reg in current_user.registrations)
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to analyze this repository")

    # Create job
    job = AnalysisJob(
        repository_id=repository_id,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue task
    run_analysis_job.delay(str(job.id))
    return job

def get_job_status(db: Session, job_id: uuid.UUID, current_user: User) -> AnalysisJob:
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Check access to repo
    has_access = any(reg.repository_id == job.repository_id for reg in current_user.registrations)
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
        
    return job
