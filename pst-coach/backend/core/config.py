"""
Application configuration using Pydantic settings.
Simplified for local-first personal usage.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os

class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "PST Coach"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field("insecure-dev-key-change-me-for-prod", min_length=10)

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://pstcoach:changeme123@127.0.0.1:5433/pst_coach"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default
    CACHE_LLM_TTL_SECONDS: int = 3600  # 1 hour for LLM responses
    RATE_LIMIT_REQUESTS: int = 60  # Max requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60  # 1 minute window

    # Storage
    # Local directory to store uploads and extracted files
    DATA_DIR: str = "data"
    UPLOAD_DIR: str = "data/uploads"
    EXTRACTED_DIR: str = "data/extracted"

    # Vector Database
    # QDRANT_URL: str = "http://localhost:6333" # Deprecated for this run
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = "serverless" # or "us-west-2" etc.
    PINECONE_INDEX_NAME: str = "pst-coach"

    # Apache Tika
    TIKA_SERVER_URL: str = "http://localhost:9998"

    # LLM Configuration
    LLM_PROVIDER: str = "google"
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-3-flash-preview"

    # Rate Limiting for LLM API calls
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 1.0  # Base delay in seconds
    LLM_MAX_RPM: int = 15  # Max requests per minute (conservative for free tier)
    LLM_BATCH_SIZE: int = 5  # Batch size for parallel operations

    # Embeddings
    # We will use local embeddings to avoid extra API costs/complexity for now, 
    # or Pinecone inference if available. Let's default to a solid local model suitable for RAG.
    EMBEDDING_PROVIDER: str = "google"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 384 # 1536 is for OpenAI, 384 for MiniLM

    # Application Limits
    MAX_PST_SIZE_MB: int = 5000
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Security
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    # Privacy
    DEFAULT_REDACTION_LEVEL: str = "strict"

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()

# Ensure data directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXTRACTED_DIR, exist_ok=True)
