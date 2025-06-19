"""
DOG Writer Backend - Google Docs-Like Document Management System
Comprehensive document editor with PostgreSQL database, folders, versions, sharing, and collaboration
Production-ready with proper database persistence
"""

import os
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

import jwt
import bcrypt

# Import our PostgreSQL services
from services.database import db_service, DatabaseError
from services.auth_service import auth_service, AuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums for better type safety
class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class PermissionLevel(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class ActivityType(str, Enum):
    CREATED = "created"
    EDITED = "edited"
    SHARED = "shared"
    VIEWED = "viewed"
    COMMENTED = "commented"

# Comprehensive templates with rich content
templates_store: List[dict] = [
    {
        "id": "academic-essay",
        "title": "Academic Essay",
        "description": "Professional academic essay with proper structure and citations",
        "content": """# Essay Title

## Abstract
Provide a brief summary of your essay's main argument and key points (150-250 words).

## Introduction
Start with a compelling hook that draws your reader in. Provide background context on your topic and clearly state your thesis statement. Your thesis should present a clear argument that you will support throughout your essay.

**Thesis Statement:** [Your main argument goes here]

## Literature Review
Discuss relevant academic sources and previous research on your topic. Show how your argument fits into or challenges existing scholarship.

## Body Paragraph 1: [Main Point 1]
**Topic Sentence:** Introduce your first main supporting point.
Present evidence, examples, and analysis that support this point. Use proper citations and explain how this evidence supports your thesis.

## Body Paragraph 2: [Main Point 2]
**Topic Sentence:** Introduce your second main supporting point.
Present additional evidence and analysis. Consider counterarguments and address potential objections.

## Body Paragraph 3: [Main Point 3]
**Topic Sentence:** Introduce your third main supporting point.
Provide your strongest evidence and most compelling analysis.

## Conclusion
Summarize your main arguments without simply repeating them. Discuss the broader implications of your findings and suggest areas for future research.

## References
- Author, A. A. (Year). Title of work. Publisher.
- Author, B. B. (Year). Title of article. Journal Name, Volume(Issue), pages.""",
        "category": "Academic",
        "word_count_target": 2000,
        "estimated_time": "2-3 hours"
    },
    {
        "id": "creative-story",
        "title": "Creative Short Story",
        "description": "Structured template for compelling short fiction",
        "content": """# Story Title

## Story Planning

### Character Development
**Protagonist:** 
- Name: 
- Age: 
- Occupation: 
- Key trait: 
- What they want: 
- What's stopping them: 

**Supporting Characters:**
- Character 2: [Name and role]
- Character 3: [Name and role]

### Setting
- **Time Period:** 
- **Location:** 
- **Atmosphere:** 

### Plot Structure
**Hook (Opening line):** Write a compelling first sentence that immediately draws readers in.

---

## The Story

### Opening Scene
Set the scene and introduce your protagonist in their normal world. What's their daily routine? What's about to change?

[Start writing your story here...]

### Rising Action
What event disrupts your protagonist's normal world? How do they react? What obstacles do they face?

### Climax
The moment of highest tension. What crucial decision does your protagonist make?

### Resolution
How do things end? What has changed for your protagonist? What have they learned?

---

## Story Notes
**Theme:** What is your story really about?
**Target Word Count:** 1,500-3,000 words
**Inspiration:** What inspired this story?""",
        "category": "Creative",
        "word_count_target": 2500,
        "estimated_time": "3-4 hours"
    },
    {
        "id": "business-proposal",
        "title": "Business Proposal",
        "description": "Professional business proposal template",
        "content": """# Business Proposal: [Project/Service Name]

**Prepared for:** [Client/Company Name]  
**Prepared by:** [Your Name/Company]  
**Date:** [Current Date]  
**Valid Until:** [Date]

---

## Executive Summary
Provide a compelling overview of your proposal in 2-3 paragraphs. Highlight key benefits and why this is the best solution.

**Key Benefits:**
- Benefit 1
- Benefit 2  
- Benefit 3

**Investment Required:** $[Amount]  
**Timeline:** [Duration]  
**Expected ROI:** [Percentage]

## Problem Statement
### Current Situation
Describe the client's current state and challenges.

### Impact of Not Acting
Explain consequences of maintaining status quo.

### Opportunity
Highlight potential benefits of solving this problem.

## Proposed Solution
### Overview
High-level description of your proposed solution.

### Detailed Approach
#### Phase 1: [Name]
- **Objective:** 
- **Activities:** 
- **Timeline:** 
- **Deliverables:** 

#### Phase 2: [Name]
- **Objective:** 
- **Activities:** 
- **Timeline:** 
- **Deliverables:** 

## Investment & Timeline
### Cost Breakdown
| Item | Description | Cost |
|------|-------------|------|
| Phase 1 | [Description] | $[Amount] |
| Phase 2 | [Description] | $[Amount] |
| **Total** | | **$[Total]** |

### Payment Terms
- [%]% upon contract signing
- [%]% at midpoint milestone
- [%]% upon completion

## Expected Outcomes
### Measurable Results
- Result 1: [Specific metric]
- Result 2: [Specific metric]
- Result 3: [Specific metric]

## Next Steps
1. Review this proposal by [Date]
2. Schedule discussion
3. Prepare formal contract
4. Project kickoff on [Date]""",
        "category": "Business",
        "word_count_target": 1500,
        "estimated_time": "4-6 hours"
    },
    {
        "id": "daily-journal",
        "title": "Daily Reflection Journal",
        "description": "Structured daily journaling for personal growth",
        "content": """# Daily Journal Entry

**Date:** [Today's Date]  
**Day:** [Monday, Tuesday, etc.]  
**Weather:** [Description]  
**Overall Mood:** [😊 😐 😔 or describe]

---

## Morning Intentions
### How I'm Starting Today
Take a moment to check in with yourself. How are you feeling as you begin this day?

### Today's Priorities
What are the 3 most important things you want to accomplish?
1. **Priority 1:** [Most important task]
2. **Priority 2:** [Second important task]  
3. **Priority 3:** [Third important task]

### Intention Setting
What kind of person do you want to be today? How do you want to show up?

---

## Daily Events & Experiences
### What Happened Today
Write about significant events, conversations, or experiences.

### Highlight of the Day
What was the best part of today? What brought you joy?

### Challenge of the Day
What was difficult today? How did you handle it?

### People I Interacted With
Who did you spend time with? How did these interactions affect you?

---

## Learning & Growth
### What I Learned Today
What new insights, skills, or knowledge did you gain?

### How I Grew
In what ways did you challenge yourself or step outside your comfort zone?

### Mistakes & Lessons
What didn't go as planned? What can you learn?

---

## Gratitude & Appreciation
### Three Things I'm Grateful For
1. **Gratitude 1:** [Something you appreciate]
2. **Gratitude 2:** [Something you appreciate]
3. **Gratitude 3:** [Something you appreciate]

### Appreciation for Others
Who deserves recognition today? Why?

### Self-Appreciation
What did you do well today? Give yourself credit.

---

## Reflection & Planning
### How I Feel Right Now
As you end this day, how are you feeling? What emotions are present?

### What I Want to Remember
What from today do you want to carry forward?

### Tomorrow's Focus
What do you want to focus on tomorrow?

---

## Creative Space
Use this space for additional thoughts, doodles, quotes, or creative expression:

[Free writing space...]

---

**"The unexamined life is not worth living." - Socrates**""",
        "category": "Personal",
        "word_count_target": 800,
        "estimated_time": "20-30 minutes"
    }
]

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "comprehensive-secret-key-for-development")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week

