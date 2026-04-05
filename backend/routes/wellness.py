"""
Wellness Log Routes
Handles wellness metric logging and retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from db import get_db
from models import User, WellnessLog
from schemas import WellnessLogCreate, WellnessLogResponse
from middleware import get_current_user

router = APIRouter()


@router.post("", response_model=WellnessLogResponse)
def log_wellness(
    wellness_data: WellnessLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log or update today's wellness metrics.
    Uses upsert logic: if entry exists for today, update it; otherwise create new.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Check if entry exists for today
    existing_log = db.query(WellnessLog).filter(
        WellnessLog.user_id == current_user.id,
        WellnessLog.date == today_str
    ).first()
    
    if existing_log:
        # Update existing entry
        if wellness_data.body_battery is not None:
            existing_log.body_battery = wellness_data.body_battery
        if wellness_data.sleep_score is not None:
            existing_log.sleep_score = wellness_data.sleep_score
        if wellness_data.hydration_liters is not None:
            existing_log.hydration_liters = wellness_data.hydration_liters
        
        existing_log.logged_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_log)
        return existing_log
    else:
        # Create new entry
        new_log = WellnessLog(
            user_id=current_user.id,
            body_battery=wellness_data.body_battery,
            sleep_score=wellness_data.sleep_score,
            hydration_liters=wellness_data.hydration_liters,
            date=today_str,
            logged_at=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log


@router.get("", response_model=WellnessLogResponse)
def get_today_wellness(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's wellness entry.
    Returns current day's wellness metrics.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    wellness_log = db.query(WellnessLog).filter(
        WellnessLog.user_id == current_user.id,
        WellnessLog.date == today_str
    ).first()
    
    if not wellness_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No wellness entry for today"
        )
    
    return wellness_log
