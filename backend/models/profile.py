"""
User Profile Model
SQLAlchemy ORM model for extended user profile information
"""

from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from models.base import Base


class Profile(Base):
    """
    Extended user profile model
    TODO: Implement profile with fitness goals, measurements, and preferences
    """
    __tablename__ = "profiles"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Fitness goals
    fitness_goal = Column(String, nullable=True)  # e.g., "weight_loss", "muscle_gain", "endurance"
    target_weight = Column(Float, nullable=True)
    current_weight = Column(Float, nullable=True)

    # Physical measurements
    height = Column(Float, nullable=True)  # in cm
    body_fat_percentage = Column(Float, nullable=True)

    # Fitness preferences
    experience_level = Column(String, nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    preferred_workouts = Column(Text, nullable=True)  # JSON string of preferences
    equipment_available = Column(Text, nullable=True)  # JSON string of available equipment
    days_per_week = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Health information
    medical_conditions = Column(Text, nullable=True)  # JSON string of conditions
    injuries = Column(Text, nullable=True)  # JSON string of current injuries

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id})>"