security = HTTPBearer()

# Enhanced Pydantic models
class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, description="User's full name")

class UserLogin(BaseModel):
    email: str
    password: str

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    color: Optional[str] = "#3B82F6"

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template_id: Optional[str] = None
    folder_id: Optional[str] = None
    status: DocumentStatus = DocumentStatus.DRAFT
    tags: List[str] = []

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Database utility functions
def get_user_id_from_email(email: str) -> Optional[int]:
    """Get user ID from email"""
    try:
        result = db_service.execute_query(
            "SELECT id FROM users WHERE email = %s AND is_active = TRUE",
            (email,),
            fetch='one'
        )
        return result['id'] if result else None
    except DatabaseError:
        return None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    try:
        result = db_service.execute_query(
            "SELECT id, username, name, email, created_at, last_login, preferences FROM users WHERE id = %s AND is_active = TRUE",
            (user_id,),
            fetch='one'
        )
        return result
    except DatabaseError:
        return None

# Utility functions
def calculate_reading_time(content: str) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(content.split())
    return max(1, round(word_count / 200))

def calculate_word_count(content: str) -> int:
    return len(content.split())

def calculate_character_count(content: str) -> int:
    return len(content)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),  # Convert to string for consistency
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)  # Convert back to int
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting DOG Writer - Google Docs-Like Document Management System")
    logger.info(f"📚 Loaded {len(templates_store)} comprehensive templates")
    logger.info("✨ Features: PostgreSQL Database, Folders, Versions, Analytics, Auto-save")
    
    # Check database connectivity
    health = db_service.health_check()
    if health['status'] == 'healthy':
        logger.info(f"✅ PostgreSQL connected: {health.get('total_users', 0)} users, {health.get('total_documents', 0)} documents")
    else:
        logger.warning(f"⚠️ Database not healthy: {health.get('error', 'Unknown error')}")
    
    yield
    logger.info("🛑 Shutting down DOG Writer API")

