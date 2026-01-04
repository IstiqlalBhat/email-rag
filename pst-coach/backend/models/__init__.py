"""
Database models package.
Note: This project primarily uses JSON files for data storage.
SQLAlchemy models are kept for potential future database integration.
"""
from models.base import Base, TimeStampedModel

__all__ = [
    "Base",
    "TimeStampedModel",
]
