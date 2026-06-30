from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class PipelineBase(BaseModel):
    position_id: uuid.UUID
    candidate_id: uuid.UUID
    status: Optional[str] = "discovered"
    score: Optional[float] = 0.0
    contact_count: Optional[int] = 0
    candidate_interest: Optional[str] = None
    notes: Optional[str] = None

class PipelineCreate(PipelineBase):
    pass

class PipelineUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None
    contact_count: Optional[int] = None
    candidate_interest: Optional[str] = None
    notes: Optional[str] = None

class Pipeline(PipelineBase):
    id: uuid.UUID
    score_detail: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True