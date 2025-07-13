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
from routers.fiction_template_router import router as fiction_template_router, legacy_router as legacy_template_router
from routers.chat_router import router as chat_router
from routers.grammar_router import router as grammar_router
from routers.indexing_router import router as indexing_router
from routers.story_generator_router import router as story_generator_router

# Import security middleware
from middleware.security_middleware import SecurityMiddleware

# Import rate limiter for health checks
from services.rate_limiter import rate_limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CRITICAL: JWT Secret validation - fail startup if not configured
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    logger.critical("🚨 SECURITY CRITICAL: JWT_SECRET_KEY environment variable is not set!")
    logger.critical("This is a critical security vulnerability that MUST be fixed before deployment")
    logger.critical("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    logger.critical("Set JWT_SECRET_KEY in Railway dashboard -> Variables tab")
    raise ValueError("JWT_SECRET_KEY must be configured for secure authentication")

if len(JWT_SECRET_KEY) < 32:
    logger.critical("🚨 SECURITY CRITICAL: JWT_SECRET_KEY is too short!")
    logger.critical(f"Current length: {len(JWT_SECRET_KEY)} characters, minimum required: 32")
    logger.critical("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for security")

logger.info("✅ JWT_SECRET_KEY configured (length: %d chars)", len(JWT_SECRET_KEY))

# App initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup with enhanced error reporting"""
    startup_success = True
    startup_errors = []
    
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
                startup_errors.append(error_msg)
                startup_success = False
            else:
                logger.info(f"✅ {var_name}: Configured")
        
        # Only try database operations if DATABASE_URL is set
        if os.getenv('DATABASE_URL'):
            try:
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
                    startup_errors.append(error_msg)
                    startup_success = False
                else:
                    logger.info("✅ Database connectivity confirmed")
                    
                    # Initialize database schema
                    logger.info("📊 Initializing database schema...")
                    db_service.init_database()
                    logger.info("✅ Database schema initialized successfully")
                    
                    # Final health check
                    final_health = db_service.health_check()
                    logger.info(f"✅ Final health check: {final_health['status']}")
                    logger.info(f"📊 Database stats: {final_health.get('total_users', 0)} users, {final_health.get('total_documents', 0)} documents")
            except Exception as db_error:
                error_msg = f"❌ DATABASE INITIALIZATION FAILED: {type(db_error).__name__}: {db_error}"
                logger.error(error_msg)
                startup_errors.append(error_msg)
                startup_success = False
        else:
            logger.warning("⚠️ DATABASE_URL not set - database operations will fail")
            startup_errors.append("DATABASE_URL not configured")
            startup_success = False
        
        if startup_success:
            logger.info("🎉 DOG Writer MVP backend started successfully!")
        else:
            logger.error("⚠️ Backend started with errors - some features may not work")
            logger.error(f"Startup errors: {startup_errors}")
        
        # Store startup status for health checks
        app.state.startup_success = startup_success
        app.state.startup_errors = startup_errors
        
        yield
        
    except Exception as e:
        logger.error(f"❌ CRITICAL STARTUP FAILURE: {type(e).__name__}: {e}")
        logger.error("🔧 This will cause 500 errors on all endpoints")
        
        # Store error information for health checks
        app.state.startup_success = False
        app.state.startup_errors = [f"Critical startup failure: {e}"]
        
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

# CRITICAL SECURITY: Enhanced CORS configuration with security considerations
# CORS middleware MUST be added BEFORE Security middleware
# This ensures CORS preflight OPTIONS requests are handled before security checks

# Define allowed origins with validation
ALLOWED_ORIGINS = [
    "https://www.owenwrites.co",                           # NEW: Primary custom domain
    "https://owenwrites.co",                               # NEW: Fallback without www
    "https://frontend-copy-production-0866.up.railway.app",  # NEW: Testing frontend
    "https://frontend-production-e178.up.railway.app",  # OLD: Keep as backup
    "https://frontend-production-88b0.up.railway.app",  # OLD: Keep as backup
    "https://owen-ai-writer.vercel.app",               # Vercel deployment
    # Local development origins
    "http://localhost:3000", "http://localhost:3001", 
    "http://localhost:4173", "http://localhost:5173", "http://localhost:5174",
    "http://localhost:5175", "http://localhost:5176", "http://localhost:5177",
    "http://localhost:5178", "http://localhost:5179", "http://localhost:8080"
]

# Validate origins format for security
import re
for origin in ALLOWED_ORIGINS:
    if not re.match(r'^https?://[a-zA-Z0-9.-]+(?::[0-9]+)?$', origin):
        logger.error(f"🚨 SECURITY: Invalid origin format detected: {origin}")
        raise ValueError(f"Invalid CORS origin format: {origin}")

# Log CORS configuration for security audit
logger.info(f"🔐 CORS: Configured {len(ALLOWED_ORIGINS)} allowed origins")
logger.info(f"🔐 CORS: Production origins: {[o for o in ALLOWED_ORIGINS if 'localhost' not in o]}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Required for authentication tokens
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
        "Access-Control-Request-Headers",
        # Security headers
        "X-CSRF-Token",
        "X-Requested-With"
    ],
    expose_headers=[
        "X-Total-Count",
        "X-Rate-Limit-Remaining", 
        "X-Rate-Limit-Reset"
    ],  # Only expose necessary headers for security
)

