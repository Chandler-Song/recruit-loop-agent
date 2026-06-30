from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./recruiting_agent.db"
    debug: bool = False
    github_token: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_port: int = 587
    email_from: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()