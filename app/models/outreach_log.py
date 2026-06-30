from sqlalchemy import Column, String, Text, Integer, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String)  # Foreign key to pipelines table
    subject = Column(String)
    body = Column(Text)
    status = Column(String, default="pending")  # pending, sent, failed
    error = Column(Text)  # Error message if failed
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)