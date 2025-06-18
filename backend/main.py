"""
DOG Writer Backend API
FastAPI application with PostgreSQL database, JWT authentication,
and comprehensive document management for creative writing.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import services
from services.database import db_service
from services.auth_service import auth_service
from services.document_service import document_service

# Import routers
from routers.chat_router import router as chat_router
from routers.checkpoint_router import router as checkpoint_router
from routers.grammar_router import router as grammar_router
from routers.session_router import router as session_router

# Import routes
from routes.auth import router as auth_router
from routes.documents import router as documents_router
# from routes.analytics import router as analytics_router  # Temporarily disabled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting DOG Writer API with PostgreSQL")
    
    try:
        # Verify database connectivity
        health = db_service.health_check()
        if health['status'] == 'healthy':
            logger.info(f"✅ Database connected: {health['database_version']}")
            logger.info(f"📊 Users: {health['total_users']}, Documents: {health['total_documents']}")
        else:
            logger.error(f"❌ Database connection failed: {health.get('error', 'Unknown error')}")
            # Don't raise exception - let app start but mark as unhealthy
            logger.warning("⚠️ Starting app with unhealthy database - check environment variables")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.warning("⚠️ Starting app without database - check DATABASE_URL")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down DOG Writer API")
    try:
        db_service.close()
    except:
        pass

# Create FastAPI app
app = FastAPI(
    title="DOG Writer API",
    description="Creative writing platform with AI assistance and document management",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://frontend-production-88b0.up.railway.app",
        "https://*.railway.app",
        "https://*.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with API status"""
    return {
        "message": "DOG Writer API",
        "version": "2.0.0",
        "status": "healthy",
        "database": "postgresql"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        db_health = db_service.health_check()
        return {
            "status": "healthy" if db_health['status'] == 'healthy' else "unhealthy",
            "database": db_health,
            "services": {
                "auth": "healthy",
                "documents": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
# app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])  # Temporarily disabled

# Legacy routers (if still needed)
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(checkpoint_router, prefix="/api/checkpoints", tags=["Checkpoints"])
app.include_router(grammar_router, prefix="/api/grammar", tags=["Grammar"])
app.include_router(session_router, prefix="/api/session", tags=["Session"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable in production
        log_level="info"
    ) 