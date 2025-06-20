# Backend API - DOG Writer Document Management System
# Version 3.0.0-MVP - Lean and focused MVP with core features only
"""
DOG Writer Backend - AI Writing Assistant MVP
Core features: Authentication, Documents, AI Chat, Grammar Check, Basic Organization
"""

import os
import sys
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from enum import Enum
import asyncio

# Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

# Import our PostgreSQL services
from services.database import db_service, DatabaseError
from services.auth_service import auth_service, AuthenticationError

# Import centralized authentication dependency
from dependencies import get_current_user_id

# Import routers
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
if not JWT_SECRET_KEY or JWT_SECRET_KEY == "your-secret-key-here-please-change-in-production":
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY not properly configured!")
    logger.error("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")

if len(JWT_SECRET_KEY) < 32:
    logger.error("🚨 SECURITY CRITICAL: JWT_SECRET_KEY too short! Must be at least 32 characters")
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

logger.info("✅ JWT_SECRET_KEY properly configured")
security = HTTPBearer()

# Enums for better type safety
class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Story Writing Templates - Essential templates only
templates_store = [
    {
        "id": "blank",
        "title": "Blank Document",
        "description": "Start with a clean slate",
        "content": "",
        "category": "General"
    },
    {
        "id": "story",
        "title": "Short Story",
        "description": "Template for creative writing and storytelling",
        "content": "",
        "category": "Fiction"
    },
    {
        "id": "essay",
        "title": "Essay",
        "description": "Template for essays and articles",
        "content": "",
        "category": "Non-Fiction"
    }
]

# Pydantic Models - Essential models only
class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, description="User's full name")

class UserLogin(BaseModel):
    email: str
    password: str

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    color: Optional[str] = "#3B82F6"

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template_id: Optional[str] = None
    folder_id: Optional[str] = None
    status: DocumentStatus = DocumentStatus.DRAFT

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[DocumentStatus] = None
    folder_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = 1800  # 30 minutes
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class DocumentFromTemplateCreate(BaseModel):
    template_id: str = Field(..., description="Template ID to use")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    folder_id: Optional[str] = None

