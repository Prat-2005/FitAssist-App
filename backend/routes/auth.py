"""
Authentication Routes
Handles user registration, login, logout, and token refresh
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta

from schemas import UserRegister, UserLogin
from models import User
from db import get_db
from middleware import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_pwd = hash_password(user_data.password)
    
    new_user = User(
        first_name=user_data.first_name,
        email=user_data.email,
        password_hash=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


from db import cache_set
from middleware import security, verify_token
from fastapi.security import HTTPAuthorizationCredentials
import datetime

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user (invalidate token)
    """
    token = credentials.credentials
    payload = verify_token(token)
    exp = payload.get("exp")
    if exp:
        now = datetime.datetime.utcnow().timestamp()
        ttl = int(exp - now)
        if ttl > 0:
            if not await cache_set(f"blacklist_{token}", "revoked", ttl=ttl):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Token revocation is temporarily unavailable",
                )
    return {"message": "Successfully logged out"}
