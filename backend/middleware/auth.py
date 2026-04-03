"""
JWT Authentication Middleware
Handles JWT token verification and user authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import bcrypt

# Get JWT secret from environment
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY must be set")
ALGORITHM = "HS256"


from sqlalchemy.orm import Session
from db import get_db, cache_get
from models import User

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Verify JWT token and retrieve the current user.
    Also checks redis blacklist for revoked tokens.
    """
    token = credentials.credentials
    import db.redis
    if not db.redis.REDIS_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security Service (Redis) is currently offline. Cannot securely verify token blacklist status."
        )

    # Check if token is blacklisted
    is_blacklisted = await cache_get(f"blacklist_{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = verify_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    from starlette.concurrency import run_in_threadpool
    def get_user_from_db():
        return db.query(User).filter(User.email == email).first()
        
    user = await run_in_threadpool(get_user_from_db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


security_optional = HTTPBearer(auto_error=False)

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional), db: Session = Depends(get_db)):
    """
    Verify JWT token if present, otherwise gracefully return None.
    """
    import db.redis
    if not db.redis.REDIS_AVAILABLE:
        # Gracefully degrade to unauthenticated state if system cannot verify revocations
        return None

    if not credentials:
        return None
    token = credentials.credentials
        
    is_blacklisted = await cache_get(f"blacklist_{token}")
    if is_blacklisted:
        return None
        
    try:
        payload = verify_token(token)
        email = payload.get("sub")
        if not email:
            return None
    except HTTPException:
        return None
        
    from starlette.concurrency import run_in_threadpool
    def get_user_from_db():
        return db.query(User).filter(User.email == email).first()
        
    user = await run_in_threadpool(get_user_from_db)
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing token claims
        expires_delta: Optional expiration delta
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        bool: True if password matches
    """
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)