# Add security middleware AFTER CORS middleware
app.add_middleware(SecurityMiddleware)

# Include all modular routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(folder_router)
app.include_router(fiction_template_router)
app.include_router(legacy_template_router)  # Backward compatibility for /api/templates
app.include_router(chat_router)
app.include_router(grammar_router)
app.include_router(indexing_router)
app.include_router(story_generator_router)

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
            "database": "unhealthy",
            "railway_deployment": "partial_failure",
            "architecture": "modular",
            "features": [],
            "error": "An internal error occurred while processing the request."
        }

@app.get("/api/health")
async def health_check(request: Request = None):
    """Enhanced health check with detailed diagnostics"""
    try:
        # Check startup status
        startup_success = getattr(app.state, 'startup_success', False)
        startup_errors = getattr(app.state, 'startup_errors', [])
        
        # Basic environment check
        env_status = {
            "DATABASE_URL": "✅ SET" if os.getenv('DATABASE_URL') else "❌ NOT SET",
            "JWT_SECRET_KEY": "✅ SET" if os.getenv('JWT_SECRET_KEY') else "❌ NOT SET",
            "GEMINI_API_KEY": "✅ SET" if os.getenv('GEMINI_API_KEY') else "⚠️ NOT SET (optional)",
            "OPENAI_API_KEY": "✅ SET" if os.getenv('OPENAI_API_KEY') else "⚠️ NOT SET (optional)",
        }
        
        # Database health check (only if DATABASE_URL is set)
        db_health = {"status": "not_configured", "error": "DATABASE_URL not set"}
        if os.getenv('DATABASE_URL'):
            try:
                db_health = db_service.health_check()
            except Exception as e:
                db_health = {"status": "unhealthy", "error": str(e)}
        
        # Overall status
        overall_status = "healthy" if startup_success and db_health['status'] == 'healthy' else "unhealthy"
        
        # CORS debugging information
        cors_info = {
            "allowed_origins": ALLOWED_ORIGINS,
            "request_origin": request.headers.get("origin") if request else None,
            "request_method": request.method if request else None,
            "user_agent": request.headers.get("user-agent") if request else None
        }
        
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "startup": {
                "success": startup_success,
                "errors": startup_errors
            },
            "environment": env_status,
            "database": db_health,
            "cors_debug": cors_info,
            "version": "3.1.0-REFACTORED",
            "architecture": "modular",
            "debug_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform,
                "railway_environment": os.getenv('RAILWAY_ENVIRONMENT', 'unknown'),
                "railway_service": os.getenv('RAILWAY_SERVICE', 'unknown')
            }
        }
        
        # Add specific error guidance
        if overall_status == "unhealthy":
            response["troubleshooting"] = {
                "startup_errors": startup_errors,
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
                    "Ensure both backend and database services are deployed",
                    "Check Railway deployment logs for specific errors"
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
            "error_type": "HealthCheckFailed",
            "error_message": "An internal error occurred during the health check.",
            "startup": {
                "success": False,
                "errors": ["Health check failed due to an internal error."]
            }
        }

@app.get("/api/rate-limiter/health")
async def rate_limiter_health():
    """Get rate limiter health and statistics"""
    try:
        # Get basic rate limiter info
        return {
            "status": "healthy",
            "backend": "memory",
            "redis_connected": False,
            "message": "Using in-memory rate limiting - suitable for single instance deployment",
            "limits": rate_limiter.limits,
            "blocked_ips": len(rate_limiter.blocked_ips),
            "active_requests": len(rate_limiter.request_counts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Rate limiter health check error: {e}")
        return {
            "status": "error",
            "backend": "unknown",
            "error": "An internal error occurred while checking rate limiter health.",
            "timestamp": datetime.utcnow().isoformat()
        }

# Railway uses start.sh script to start the hypercorn server
# No direct execution needed in main.py 