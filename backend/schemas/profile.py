from pydantic import BaseModel
from typing import Optional
import uuid

class ProfileBase(BaseModel):
    fitness_goal: Optional[str] = None
    target_weight: Optional[float] = None
    current_weight: Optional[float] = None
    height: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    experience_level: Optional[str] = None
    preferred_workouts: Optional[str] = None
    equipment_available: Optional[str] = None
    days_per_week: Optional[int] = None
    duration_minutes: Optional[int] = None
    medical_conditions: Optional[str] = None
    injuries: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {
        "from_attributes": True
    }

class PublicProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_workouts: Optional[str] = None
    equipment_available: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
