"""
FitAssist Backend - Main Entry Point
AI-powered fitness trainer application
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Import routes (use absolute imports)
from routes import auth_router as auth, profile_router as profile, plan_router as plan
from db import init_db


# Initialize FastAPI application
app = FastAPI(
    title="FitAssist",
    description="The Personal fitness trainer App",
    version="1.0.0"
)

# CORS middleware configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

if not origins:
    raise ValueError("ALLOWED_ORIGINS environment variable is empty or not set. Explicit origins are required when credentials are allowed.")
if "*" in origins:
    raise ValueError("ALLOWED_ORIGINS cannot contain '*' when allow_credentials=True. Please specify exact domain URLs.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include route modules
app.include_router(auth, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile, prefix="/api/profile", tags=["Profile"])
app.include_router(plan, prefix="/api/plan", tags=["Fitness Plans"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    return {"status": "healthy", "service": "FitAssist API"}

from db import get_redis_client

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    """
    init_db()
    
    # Check redis connection
    redis_client = get_redis_client()
    try:
        await redis_client.ping()
    except Exception as e:
        print(f"Warning: Redis connection failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown
    """
    redis_client = get_redis_client()
    await redis_client.aclose() if hasattr(redis_client, 'aclose') else await redis_client.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
