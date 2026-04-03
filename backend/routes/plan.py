"""
Fitness Plan Routes
Handles fitness plan generation, retrieval, and updates
"""

import asyncio
import redis
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from ai.generator import generate_workout_plan, generate_nutrition_plan
from db import get_redis_client

router = APIRouter()

from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from db import get_db
from models import User, Plan
from schemas import PlanCreate, PlanUpdate, PlanResponse
from middleware import get_current_user, get_current_user_optional
import uuid

class UserProfile(BaseModel):
    goal: str = "General Fitness"
    fitness_level: str = "Beginner"
    days_per_week: int = 3
    equipment: str = "None"
    duration_minutes: int = 30
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    dietary_preference: Optional[str] = None

    model_config = {
        "extra": "allow"
    }

@router.post("/generate-workout-plan")
async def generate_workout_endpoint(profile: UserProfile, current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Generate a personalized workout plan using AI.
    Includes rate limiting of 2 requests per user per day.
    """
    redis_client = get_redis_client()
    date_str = datetime.now().strftime("%Y-%m-%d")
    user_id = str(current_user.id) if current_user else "anonymous"
    
    global_key = f"rate_limit:global:{date_str}"
    workout_key = f"workout_requests:{user_id}:{date_str}"
    
    try:
       # Atomically increment and check global rate limit
        global_count = await redis_client.incr(global_key)
        if global_count == 1:
            await redis_client.expire(global_key, 86400)
        if global_count > 1400:
            await redis_client.decr(global_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Global daily API limit exceeded."
            )
            
        # Atomically increment and check user rate limit
        user_count = await redis_client.incr(workout_key)
        if user_count == 1:
            await redis_client.expire(workout_key, 86400)
        if user_count > 2:
            await redis_client.decr(workout_key)
            await redis_client.decr(global_key)  # Rollback global too
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You have already generated your workout plan for today. Come back tomorrow!"
            )
    except redis.RedisError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter temporarily unavailable. Please try again later."
        ) from e

    try:
        # Pydantic v2 compatible dict dump
        profile_dict = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
        profile_dict["user_id"] = user_id
        plan = await generate_workout_plan(profile_dict)
    except Exception as e:
        try:
            await redis_client.decr(workout_key)
            await redis_client.decr(global_key)
        except redis.RedisError:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate workout plan: {e!s}"
        ) from e

    return {"workout_plan": plan}


@router.post("/generate-nutrition-plan")
async def generate_nutrition_endpoint(profile: UserProfile, current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Generate a personalized nutrition plan using AI.
    Includes rate limiting of 2 requests per user per day.
    """
    redis_client = get_redis_client()
    date_str = datetime.now().strftime("%Y-%m-%d")
    user_id = str(current_user.id) if current_user else "anonymous"
    
    global_key = f"rate_limit:global:{date_str}"
    nutrition_key = f"nutrition_requests:{user_id}:{date_str}"
    
    try:
        # Atomically increment and check global rate limit
        global_count = await redis_client.incr(global_key)
        if global_count == 1:
            await redis_client.expire(global_key, 86400)
        if global_count > 1400:
            await redis_client.decr(global_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Global daily API limit exceeded."
            )
            
        # Atomically increment and check user rate limit
        user_count = await redis_client.incr(nutrition_key)
        if user_count == 1:
            await redis_client.expire(nutrition_key, 86400)
        if user_count > 2:
            await redis_client.decr(nutrition_key)
            await redis_client.decr(global_key)  # Rollback global too
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You have already generated your nutrition plan for today. Come back tomorrow!"
            )
    except redis.RedisError as e:
        print(f"Redis connection error during rate limit check: {e}")
        pass

    try:
        profile_dict = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
        profile_dict["user_id"] = user_id
        plan = await generate_nutrition_plan(profile_dict)
    except Exception as e:
        # Rollback counters on generation failure
        try:
            await redis_client.decr(nutrition_key)
            await redis_client.decr(global_key)
        except redis.RedisError:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate nutrition plan: {e!s}"
        ) from e

    return {"nutrition_plan": plan}


@router.get("/current", response_model=PlanResponse)
def get_current_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get current user's active fitness plan
    """
    plan = db.query(Plan).filter(
        Plan.user_id == current_user.id,
        Plan.is_active == True
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get specific fitness plan by ID
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: uuid.UUID, plan_data: PlanUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update existing fitness plan
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    allowed_keys = {"name", "description", "goal", "duration_days"}
    for key, value in plan_data.model_dump(exclude_unset=True).items():
        if key in allowed_keys:
            setattr(plan, key, value)
        
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/{plan_id}/start", response_model=PlanResponse)
def start_plan(plan_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Start executing a fitness plan
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.is_completed:
        raise HTTPException(status_code=400, detail="Completed plans cannot be started")
        
    active_plans = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.is_active == True).all()
    for active_plan in active_plans:
        active_plan.is_active = False
        
    plan.is_active = True
    if not plan.started_at:
        plan.started_at = datetime.utcnow()
        
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/{plan_id}/complete-workout", response_model=PlanResponse)
def complete_workout(plan_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Log completion of a workout session
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if not plan.is_active or plan.is_completed:
        raise HTTPException(
            status_code=400,
            detail="Only active, incomplete plans can record workout progress",
        )
    
    plan.progress_percentage = min(100, plan.progress_percentage + 10)
    
    if plan.progress_percentage == 100:
        plan.is_completed = True
        plan.completed_at = datetime.utcnow()
        plan.is_active = False
        
    db.commit()
    db.refresh(plan)
    return plan
