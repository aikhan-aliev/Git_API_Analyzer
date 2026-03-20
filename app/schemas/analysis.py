from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional

class AnalysisJobResponse(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
