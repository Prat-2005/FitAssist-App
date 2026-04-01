"""
Fitness Plan Routes
Handles fitness plan generation, retrieval, and updates
"""

import asyncio
import redis
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from ai.generator import generate_workout_plan, generate_nutrition_plan
from db.redis import get_redis_client

router = APIRouter()

from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    user_id: str = "anonymous"
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
async def generate_workout_endpoint(profile: UserProfile):
    """
    Generate a personalized workout plan using AI.
    Includes rate limiting of 2 requests per user per day.
    """
    redis_client = get_redis_client()
    date_str = datetime.now().strftime("%Y-%m-%d")
    user_id = profile.user_id
    
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
async def generate_nutrition_endpoint(profile: UserProfile):
    """
    Generate a personalized nutrition plan using AI.
    Includes rate limiting of 2 requests per user per day.
    """
    redis_client = get_redis_client()
    date_str = datetime.now().strftime("%Y-%m-%d")
    user_id = profile.user_id
    
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


@router.get("/current")
async def get_current_plan():
    """
    Get current user's active fitness plan
    TODO: Implement current plan retrieval
    """
    pass


@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    """
    Get specific fitness plan by ID
    TODO: Implement plan retrieval by ID
    """
    pass


@router.put("/{plan_id}")
async def update_plan(plan_id: str):
    """
    Update existing fitness plan
    TODO: Implement plan update with validation
    """
    pass


@router.post("/{plan_id}/start")
async def start_plan(plan_id: str):
    """
    Start executing a fitness plan
    TODO: Implement plan activation and tracking initiation
    """
    pass


@router.post("/{plan_id}/complete-workout")
async def complete_workout(plan_id: str):
    """
    Log completion of a workout session
    TODO: Implement workout completion tracking and progress update
    """
    pass
