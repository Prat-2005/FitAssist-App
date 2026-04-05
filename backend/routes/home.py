"""
Home Dashboard Routes
Handles all home screen data retrieval
"""

import json
from arrow import now
from fastapi import APIRouter, Depends, HTTPException
import redis
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from db import get_db, get_redis_client
from models import User, Plan
from middleware import get_current_user
import logging
import asyncio
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
router = APIRouter()

# TODO: Move wellness tips to config/CMS for easy updates and legal review audit
# AUDIT_STATUS: Content pending legal/medical review before production deployment
# Replace with CMS-managed content and ensure all claims are verified by legal team

# Static list of rotating wellness tips
# NOTE: These tips should be reviewed by legal and medical professionals
# before deploying to production. Avoid specific medical claims.
WELLNESS_TIPS = [
    "Remember to take breaks during your workout and listen to your body's signals.",
    "Proper technique matters more than intensity when learning new exercises.",
    "Stay hydrated throughout your day and especially during workouts.",
    "Aim for consistent activity rather than sporadic intense sessions.",
    "Quality sleep supports your body's adaptation to training.",
    "A balanced approach to nutrition complements your fitness routine.",
    "Recovery days are an important part of any training program.",
    "Gradual progression helps prevent injury and builds sustainable habits.",
    "Consistency with your routine contributes to long-term fitness goals.",
    "Listen to your body and adjust intensity as needed for your fitness level."
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
    # Rotate across all tips by calendar day
    today_index = now.toordinal()
    
    # Get user's active plan (offload blocking query to thread pool)
    active_plan = await run_in_threadpool(
        lambda: db.query(Plan).filter(
            Plan.user_id == current_user.id,
            Plan.is_active == True
        ).first()
    )
    
    plan_progress_percent = 0
    active_plan_name = "No Active Plan"
    is_today_rest_day = False
    
    if active_plan:
        plan_progress_percent = active_plan.progress_percentage
        active_plan_name = active_plan.name
        
        # Determine if today is a rest day (using consistent date_str)
        try:
            schedule = json.loads(active_plan.workout_schedule) if isinstance(active_plan.workout_schedule, str) else active_plan.workout_schedule
            days = schedule.get("days") if isinstance(schedule, dict) else None
            if isinstance(days, list):
                for day in days:
                    if (
                        isinstance(day, dict)
                        and day.get("day") == today_weekday
                        and day.get("is_rest_day")
                    ):
                        is_today_rest_day = True
                        break
        except (json.JSONDecodeError, ValueError):
            is_today_rest_day = False
    
    # Get generation counts for today (using consistent date_str)
    redis_client = get_redis_client()
    user_id = str(current_user.id)
    
    workout_generations_today = 0
    nutrition_generations_today = 0
    
    workout_key = f"workout_requests:{user_id}:{date_str}"
    nutrition_key = f"nutrition_requests:{user_id}:{date_str}"

    try:
        workout_count = await redis_client.get(workout_key)
        workout_generations_today = int(workout_count) if workout_count else 0
    except (redis.RedisError, ValueError) as exc:
        logger.warning("Failed to read Redis counter %s: %s", workout_key, exc)

    try:
        nutrition_count = await redis_client.get(nutrition_key)
        nutrition_generations_today = int(nutrition_count) if nutrition_count else 0
    except (redis.RedisError, ValueError) as exc:
        logger.warning("Failed to read Redis counter %s: %s", nutrition_key, exc)
    
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
