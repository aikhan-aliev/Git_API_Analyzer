import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict

class RepositoryBase(BaseModel):
    github_owner: str
    github_name: str
    full_name: str
    html_url: HttpUrl
    clone_url: HttpUrl
    default_branch: str = "main"
    description: str | None = None
    primary_language: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    is_private: bool = False
    is_archived: bool = False

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: uuid.UUID
    last_pushed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RepositoryRegistrationRequest(BaseModel):
    repository_url_or_name: str
