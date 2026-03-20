import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MetricResponse(BaseModel):
    id: uuid.UUID
    key: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FindingResponse(BaseModel):
    id: uuid.UUID
    category: str
    severity: str
    title: str
    description: str
    recommendation: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SnapshotResponse(BaseModel):
    id: uuid.UUID
    analysis_job_id: uuid.UUID
    overall_score: Optional[float] = None
    overall_risk_level: Optional[str] = None
    maintainability_score: Optional[float] = None
    security_score: Optional[float] = None
    activity_score: Optional[float] = None
    collaboration_score: Optional[float] = None
    sustainability_score: Optional[float] = None
    generated_at: datetime
    findings: List[FindingResponse] = []
    metrics: List[MetricResponse] = []
    model_config = ConfigDict(from_attributes=True)
