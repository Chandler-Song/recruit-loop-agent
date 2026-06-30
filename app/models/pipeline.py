from sqlalchemy import Column, String, Text, Integer, DateTime, Float
from app.database.base import Base
from datetime import datetime
import uuid

class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    position_id = Column(String)  # Foreign key to positions table
    candidate_id = Column(String)  # Foreign key to candidates table
    status = Column(String, default="discovered")  # discovered, contacted, replied, interview, offer, rejected
    score = Column(Float, default=0.0)  # Calculated score
    score_detail = Column(Text)  # Detailed score breakdown as JSON string
    contact_count = Column(Integer, default=0)
    last_contacted_at = Column(DateTime)
    next_followup_at = Column(DateTime)
    candidate_interest = Column(String)  # high, medium, low
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)