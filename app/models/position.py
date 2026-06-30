from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class Position(Base):
    __tablename__ = "positions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    required_skills = Column(Text)  # Stored as JSON string
    search_keywords = Column(Text)  # Stored as JSON string
    status = Column(String, default="active")  # active, paused, closed
    loop_interval = Column(Integer, default=60)  # minutes
    loop_enabled = Column(Boolean, default=True)
    last_loop_at = Column(DateTime)
    next_loop_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)