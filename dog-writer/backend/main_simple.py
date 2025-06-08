"""
DOG Writer API - Simplified Main Application for Railway Deployment
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Owen AI Writer API", 
    description="AI-powered writing assistant",
    version="1.0.0"
)

# CORS Configuration for Railway
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*"  # Allow all origins for initial deployment testing
]

# Add production URLs
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)
    logger.info(f"Added production frontend URL: {FRONTEND_URL}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health Check Endpoints
@app.get("/")
async def root():
    """Root endpoint for Railway health check"""
    return {
        "message": "Owen AI Writer API is running successfully!",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "message": "Owen AI Writer API is operational",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production")
    }

@app.get("/api/status")
async def status():
    """Extended status endpoint"""
    return {
        "api": "Owen AI Writer",
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "features": {
            "auth": "JWT Ready",
            "encryption": "Database Encryption Ready", 
            "validation": "Input Validation Ready",
            "ai": "OpenAI/Anthropic/Google Ready"
        }
    }

# Simple test endpoint
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"message": "API is working correctly", "test": "passed"}

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions gracefully"""
    logger.error(f"Error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    ) 