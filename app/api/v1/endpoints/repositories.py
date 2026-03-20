from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.api.dependencies import get_db, get_current_user
from app.schemas.repository import RepositoryResponse, RepositoryRegistrationRequest
from app.services import repository_service
from app.db.models.user import User
from app.db.models.repository import Repository, RepositoryRegistration

router = APIRouter()

@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def register_repo(
    request: RepositoryRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new repository for analysis."""
    return repository_service.register_repository(db, request.repository_url_or_name, current_user)

@router.get("", response_model=List[RepositoryResponse])
def get_user_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all repositories registered by the current user."""
    return [reg.repository for reg in current_user.registrations[skip:skip+limit]]

@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository(
    repository_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get repository by ID."""
    repo = db.query(Repository).join(RepositoryRegistration).filter(
        Repository.id == repository_id,
        RepositoryRegistration.user_id == current_user.id
    ).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo
