from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class AgentRunBase(BaseModel):
    position_id: uuid.UUID
    candidates_found: Optional[int] = 0
    candidates_added: Optional[int] = 0
    emails_sent: Optional[int] = 0
    status: Optional[str] = "running"  # running, success, failed
    error: Optional[str] = None

class AgentRunCreate(AgentRunBase):
    position_id: uuid.UUID
    started_at: datetime

class AgentRunUpdate(BaseModel):
    candidates_found: Optional[int] = None
    candidates_added: Optional[int] = None
    emails_sent: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None

class AgentRun(AgentRunBase):
    id: uuid.UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    class Config:
        from_attributes = True