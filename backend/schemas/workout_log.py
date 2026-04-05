"""
Workout Log Schemas
Pydantic models for WorkoutLog requests and responses
"""

from pydantic import BaseModel
from datetime import datetime
import uuid


class WorkoutLogCreate(BaseModel):
    day_number: int
    exercises_completed: int


class WorkoutLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    day_number: int
    exercises_completed: int
    week_number: int
    year: int
    completed_at: datetime

    model_config = {
        "from_attributes": True
    }
