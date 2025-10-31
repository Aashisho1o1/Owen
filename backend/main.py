import os
import sys
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Disable ChromaDB telemetry to prevent backend crashes on Railway (connection test: comment updated)
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# --- Centralized Logging Configuration ---
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True
        },
        "chromadb.telemetry": {
            "level": "CRITICAL",
            "handlers": ["console"],
            "propagate": False
        },
        "chromadb.telemetry.product.posthog": {
            "level": "CRITICAL",
            "handlers": ["console"],
            "propagate": False
        }
    }
}

# Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

# Add comprehensive startup logging
print("🚀 DOG Writer Backend Starting...")
print(f"📍 Current working directory: {os.getcwd()}")
print(f"🐍 Python version: {sys.version}")
print(f"🌍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
print(f"🔧 PORT: {os.getenv('PORT', 'not set')}")
print(f"🔑 JWT_SECRET_KEY: {'✅ SET' if os.getenv('JWT_SECRET_KEY') else '❌ NOT SET'}")
print(f"🗄️ DATABASE_URL: {'✅ SET' if os.getenv('DATABASE_URL') else '❌ NOT SET'}")

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI imports successful")
except Exception as e:
    print(f"❌ FastAPI imports failed: {e}")
    sys.exit(1)

try:
    # Import our PostgreSQL services with lazy initialization
    from services.database import get_db_service
    print("✅ Database service import successful")
except Exception as e:
    print(f"❌ Database service import failed: {e}")
    # Continue without database for now
    get_db_service = None

# Import all routers with error handling - Cleaned up for Google AI competition
routers_to_import = [
    ("routers.auth_router", "auth_router"),
    ("routers.document_router", "document_router"),
    ("routers.folder_router", "folder_router"),
    ("routers.chat_router", "chat_router"),
    # grammar_router removed - non-essential feature
    ("routers.indexing_router", "indexing_router"),
    ("routers.story_generator_router", "story_generator_router"),
    ("routers.character_voice_router", "character_voice_router"),
    ("routers.cost_optimization_router", "cost_optimization_router"),
    # local_ai_router removed - using Google Gemini only
]

imported_routers = []
for module_name, router_name in routers_to_import:
    try:
        print(f"🔄 Importing {router_name} from {module_name}...")
        module = __import__(module_name, fromlist=[router_name])
        router = getattr(module, "router")
        imported_routers.append((router_name, router))
        print(f"✅ {router_name} imported successfully")
        # DEBUG: Check if router has routes
        if hasattr(router, 'routes'):
            print(f"   Router has {len(router.routes)} routes defined")
        else:
            print(f"   ⚠️ Router has no routes attribute")
    except Exception as e:
        print(f"❌ {router_name} import failed: {e}")
        import traceback
        print(f"   Import error details: {traceback.format_exc()}")
        # Continue without this router

try:
    # Import security middleware
    from middleware.security_middleware import SecurityMiddleware
    print("✅ Security middleware import successful")
except Exception as e:
    print(f"❌ Security middleware import failed: {e}")
    SecurityMiddleware = None

try:
    # Import rate limiter for health checks
    from services.rate_limiter import rate_limiter
    print("✅ Rate limiter import successful")
except Exception as e:
    print(f"❌ Rate limiter import failed: {e}")
    rate_limiter = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CRITICAL: Suppress ChromaDB telemetry errors at the logging level
# This prevents telemetry errors from appearing in logs even if they occur
chromadb_logger = logging.getLogger('chromadb.telemetry')
chromadb_logger.setLevel(logging.CRITICAL)  # Only show critical errors, not telemetry failures

posthog_logger = logging.getLogger('chromadb.telemetry.product.posthog')
posthog_logger.setLevel(logging.CRITICAL)  # Suppress PostHog telemetry errors

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
        print("🚀 Starting DOG Writer MVP backend lifespan...")
        logger.info("🚀 Starting DOG Writer MVP backend...")
        
        # Check critical environment variables first
        critical_vars = {
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
        }
        
        print(f"🔍 Checking critical environment variables...")
        for var_name, var_value in critical_vars.items():
            status = "✅ SET" if var_value else "❌ NOT SET"
            print(f"   {var_name}: {status}")
        
        for var_name, var_value in critical_vars.items():
            if not var_value:
                error_msg = f"❌ CRITICAL: {var_name} environment variable is not set!"
                logger.error(error_msg)
                startup_errors.append(error_msg)
                startup_success = False
            else:
                logger.info(f"✅ {var_name}: Configured")
        
        # The database will be initialized lazily on the first request.
        # No need to initialize it here.
        
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
            db = get_db_service()
            if db and hasattr(db, 'close'):
                db.close()
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
    allow_origins=[origin for origin in ALLOWED_ORIGINS if origin],
    allow_credentials=True,
    # CRITICAL FIX: Add "POST", "PUT", and "DELETE" to allow all necessary API methods
    # This was the root cause of the 405 Method Not Allowed error
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    # Add a max_age to cache preflight responses for better performance
    max_age=600 # Cache for 10 minutes
)

