"""
Mailbox and message models.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text, Boolean, ARRAY, JSON
from sqlalchemy.orm import relationship
import enum

from models.base import TimeStampedModel


class Direction(str, enum.Enum):
    """Message direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Mailbox(TimeStampedModel):
    """Mailbox model representing a user's email account."""

    __tablename__ = "mailboxes"

    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    display_name = Column(String(255), nullable=False)
    primary_email_hash = Column(String(64), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="mailboxes")
    user = relationship("User", back_populates="mailboxes")
    messages = relationship("Message", back_populates="mailbox", cascade="all, delete-orphan")
    threads = relationship("Thread", back_populates="mailbox", cascade="all, delete-orphan")


class Message(TimeStampedModel):
    """Email message model."""

    __tablename__ = "messages"

    tenant_id = Column(Integer, nullable=False, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False, index=True)
    message_uid = Column(String(255), nullable=False, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="SET NULL"), index=True)

    folder = Column(String(255))
    direction = Column(Enum(Direction), nullable=False, index=True)

    sent_at = Column(DateTime, index=True)
    received_at = Column(DateTime, index=True)

    from_hash = Column(String(64), index=True)
    to_hashes = Column(ARRAY(String), default=[])
    cc_hashes = Column(ARRAY(String), default=[])

    subject = Column(Text)
    body_clean_text = Column(Text)
    body_raw_ref = Column(String(500))

    has_attachments = Column(Boolean, default=False)
    meta_json = Column(JSON, default={})

    # Relationships
    mailbox = relationship("Mailbox", back_populates="messages")
    thread = relationship("Thread", back_populates="messages")


class Thread(TimeStampedModel):
    """Email thread model for conversation grouping."""

    __tablename__ = "threads"

    tenant_id = Column(Integer, nullable=False, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_key = Column(String(64), nullable=False, index=True)
    subject_norm = Column(Text)

    first_ts = Column(DateTime)
    last_ts = Column(DateTime, index=True)

    participant_hashes = Column(ARRAY(String), default=[])
    message_count = Column(Integer, default=0)

    # Relationships
    mailbox = relationship("Mailbox", back_populates="threads")
    messages = relationship("Message", back_populates="thread")
