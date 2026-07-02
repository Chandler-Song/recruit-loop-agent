from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from datetime import datetime
import json
import uuid

class PositionBase(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[List[str]] = None
    search_keywords: Optional[List[str]] = None
    loop_interval: Optional[int] = 60

class PositionCreate(PositionBase):
    pass

class PositionUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[List[str]] = None
    search_keywords: Optional[List[str]] = None
    loop_interval: Optional[int] = None
    status: Optional[str] = None

class Position(PositionBase):
    id: uuid.UUID
    status: str = "active"
    loop_enabled: bool = True
    last_loop_at: Optional[datetime] = None
    next_loop_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('required_skills', 'search_keywords', mode='before')
    @classmethod
    def deserialize_json_fields(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return v
        return v

    class Config:
        from_attributes = True