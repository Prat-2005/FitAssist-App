"""
User Profile Routes
Handles user profile management and personal information
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User, Profile, Plan
from schemas import ProfileCreate, ProfileUpdate, ProfileResponse, PublicProfileResponse
from middleware import get_current_user
import uuid

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me", response_model=ProfileResponse)
def update_profile(profile_data: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update current user profile. Creates one if it doesn't exist.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    if not profile:
        profile = Profile(user_id=current_user.id, **profile_data.model_dump(exclude_unset=True))
        db.add(profile)
    else:
        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
            
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}", response_model=PublicProfileResponse)
def get_user_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Get user profile by ID (public endpoint)
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/me")
def delete_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete user account and profile
    """
    # Delete associated plans first to avoid foreign key constraints
    db.query(Plan).filter(Plan.user_id == current_user.id).delete()
    
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile:
        db.delete(profile)
    db.delete(current_user)
    db.commit()
    return {"message": "Account and profile deleted successfully"}
