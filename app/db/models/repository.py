import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin

class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    github_owner: Mapped[str] = mapped_column(String(255), index=True)
    github_name: Mapped[str] = mapped_column(String(255), index=True)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    html_url: Mapped[str] = mapped_column(String())
    clone_url: Mapped[str] = mapped_column(String())
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    primary_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    open_issues: Mapped[int] = mapped_column(Integer, default=0)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    last_pushed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    registrations = relationship("RepositoryRegistration", back_populates="repository")
    analysis_jobs = relationship("AnalysisJob", back_populates="repository")
    webhook_events = relationship("WebhookEvent", back_populates="repository")

class RepositoryRegistration(Base):
    __tablename__ = "repository_registrations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="registrations")
    repository = relationship("Repository", back_populates="registrations")
