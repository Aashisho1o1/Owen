"""
DOG Writer Backend - AI Writing Assistant MVP
Clean main application file with modular architecture.
Refactored from 934-line God file to focused app initialization.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

# Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import our PostgreSQL services
from services.database import db_service

# Import all routers
from routers.auth_router import router as auth_router
from routers.document_router import router as document_router
from routers.folder_router import router as folder_router
from routers.template_router import router as template_router
from routers.chat_router import router as chat_router
from routers.grammar_router import router as grammar_router

# Import security middleware
from middleware.security_middleware import SecurityMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CRITICAL: JWT Secret validation - fail startup if not configured
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY not properly configured!")
    logger.error("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")

if len(JWT_SECRET_KEY) < 32:
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY too short! Must be at least 32 characters")
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

logger.info("✅ JWT_SECRET_KEY properly configured")

# App initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup with enhanced error reporting"""
    try:
        logger.info("🚀 Starting DOG Writer MVP backend...")
        
        # Check critical environment variables first
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
        
        # Test database connection before initializing schema
        logger.info("🔍 Testing database connectivity...")
        health = db_service.health_check()
        if health['status'] != 'healthy':
            error_msg = f"❌ DATABASE HEALTH CHECK FAILED: {health.get('error', 'Unknown error')}"
            logger.error(error_msg)
            logger.error("💡 DEBUGGING TIPS:")
            logger.error("   1. Check if Railway PostgreSQL service is running")
            logger.error("   2. Verify DATABASE_URL uses 'postgres.railway.internal:5432'")
            logger.error("   3. Ensure DATABASE_URL has correct credentials")
            logger.error("   4. Check if DATABASE_URL env var is actually set in Railway")
            raise RuntimeError(error_msg)
        
        logger.info("✅ Database connectivity confirmed")
        
        # Initialize database schema
        logger.info("📊 Initializing database schema...")
        db_service.init_database()
        logger.info("✅ Database schema initialized successfully")
        
        # Final health check
        final_health = db_service.health_check()
        logger.info(f"✅ Final health check: {final_health['status']}")
        logger.info(f"📊 Database stats: {final_health.get('total_users', 0)} users, {final_health.get('total_documents', 0)} documents")
        
        logger.info("🎉 DOG Writer MVP backend started successfully!")
        yield
        
    except Exception as e:
        logger.error(f"❌ CRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
        logger.error("🔧 This will cause 500 errors on all endpoints")
        
        # Still yield to prevent FastAPI from crashing completely
        # This allows the health endpoint to return error information
        yield
    finally:
        logger.info("🔄 Shutting down database connections...")
        try:
            # Ensure we're in the right context for database cleanup
            if hasattr(db_service, 'close'):
                db_service.close()
                logger.info("✅ Database connections closed cleanly")
        except Exception as e:
            logger.error(f"⚠️ Error during shutdown: {e}")
        finally:
            # Give a moment for cleanup to complete
            await asyncio.sleep(0.1)

app = FastAPI(
    title="DOG Writer MVP",
    description="AI Writing Assistant with Modular Architecture",
    version="3.1.0-REFACTORED",
    lifespan=lifespan
)

# CRITICAL: CORS middleware MUST be added BEFORE Security middleware
# This ensures CORS preflight OPTIONS requests are handled before security checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-production-e178.up.railway.app",  # Your NEW frontend URL
        "https://frontend-production-88b0.up.railway.app",  # Keep old as backup
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
    allow_credentials=True,  # Enable credentials for auth tokens
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Added PATCH and explicit OPTIONS
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
    expose_headers=["*"],  # Allow frontend to access response headers
)

# Add security middleware AFTER CORS middleware
# TEMPORARILY DISABLED FOR DEBUGGING
# app.add_middleware(SecurityMiddleware)

# Include all modular routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(folder_router)
app.include_router(template_router)
app.include_router(chat_router)
app.include_router(grammar_router)

# Explicit CORS preflight handler for all routes
@app.options("/{path:path}")
async def preflight_handler(path: str):
    """Handle CORS preflight requests for all paths"""
    return {"message": "OK"}

# Health endpoints
@app.get("/")
async def root():
    """Root endpoint for Railway health checks"""
    try:
        db_health = db_service.health_check()
        return {
            "message": "DOG Writer - AI Writing Assistant MVP",
            "version": "3.1.0-REFACTORED",
            "status": "healthy",
            "database": db_health['status'],
            "railway_deployment": "success",
            "architecture": "modular",
            "features": [
                "ai_writing_assistance",
                "document_management",
                "grammar_checking",
                "template_system",
                "folder_organization",
                "auto_save"
            ]
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return {
            "message": "DOG Writer - AI Writing Assistant MVP",
            "version": "3.1.0-REFACTORED", 
            "status": "unhealthy",
            "error": str(e),
            "railway_deployment": "partial_failure"
        }

@app.get("/api/health")
async def health_check(request: Request = None):
    """Enhanced health check with detailed diagnostics"""
    try:
        # Basic environment check
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
        
        # CORS debugging information
        cors_info = {
            "allowed_origins": [
                "https://frontend-production-e178.up.railway.app",  # NEW frontend URL
                "https://frontend-production-88b0.up.railway.app",  # Keep old as backup
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
            "request_origin": request.headers.get("origin") if request else None,
            "request_method": request.method if request else None,
            "request_headers": dict(request.headers) if request else None
        }
        
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": env_status,
            "database": db_health,
            "cors_debug": cors_info,
            "version": "3.1.0-REFACTORED",
            "architecture": "modular",
            "debug_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
            }
        }
        
        # Add specific error guidance
        if overall_status == "unhealthy":
            response["troubleshooting"] = {
                "common_issues": [
                    "DATABASE_URL not set or incorrect format",
                    "PostgreSQL service not running",
                    "Using external URL instead of postgres.railway.internal",
                    "Missing JWT_SECRET_KEY",
                    "Network connectivity issues"
                ],
                "railway_specific": [
                    "Check Railway PostgreSQL service status",
                    "Verify environment variables are set in Railway dashboard",
                    "Use internal URL: postgres.railway.internal:5432",
                    "Ensure both backend and database services are deployed"
                ],
                "cors_specific": [
                    "Verify frontend URL matches allowed origins",
                    "Check if CORS preflight requests are being blocked",
                    "Ensure OPTIONS method is allowed",
                    "Verify security middleware allows CORS preflight"
                ]
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": f"Health check failed: {str(e)}",
            "error_type": type(e).__name__
        }

# Railway uses start.sh script to start the hypercorn server
# No direct execution needed in main.py 