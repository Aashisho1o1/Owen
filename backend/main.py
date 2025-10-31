"""
Minimal FastAPI Backend for Competition
Chrome Built-in AI Challenge 2025
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth_router, character_voice_router
from services.database import db_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Owen Voice Analyzer Backend")

    # Connect to database
    await db_service.connect()

    yield

    # Cleanup
    logger.info("👋 Shutting down")
    await db_service.disconnect()

# Create FastAPI app
app = FastAPI(
    title="Owen Voice Analyzer API",
    description="Character voice consistency analysis for fiction writers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(character_voice_router.router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Owen Voice Analyzer",
        "version": "1.0.0",
        "database": "connected" if db_service.is_available() else "disconnected"
    }

@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": db_service.is_available(),
        "timestamp": "2025-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
