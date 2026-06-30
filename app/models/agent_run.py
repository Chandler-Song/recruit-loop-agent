from sqlalchemy import Column, String, Text, Integer, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    position_id = Column(String)  # Foreign key to positions table
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer)  # Duration in milliseconds
    candidates_found = Column(Integer, default=0)
    candidates_added = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    status = Column(String, default="running")  # running, success, failed
    error = Column(Text)  # Error message if failed