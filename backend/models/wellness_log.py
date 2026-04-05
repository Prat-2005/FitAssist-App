"""
Wellness Log Model
SQLAlchemy ORM model for tracking daily wellness metrics
"""

from sqlalchemy import Column, DateTime, Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models.base import Base


class WellnessLog(Base):
    """
    Wellness log model for tracking daily wellness metrics
    Records body battery, sleep quality, and hydration levels
    One entry per user per day (enforced by unique constraint)
    """
    __tablename__ = "wellness_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Wellness metrics (all optional)
    body_battery = Column(Integer, nullable=True)  # 0-100
    sleep_score = Column(Integer, nullable=True)  # 0-100
    hydration_liters = Column(Float, nullable=True)

    # Date tracking
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD for daily lookup

    # Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite unique constraint: one row per user per day
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_wellness_log_user_date'),
    )

    def __repr__(self):
        return f"<WellnessLog(id={self.id}, user_id={self.user_id}, date={self.date})>"
