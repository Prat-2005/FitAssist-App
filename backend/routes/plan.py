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
from pydantic import BaseModel, conint
from typing import Optional, List
from sqlalchemy.orm import Session
from db import get_db
from models import User, Plan, WorkoutLog, WellnessLog
from schemas import PlanCreate, PlanUpdate, PlanResponse
from middleware import get_current_user, get_current_user_optional
import uuid
import json

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

# Request/Response models for log-day endpoint
class LogDayRequest(BaseModel):
    day_number: conint(ge=1, le=7)  # Must be 1-7 (one week)
    exercises_completed: conint(ge=0)  # Must be non-negative

class LogDayResponse(BaseModel):
    plan: PlanResponse
    current_streak: int
    message: str

# Response models for weekly-report endpoint
class CompletionGridItem(BaseModel):
    day: str
    status: str  # "completed" | "rest" | "missed" | "upcoming"

class WeeklyReportResponse(BaseModel):
    week_range: str
    days_completed: int
    exercises_done: int
    rest_days: int
    current_streak: int
    longest_streak: int
    streak_target: int
    volume_change_percent: int
    completion_grid: List[CompletionGridItem]

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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter temporarily unavailable. Please try again later."
        ) from e
        
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


@router.post("/{plan_id}/log-day")
def log_workout_day(
    plan_id: uuid.UUID,
    log_day_req: LogDayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log completion of a workout day.
    Updates plan progress, handles streak logic, and returns updated plan + streak.
    """
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if not plan.is_active or plan.is_completed:
        raise HTTPException(status_code=400, detail="Only active, incomplete plans can log days")
    
    # Create WorkoutLog entry with ISO week and year (for idempotency)
    today = datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")
    iso_calendar = today.isocalendar()
    week_number = iso_calendar[1]
    year = iso_calendar[0]
    
    # Check if WorkoutLog already exists for this user, plan, and logical slot (day + week/year)
    existing_log = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.plan_id == plan_id,
        WorkoutLog.day_number == log_day_req.day_number,
        WorkoutLog.week_number == week_number,
        WorkoutLog.year == year
    ).first()
    
    if existing_log:
        # Update existing record (idempotent)
        existing_log.exercises_completed = log_day_req.exercises_completed
        existing_log.completed_at = today
        workout_log = existing_log
    else:
        # Create new record
        workout_log = WorkoutLog(
            user_id=current_user.id,
            plan_id=plan_id,
            day_number=log_day_req.day_number,
            exercises_completed=log_day_req.exercises_completed,
            week_number=week_number,
            year=year,
            completed_at=today
        )
        db.add(workout_log)
    
    # Recompute plan progress from scratch by counting completed WorkoutLog rows
    # Progress = (completed_logs / duration_days) * 100, clamped 0–100
    if plan.duration_days and plan.duration_days > 0:
        completed_count = db.query(WorkoutLog).filter(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.plan_id == plan_id
        ).count()
        progress = (completed_count / float(plan.duration_days)) * 100.0
        plan.progress_percentage = max(0.0, min(100.0, progress))
    else:
        plan.progress_percentage = 0.0
    
    # Handle streak logic
    last_workout_date = current_user.last_workout_date
    today_str = date_str
    
    if last_workout_date is None:
        # First workout ever
        current_user.current_streak = 1
    else:
        # Calculate days since last workout
        from datetime import datetime as dt, timedelta
        today_date = dt.strptime(today_str, "%Y-%m-%d").date()
        last_date = dt.strptime(last_workout_date, "%Y-%m-%d").date()
        days_gap = (today_date - last_date).days
        
        if days_gap == 1:
            # Consecutive day
            current_user.current_streak += 1
        elif days_gap == 0:
            # Already logged today, no change
            pass
        else:
            # Gap > 1 day, reset streak
            current_user.current_streak = 1
    
    # Update longest streak if current exceeds it
    if current_user.current_streak > current_user.longest_streak:
        current_user.longest_streak = current_user.current_streak
    
    # Update last workout date
    current_user.last_workout_date = today_str
    
    # Mark plan as completed if progress reaches 100
    if plan.progress_percentage >= 100:
        plan.is_completed = True
        plan.completed_at = today
        plan.is_active = False
    
    db.commit()
    db.refresh(plan)
    db.refresh(current_user)
    
    return LogDayResponse(
        plan=PlanResponse.model_validate(plan),
        current_streak=current_user.current_streak,
        message=f"Day {log_day_req.day_number} logged successfully!"
    )


@router.get("/weekly-report", response_model=WeeklyReportResponse)
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get weekly progress report for current week.
    Returns completion status, exercises done, and streak info.
    """
    from datetime import datetime as dt, timedelta
    
    # Get current ISO week and year
    now = dt.utcnow()
    iso_calendar = now.isocalendar()
    current_week = iso_calendar[1]
    current_year = iso_calendar[0]
    
    # Query active plan to get rest days
    active_plan = db.query(Plan).filter(
        Plan.user_id == current_user.id,
        Plan.is_active == True
    ).first()
    
    # Get workout logs for this week
    week_logs = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.week_number == current_week,
        WorkoutLog.year == current_year
    ).all()
    
    # Get last week's exercises for comparison
    last_week = current_week - 1
    last_year = current_year
    if last_week < 1:
        last_week = 52
        last_year -= 1
    
    last_week_logs = db.query(WorkoutLog).filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.week_number == last_week,
        WorkoutLog.year == last_year
    ).all()
    
    # Calculate metrics
    days_completed = len(set(log.day_number for log in week_logs))
    exercises_done = sum(log.exercises_completed for log in week_logs)
    last_week_exercises = sum(log.exercises_completed for log in last_week_logs)
    
    # Parse rest days from active plan
    rest_days = 0
    rest_day_set = set()
    if active_plan:
        try:
            schedule = json.loads(active_plan.workout_schedule) if isinstance(active_plan.workout_schedule, str) else active_plan.workout_schedule
            if isinstance(schedule, dict) and "days" in schedule:
                for day in schedule["days"]:
                    if day.get("is_rest_day"):
                        rest_day_set.add(day.get("day", 0))
                rest_days = len(rest_day_set)
        except (json.JSONDecodeError, ValueError):
            rest_days = 0
    
    # Build completion grid (Mon-Sun for this week)
    days_of_week = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    completed_days = set(log.day_number for log in week_logs)
    completion_grid = []
    
    for i, day_name in enumerate(days_of_week):
        day_num = i + 1
        if day_num in completed_days:
            status = "completed"
        elif day_num in rest_day_set:
            status = "rest"
        elif day_num < now.weekday() + 1:
            status = "missed"
        else:
            status = "upcoming"
        completion_grid.append(CompletionGridItem(day=day_name, status=status))
    
    # Calculate volume change with explicit zero-baseline handling
    if last_week_exercises == 0:
        # No baseline from last week, return 0 instead of dividing by zero
        volume_change_percent = 0
    else:
        # Calculate percent change: (this_week - last_week) / last_week * 100
        volume_change_percent = round(((exercises_done - last_week_exercises) / last_week_exercises * 100))
    
    # Week range
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
    
    return WeeklyReportResponse(
        week_range=week_range,
        days_completed=days_completed,
        exercises_done=exercises_done,
        rest_days=rest_days,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        streak_target=20,
        volume_change_percent=volume_change_percent,
        completion_grid=completion_grid
    )


