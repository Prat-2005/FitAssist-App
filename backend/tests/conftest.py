"""
Shared test fixtures for FitAssist backend tests.

Uses SQLite in-memory database with patched UUID types and mocked Redis client.
"""

import sys
import os
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Float, Text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add backend directory to path so absolute imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch PostgreSQL UUID before importing models
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import types as sa_types

_original_uuid = pg.UUID


class _SQLiteUUID(sa_types.TypeDecorator):
    """Store UUID as String in SQLite."""
    impl = sa_types.String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


# Monkey-patch the postgresql UUID dialect for SQLite compatibility in tests
def _uuid_patched(as_uuid=False):
    return _SQLiteUUID()


pg.UUID = _uuid_patched  # type: ignore

# Now import models and app (after patching UUID)
from models.base import Base
from models.user import User
from models.profile import Profile
from models.plan import Plan
from middleware.auth import create_access_token


# ---------------------------------------------------------------------------
# SQLite in-memory database engine
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _create_all_tables():
    Base.metadata.create_all(bind=test_engine)


def _drop_all_tables():
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    _create_all_tables()
    yield
    _drop_all_tables()


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Provide a transactional DB session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def mock_redis() -> AsyncMock:
    """Return a mock async Redis client."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.setex = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.flushdb = AsyncMock(return_value=True)
    client.ping = AsyncMock(return_value=True)
    client.incr = AsyncMock(return_value=1)
    client.decr = AsyncMock(return_value=0)
    client.expire = AsyncMock(return_value=True)
    return client


@pytest.fixture()
def sample_user(db: Session) -> User:
    """Create and return a sample user in the test DB."""
    from middleware.auth import hash_password
    user = User(
        id=uuid.uuid4(),
        first_name="Test",
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_token(sample_user: User) -> str:
    """Return a valid JWT token for the sample user."""
    return create_access_token(data={"sub": sample_user.email}, expires_delta=timedelta(hours=1))


@pytest.fixture()
def sample_plan(db: Session, sample_user: User) -> Plan:
    """Create and return a sample plan in the test DB."""
    plan = Plan(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        name="Test Plan",
        goal="General Fitness",
        workout_schedule='{"day1": "rest"}',
        is_active=False,
        is_completed=False,
        progress_percentage=0,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@pytest.fixture()
def sample_profile(db: Session, sample_user: User) -> Profile:
    """Create and return a sample profile in the test DB."""
    profile = Profile(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        fitness_goal="weight_loss",
        experience_level="beginner",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# FastAPI TestClient with dependency overrides
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db: Session, mock_redis: AsyncMock) -> TestClient:
    """
    Return a TestClient with overridden DB and Redis dependencies.
    The mock_redis is injected into the redis module so all cache calls use it.
    """
    from main import app
    from db import database as db_module
    import db.redis as redis_module

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[db_module.get_db] = override_get_db

    # Patch the module-level redis_client used by cache_* functions
    with patch.object(redis_module, "redis_client", mock_redis):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def authed_client(db: Session, mock_redis: AsyncMock, sample_user: User, auth_token: str) -> TestClient:
    """
    Return a TestClient authenticated as sample_user.
    Also overrides get_current_user so protected routes work without real JWT validation.
    """
    from main import app
    from db import database as db_module
    from middleware.auth import get_current_user
    import db.redis as redis_module

    def override_get_db():
        yield db

    async def override_get_current_user():
        return sample_user

    app.dependency_overrides[db_module.get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with patch.object(redis_module, "redis_client", mock_redis):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()