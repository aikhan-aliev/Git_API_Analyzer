import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.db.base import Base

class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analysis_snapshots.id"))
    category: Mapped[str] = mapped_column(String(100)) # structure, activity, contributor, complexity, security
    severity: Mapped[str] = mapped_column(String(50)) # info, warning, error, critical
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    metric_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metric_value_text: Mapped[str | None] = mapped_column(String, nullable=True)
    metric_value_numeric: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    snapshot = relationship("AnalysisSnapshot", back_populates="findings")
