"""
Redis Cache Configuration
Handles caching and session management with Redis
"""

import os
import redis.asyncio as redis
from typing import Optional

# Get Redis URL from environment
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Initialize Redis client
# TODO: Configure connection pooling and other parameters for production
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_redis_client() -> redis.Redis:
    """
    Get Redis client instance
    """
    return redis_client


REDIS_AVAILABLE = False  # Track cluster health deterministically safely

CACHE_PREFIX = "fitassist:"  # Define at module level


async def cache_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Set a key-value pair in Redis cache
    
    Args:
        key: Cache key
        value: Cache value
        ttl: Time to live in seconds (optional)
    
    Returns:
        bool: True if successful
    """
    try:
        full_key = f"{CACHE_PREFIX}{key}"
        if ttl:
            await redis_client.setex(full_key, ttl, value)
        else:
            await redis_client.set(full_key, value)
        return True
    except Exception as e:
        print(f"Redis cache_set error for {key}: {e}")
        return False


async def cache_get(key: str) -> Optional[str]:
    """
    Get a value from Redis cache
    
    Args:
        key: Cache key
    
    Returns:
        str or None: Cached value or None if not found
    """
    try:
        full_key = f"{CACHE_PREFIX}{key}"
        return await redis_client.get(full_key)
    except Exception as e:
        print(f"Redis cache_get error for {key}: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """
    Delete a key from Redis cache
    
    Args:
        key: Cache key
    
    Returns:
        bool: True if successful
    """
    try:
        full_key = f"{CACHE_PREFIX}{key}"
        await redis_client.delete(full_key)
        return True
    except Exception as e:
        print(f"Redis cache_delete error for {key}: {e}")
        return False


async def cache_clear() -> bool:
    """
    Clear all application cache keys (not entire database)
    
    Returns:
        bool: True if successful
    """
    try:
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match=f"{CACHE_PREFIX}*", count=100)
            if keys:
                await redis_client.delete(*keys)
            if cursor == 0:
                break
        return True
    except Exception as e:
        print(f"Redis cache_clear error: {e}")
        return False
