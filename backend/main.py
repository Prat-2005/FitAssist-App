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
from routes import auth, profile, plan
from db.database import init_db

# Note: JWTMiddleware is commented out until fully implemented
# from middleware.auth import JWTMiddleware

# Initialize FastAPI application
app = FastAPI(
    title="FitAssist",
    description="The Personal fitness trainer App",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure allowed origins from environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT authentication middleware
# TODO: Uncomment when JWTMiddleware is fully implemented
# app.add_middleware(JWTMiddleware)

# Include route modules
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(plan.router, prefix="/api/plan", tags=["Fitness Plans"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    """
    return {"status": "healthy", "service": "FitAssist API"}

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    TODO: Add other startup tasks (Redis connection, cache warming, etc.)
    """
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown
    TODO: Add cleanup tasks (close Redis connection, etc.)
    """
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
