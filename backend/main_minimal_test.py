"""
Minimal main.py to test lifespan issues
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CRITICAL: JWT Secret validation
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or JWT_SECRET_KEY == "your-secret-key-here-please-change-in-production":
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY not properly configured!")
    raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")

if len(JWT_SECRET_KEY) < 32:
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY too short!")
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

logger.info("✅ JWT_SECRET_KEY properly configured")

# Test the lifespan function (this might be the issue)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Test lifespan function"""
    try:
        logger.info("🚀 Starting DOG Writer MVP backend...")
        
        # Check environment variables
        critical_vars = {
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
        }
        
        for var_name, var_value in critical_vars.items():
            if not var_value:
                error_msg = f"❌ CRITICAL: {var_name} environment variable is not set!"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            else:
                logger.info(f"✅ {var_name}: Configured")
        
        # Test database import and connection
        logger.info("🔍 Testing database connectivity...")
        from services.database import db_service
        
        health = db_service.health_check()
        if health['status'] != 'healthy':
            error_msg = f"❌ DATABASE HEALTH CHECK FAILED: {health.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info("✅ Database connectivity confirmed")
        
        # Initialize database schema
        logger.info("📊 Initializing database schema...")
        db_service.init_database()
        logger.info("✅ Database schema initialized successfully")
        
        logger.info("🎉 DOG Writer MVP backend started successfully!")
        yield
        
    except Exception as e:
        logger.error(f"❌ CRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
        logger.error("🔧 This will cause 500 errors on all endpoints")
        # Still yield to prevent FastAPI from crashing completely
        yield
    finally:
        logger.info("🔄 Shutting down...")
        await asyncio.sleep(0.1)

# Create app with lifespan
app = FastAPI(
    title="DOG Writer MVP - Minimal Test",
    description="Testing lifespan issues",
    version="3.0.0-MVP",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-production-e178.up.railway.app",
        "https://frontend-production-88b0.up.railway.app", 
        "https://owen-ai-writer.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:4173",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175", 
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "X-Requested-With",
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

@app.options("/{path:path}")
async def preflight_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/")
async def root():
    """Root endpoint"""
    try:
        from services.database import db_service
        db_health = db_service.health_check()
        return {
            "message": "DOG Writer - AI Writing Assistant MVP",
            "version": "3.0.0-MVP",
            "status": "healthy",
            "database": db_health['status'],
            "railway_deployment": "success"
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return {
            "message": "DOG Writer - AI Writing Assistant MVP",
            "version": "3.0.0-MVP", 
            "status": "unhealthy",
            "error": str(e),
            "railway_deployment": "partial_failure"
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        from services.database import db_service
        
        # Environment check
        env_status = {
            "DATABASE_URL": "✅ SET" if os.getenv('DATABASE_URL') else "❌ NOT SET",
            "JWT_SECRET_KEY": "✅ SET" if os.getenv('JWT_SECRET_KEY') else "❌ NOT SET",
            "GEMINI_API_KEY": "✅ SET" if os.getenv('GEMINI_API_KEY') else "❌ NOT SET",
            "OPENAI_API_KEY": "✅ SET" if os.getenv('OPENAI_API_KEY') else "❌ NOT SET",
        }
        
        # Database health check
        db_health = db_service.health_check()
        
        # Overall status
        overall_status = "healthy" if db_health['status'] == 'healthy' else "unhealthy"
        if "❌ NOT SET" in env_status.values():
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "environment": env_status,
            "database": db_health,
            "version": "3.0.0-MVP"
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": f"Health check failed: {str(e)}",
            "error_type": type(e).__name__
        }

# Basic auth endpoints for testing
@app.post("/api/auth/register")
async def register():
    """Test registration endpoint"""
    return {"message": "Registration endpoint working", "test": True}

@app.post("/api/auth/login") 
async def login():
    """Test login endpoint"""
    return {"message": "Login endpoint working", "test": True}