class UsageResponse(BaseModel):
    workout_count: int
    workout_limit: int
    nutrition_count: int
    nutrition_limit: int


@router.get("/usage-today", response_model=UsageResponse)
async def get_usage_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current day's AI generation usage for the user.
    Returns counts and limits for workout and nutrition plans.
    """
    redis_client = get_redis_client()
    date_str = datetime.now().strftime("%Y-%m-%d")
    user_id = str(current_user.id)
    
    workout_count = 0
    nutrition_count = 0
    
    try:
        workout_key = f"workout_requests:{user_id}:{date_str}"
        nutrition_key = f"nutrition_requests:{user_id}:{date_str}"
        
        workout_val = await redis_client.get(workout_key)
        nutrition_val = await redis_client.get(nutrition_key)
        
        workout_count = int(workout_val) if workout_val else 0
        nutrition_count = int(nutrition_val) if nutrition_val else 0
    except Exception:
        # Redis unavailable, default to 0
        pass
    
    return UsageResponse(
        workout_count=workout_count,
        workout_limit=2,
        nutrition_count=nutrition_count,
        nutrition_limit=2
    )


class CacheDeleteResponse(BaseModel):
    message: str


@router.delete("/cache", response_model=CacheDeleteResponse)
def clear_plan_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear completed plans from storage.
    Deletes all inactive, completed plans for the user.
    Cascades delete to associated WorkoutLog rows to prevent orphans.
    """
    # First, identify all Plan IDs matching the filter
    plans_to_delete = db.query(Plan.id).filter(
        Plan.user_id == current_user.id,
        Plan.is_active == False,
        Plan.is_completed == True
    ).all()
    
    plan_ids = [plan[0] for plan in plans_to_delete]
    
    # Delete dependent WorkoutLog rows first (prevents orphans)
    if plan_ids:
        db.query(WorkoutLog).filter(WorkoutLog.plan_id.in_(plan_ids)).delete()
    
    # Then delete the Plan rows using the same filter
    deleted_count = db.query(Plan).filter(
        Plan.user_id == current_user.id,
        Plan.is_active == False,
        Plan.is_completed == True
    ).delete()
    
    db.commit()
    
    return CacheDeleteResponse(
        message=f"Storage cleared. {deleted_count} completed plan(s) removed."
    )
