from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class SchedulerJobBase(BaseModel):
    position_id: uuid.UUID
    enabled: Optional[bool] = True
    interval_minutes: Optional[int] = 60
    status: Optional[str] = "waiting"  # waiting, running, paused, error

class SchedulerJobCreate(SchedulerJobBase):
    position_id: uuid.UUID

class SchedulerJobUpdate(BaseModel):
    enabled: Optional[bool] = None
    interval_minutes: Optional[int] = None
    status: Optional[str] = None

class SchedulerJob(SchedulerJobBase):
    id: uuid.UUID
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    total_runs: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True