"""
DOG Writer Backend - Google Docs-Like Document Management System
Comprehensive document editor with folders, versions, sharing, analytics, and collaboration features
"""

import os
import logging
import uuid
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

# Enhanced in-memory storage
users_store: Dict[str, dict] = {}
documents_store: Dict[str, dict] = {}
folders_store: Dict[str, dict] = {}
document_versions_store: Dict[str, List[dict]] = {}
document_analytics_store: Dict[str, dict] = {}
activity_logs_store: Dict[str, List[dict]] = {}
favorites_store: Dict[str, Set[str]] = {}

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

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting DOG Writer - Google Docs-Like Document Management System")
    logger.info(f"📚 Loaded {len(templates_store)} comprehensive templates")
    logger.info("✨ Features: Folders, Versions, Analytics, Auto-save, Collaboration-ready")
    yield
    logger.info("🛑 Shutting down DOG Writer API")

# Create FastAPI app
app = FastAPI(
    title="DOG Writer - Google Docs-Like Document System",
    description="Comprehensive document management with folders, versions, sharing, and collaboration",
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
    return {
        "message": "DOG Writer - Google Docs-Like Document Management System",
        "version": "2.0.0",
        "status": "healthy",
        "features": [
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
            "total_users": len(users_store),
            "total_documents": len(documents_store),
            "total_folders": len(folders_store),
            "total_templates": len(templates_store)
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "users_count": len(users_store),
            "documents_count": len(documents_store),
            "folders_count": len(folders_store),
            "templates_count": len(templates_store),
            "total_document_versions": sum(len(versions) for versions in document_versions_store.values()),
            "total_activities": sum(len(activities) for activities in activity_logs_store.values())
        }
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> TokenResponse:
    if any(user['email'] == user_data.email for user in users_store.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
        "last_login": datetime.utcnow().isoformat(),
        "preferences": {
            "theme": "light",
            "auto_save_interval": 30,
            "default_folder": None
        }
    }
    
    users_store[user_id] = user
    favorites_store[user_id] = set()
    
    access_token = create_access_token(user_id)
    user_response = {key: value for key, value in user.items() if key != 'password_hash'}
    
    logger.info(f"New user registered: {user_data.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.post("/api/auth/login")
async def login(login_data: UserLogin) -> TokenResponse:
    user = None
    for stored_user in users_store.values():
        if stored_user['email'] == login_data.email:
            user = stored_user
            break
    
    if not user or not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user['last_login'] = datetime.utcnow().isoformat()
    access_token = create_access_token(user['id'])
    user_response = {key: value for key, value in user.items() if key != 'password_hash'}
    
    logger.info(f"User logged in: {login_data.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@app.get("/api/auth/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    user = users_store.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_documents = [doc for doc in documents_store.values() if doc['user_id'] == user_id]
    user_folders = [folder for folder in folders_store.values() if folder['user_id'] == user_id]
    
    profile = {key: value for key, value in user.items() if key != 'password_hash'}
    profile['statistics'] = {
        "total_documents": len(user_documents),
        "total_folders": len(user_folders),
        "favorite_documents": len(favorites_store.get(user_id, set())),
        "total_words": sum(calculate_word_count(doc['content']) for doc in user_documents)
    }
    
    return profile

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
async def get_folders(user_id: str = Depends(get_current_user_id)):
    user_folders = [folder for folder in folders_store.values() if folder['user_id'] == user_id]
    
    for folder in user_folders:
        folder['document_count'] = len([
            doc for doc in documents_store.values() 
            if doc.get('folder_id') == folder['id'] and doc['user_id'] == user_id
        ])
    
    return user_folders

@app.post("/api/folders")
async def create_folder(folder_data: FolderCreate, user_id: str = Depends(get_current_user_id)):
    folder_id = str(uuid.uuid4())
    
    folder = {
        "id": folder_id,
        "name": folder_data.name,
        "description": folder_data.description,
        "parent_id": folder_data.parent_id,
        "color": folder_data.color,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    folders_store[folder_id] = folder
    logger.info(f"Folder created: {folder_data.name} by user {user_id}")
    
    return folder

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder_data: FolderUpdate, user_id: str = Depends(get_current_user_id)):
    folder = folders_store.get(folder_id)
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
    
    folder['updated_at'] = datetime.utcnow().isoformat()
    
    return folder

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str, user_id: str = Depends(get_current_user_id)):
    folder = folders_store.get(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if folder['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Move documents to root
    for document in documents_store.values():
        if document.get('folder_id') == folder_id and document['user_id'] == user_id:
            document['folder_id'] = None
    
    del folders_store[folder_id]
    
    return {"message": "Folder deleted successfully"}

# Enhanced document endpoints
@app.get("/api/documents")
async def get_documents(
    user_id: str = Depends(get_current_user_id),
    folder_id: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    offset: Optional[int] = Query(0)
):
    user_documents = [doc for doc in documents_store.values() if doc['user_id'] == user_id]
    
    # Apply filters
    if folder_id:
        user_documents = [doc for doc in user_documents if doc.get('folder_id') == folder_id]
    
    if status:
        user_documents = [doc for doc in user_documents if doc.get('status') == status.value]
    
    if search:
        search_lower = search.lower()
        user_documents = [
            doc for doc in user_documents 
            if search_lower in doc['title'].lower() or search_lower in doc['content'].lower()
        ]
    
    # Sort by updated_at (most recent first)
    user_documents.sort(key=lambda x: x['updated_at'], reverse=True)
    
    total_count = len(user_documents)
    user_documents = user_documents[offset:offset + limit]
    
    # Add analytics
    for doc in user_documents:
        analytics = document_analytics_store.get(doc['id'], {})
        doc['analytics'] = {
            "word_count": calculate_word_count(doc['content']),
            "character_count": calculate_character_count(doc['content']),
            "reading_time_minutes": calculate_reading_time(doc['content']),
            "view_count": analytics.get('view_count', 0),
            "edit_count": analytics.get('edit_count', 0)
        }
        doc['is_favorite'] = doc['id'] in favorites_store.get(user_id, set())
    
    return {
        "documents": user_documents,
        "total_count": total_count,
        "page_info": {
            "has_next": offset + limit < total_count,
            "has_previous": offset > 0,
            "current_offset": offset,
            "limit": limit
        }
    }

@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate, user_id: str = Depends(get_current_user_id)):
    doc_id = str(uuid.uuid4())
    
    # Use template content if provided
    content = doc_data.content
    template_used = None
    if doc_data.template_id:
        template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
        if template:
            content = template['content']
            template_used = template
    
    document = {
        "id": doc_id,
        "title": doc_data.title,
        "content": content,
        "user_id": user_id,
        "template_id": doc_data.template_id,
        "folder_id": doc_data.folder_id,
        "status": doc_data.status.value,
        "tags": doc_data.tags,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "template_used": template_used['title'] if template_used else None
    }
    
    documents_store[doc_id] = document
    
    # Initialize analytics
    document_analytics_store[doc_id] = {
        "document_id": doc_id,
        "view_count": 0,
        "edit_count": 1,
        "word_count": calculate_word_count(content),
        "character_count": calculate_character_count(content),
        "reading_time_minutes": calculate_reading_time(content),
        "last_viewed": None,
        "last_edited": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Document created: {doc_data.title} by user {user_id}")
    return document

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update view analytics
    if document_id not in document_analytics_store:
        document_analytics_store[document_id] = {
            "document_id": document_id,
            "view_count": 0,
            "edit_count": 0,
            "word_count": calculate_word_count(document['content']),
            "character_count": calculate_character_count(document['content']),
            "reading_time_minutes": calculate_reading_time(document['content']),
            "last_viewed": None,
            "last_edited": None
        }
    
    analytics = document_analytics_store[document_id]
    analytics['view_count'] += 1
    analytics['last_viewed'] = datetime.utcnow().isoformat()
    
    document['analytics'] = analytics
    document['is_favorite'] = document_id in favorites_store.get(user_id, set())
    
    return document

@app.put("/api/documents/{document_id}")
async def update_document(
    document_id: str, 
    doc_data: DocumentUpdate, 
    user_id: str = Depends(get_current_user_id)
):
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create version for significant changes
    if doc_data.content is not None and doc_data.content != document['content']:
        if abs(len(doc_data.content) - len(document['content'])) > 50:
            if document_id not in document_versions_store:
                document_versions_store[document_id] = []
            
            version = {
                "id": str(uuid.uuid4()),
                "content": document['content'],
                "title": document['title'],
                "created_at": datetime.utcnow().isoformat(),
                "version_number": len(document_versions_store[document_id]) + 1
            }
            
            document_versions_store[document_id].append(version)
            
            # Keep only last 20 versions
            if len(document_versions_store[document_id]) > 20:
                document_versions_store[document_id] = document_versions_store[document_id][-20:]
    
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
    
    document['updated_at'] = datetime.utcnow().isoformat()
    
    # Update analytics
    if document_id in document_analytics_store:
        analytics = document_analytics_store[document_id]
        analytics['edit_count'] += 1
        analytics['last_edited'] = datetime.utcnow().isoformat()
        if doc_data.content is not None:
            analytics['word_count'] = calculate_word_count(doc_data.content)
            analytics['character_count'] = calculate_character_count(doc_data.content)
            analytics['reading_time_minutes'] = calculate_reading_time(doc_data.content)
    
    return document

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Clean up related data
    if document_id in document_versions_store:
        del document_versions_store[document_id]
    if document_id in document_analytics_store:
        del document_analytics_store[document_id]
    
    # Remove from favorites
    if user_id in favorites_store:
        favorites_store[user_id].discard(document_id)
    
    del documents_store[document_id]
    
    logger.info(f"Document deleted: {document['title']} by user {user_id}")
    return {"message": "Document deleted successfully"}

# Document versions
@app.get("/api/documents/{document_id}/versions")
async def get_document_versions(document_id: str, user_id: str = Depends(get_current_user_id)):
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    versions = document_versions_store.get(document_id, [])
    return {"versions": versions}

# Document favorites
@app.post("/api/documents/{document_id}/favorite")
async def toggle_document_favorite(document_id: str, user_id: str = Depends(get_current_user_id)):
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id not in favorites_store:
        favorites_store[user_id] = set()
    
    if document_id in favorites_store[user_id]:
        favorites_store[user_id].remove(document_id)
        is_favorite = False
    else:
        favorites_store[user_id].add(document_id)
        is_favorite = True
    
    return {
        "document_id": document_id,
        "is_favorite": is_favorite,
        "message": f"Document {'added to' if is_favorite else 'removed from'} favorites"
    }

@app.get("/api/documents/favorites")
async def get_favorite_documents(user_id: str = Depends(get_current_user_id)):
    favorite_ids = favorites_store.get(user_id, set())
    favorite_documents = [
        documents_store[doc_id] for doc_id in favorite_ids 
        if doc_id in documents_store and documents_store[doc_id]['user_id'] == user_id
    ]
    
    # Add analytics
    for doc in favorite_documents:
        analytics = document_analytics_store.get(doc['id'], {})
        doc['analytics'] = {
            "word_count": calculate_word_count(doc['content']),
            "character_count": calculate_character_count(doc['content']),
            "reading_time_minutes": calculate_reading_time(doc['content']),
            "view_count": analytics.get('view_count', 0),
            "edit_count": analytics.get('edit_count', 0)
        }
        doc['is_favorite'] = True
    
    return favorite_documents

# Analytics endpoints
@app.get("/api/analytics/overview")
async def get_analytics_overview(user_id: str = Depends(get_current_user_id)):
    user_documents = [doc for doc in documents_store.values() if doc['user_id'] == user_id]
    
    total_words = sum(calculate_word_count(doc['content']) for doc in user_documents)
    total_documents = len(user_documents)
    total_folders = len([folder for folder in folders_store.values() if folder['user_id'] == user_id])
    
    # Status distribution
    status_counts = {}
    for doc in user_documents:
        status = doc.get('status', 'draft')
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
                "word_count": calculate_word_count(doc['content'])
            } for doc in recent_documents
        ]
    }

# Auto-save endpoint
@app.put("/api/documents/{document_id}/auto-save")
async def auto_save_document(
    document_id: str,
    content: str,
    user_id: str = Depends(get_current_user_id)
):
    """Auto-save document content without creating versions"""
    document = documents_store.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Only save if content changed
    if document['content'] != content:
        document['content'] = content
        document['updated_at'] = datetime.utcnow().isoformat()
        
        # Update analytics
        if document_id in document_analytics_store:
            analytics = document_analytics_store[document_id]
            analytics['word_count'] = calculate_word_count(content)
            analytics['character_count'] = calculate_character_count(content)
            analytics['reading_time_minutes'] = calculate_reading_time(content)
    
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