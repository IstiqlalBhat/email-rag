"""
Application configuration using Pydantic settings.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "PST Coach"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(..., min_length=32)

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Object Storage
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str = "pst-coach"
    S3_REGION: str = "us-east-1"

    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "pst-coach"

    # Apache Tika
    TIKA_SERVER_URL: str = "http://localhost:9998"

    # LLM Configuration
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # Application Limits
    MAX_PST_SIZE_MB: int = 5000
    MAX_EMAILS_PER_UPLOAD: int = 500000
    MAX_INDEXED_TIME_RANGE_MONTHS: int = 24
    MAX_CHAT_MESSAGES_PER_DAY: int = 100
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Privacy
    DEFAULT_REDACTION_LEVEL: str = "strict"
    DEFAULT_RETENTION_DAYS: int = 365
    AUTO_DELETE_PST_AFTER_EXTRACTION: bool = True

    # Monitoring
    SENTRY_DSN: str = ""
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"

    # Feature Flags
    ENABLE_INSIGHTS: bool = True
    ENABLE_COACH_MODE: bool = True
    ENABLE_ATTACHMENT_EXTRACTION: bool = False

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
