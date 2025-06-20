#!/usr/bin/env python3
"""
Simple health test to diagnose Railway 500 errors
This will help us identify what's causing the request-level failures
"""

import os
import sys
import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create minimal app
app = FastAPI(title="Health Test", description="Minimal test to diagnose 500 errors")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-production-e178.up.railway.app",
        "https://frontend-production-88b0.up.railway.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and return detailed error info"""
    logger.error(f"Global exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    try:
        logger.info("Root endpoint called")
        return {
            "message": "Health test running",
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        raise

@app.get("/test/basic")
async def test_basic():
    """Basic test"""
    try:
        logger.info("Basic test called")
        return {
            "test": "basic",
            "status": "pass",
            "environment": {
                "DATABASE_URL": "SET" if os.getenv('DATABASE_URL') else "NOT_SET",
                "JWT_SECRET_KEY": "SET" if os.getenv('JWT_SECRET_KEY') else "NOT_SET"
            }
        }
    except Exception as e:
        logger.error(f"Basic test error: {e}")
        raise

@app.get("/test/database")
async def test_database():
    """Test database connection"""
    try:
        logger.info("Database test starting...")
        
        # Try importing database service
        try:
            from services.database import db_service
            logger.info("Database service imported successfully")
        except Exception as e:
            logger.error(f"Failed to import database service: {e}")
            return {
                "test": "database",
                "status": "fail",
                "error": f"Import failed: {e}",
                "phase": "import"
            }
        
        # Try health check
        try:
            health = db_service.health_check()
            logger.info(f"Database health check result: {health}")
            return {
                "test": "database",
                "status": "pass",
                "health": health
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "test": "database", 
                "status": "fail",
                "error": str(e),
                "phase": "health_check"
            }
            
    except Exception as e:
        logger.error(f"Database test error: {e}")
        raise

@app.get("/test/auth")
async def test_auth():
    """Test auth service"""
    try:
        logger.info("Auth test starting...")
        
        # Try importing auth service
        try:
            from services.auth_service import auth_service
            logger.info("Auth service imported successfully")
        except Exception as e:
            logger.error(f"Failed to import auth service: {e}")
            return {
                "test": "auth",
                "status": "fail", 
                "error": f"Import failed: {e}",
                "phase": "import"
            }
        
        return {
            "test": "auth",
            "status": "pass",
            "service_available": True
        }
            
    except Exception as e:
        logger.error(f"Auth test error: {e}")
        raise

@app.get("/test/dependencies")
async def test_dependencies():
    """Test dependencies"""
    try:
        logger.info("Dependencies test starting...")
        
        # Try importing dependencies
        try:
            from dependencies import get_current_user_id
            logger.info("Dependencies imported successfully")
        except Exception as e:
            logger.error(f"Failed to import dependencies: {e}")
            return {
                "test": "dependencies",
                "status": "fail",
                "error": f"Import failed: {e}",
                "phase": "import"
            }
        
        return {
            "test": "dependencies",
            "status": "pass"
        }
            
    except Exception as e:
        logger.error(f"Dependencies test error: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 