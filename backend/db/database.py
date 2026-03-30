"""
PostgreSQL Database Configuration
Handles database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
from models.base import Base

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/fitassist"
)

# Create database engine
# TODO: Configure connection pooling and other engine parameters for production
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Use NullPool for development; configure for production
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session dependency
    TODO: Implement session lifecycle management
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database with all tables
    TODO: Run this on application startup to create tables
    """
    # Create all tables using the shared Base
    Base.metadata.create_all(bind=engine)
