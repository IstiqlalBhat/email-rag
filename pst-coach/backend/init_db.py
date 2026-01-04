"""
Initialize database tables.
Note: This project primarily uses JSON files for data storage.
This script is kept for potential future database integration.
"""
from sqlalchemy import create_engine
from core.config import settings
from models import Base


def init_database():
    """Create all database tables."""
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
