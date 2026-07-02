from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import json
import uuid

class CandidateBase(BaseModel):
    source: str
    source_id: str
    github_login: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = 0
    public_repos: Optional[int] = 0
    skills: Optional[List[str]] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    search_keywords: Optional[List[str]] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    public_repos: Optional[int] = None
    skills: Optional[List[str]] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None

class Candidate(CandidateBase):
    id: uuid.UUID
    appearance_count: int = 1
    source_weight: float = 1.0
    created_at: datetime
    updated_at: datetime

    @field_validator('skills', 'search_keywords', mode='before')
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