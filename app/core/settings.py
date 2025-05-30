from pydantic import EmailStr, AnyHttpUrl
from typing import List, Optional
from pydantic_settings import BaseSettings
from pathlib import Path
import os

env_path = Path(__file__).parent.parent.parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Food Forum SWD392"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"

    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    FIRST_SUPERUSER_GMAIL: EmailStr
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_API_TOKEN: Optional[str] = ""

    # Google OAuth
    CLIENT_ID: str
    CLIENT_SECRET: str

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    FRONTEND_HOST: List[AnyHttpUrl] = []
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Email settings
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str
    SMTP_USER: EmailStr
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: EmailStr
    EMAILS_FROM_NAME: str
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: EmailStr

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings(_env_file=Path(__file__).parent.parent.parent / ".env")
