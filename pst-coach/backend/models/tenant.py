"""
Tenant and user models for multi-tenancy.
"""
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
import enum

from models.base import TimeStampedModel


class PlanType(str, enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class UserRole(str, enum.Enum):
    """User role types."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Tenant(TimeStampedModel):
    """Tenant model for multi-tenant isolation."""

    __tablename__ = "tenants"

    name = Column(String(255), nullable=False)
    plan = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    mailboxes = relationship("Mailbox", back_populates="tenant", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="tenant", cascade="all, delete-orphan")


class User(TimeStampedModel):
    """User model."""

    __tablename__ = "users"

    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    mailboxes = relationship("Mailbox", back_populates="user")
