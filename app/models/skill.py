from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # github_search, linkedin_search, etc
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)