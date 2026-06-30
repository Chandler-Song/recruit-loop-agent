from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Float
from app.database.base import Base
from datetime import datetime
import uuid

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)  # github, linkedin, etc
    source_id = Column(String, nullable=False)  # GitHub user ID
    github_login = Column(String)  # GitHub username
    name = Column(String)
    email = Column(String)
    location = Column(String)
    company = Column(String)
    title = Column(String)
    bio = Column(Text)
    followers = Column(Integer, default=0)
    public_repos = Column(Integer, default=0)
    skills = Column(Text)  # Stored as JSON string
    profile_url = Column(String)
    avatar_url = Column(String)
    search_keywords = Column(Text)  # Stored as JSON string
    appearance_count = Column(Integer, default=1)
    source_weight = Column(Float, default=1.0)  # Weight based on how often they appear
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)