# Helper functions - Essential only
def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user details by ID"""
    try:
        result = db_service.execute_query(
            "SELECT id, username, name, email, created_at FROM users WHERE id = %s AND is_active = TRUE",
            (user_id,),
            fetch='one'
        )
        return dict(result) if result else None
    except Exception:
        return None

def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0

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
    description="AI Writing Assistant with Core Features",
    version="3.0.0-MVP",
    lifespan=lifespan
)

# CRITICAL: CORS middleware MUST be added BEFORE Security middleware
# This ensures CORS preflight OPTIONS requests are handled before security checks
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-production-88b0.up.railway.app",  # Your current production frontend
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
app.add_middleware(SecurityMiddleware)

# Include routers
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
            "version": "3.0.0-MVP",
            "status": "healthy",
            "database": db_health['status'],
            "railway_deployment": "success",
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
            "version": "3.0.0-MVP", 
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
            "version": "3.0.0-MVP",
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

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> TokenResponse:
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        # Use auth service for registration
        result = auth_service.register_user(
            username=user_data.email.split('@')[0],
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        logger.info(f"New user registered: {user_data.email}")
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            token_type=result['token_type'],
            expires_in=1800,
            user={
                "id": result['user']['id'],
                "name": result['user']['name'],
                "email": result['user']['email'],
                "created_at": result['user']['created_at']
            }
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error during registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected registration error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login")
async def login(login_data: UserLogin) -> TokenResponse:
    try:
        result = auth_service.login_user(login_data.email, login_data.password)
        
        logger.info(f"User logged in: {login_data.email}")
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            token_type=result['token_type'],
            expires_in=1800,
            user={
                "id": result['user']['id'],
                "name": result['user']['name'],
                "email": result['user']['email']
            }
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/refresh")
async def refresh_token(refresh_data: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token"""
    try:
        result = auth_service.refresh_access_token(refresh_data.refresh_token)
        
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=refresh_data.refresh_token,
            token_type=result['token_type'],
            expires_in=1800,
            user={}
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/api/auth/logout")
async def logout(user_id: int = Depends(get_current_user_id)):
    """Logout user"""
    try:
        logger.info(f"User {user_id} logged out")
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.get("/api/auth/profile")
async def get_profile(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get basic document count only
    try:
        doc_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_documents FROM documents WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        user['total_documents'] = doc_stats['total_documents'] if doc_stats else 0
    except Exception as e:
        logger.error(f"Error getting document count: {e}")
        user['total_documents'] = 0
    
    return user

# Templates endpoints
@app.get("/api/templates")
async def get_templates():
    return templates_store

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    template = next((t for t in templates_store if t['id'] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

# Folder management endpoints
@app.get("/api/folders")
async def get_folders(user_id: int = Depends(get_current_user_id)):
    try:
        folders = db_service.execute_query(
            """SELECT f.*, 
               (SELECT COUNT(*) FROM documents d WHERE d.folder_id = f.id) as document_count
               FROM folders f 
               WHERE f.user_id = %s 
               ORDER BY f.created_at DESC""",
            (user_id,),
            fetch='all'
        )
        return folders
    except DatabaseError as e:
        logger.error(f"Error fetching folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch folders")

@app.post("/api/folders")
async def create_folder(folder_data: FolderCreate, user_id: int = Depends(get_current_user_id)):
    try:
        folder_id = str(uuid.uuid4())
        
        result = db_service.execute_query(
            """INSERT INTO folders (id, user_id, name, parent_id, color, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING id, name, parent_id, color, created_at""",
            (folder_id, user_id, folder_data.name, folder_data.parent_id, folder_data.color, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create folder")
            
        return {
            "id": result['id'],
            "name": result['name'],
            "parent_id": result['parent_id'],
            "color": result['color'],
            "created_at": result['created_at'].isoformat() if result['created_at'] else None,
            "document_count": 0
        }
        
    except DatabaseError as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to create folder")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder_data: FolderUpdate, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id, name, color FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Update fields
        updates = []
        params = []
        
        if folder_data.name is not None:
            updates.append("name = %s")
            params.append(folder_data.name)
        if folder_data.color is not None:
            updates.append("color = %s")
            params.append(folder_data.color)
        
        if not updates:
            return folder
        
        updates.append("updated_at = %s")
        params.extend([datetime.utcnow(), folder_id, user_id])
        
        result = db_service.execute_query(
            f"UPDATE folders SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING id, name, color, updated_at",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update folder")
        
        return result
        
    except DatabaseError as e:
        logger.error(f"Error updating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to update folder")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Move documents out of this folder
        db_service.execute_query(
            "UPDATE documents SET folder_id = NULL WHERE folder_id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        # Delete the folder
        db_service.execute_query(
            "DELETE FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        return {"message": "Folder deleted successfully"}
        
    except DatabaseError as e:
        logger.error(f"Error deleting folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete folder")

# Document management endpoints
@app.get("/api/documents")
async def get_documents(
    user_id: int = Depends(get_current_user_id),
    folder_id: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    offset: Optional[int] = Query(0)
):
    try:
        # Build query conditions
        conditions = ["user_id = %s"]
        params = [user_id]
        
        if folder_id:
            conditions.append("folder_id = %s")
            params.append(folder_id)
        
        if status:
            conditions.append("status = %s")
            params.append(status.value)
        
        if search:
            conditions.append("(title ILIKE %s OR content ILIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM documents WHERE {' AND '.join(conditions)}"
        total_count = db_service.execute_query(count_query, params, fetch='one')['count']
        
        # Get documents
        query = f"""
            SELECT id, title, content, status, word_count, 
                   created_at, updated_at, folder_id
            FROM documents 
            WHERE {' AND '.join(conditions)}
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        documents = db_service.execute_query(query, params, fetch='all')
        
        # Format response
        for doc in documents:
            doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return {
            "documents": documents,
            "total_count": total_count,
            "page_info": {
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0,
                "current_offset": offset,
                "limit": limit
            }
        }
    except DatabaseError as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.post("/api/documents/from-template")
async def create_document_from_template(doc_data: DocumentFromTemplateCreate, user_id: int = Depends(get_current_user_id)):
    try:
        logger.info(f"Creating document from template: {doc_data.template_id}")
        
        # Find the template
        template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        doc_id = str(uuid.uuid4())
        content = template['content']
        word_count = calculate_word_count(content)
        
        result = db_service.execute_query(
            """INSERT INTO documents (id, user_id, title, content, folder_id, status, word_count, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id, title, content, folder_id, status, word_count, created_at, updated_at""",
            (doc_id, user_id, doc_data.title, content, doc_data.folder_id, 'draft', word_count, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create document from template")
        
        # Format response
        document = dict(result)
        document['created_at'] = document['created_at'].isoformat() if document['created_at'] else None
        document['updated_at'] = document['updated_at'].isoformat() if document['updated_at'] else None
        
        logger.info(f"Document created from template: {document['title']}")
        return document
        
    except DatabaseError as e:
        logger.error(f"Database error creating document from template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document from template")

@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate, user_id: int = Depends(get_current_user_id)):
    try:
        logger.info(f"Creating document: {doc_data.title}")
        
        doc_id = str(uuid.uuid4())
        content = doc_data.content
        
        # Use template content if provided
        if doc_data.template_id:
            template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
            if template:
                content = template['content']
        
        word_count = calculate_word_count(content)
        
        result = db_service.execute_query(
            """INSERT INTO documents (id, user_id, title, content, folder_id, status, word_count, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id, title, content, folder_id, status, word_count, created_at, updated_at""",
            (doc_id, user_id, doc_data.title, content, doc_data.folder_id, doc_data.status.value, word_count, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create document")
        
        # Format response
        document = dict(result)
        document['created_at'] = document['created_at'].isoformat() if document['created_at'] else None
        document['updated_at'] = document['updated_at'].isoformat() if document['updated_at'] else None
        
        logger.info(f"Document created: {document['title']}")
        return document
        
    except DatabaseError as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        document = db_service.execute_query(
            """SELECT id, title, content, status, word_count, 
                      created_at, updated_at, folder_id
               FROM documents 
               WHERE id = %s AND user_id = %s""",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Format response
        doc = dict(document)
        doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
        doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return doc
        
    except DatabaseError as e:
        logger.error(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")

@app.put("/api/documents/{document_id}")
async def update_document(document_id: str, doc_data: DocumentUpdate, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        existing = db_service.execute_query(
            "SELECT id FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Build update query
        updates = []
        params = []
        
        if doc_data.title is not None:
            updates.append("title = %s")
            params.append(doc_data.title)
        
        if doc_data.content is not None:
            updates.append("content = %s")
            params.append(doc_data.content)
            updates.append("word_count = %s")
            params.append(calculate_word_count(doc_data.content))
        
        if doc_data.status is not None:
            updates.append("status = %s")
            params.append(doc_data.status.value)
        
        if doc_data.folder_id is not None:
            updates.append("folder_id = %s")
            params.append(doc_data.folder_id)
        
        if not updates:
            return await get_document(document_id, user_id)
        
        updates.append("updated_at = %s")
        params.extend([datetime.utcnow(), document_id, user_id])
        
        result = db_service.execute_query(
            f"""UPDATE documents SET {', '.join(updates)} 
                WHERE id = %s AND user_id = %s
                RETURNING id, title, content, status, word_count, created_at, updated_at, folder_id""",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update document")
        
        # Format response
        doc = dict(result)
        doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
        doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return doc
        
    except DatabaseError as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        document = db_service.execute_query(
            "SELECT id, title FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete the document
        db_service.execute_query(
            "DELETE FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id)
        )
        
        logger.info(f"Document deleted: {document['title']} by user {user_id}")
        return {"message": "Document deleted successfully"}
        
    except DatabaseError as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

# Auto-save endpoint
@app.put("/api/documents/{document_id}/auto-save")
async def auto_save_document(document_id: str, content: str = Query(...), user_id: int = Depends(get_current_user_id)):
    """Auto-save document content"""
    try:
        # Check if document exists and belongs to user
        existing = db_service.execute_query(
            "SELECT id, content FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Only save if content changed
        if existing['content'] != content:
            word_count = calculate_word_count(content)
            
            db_service.execute_query(
                """UPDATE documents 
                   SET content = %s, word_count = %s, updated_at = %s 
                   WHERE id = %s AND user_id = %s""",
                (content, word_count, datetime.utcnow(), document_id, user_id)
            )
        
        return {"status": "auto_saved", "timestamp": datetime.utcnow().isoformat()}
        
    except DatabaseError as e:
        logger.error(f"Error auto-saving document: {e}")
        raise HTTPException(status_code=500, detail="Failed to auto-save document")

if __name__ == "__main__":
    # On Railway, the start.sh script handles process startup
    # This section only runs for local development
    if not os.getenv("RAILWAY_ENVIRONMENT"):
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        logger.info("💻 Running locally - using uvicorn")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
    else:
        logger.info("🚂 Railway detected - startup handled by start.sh script")
        # Don't start anything here on Railway - let start.sh handle it 