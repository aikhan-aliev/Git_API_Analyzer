import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, String, DateTime, ForeignKey
from datetime import datetime, timezone
from app.db.base import Base

class AnalysisSnapshot(Base):
    __tablename__ = "analysis_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analysis_jobs.id"))
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True) # low, moderate, elevated, high
    maintainability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    security_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    collaboration_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sustainability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    job = relationship("AnalysisJob", back_populates="snapshots")
    findings = relationship("Finding", back_populates="snapshot")
    metrics = relationship("Metric", back_populates="snapshot")
