"""
Wellness Log Routes
Handles wellness metric logging and retrieval
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert, text
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
    Uses atomic upsert: INSERT with ON CONFLICT (user_id, date) DO UPDATE
    Ensures only one entry per user per day, even with concurrent requests.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Build insert statement with conflict handling
    stmt = insert(WellnessLog).values(
        user_id=current_user.id,
        date=today_str,
        body_battery=wellness_data.body_battery,
        sleep_score=wellness_data.sleep_score,
        hydration_liters=wellness_data.hydration_liters,
        logged_at=datetime.utcnow()
    ).on_conflict_do_update(
        index_elements=['user_id', 'date'],
        set_={
            'body_battery': wellness_data.body_battery,
            'sleep_score': wellness_data.sleep_score,
            'hydration_liters': wellness_data.hydration_liters,
            'logged_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ).returning(WellnessLog)
    
    # Execute atomic upsert
    result = db.execute(stmt)
    db.commit()
    
    # Fetch the upserted record
    wellness_log = db.query(WellnessLog).filter(
        WellnessLog.user_id == current_user.id,
        WellnessLog.date == today_str
    ).first()
    
    return wellness_log


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
