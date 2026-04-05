"""
Workout Log Model
SQLAlchemy ORM model for tracking completed workout days
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models.base import Base


class WorkoutLog(Base):
    """
    Workout log model for tracking completed workout days
    Records user's completion of individual workout days from a plan
    One entry per user per plan per specific day/week/year combo (enforced by unique constraint)
    """
    __tablename__ = "workout_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)

    # Workout day details
    day_number = Column(Integer, nullable=False)  # 1-7, which day of the plan was completed
    exercises_completed = Column(Integer, nullable=False)  # count of exercises marked done

    # Grouping information
    week_number = Column(Integer, nullable=False)  # ISO week number for grouping
    year = Column(Integer, nullable=False)  # year for grouping

    # Timestamps
    completed_at = Column(DateTime, nullable=False)  # when this day was marked done
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite unique constraint: one log per user per plan per day/week/year
    __table_args__ = (
        UniqueConstraint('user_id', 'plan_id', 'day_number', 'week_number', 'year', 
                        name='uq_workout_log_user_plan_day_week_year'),
    )

    def __repr__(self):
        return f"<WorkoutLog(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id}, day={self.day_number})>"
