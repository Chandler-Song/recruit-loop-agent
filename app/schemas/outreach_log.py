from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class OutreachLogBase(BaseModel):
    pipeline_id: uuid.UUID
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = "pending"  # pending, sent, failed
    error: Optional[str] = None

class OutreachLogCreate(OutreachLogBase):
    pipeline_id: uuid.UUID
    subject: str
    body: str

class OutreachLogUpdate(BaseModel):
    status: Optional[str] = None
    error: Optional[str] = None

class OutreachLog(OutreachLogBase):
    id: uuid.UUID
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True