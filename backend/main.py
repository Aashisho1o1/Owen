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

# JWT Configuration from auth service
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-please-change-in-production")
security = HTTPBearer()

# Document Templates - Production-Ready Google Docs-Like Templates
templates_store = [
    {
        "id": "academic-essay",
        "title": "Academic Essay",
        "description": "Professional academic essay template with proper structure",
        "content": """# [Essay Title]

**Author:** [Your Name]  
**Course:** [Course Name]  
**Date:** [Date]  
**Word Count Target:** 1,500-2,000 words

## Abstract
Provide a brief summary of your essay's main argument and key points (150-250 words).

## Introduction
Begin with a compelling hook that draws readers into your topic. Provide necessary background information and context. Clearly state your thesis statement - the main argument you will defend throughout the essay.

### Thesis Statement
*"[Insert your clear, specific, and arguable thesis statement here.]*"

## Body Paragraph 1: [Main Point 1]
**Topic Sentence:** Begin with a clear statement that introduces your first main point.

**Evidence:** Present specific evidence, examples, data, or quotes from credible sources to support your point.

**Analysis:** Explain how this evidence supports your thesis. Connect the dots for your reader.

**Transition:** Link to your next point smoothly.

## Body Paragraph 2: [Main Point 2]
**Topic Sentence:** [Second supporting argument]

**Evidence:** [Supporting evidence and sources]

**Analysis:** [Explanation of how evidence supports thesis]

**Transition:** [Connection to next point]

## Body Paragraph 3: [Main Point 3]
**Topic Sentence:** [Third supporting argument]

**Evidence:** [Supporting evidence and sources]

**Analysis:** [Explanation of how evidence supports thesis]

## Counterarguments and Rebuttal
Acknowledge opposing viewpoints to demonstrate thorough understanding of the topic. Present the strongest counterargument fairly, then provide a thoughtful rebuttal that reinforces your position.

## Conclusion
Restate your thesis in new words. Summarize your main supporting points. Discuss the broader implications of your argument. End with a powerful closing thought that leaves a lasting impression.

## References
*Use appropriate citation style (APA, MLA, Chicago, etc.)*

1. [Source 1]
2. [Source 2]
3. [Source 3]

---

## Writing Checklist
- [ ] Clear thesis statement
- [ ] Strong topic sentences
- [ ] Sufficient evidence for each point
- [ ] Proper citations
- [ ] Smooth transitions
- [ ] Compelling introduction and conclusion
- [ ] Proofread for grammar and style""",
        "category": "Academic",
        "word_count_target": 1800,
        "estimated_time": "4-6 hours"
    },
    {
        "id": "creative-story",
        "title": "Creative Short Story",
        "description": "Creative writing template with character development and plot structure",
        "content": """# [Story Title]

**Genre:** [Mystery/Romance/Sci-Fi/Fantasy/Literary Fiction]  
**Target Length:** 2,500-4,000 words  
**Setting:** [Time and Place]

## Character Profiles
### Protagonist: [Name]
- **Age:** [Age]
- **Occupation:** [Job/Role]
- **Key Traits:** [3-4 defining characteristics]
- **Goal:** [What they want]
- **Conflict:** [What stands in their way]
- **Arc:** [How they change]

### Antagonist/Challenge: [Name/Force]
- **Nature:** [Person, internal struggle, society, nature, etc.]
- **Motivation:** [Why they oppose the protagonist]

## Story Outline
### Act I: Setup (25%)
**Hook:** Start with action, dialogue, or intriguing situation
**World Building:** Establish setting and atmosphere
**Character Introduction:** Show protagonist in their normal world
**Inciting Incident:** The event that starts the main conflict

### Act II: Confrontation (50%)
**Rising Action:** Complications and obstacles increase
**Midpoint:** Major revelation or setback
**Obstacles:** Character faces increasing challenges
**Crisis:** Darkest moment/biggest challenge

### Act III: Resolution (25%)
**Climax:** Confrontation with main conflict
**Falling Action:** Immediate consequences
**Resolution:** New normal, character growth shown

---

## Chapter 1: [Chapter Title]

[Begin your story here. Remember to:]
- Start with action or compelling dialogue
- Show, don't tell
- Use sensory details to immerse readers
- Establish voice and tone immediately

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
        "title": "Daily Journal",
        "description": "Personal reflection and daily planning template",
        "content": """# Daily Journal - [Date]

## Morning Intention Setting
**Today's Date:** [Date]  
**Weather:** [Description]  
**Mood:** [How I'm feeling]

### Top 3 Priorities for Today
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

### Intention for the Day
[What do I want to focus on or embody today?]

## Gratitude Practice
### Three Things I'm Grateful For
1. [Gratitude 1]
2. [Gratitude 2]
3. [Gratitude 3]

## Daily Reflection
### What Happened Today
[Free writing about the day's events, thoughts, and experiences]

### Challenges I Faced
[What was difficult and how did I handle it?]

### Victories and Accomplishments
[What went well? What am I proud of?]

### Lessons Learned
[What did I discover about myself or the world?]

## Evening Review
### Goals Progress
- Priority 1: [Completed/In Progress/Not Started]
- Priority 2: [Completed/In Progress/Not Started]
- Priority 3: [Completed/In Progress/Not Started]

### Tomorrow's Preparation
**Top 3 priorities for tomorrow:**
1. [Tomorrow's priority 1]
2. [Tomorrow's priority 2]
3. [Tomorrow's priority 3]

### Affirmation for Tomorrow
[A positive statement about tomorrow or myself]

---

## Weekly Themes (Optional)
- **Monday:** Fresh starts and goal setting
- **Tuesday:** Building momentum
- **Wednesday:** Mid-week reflection
- **Thursday:** Pushing through challenges
- **Friday:** Celebrating progress
- **Saturday:** Rest and relationships
- **Sunday:** Preparation and planning""",
        "category": "Personal",
        "word_count_target": 500,
        "estimated_time": "15-30 minutes"
    }
]

# Pydantic Models
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

# Helper functions
def get_user_id_from_email(email: str) -> Optional[int]:
    """Get user ID from email"""
    try:
        result = db_service.execute_query(
            "SELECT id FROM users WHERE email = %s AND is_active = TRUE",
            (email,),
            fetch='one'
        )
        return result['id'] if result else None
    except Exception:
        return None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user details by ID"""
    try:
        result = db_service.execute_query(
            "SELECT id, username, name, email, created_at, last_login, preferences FROM users WHERE id = %s AND is_active = TRUE",
            (user_id,),
            fetch='one'
        )
        return dict(result) if result else None
    except Exception:
        return None

def calculate_reading_time(content: str) -> int:
    """Calculate reading time in minutes (average 200 words per minute)"""
    word_count = len(content.split()) if content else 0
    return max(1, word_count // 200)

def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0

def calculate_character_count(content: str) -> int:
    """Calculate character count"""
    return len(content) if content else 0

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(weeks=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# App initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        db_service.init_database()
        logger.info("Database initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        yield
    finally:
        logger.info("Closing database connections...")
        db_service.close()

app = FastAPI(
    title="DOG Writer",
    description="Google Docs-Like Document Management System with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
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

# Test endpoint for debugging
@app.post("/api/test/register")
async def test_register(user_data: UserCreate):
    try:
        logger.info(f"🧪 TEST: Registration attempt for {user_data.email}")
        
        # Test database connection
        test_query = db_service.execute_query("SELECT 1 as test", fetch='one')
        logger.info(f"🧪 Database connection test: {test_query}")
        
        # Check if user exists
        existing_user = db_service.execute_query(
            "SELECT id, email FROM users WHERE email = %s",
            (user_data.email,),
            fetch='one'
        )
        
        if existing_user:
            logger.info(f"🧪 User already exists: {existing_user}")
            return {"error": "User already exists", "existing_user": existing_user}
        
        # Try simple user creation without auth service
        username = user_data.email.split('@')[0]
        password_hash = hash_password(user_data.password)
        
        new_user = db_service.execute_query(
            """INSERT INTO users (username, email, password_hash, name, created_at)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING id, username, email, name, created_at""",
            (username, user_data.email, password_hash, user_data.name, datetime.utcnow()),
            fetch='one'
        )
        
        logger.info(f"🧪 User created successfully: {new_user}")
        return {"success": True, "user": dict(new_user)}
        
    except Exception as e:
        logger.error(f"🧪 TEST ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"🧪 TEST TRACEBACK: {traceback.format_exc()}")
        return {"error": str(e), "type": type(e).__name__}

# Test auth service flow step by step
@app.post("/api/test/auth-flow")  
async def test_auth_flow(user_data: UserCreate):
    try:
        logger.info(f"🧪 AUTH FLOW TEST: Starting for {user_data.email}")
        
        # Step 1: Email validation (like auth service)
        try:
            from email_validator import validate_email, EmailNotValidError
            valid_email = validate_email(user_data.email)
            email = valid_email.email
            logger.info(f"🧪 Step 1 - Email validation: ✅ {email}")
        except EmailNotValidError as e:
            logger.error(f"🧪 Step 1 - Email validation: ❌ {e}")
            return {"error": f"Invalid email: {e}", "step": "email_validation"}
        except ImportError as e:
            logger.error(f"🧪 Step 1 - Email validator import: ❌ {e}")
            return {"error": f"Email validator not available: {e}", "step": "email_validator_import"}
        
        # Step 2: Check existing user
        existing_user = db_service.execute_query(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, user_data.email.split('@')[0]),
            fetch='one'
        )
        
        if existing_user:
            logger.info(f"🧪 Step 2 - User exists: ✅ Found existing user {existing_user['id']}")
            return {"error": "User already exists", "step": "user_exists", "existing_user_id": existing_user['id']}
        
        logger.info(f"🧪 Step 2 - User exists: ✅ No existing user found")
        
        # Step 3: Password hashing
        password_hash = hash_password(user_data.password)
        logger.info(f"🧪 Step 3 - Password hashing: ✅")
        
        # Step 4: Create user
        username = user_data.email.split('@')[0]
        new_user = db_service.execute_query(
            """INSERT INTO users (username, email, password_hash, name, created_at)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING id, username, email, name, created_at""",
            (username, email, password_hash, user_data.name, datetime.utcnow()),
            fetch='one'
        )
        
        if not new_user:
            logger.error(f"🧪 Step 4 - User creation: ❌ No user returned")
            return {"error": "Failed to create user", "step": "user_creation"}
        
        logger.info(f"🧪 Step 4 - User creation: ✅ User ID {new_user['id']}")
        
        # Step 5: Generate tokens (simplified)
        access_token = create_access_token(new_user['id'])
        logger.info(f"🧪 Step 5 - Token generation: ✅")
        
        # Step 6: Test login_logs table
        try:
            db_service.execute_query(
                """INSERT INTO login_logs (user_id, email, success, attempted_at, failure_reason)
                   VALUES (%s, %s, %s, %s, %s)""",
                (new_user['id'], email, True, datetime.utcnow(), "Registration successful"),
            )
            logger.info(f"🧪 Step 6 - Login logs: ✅")
        except Exception as e:
            logger.error(f"🧪 Step 6 - Login logs: ❌ {e}")
            return {"error": f"Login logs failed: {e}", "step": "login_logs", "user_created": True, "user_id": new_user['id']}
        
        logger.info(f"🧪 AUTH FLOW TEST: ✅ All steps successful")
        return {
            "success": True, 
            "user": dict(new_user),
            "access_token": access_token,
            "message": "All auth service steps successful"
        }
        
    except Exception as e:
        logger.error(f"🧪 AUTH FLOW ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"🧪 AUTH FLOW TRACEBACK: {traceback.format_exc()}")
        return {"error": str(e), "type": type(e).__name__}

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> TokenResponse:
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        logger.info(f"Registration data: name='{user_data.name}', email='{user_data.email}', password_length={len(user_data.password)}")
        
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
        logger.error(f"Authentication error during registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected registration error: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Registration traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

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
            "SELECT COUNT(*) as total_documents, COALESCE(SUM(word_count), 0) as total_words, COUNT(CASE WHEN is_favorite THEN 1 END) as favorite_documents FROM documents WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        folder_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_folders FROM folders WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        user['statistics'] = {
            "total_documents": doc_stats['total_documents'] if doc_stats else 0,
            "total_words": doc_stats['total_words'] if doc_stats else 0,
            "total_folders": folder_stats['total_folders'] if folder_stats else 0,
            "favorite_documents": doc_stats['favorite_documents'] if doc_stats else 0
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
        result = db_service.execute_query(
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
            SELECT id, title, content, status, tags, is_favorite, word_count, 
                   created_at, updated_at, folder_id, series_id
            FROM documents 
            WHERE {' AND '.join(conditions)}
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        documents = db_service.execute_query(query, params, fetch='all')
        
        # Format response
        for doc in documents:
            # Parse tags from JSON if needed
            if isinstance(doc['tags'], str):
                try:
                    doc['tags'] = json.loads(doc['tags'])
                except:
                    doc['tags'] = []
            
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

@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate, user_id: int = Depends(get_current_user_id)):
    try:
        doc_id = str(uuid.uuid4())
        
        # Use template content if provided
        content = doc_data.content
        if doc_data.template_id:
            template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
            if template:
                content = template['content']
        
        # Calculate analytics
        word_count = calculate_word_count(content)
        
        result = db_service.execute_query(
            """INSERT INTO documents (id, user_id, title, content, folder_id, status, tags, word_count, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id, title, content, folder_id, status, tags, word_count, created_at, updated_at""",
            (doc_id, user_id, doc_data.title, content, doc_data.folder_id, doc_data.status.value, json.dumps(doc_data.tags), word_count, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create document")
        
        # Format response
        document = dict(result)
        document['tags'] = json.loads(document['tags']) if document['tags'] else []
        document['created_at'] = document['created_at'].isoformat() if document['created_at'] else None
        document['updated_at'] = document['updated_at'].isoformat() if document['updated_at'] else None
        
        logger.info(f"Document created: {document['title']} by user {user_id}")
        return document
        
    except DatabaseError as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        document = db_service.execute_query(
            """SELECT id, title, content, status, tags, is_favorite, word_count, 
                      created_at, updated_at, folder_id, series_id
               FROM documents 
               WHERE id = %s AND user_id = %s""",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Format response
        doc = dict(document)
        doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
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
            "SELECT id, content FROM documents WHERE id = %s AND user_id = %s",
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
            # Create version for significant changes
            if abs(len(doc_data.content) - len(existing['content'] or '')) > 50:
                version_id = str(uuid.uuid4())
                db_service.execute_query(
                    """INSERT INTO document_versions (id, document_id, content, title, created_at, version_number)
                       VALUES (%s, %s, %s, %s, %s, 
                               (SELECT COALESCE(MAX(version_number), 0) + 1 FROM document_versions WHERE document_id = %s))""",
                    (version_id, document_id, existing['content'], 
                     db_service.execute_query("SELECT title FROM documents WHERE id = %s", (document_id,), fetch='one')['title'],
                     datetime.utcnow(), document_id)
                )
            
            updates.append("content = %s")
            params.append(doc_data.content)
            updates.append("word_count = %s")
            params.append(calculate_word_count(doc_data.content))
        
        if doc_data.status is not None:
            updates.append("status = %s")
            params.append(doc_data.status.value)
        
        if doc_data.tags is not None:
            updates.append("tags = %s")
            params.append(json.dumps(doc_data.tags))
        
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
                RETURNING id, title, content, status, tags, is_favorite, word_count, created_at, updated_at, folder_id""",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update document")
        
        # Format response
        doc = dict(result)
        doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
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
        
        # Delete document versions first (foreign key constraint)
        db_service.execute_query(
            "DELETE FROM document_versions WHERE document_id = %s",
            (document_id,)
        )
        
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

# Document versions
@app.get("/api/documents/{document_id}/versions")
async def get_document_versions(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Verify document ownership
        document = db_service.execute_query(
            "SELECT id FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        versions = db_service.execute_query(
            """SELECT id, content, title, created_at, version_number, change_summary
               FROM document_versions 
               WHERE document_id = %s 
               ORDER BY version_number DESC""",
            (document_id,),
            fetch='all'
        )
        
        # Format response
        for version in versions:
            version['created_at'] = version['created_at'].isoformat() if version['created_at'] else None
        
        return {"versions": versions}
        
    except DatabaseError as e:
        logger.error(f"Error fetching document versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document versions")

# Document favorites
@app.post("/api/documents/{document_id}/favorite")
async def toggle_document_favorite(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        document = db_service.execute_query(
            "SELECT id, is_favorite FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Toggle favorite status
        new_status = not document['is_favorite']
        
        db_service.execute_query(
            "UPDATE documents SET is_favorite = %s WHERE id = %s AND user_id = %s",
            (new_status, document_id, user_id)
        )
        
        return {
            "document_id": document_id,
            "is_favorite": new_status,
            "message": f"Document {'added to' if new_status else 'removed from'} favorites"
        }
        
    except DatabaseError as e:
        logger.error(f"Error toggling favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle favorite")

@app.get("/api/documents/favorites")
async def get_favorite_documents(user_id: int = Depends(get_current_user_id)):
    try:
        documents = db_service.execute_query(
            """SELECT id, title, content, status, tags, word_count, created_at, updated_at, folder_id
               FROM documents 
               WHERE user_id = %s AND is_favorite = TRUE
               ORDER BY updated_at DESC""",
            (user_id,),
            fetch='all'
        )
        
        # Format response
        for doc in documents:
            doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
            doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
            doc['is_favorite'] = True
        
        return documents
        
    except DatabaseError as e:
        logger.error(f"Error fetching favorite documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch favorite documents")

# Analytics endpoints
@app.get("/api/analytics/overview")
async def get_analytics_overview(user_id: int = Depends(get_current_user_id)):
    try:
        # Get overview statistics
        overview_stats = db_service.execute_query(
            """SELECT 
                COUNT(*) as total_documents,
                COALESCE(SUM(word_count), 0) as total_words,
                COUNT(CASE WHEN is_favorite THEN 1 END) as favorite_documents
               FROM documents 
               WHERE user_id = %s""",
            (user_id,),
            fetch='one'
        )
        
        folder_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_folders FROM folders WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        # Status distribution
        status_stats = db_service.execute_query(
            """SELECT status, COUNT(*) as count 
               FROM documents 
               WHERE user_id = %s 
               GROUP BY status""",
            (user_id,),
            fetch='all'
        )
        
        status_counts = {stat['status']: stat['count'] for stat in status_stats}
        
        # Recent documents
        recent_docs = db_service.execute_query(
            """SELECT id, title, updated_at, word_count
               FROM documents 
               WHERE user_id = %s 
               ORDER BY updated_at DESC 
               LIMIT 5""",
            (user_id,),
            fetch='all'
        )
        
        # Format recent docs
        for doc in recent_docs:
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return {
            "overview": {
                "total_words": overview_stats['total_words'] or 0,
                "total_documents": overview_stats['total_documents'] or 0,
                "total_folders": folder_stats['total_folders'] if folder_stats else 0,
                "favorite_documents": overview_stats['favorite_documents'] or 0
            },
            "status_distribution": status_counts,
            "recent_documents": recent_docs
        }
        
    except DatabaseError as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

# Auto-save endpoint
@app.put("/api/documents/{document_id}/auto-save")
async def auto_save_document(document_id: str, content: str = Query(...), user_id: int = Depends(get_current_user_id)):
    """Auto-save document content without creating versions"""
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

# Simple endpoints for compatibility
@app.get("/api/series")
async def get_series(user_id: int = Depends(get_current_user_id)):
    try:
        series = db_service.execute_query(
            "SELECT id, name, description, total_chapters, total_words, created_at FROM series WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
            fetch='all'
        )
        # Format dates
        for s in series:
            s['created_at'] = s['created_at'].isoformat() if s['created_at'] else None
        return series
    except:
        return []

@app.get("/api/goals")
async def get_goals():
    return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 