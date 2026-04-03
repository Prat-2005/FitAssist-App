from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    goal: str
    duration_days: Optional[int] = None
    workout_schedule: str
    nutrition_guidelines: Optional[str] = None
    ai_model_used: Optional[str] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    duration_days: Optional[int] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None
    progress_percentage: Optional[int] = None

class PlanResponse(PlanBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool
    is_completed: bool
    progress_percentage: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