# Add security middleware AFTER CORS middleware (if available)
security_middleware_instance = None
if SecurityMiddleware:
    app.add_middleware(SecurityMiddleware)
    print("✅ Security middleware added")
    # Note: We can't directly access the middleware instance from FastAPI
    # The admin endpoints will need to be implemented differently
else:
    print("⚠️ Security middleware not available - continuing without it")

# Include all imported routers
for router_name, router in imported_routers:
    try:
        app.include_router(router)
        print(f"✅ {router_name} included successfully")
    except Exception as e:
        print(f"❌ Failed to include {router_name}: {e}")

# Explicit CORS preflight handler for all routes
@app.options("/{path:path}")
async def preflight_handler(path: str):
    """Handle CORS preflight requests for all paths"""
    return {"message": "OK"}

# DEBUGGING: The character voice router is not being registered properly
# The issue is likely in the router import chain - let's check dependencies

# Health endpoints
@app.get("/")
async def root():
    """Root endpoint for Railway health checks"""
    try:
        if get_db_service:
            db_health = get_db_service().health_check()
            db_status = db_health['status']
        else:
            db_status = "unavailable"
        
        return {
            "message": "DOG Writer - AI Writing Assistant MVP",
            "version": "3.1.0-REFACTORED",
            "status": "healthy",
            "database": db_status,
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

@app.post("/admin/clear-rate-limits")
async def clear_rate_limits():
    """Admin endpoint to clear all rate limiting data"""
    try:
        # Since we can't access the middleware instance directly,
        # we'll return a message indicating the feature is not available
        # In production, this would be handled by a separate admin API
        return {"message": "Rate limiting data management not available in current setup"}
    except Exception as e:
        logger.error(f"Failed to clear rate limits: {e}")
        return {"error": "Failed to clear rate limits"}

@app.post("/admin/clear-ip-rate-limit/{ip}")
async def clear_ip_rate_limit(ip: str):
    """Admin endpoint to clear rate limiting data for a specific IP"""
    try:
        # Since we can't access the middleware instance directly,
        # we'll return a message indicating the feature is not available
        return {"message": f"IP rate limit management not available in current setup for IP: {ip}"}
    except Exception as e:
        logger.error(f"Failed to clear rate limit for IP {ip}: {e}")
        return {"error": f"Failed to clear rate limit for IP {ip}"}

@app.get("/api/health")
async def health_check(request: Request = None):
    """
    Enhanced health check endpoint
    Provides detailed status of the application and its dependencies.
    """
    # Get startup status from app state
    startup_success = app.state.startup_success if hasattr(app.state, 'startup_success') else False
    startup_errors = app.state.startup_errors if hasattr(app.state, 'startup_errors') else ["State not found"]
    
    db_status = "uninitialized"
    if get_db_service:
        try:
            db_status = get_db_service().health_check().get('status', 'error')
        except Exception as e:
            db_status = f"error: {str(e)}"

    # Check LLM service status
    llm_status = "unknown"
    try:
        from services.llm_service import llm_service, SERVICES_AVAILABLE, gemini_service
        llm_status = {
            "services_available": SERVICES_AVAILABLE,
            "gemini_exists": gemini_service is not None,
            "gemini_available": gemini_service.is_available() if gemini_service else False,
            "providers": list(llm_service.providers.keys()) if SERVICES_AVAILABLE else [],
            "env_var_set": bool(os.getenv("GEMINI_API_KEY"))
        }
    except Exception as e:
        llm_status = f"error: {str(e)}"

    response_data = {
        "status": "healthy" if startup_success and db_status == 'healthy' else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database_status": db_status,
        "llm_status": llm_status,
        "startup_errors": startup_errors,
        "api_version": "1.2.0",  # TRACER BULLET: Check for this version
        "deployment_verification": "CORS_FIX_APPLIED_SUCCESSFULLY" # TRACER BULLET
    }
    
    status_code = 200 if response_data["status"] == "healthy" else 503
    
    return JSONResponse(content=response_data, status_code=status_code)

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