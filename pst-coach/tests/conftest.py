"""
Pytest configuration and shared fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.models.base import Base
from backend.api.main import app


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create database session for tests."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_pst_data():
    """Sample PST message data."""
    return {
        "message_id": "msg_123",
        "subject": "Test Email",
        "from": "sender@example.com",
        "to": ["recipient@example.com"],
        "body": "This is a test email message.",
        "date": "2024-01-01T10:00:00Z"
    }
