from sqlalchemy import Column, String, Text, Integer, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class NodeLog(Base):
    __tablename__ = "node_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String)  # Foreign key to agent_runs table
    node_name = Column(String)  # search, dedup, score, outreach, evaluate
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer)  # Duration in milliseconds
    status = Column(String)  # success, failed
    input = Column(Text)  # Input data as JSON string
    output = Column(Text)  # Output data as JSON string
    error = Column(Text)  # Error message if failed