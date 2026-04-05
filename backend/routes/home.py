"""
Home Dashboard Routes
Handles all home screen data retrieval
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from db import get_db, get_redis_client
from models import User, Plan
from middleware import get_current_user

router = APIRouter()

# Static list of rotating wellness tips
WELLNESS_TIPS = [
    "Optimizing your parasympathetic tone through 4-7-8 breathing post-workout accelerates myofibrillar repair cycles.",
    "Strategic cold water immersion post-lift enhances hormone-sensitive lipase activity and mitochondrial density.",
    "Phosphocreatine recovery demands precise sleep architecture — prioritize deep stage 3 NREM for ATP resynthesis.",
    "Circadian cortisol peaks optimize power output — schedule compound lifts within 2 hours of waking.",
    "Intermittent fasting triggers autophagy, but maintain amino acid availability during training windows.",
    "Magnesium glycinate supplementation before bed potentiates GABA receptor sensitivity for recovery.",
    "Progressive overload activates neuromuscular adaptation before hypertrophy — focus on form the first 3 weeks.",
    "Proper breathing patterns stabilize intra-abdominal pressure, enhancing force transfer efficiency by up to 15%.",
    "Nutrient timing around training windows maximizes mTOR signaling and glycogen repletion.",
    "Sleep deprivation reduces testosterone secretion by 25-30% — consistency beats perfection."
]


class HomeResponse(BaseModel):
    plan_progress_percent: int
    active_plan_name: str
    is_today_rest_day: bool
    current_streak: int
    workout_generations_today: int
    nutrition_generations_today: int
    body_function_tip: str


@router.get("", response_model=HomeResponse)
async def get_home_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Home screen dashboard endpoint.
    Returns plan progress, streak, generation counts, and a rotating wellness tip.
    Uses consistent UTC timezone for all date/time operations.
    """
    
    # Capture single timezone reference for entire handler
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    today_weekday = now.weekday() + 1  # 1-7 (Mon-Sun)
    today_index = now.weekday()
    
    # Get user's active plan
    active_plan = db.query(Plan).filter(
        Plan.user_id == current_user.id,
        Plan.is_active == True
    ).first()
    
    plan_progress_percent = 0
    active_plan_name = "No Active Plan"
    is_today_rest_day = False
    
    if active_plan:
        plan_progress_percent = active_plan.progress_percentage
        active_plan_name = active_plan.name
        
        # Determine if today is a rest day (using consistent date_str)
        try:
            schedule = json.loads(active_plan.workout_schedule) if isinstance(active_plan.workout_schedule, str) else active_plan.workout_schedule
            if isinstance(schedule, dict) and "days" in schedule:
                for day in schedule["days"]:
                    if day.get("day") == today_weekday and day.get("is_rest_day"):
                        is_today_rest_day = True
                        break
        except (json.JSONDecodeError, ValueError):
            is_today_rest_day = False
    
    # Get generation counts for today (using consistent date_str)
    redis_client = get_redis_client()
    user_id = str(current_user.id)
    
    workout_generations_today = 0
    nutrition_generations_today = 0
    
    try:
        workout_key = f"workout_requests:{user_id}:{date_str}"
        nutrition_key = f"nutrition_requests:{user_id}:{date_str}"
        
        workout_count = await redis_client.get(workout_key)
        nutrition_count = await redis_client.get(nutrition_key)
        
        workout_generations_today = int(workout_count) if workout_count else 0
        nutrition_generations_today = int(nutrition_count) if nutrition_count else 0
    except Exception:
        # Redis unavailable, default to 0
        pass
    
    # Select rotating tip based on same day reference as rest_day check
    body_function_tip = WELLNESS_TIPS[today_index % len(WELLNESS_TIPS)]
    
    return HomeResponse(
        plan_progress_percent=plan_progress_percent,
        active_plan_name=active_plan_name,
        is_today_rest_day=is_today_rest_day,
        current_streak=current_user.current_streak,
        workout_generations_today=workout_generations_today,
        nutrition_generations_today=nutrition_generations_today,
        body_function_tip=body_function_tip
    )
