"""
Wellness Log Schemas
Pydantic models for WellnessLog requests and responses
"""

from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional, Self
import uuid


class WellnessLogCreate(BaseModel):
    body_battery: Optional[int] = None
    sleep_score: Optional[int] = None
    hydration_liters: Optional[float] = None

    @field_validator('body_battery')
    @classmethod
    def validate_body_battery(cls, v):
        """Validate body_battery is between 0-100 if provided"""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('body_battery must be an integer between 0 and 100 inclusive')
        return v

    @field_validator('sleep_score')
    @classmethod
    def validate_sleep_score(cls, v):
        """Validate sleep_score is between 0-100 if provided"""
        if v is not None:
            if v < 0 or v > 100:
                raise ValueError('sleep_score must be an integer between 0 and 100 inclusive')
        return v

    @field_validator('hydration_liters')
    @classmethod
    def validate_hydration_liters(cls, v):
        """Validate hydration_liters is non-negative if provided"""
        if v is not None:
            if v < 0:
                raise ValueError('hydration_liters must be a non-negative number')
        return v

    @model_validator(mode='after')
    def check_at_least_one_provided(self) -> Self:
        """Ensure at least one wellness metric is provided"""
        if self.body_battery is None and self.sleep_score is None and self.hydration_liters is None:
            raise ValueError('At least one of body_battery, sleep_score, or hydration_liters must be provided')
        return self


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
