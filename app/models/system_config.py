from sqlalchemy import Column, String, Text, DateTime
from app.database.base import Base
from datetime import datetime
import uuid

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, nullable=False)  # SMTP_HOST, GITHUB_TOKEN, etc
    value = Column(Text)  # Configuration value
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)