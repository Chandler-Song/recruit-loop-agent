from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./recruiting_agent.db"
    debug: bool = False

    # GitHub
    github_token: Optional[str] = None

    # Email / SMTP
    smtp_host: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_port: int = 587
    email_from: Optional[str] = None

    # LLM (Large Language Model)
    llm_api_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model_name: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_timeout: float = 60.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()