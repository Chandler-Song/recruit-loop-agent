from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
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

    class Config:
        from_attributes = True