from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class SchedulerJob(Base):
    __tablename__ = "scheduler_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    position_id = Column(String)  # Foreign key to positions table
    enabled = Column(Boolean, default=True)
    interval_minutes = Column(Integer, default=60)
    next_run = Column(DateTime)
    last_run = Column(DateTime)
    total_runs = Column(Integer, default=0)
    status = Column(String, default="waiting")  # waiting, running, paused