from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies import get_db, get_current_user
from app.schemas.analysis import AnalysisJobResponse
from app.services import analysis_service
from app.db.models.user import User

router = APIRouter()

@router.post("/repositories/{repository_id}/analyze", response_model=AnalysisJobResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_analysis(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a new analysis task for a repository."""
    return analysis_service.create_analysis_job(db, repository_id, current_user)

@router.get("/jobs/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of an analysis task."""
    return analysis_service.get_job_status(db, job_id, current_user)
