"""
Job and upload models for async processing.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, BigInteger, Text, JSON
from sqlalchemy.orm import relationship
import enum

from models.base import TimeStampedModel


class UploadStatus(str, enum.Enum):
    """Upload status types."""
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class JobType(str, enum.Enum):
    """Job types."""
    PARSE_PST = "parse_pst"
    INDEX_CONTENT = "index_content"
    COMPUTE_METRICS = "compute_metrics"
    GENERATE_INSIGHTS = "generate_insights"
    INDEX_INSIGHTS = "index_insights"


class JobStatus(str, enum.Enum):
    """Job status types."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Upload(TimeStampedModel):
    """PST upload model."""

    __tablename__ = "uploads"

    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    object_key = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.PENDING, nullable=False, index=True)
    error_message = Column(Text)

    # Relationships
    tenant = relationship("Tenant", back_populates="uploads")
    jobs = relationship("Job", back_populates="upload", cascade="all, delete-orphan")


class Job(TimeStampedModel):
    """Background job model."""

    __tablename__ = "jobs"

    tenant_id = Column(Integer, nullable=False, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), index=True)
    job_type = Column(Enum(JobType), nullable=False, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    progress = Column(Integer, default=0)
    total = Column(Integer, default=100)
    current_stage = Column(String(255))
    error_json = Column(JSON)

    # Relationships
    upload = relationship("Upload", back_populates="jobs")
    checkpoints = relationship("JobCheckpoint", back_populates="job", cascade="all, delete-orphan")


class JobCheckpoint(TimeStampedModel):
    """Job checkpoint for resumability."""

    __tablename__ = "job_checkpoints"

    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    checkpoint_key = Column(String(255), nullable=False)
    checkpoint_value_json = Column(JSON, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="checkpoints")
