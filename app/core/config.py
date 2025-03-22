import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Base application settings
    APP_NAME: str = "Auto Plate Bidding API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for auto license plate bidding system"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    PORT: int = 8000

    # Redis/Celery settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)


    # JWT Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./auto_plate_bidding.db"
    )

    @classmethod
    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite"):
            # Make sure SQLite database uses asynchronous driver
            if not v.startswith("sqlite+aiosqlite"):
                v = v.replace("sqlite", "sqlite+aiosqlite", 1)
        return v

    # CORS settings
    CORS_ORIGINS: [str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
