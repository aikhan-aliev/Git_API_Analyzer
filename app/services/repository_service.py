from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.repository import Repository, RepositoryRegistration
from app.db.models.user import User
from app.schemas.repository import RepositoryCreate
from app.services.github_service import GitHubService
from app.core.config import settings

def register_repository(db: Session, repo_input: str, user: User) -> Repository:
    github_service = GitHubService(token=settings.GITHUB_TOKEN)
    try:
        owner, name = github_service.parse_input(repo_input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Check if repo already registered by ANY user (system-wide)
    full_name = f"{owner}/{name}".lower()
    existing_repo = db.query(Repository).filter(Repository.full_name == full_name).first()
    
    if not existing_repo:
        metadata = github_service.fetch_repo_metadata(owner, name)
        
        # Create repo
        repo_create = RepositoryCreate(
            github_owner=metadata["owner"]["login"],
            github_name=metadata["name"],
            full_name=metadata["full_name"].lower(),
            html_url=metadata["html_url"],
            clone_url=metadata["clone_url"],
            default_branch=metadata["default_branch"],
            description=metadata.get("description"),
            primary_language=metadata.get("language"),
            stars=metadata.get("stargazers_count", 0),
            forks=metadata.get("forks_count", 0),
            open_issues=metadata.get("open_issues_count", 0),
            is_private=metadata.get("private", False),
            is_archived=metadata.get("archived", False)
        )
        
        repo_data = repo_create.model_dump()
        repo_data["html_url"] = str(repo_data["html_url"])
        repo_data["clone_url"] = str(repo_data["clone_url"])
        
        existing_repo = Repository(**repo_data)
        db.add(existing_repo)
        db.flush() # flush to get ID
        
    # Check if user already linked
    existing_link = db.query(RepositoryRegistration).filter(
        RepositoryRegistration.user_id == user.id,
        RepositoryRegistration.repository_id == existing_repo.id
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="User already registered this repository")
        
    # Create link
    new_link = RepositoryRegistration(user_id=user.id, repository_id=existing_repo.id)
    db.add(new_link)
    db.commit()
    db.refresh(existing_repo)
    
    return existing_repo