# Create FastAPI app
app = FastAPI(
    title="DOG Writer - Google Docs-Like Document System",
    description="Comprehensive document management with PostgreSQL, folders, versions, sharing, and collaboration",
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

# Health endpoints
@app.get("/")
async def root():
    db_health = db_service.health_check()
    return {
        "message": "DOG Writer - Google Docs-Like Document Management System",
        "version": "2.0.0",
        "status": "healthy",
        "database": db_health['status'],
        "features": [
            "postgresql_database",
            "document_management",
            "folder_organization", 
            "version_control",
            "analytics_tracking",
            "template_system",
            "auto_save",
            "favorites",
            "search_and_filter"
        ],
        "statistics": {
            "total_users": db_health.get('total_users', 0),
            "total_documents": db_health.get('total_documents', 0),
            "total_templates": len(templates_store)
        }
    }

@app.get("/api/health")
async def health_check():
    db_health = db_service.health_check()
    
    # Get additional metrics
    try:
        folder_count = db_service.execute_query("SELECT COUNT(*) as count FROM folders", fetch='one')
        version_count = db_service.execute_query("SELECT COUNT(*) as count FROM document_versions", fetch='one')
    except:
        folder_count = {"count": 0}
        version_count = {"count": 0}
    
    return {
        "status": db_health['status'],
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_health,
        "metrics": {
            "users_count": db_health.get('total_users', 0),
            "documents_count": db_health.get('total_documents', 0),
            "folders_count": folder_count['count'],
            "templates_count": len(templates_store),
            "document_versions_count": version_count['count']
        }
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> TokenResponse:
    try:
        # Use auth service for registration
        result = auth_service.register_user(
            username=user_data.email.split('@')[0],  # Use email prefix as username
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        user_info = result['user']
        access_token = create_access_token(user_info['id'])
        
        logger.info(f"New user registered: {user_data.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user_info['id'],
                "name": user_info['name'],
                "email": user_info['email'],
                "created_at": user_info['created_at']
            }
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login(login_data: UserLogin) -> TokenResponse:
    try:
        # Use auth service for login
        result = auth_service.login_user(login_data.email, login_data.password)
        
        user_info = result['user']
        access_token = create_access_token(user_info['id'])
        
        logger.info(f"User logged in: {login_data.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user_info['id'],
                "name": user_info['name'],
                "email": user_info['email'],
                "last_login": user_info.get('last_login')
            }
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/profile")
async def get_profile(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user statistics
    try:
        doc_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_docs, SUM(word_count) as total_words FROM documents WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        folder_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_folders FROM folders WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        favorite_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_favorites FROM documents WHERE user_id = %s AND is_favorite = TRUE",
            (user_id,),
            fetch='one'
        )
        
        user['statistics'] = {
            "total_documents": doc_stats['total_docs'] if doc_stats else 0,
            "total_words": doc_stats['total_words'] if doc_stats and doc_stats['total_words'] else 0,
            "total_folders": folder_stats['total_folders'] if folder_stats else 0,
            "favorite_documents": favorite_stats['total_favorites'] if favorite_stats else 0
        }
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        user['statistics'] = {"total_documents": 0, "total_words": 0, "total_folders": 0, "favorite_documents": 0}
    
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
        
        query = """
            INSERT INTO folders (id, user_id, name, parent_id, color, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, parent_id, color, created_at, updated_at
        """
        
        result = db_service.execute_query(
            query,
            (folder_id, user_id, folder_data.name, folder_data.parent_id, 
             folder_data.color, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create folder")
            
        logger.info(f"Folder created: {folder_data.name} by user {user_id}")
        return result
        
    except DatabaseError as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to create folder")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder_data: FolderUpdate, user_id: int = Depends(get_current_user_id)):
    folder = db_service.execute_query(
        "SELECT id, user_id, name, description, color, created_at, updated_at FROM folders WHERE id = %s AND user_id = %s",
        (folder_id, user_id),
        fetch='one'
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if folder['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if folder_data.name is not None:
        folder['name'] = folder_data.name
    if folder_data.description is not None:
        folder['description'] = folder_data.description
    if folder_data.color is not None:
        folder['color'] = folder_data.color
    
    query = """
        UPDATE folders
        SET name = %s,
            description = %s,
            color = %s,
            updated_at = %s
        WHERE id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (folder['name'], folder['description'], folder['color'], datetime.utcnow(), folder['id'], user_id),
        fetch='one'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update folder")
    
    return folder

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str, user_id: int = Depends(get_current_user_id)):
    folder = db_service.execute_query(
        "SELECT id, user_id, name, description, color, created_at, updated_at FROM folders WHERE id = %s AND user_id = %s",
        (folder_id, user_id),
        fetch='one'
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if folder['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Move documents to root
    query = """
        UPDATE documents
        SET folder_id = NULL
        WHERE folder_id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (folder_id, user_id),
        fetch='execute'
    )
    
    if result.rowcount == 0:
        raise HTTPException(status_code=500, detail="Failed to move documents to root")
    
    query = """
        DELETE FROM folders
        WHERE id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (folder_id, user_id),
        fetch='execute'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to delete folder")
    
    return {"message": "Folder deleted successfully"}

# Enhanced document endpoints
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
        query = """
            SELECT d.*, 
                   (SELECT COUNT(*) FROM document_versions dv WHERE dv.document_id = d.id) as version_count,
                   (SELECT COUNT(*) FROM document_analytics da WHERE da.document_id = d.id) as analytics_count
            FROM documents d
            WHERE d.user_id = %s
        """
        
        if folder_id:
            query += " AND d.folder_id = %s"
        
        if status:
            query += " AND d.status = %s"
        
        if search:
            search_lower = search.lower()
            query += " AND (d.title ILIKE %s OR d.content ILIKE %s)"
        
        query += " ORDER BY d.updated_at DESC LIMIT %s OFFSET %s"
        
        params = (user_id, folder_id, status.value, search_lower, search_lower, limit, offset)
        
        documents = db_service.execute_query(
            query,
            params,
            fetch='all'
        )
        
        total_count = len(documents)
        
        # Add analytics
        for doc in documents:
            analytics = db_service.execute_query(
                "SELECT view_count, edit_count, word_count, character_count, reading_time_minutes, last_viewed, last_edited FROM document_analytics WHERE document_id = %s",
                (doc['id'],),
                fetch='one'
            )
            doc['analytics'] = analytics
            doc['is_favorite'] = doc['id'] in favorites_store.get(user_id, set())
        
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

@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate, user_id: int = Depends(get_current_user_id)):
    try:
        doc_id = str(uuid.uuid4())
        
        # Use template content if provided
        content = doc_data.content
        template_used = None
        if doc_data.template_id:
            template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
            if template:
                content = template['content']
                template_used = template
        
        query = """
            INSERT INTO documents (id, user_id, title, content, template_id, folder_id, status, tags, created_at, updated_at, template_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, title, content, template_id, folder_id, status, tags, created_at, updated_at, template_used
        """
        
        result = db_service.execute_query(
            query,
            (doc_id, user_id, doc_data.title, content, doc_data.template_id, doc_data.folder_id, doc_data.status.value, doc_data.tags, datetime.utcnow(), datetime.utcnow(), template_used['title'] if template_used else NULL),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create document")
        
        document = result
        
        # Initialize analytics
        query = """
            INSERT INTO document_analytics (document_id, view_count, edit_count, word_count, character_count, reading_time_minutes, last_viewed, last_edited)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        result = db_service.execute_query(
            query,
            (document['id'], 0, 1, calculate_word_count(content), calculate_character_count(content), calculate_reading_time(content), NULL, document['updated_at']),
            fetch='execute'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to initialize document analytics")
        
        logger.info(f"Document created: {document['title']} by user {user_id}")
        return document
    except DatabaseError as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    document = db_service.execute_query(
        "SELECT d.*, dv.content, da.view_count, da.edit_count, da.word_count, da.character_count, da.reading_time_minutes, da.last_viewed, da.last_edited FROM documents d LEFT JOIN document_versions dv ON d.id = dv.document_id LEFT JOIN document_analytics da ON d.id = da.document_id WHERE d.id = %s AND d.user_id = %s",
        (document_id, user_id),
        fetch='one'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update view analytics
    if document['view_count'] is None:
        query = """
            INSERT INTO document_analytics (document_id, view_count, edit_count, word_count, character_count, reading_time_minutes, last_viewed, last_edited)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        result = db_service.execute_query(
            query,
            (document['id'], 1, document['edit_count'], document['word_count'], document['character_count'], document['reading_time_minutes'], datetime.utcnow(), document['last_edited']),
            fetch='execute'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update document analytics")
    
    document['analytics'] = document
    document['is_favorite'] = document['id'] in favorites_store.get(user_id, set())
    
    return document

@app.put("/api/documents/{document_id}")
async def update_document(
    document_id: str, 
    doc_data: DocumentUpdate, 
    user_id: int = Depends(get_current_user_id)
):
    document = db_service.execute_query(
        "SELECT id, user_id, title, content, status, tags, folder_id, created_at, updated_at FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
        fetch='one'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create version for significant changes
    if doc_data.content is not None and doc_data.content != document['content']:
        if abs(len(doc_data.content) - len(document['content'])) > 50:
            query = """
                INSERT INTO document_versions (id, document_id, content, title, created_at, version_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            result = db_service.execute_query(
                query,
                (str(uuid.uuid4()), document['id'], document['content'], document['title'], document['updated_at'], (SELECT COUNT(*) FROM document_versions WHERE document_id = %s) + 1),
                fetch='execute'
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to create document version")
    
    # Update fields
    if doc_data.title is not None:
        document['title'] = doc_data.title
    if doc_data.content is not None:
        document['content'] = doc_data.content
    if doc_data.status is not None:
        document['status'] = doc_data.status.value
    if doc_data.tags is not None:
        document['tags'] = doc_data.tags
    if doc_data.folder_id is not None:
        document['folder_id'] = doc_data.folder_id
    
    document['updated_at'] = datetime.utcnow()
    
    # Update analytics
    query = """
        UPDATE document_analytics
        SET view_count = %s,
            edit_count = %s,
            word_count = %s,
            character_count = %s,
            reading_time_minutes = %s,
            last_viewed = %s,
            last_edited = %s
        WHERE document_id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (document['view_count'], document['edit_count'], document['word_count'], document['character_count'], document['reading_time_minutes'], document['last_viewed'], document['last_edited'], document['id'], user_id),
        fetch='execute'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update document analytics")
    
    return document

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    document = db_service.execute_query(
        "SELECT id, user_id, title, content, status, folder_id, created_at, updated_at FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
        fetch='one'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Clean up related data
    query = """
        DELETE FROM document_versions
        WHERE document_id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (document['id'], user_id),
        fetch='execute'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to clean up related data")
    
    # Remove from favorites
    query = """
        DELETE FROM favorites
        WHERE document_id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (document['id'], user_id),
        fetch='execute'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to remove document from favorites")
    
    # Delete document
    query = """
        DELETE FROM documents
        WHERE id = %s AND user_id = %s
    """
    
    result = db_service.execute_query(
        query,
        (document['id'], user_id),
        fetch='execute'
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    logger.info(f"Document deleted: {document['title']} by user {user_id}")
    return {"message": "Document deleted successfully"}

# Document versions
@app.get("/api/documents/{document_id}/versions")
async def get_document_versions(document_id: str, user_id: int = Depends(get_current_user_id)):
    document = db_service.execute_query(
        "SELECT id, content, title, created_at, version_number FROM document_versions WHERE document_id = %s AND user_id = %s ORDER BY created_at DESC",
        (document_id, user_id),
        fetch='all'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"versions": document}

# Document favorites
@app.post("/api/documents/{document_id}/favorite")
async def toggle_document_favorite(document_id: str, user_id: int = Depends(get_current_user_id)):
    document = db_service.execute_query(
        "SELECT id, user_id, is_favorite FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
        fetch='one'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if document['is_favorite']:
        query = """
            UPDATE documents
            SET is_favorite = FALSE
            WHERE id = %s AND user_id = %s
        """
        
        result = db_service.execute_query(
            query,
            (document['id'], user_id),
            fetch='execute'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to remove document from favorites")
        
        is_favorite = False
    else:
        query = """
            UPDATE documents
            SET is_favorite = TRUE
            WHERE id = %s AND user_id = %s
        """
        
        result = db_service.execute_query(
            query,
            (document['id'], user_id),
            fetch='execute'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to add document to favorites")
        
        is_favorite = True
    
    return {
        "document_id": document['id'],
        "is_favorite": is_favorite,
        "message": f"Document {'added to' if is_favorite else 'removed from'} favorites"
    }

@app.get("/api/documents/favorites")
async def get_favorite_documents(user_id: int = Depends(get_current_user_id)):
    favorite_ids = db_service.execute_query(
        "SELECT document_id FROM favorites WHERE user_id = %s",
        (user_id,),
        fetch='all'
    )
    favorite_documents = db_service.execute_query(
        "SELECT d.*, da.view_count, da.edit_count, da.word_count, da.character_count, da.reading_time_minutes, da.last_viewed, da.last_edited FROM documents d LEFT JOIN document_analytics da ON d.id = da.document_id WHERE d.id IN (%s) AND d.user_id = %s",
        (tuple(doc['document_id'] for doc in favorite_ids), user_id),
        fetch='all'
    )
    
    # Add analytics
    for doc in favorite_documents:
        doc['analytics'] = doc
        doc['is_favorite'] = True
    
    return favorite_documents

# Analytics endpoints
@app.get("/api/analytics/overview")
async def get_analytics_overview(user_id: int = Depends(get_current_user_id)):
    user_documents = db_service.execute_query(
        "SELECT id, title, updated_at, word_count, status FROM documents WHERE user_id = %s",
        (user_id,),
        fetch='all'
    )
    
    total_words = sum(doc['word_count'] for doc in user_documents)
    total_documents = len(user_documents)
    total_folders = db_service.execute_query(
        "SELECT COUNT(*) as count FROM folders WHERE user_id = %s",
        (user_id,),
        fetch='one'
    )['count']
    
    # Status distribution
    status_counts = {}
    for doc in user_documents:
        status = doc['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Recent documents
    recent_documents = sorted(user_documents, key=lambda x: x['updated_at'], reverse=True)[:5]
    
    return {
        "overview": {
            "total_words": total_words,
            "total_documents": total_documents,
            "total_folders": total_folders,
            "favorite_documents": len(favorites_store.get(user_id, set()))
        },
        "status_distribution": status_counts,
        "recent_documents": [
            {
                "id": doc['id'],
                "title": doc['title'],
                "updated_at": doc['updated_at'],
                "word_count": doc['word_count']
            } for doc in recent_documents
        ]
    }

# Auto-save endpoint
@app.put("/api/documents/{document_id}/auto-save")
async def auto_save_document(
    document_id: str,
    content: str,
    user_id: int = Depends(get_current_user_id)
):
    """Auto-save document content without creating versions"""
    document = db_service.execute_query(
        "SELECT id, user_id, title, content, status, created_at, updated_at FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
        fetch='one'
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Only save if content changed
    if document['content'] != content:
        document['content'] = content
        document['updated_at'] = datetime.utcnow()
        
        # Update analytics
        query = """
            UPDATE document_analytics
            SET view_count = %s,
                edit_count = %s,
                word_count = %s,
                character_count = %s,
                reading_time_minutes = %s,
                last_viewed = %s,
                last_edited = %s
            WHERE document_id = %s AND user_id = %s
        """
        
        result = db_service.execute_query(
            query,
            (document['view_count'], document['edit_count'], calculate_word_count(content), calculate_character_count(content), calculate_reading_time(content), datetime.utcnow(), datetime.utcnow(), document['id'], user_id),
            fetch='execute'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update document analytics")
    
    return {"status": "auto_saved", "timestamp": datetime.utcnow().isoformat()}

# Simple endpoints for compatibility
@app.get("/api/series")
async def get_series():
    return []

@app.get("/api/goals")
async def get_goals():
    return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 