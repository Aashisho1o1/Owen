"""
DOG Writer API - Main Application Entry Point

A culturally-aware AI writing assistant with productivity analytics.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

# Import all routers
from routers import (
    chat_router,
    voice_router, 
    manga_router,
    checkpoint_router,
    session_router
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 DOG Writer API starting up...")
    yield
    logger.info("📝 DOG Writer API shutting down...")

# Initialize FastAPI application with lifespan events
app = FastAPI(
    title="DOG Writer API", 
    description="AI-powered writing assistant with productivity analytics",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration - Flexible for development
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Default Vite port
    "http://localhost:5174",  # Alternative Vite port
    "http://localhost:5175",  # Another alternative
    "http://localhost:3000",  # Common React port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174", 
    "http://127.0.0.1:5175",
    "http://localhost:8000",  # API self-reference if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions globally"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions globally"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "detail": "An unexpected error occurred"
        }
    )

# Health Check Endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """API health check endpoint"""
    return {"status": "ok", "message": "DOG Writer API is running"}

# Include all routers with proper prefixes
app.include_router(chat_router.router, prefix="/api")
app.include_router(voice_router.router, prefix="/api") 
app.include_router(manga_router.router)  # Already has /api/manga prefix
app.include_router(checkpoint_router.router)  # Already has /api/checkpoint prefix
app.include_router(session_router.router)  # Already has /api/sessions prefix

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 