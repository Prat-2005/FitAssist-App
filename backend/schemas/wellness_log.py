"""
Wellness Log Schemas
Pydantic models for WellnessLog requests and responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class WellnessLogCreate(BaseModel):
    body_battery: Optional[int] = None
    sleep_score: Optional[int] = None
    hydration_liters: Optional[float] = None


class WellnessLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    body_battery: Optional[int] = None
    sleep_score: Optional[int] = None
    hydration_liters: Optional[float] = None
    date: str
    logged_at: datetime

    model_config = {
        "from_attributes": True
    }
