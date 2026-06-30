from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class NodeLogBase(BaseModel):
    run_id: uuid.UUID
    node_name: str  # search, dedup, score, outreach, evaluate
    status: Optional[str] = None  # success, failed
    input: Optional[str] = None  # JSON string of input data
    output: Optional[str] = None  # JSON string of output data
    error: Optional[str] = None

class NodeLogCreate(NodeLogBase):
    run_id: uuid.UUID
    node_name: str

class NodeLogUpdate(BaseModel):
    status: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None

class NodeLog(NodeLogBase):
    id: uuid.UUID
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    class Config:
        from_attributes = True