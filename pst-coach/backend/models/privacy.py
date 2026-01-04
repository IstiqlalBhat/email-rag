"""
Privacy settings and deletion models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum

from models.base import TimeStampedModel


class RedactionLevel(str, enum.Enum):
    """Redaction level types."""
    STRICT = "strict"
    MODERATE = "moderate"
    MINIMAL = "minimal"
    NONE = "none"


class ExcerptPolicy(str, enum.Enum):
    """Excerpt display policy."""
    NEVER = "never"
    ASK = "ask"
    ALWAYS = "always"


class DeletionScope(str, enum.Enum):
    """Deletion scope types."""
    UPLOAD = "upload"
    MAILBOX = "mailbox"
    ALL = "all"


class DeletionStatus(str, enum.Enum):
    """Deletion request status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PrivacySettings(TimeStampedModel):
    """Privacy settings per tenant/mailbox."""

    __tablename__ = "privacy_settings"

    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), index=True)
    redaction_level = Column(Enum(RedactionLevel), default=RedactionLevel.STRICT, nullable=False)
    excerpt_policy = Column(Enum(ExcerptPolicy), default=ExcerptPolicy.ASK, nullable=False)
    retention_days = Column(Integer, default=365)
    auto_delete_pst = Column(Boolean, default=True)


class DeletionRequest(TimeStampedModel):
    """Deletion request tracking."""

    __tablename__ = "deletion_requests"

    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    scope = Column(Enum(DeletionScope), nullable=False)
    status = Column(Enum(DeletionStatus), default=DeletionStatus.PENDING, nullable=False, index=True)
    target_id = Column(Integer)
    completed_at = Column(DateTime)
    error_message = Column(String(500))
