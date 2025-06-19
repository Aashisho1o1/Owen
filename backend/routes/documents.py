"""
Document Routes for DOG Writer API
PostgreSQL-based document management with modern REST API design.
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from services.auth_service import auth_service, AuthenticationError
from services.document_service import document_service, DocumentError

logger = logging.getLogger(__name__)

router = APIRouter()# THIS IS THE CORRECT FUNCTION THAT SHOULD BE IN documents.py

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    try:
        token = credentials.credentials
        user_info = auth_service.verify_token(token)
        return user_info['user_id']
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Authentication error in documents route: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token or authentication error.")

# Request/Response Models
class DocumentCreateRequest(BaseModel):
    title: str
    content: str = ""
    document_type: str = "novel"
    folder_id: Optional[str] = None
    series_id: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    auto_save: Optional[bool] = False

class FolderCreateRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None
    color: Optional[str] = None

@router.post("/")
async def create_document(
    request: DocumentCreateRequest,
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Create a new document"""
    try:
        document = document_service.create_document(
            user_id=user_id,
            title=request.title,
            content=request.content,
            document_type=request.document_type,
            folder_id=request.folder_id,
            series_id=request.series_id,
            tags=request.tags
        )
        
        return {
            "success": True,
            "document": document,
            "message": "Document created successfully"
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def get_user_documents(
    user_id: int = Depends(get_current_user_id_from_documents),
    folder_id: Optional[str] = Query(None),
    series_id: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's documents with optional filtering"""
    try:
        documents = document_service.get_user_documents(
            user_id=user_id,
            folder_id=folder_id,
            series_id=series_id,
            document_type=document_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user_documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Get a specific document"""
    try:
        document = document_service.get_document(document_id, user_id)
        
        return {
            "success": True,
            "document": document
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Update a document"""
    try:
        document = document_service.update_document(
            document_id=document_id,
            user_id=user_id,
            title=request.title,
            content=request.content,
            status=request.status,
            tags=request.tags,
            is_favorite=request.is_favorite,
            auto_save=request.auto_save or False
        )
        
        return {
            "success": True,
            "document": document,
            "message": "Document updated successfully"
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Delete a document"""
    try:
        success = document_service.delete_document(document_id, user_id)
        
        return {
            "success": success,
            "message": "Document deleted successfully"
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: str,
    user_id: int = Depends(get_current_user_id_from_documents),
    limit: int = Query(20, ge=1, le=50)
):
    """Get document version history"""
    try:
        versions = document_service.get_document_versions(
            document_id=document_id,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "success": True,
            "versions": versions,
            "count": len(versions)
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_document_versions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/folders")
async def create_folder(
    request: FolderCreateRequest,
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Create a new folder"""
    try:
        folder = document_service.create_folder(
            user_id=user_id,
            name=request.name,
            parent_id=request.parent_id,
            color=request.color
        )
        
        return {
            "success": True,
            "folder": folder,
            "message": "Folder created successfully"
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_folder: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/folders")
async def get_user_folders(
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Get user's folders"""
    try:
        folders = document_service.get_user_folders(user_id)
        
        return {
            "success": True,
            "folders": folders,
            "count": len(folders)
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user_folders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Debug endpoint (remove in production)
@router.get("/debug/system-status")
async def debug_system_status(
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Debug endpoint to check system status and database connectivity"""
    try:
        # Test database connectivity
        test_docs = document_service.get_user_documents(user_id, limit=1)
        
        # Get database configuration
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        return {
            "status": "healthy",
            "user_id": user_id,
            "database_type": "postgresql",
            "database_url_present": bool(DATABASE_URL),
            "can_query_documents": True,
            "test_document_count": len(test_docs),
            "message": "All systems operational"
        }
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "user_id": user_id,
            "message": "System check failed"
        }

# Series endpoints
@router.get("/series")
async def get_user_series(
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Get user's series (placeholder implementation)"""
    try:
        # TODO: Implement series functionality
        return {
            "success": True,
            "series": [],
            "count": 0,
            "message": "Series feature coming soon"
        }
    except Exception as e:
        logger.error(f"Error in get_user_series: {e}")
        return {
            "success": True,
            "series": [],
            "count": 0
        }

# Templates endpoints
@router.get("/templates")
async def get_templates(
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Get available document templates (sophisticated implementation)"""
    try:
        # Sophisticated templates matching frontend FICTION_TEMPLATES
        templates = [
            {
                "id": "romance",
                "name": "Romance Novel",
                "content": """# Romance Novel Template

## Main Characters
### Protagonist
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- Internal conflict:

### Love Interest
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- What makes them attractive:

## Plot Structure
### Meet-Cute (Chapter 1-2)
- How do they first encounter each other?
- What's the initial impression?
- What sparks their interest?

### Building Tension (Chapter 3-8)
- Obstacles to their relationship:
- Moments of connection:
- Misunderstandings:

### The Crisis (Chapter 9-10)
- What threatens to keep them apart?
- Dark moment:

### Resolution (Chapter 11-12)
- How do they overcome obstacles?
- The declaration of love:
- Happy ending:

## Chapter Outline
1. Chapter 1: [Title] - [Brief description]
2. Chapter 2: [Title] - [Brief description]
...

## Key Themes
- 
- 
- 

## Setting
- Time period:
- Location:
- Atmosphere:
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for romantic fiction with character development arcs"
            },
            {
                "id": "fantasy",
                "name": "Fantasy Epic",
                "content": """# Fantasy Epic Template

## World Building
### Magic System
- How magic works:
- Rules and limitations:
- Who can use magic:
- Cost of magic:

### Geography
- Main kingdoms/regions:
- Important locations:
- Climate and terrain:

### Cultures
- Major races/peoples:
- Languages:
- Customs and beliefs:
- Political structures:

## Main Characters
### Hero/Heroine
- Name:
- Background:
- Special abilities:
- Quest/goal:
- Character arc:

### Supporting Characters
- Mentor:
- Allies:
- Love interest:
- Companions:

### Villain
- Name:
- Motivation:
- Powers:
- Army/followers:

## The Quest
### Call to Adventure
- What forces the hero to act?
- Initial refusal:
- Crossing the threshold:

### Trials and Challenges
- Tests of character:
- Allies gained:
- Enemies faced:
- Magical items acquired:

### Final Battle
- Ultimate confrontation:
- Sacrifice required:
- Victory and transformation:

## Chapter Outline
1. Chapter 1: [Title] - [Ordinary world]
2. Chapter 2: [Title] - [Call to adventure]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for epic fantasy adventures"
            },
            {
                "id": "thriller",
                "name": "Thriller Novel",
                "content": """# Thriller Novel Template

## Main Characters
### Protagonist
- Name:
- Profession:
- Special skills:
- Personal stakes:
- Fatal flaw:

### Antagonist
- Name:
- Motivation:
- Methods:
- Resources:
- Connection to protagonist:

## Plot Structure
### The Hook (Chapter 1)
- Inciting incident:
- What grabs the reader immediately?

### Rising Action (Chapters 2-8)
- Clues discovered:
- Red herrings:
- Escalating danger:
- Plot twists:

### Climax (Chapters 9-10)
- Final confrontation:
- Revelation of truth:

### Resolution (Chapter 11)
- Aftermath:
- Justice served:

## Mystery Elements
- Central mystery:
- Key clues:
- False leads:
- Final revelation:

## Suspense Techniques
- Ticking clock:
- Information gaps:
- Foreshadowing:
- Cliffhangers:

## Chapter Outline
1. Chapter 1: [Title] - [The hook]
2. Chapter 2: [Title] - [First clue]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for suspenseful thrillers and mysteries"
            },
            {
                "id": "scifi",
                "name": "Science Fiction",
                "content": """# Science Fiction Template

## Setting
### Time Period
- Year/era:
- Technological level:
- Scientific advances:

### World/Universe
- Planets/locations:
- Societies:
- Governments:
- Conflicts:

### Technology
- Key inventions:
- Transportation:
- Communication:
- Weapons:

## Main Characters
### Protagonist
- Name:
- Role/profession:
- Relationship to technology:
- Scientific knowledge:
- Personal conflict:

### Supporting Characters
- Scientists/engineers:
- Military/government:
- Aliens/AIs:
- Civilians:

## Central Concept
- Scientific premise:
- "What if" question:
- Implications explored:

## Plot Structure
### Setup (Chapters 1-3)
- World establishment:
- Character introduction:
- Scientific concept revealed:

### Development (Chapters 4-8)
- Consequences unfold:
- Characters adapt:
- Conflicts arise:

### Resolution (Chapters 9-12)
- Scientific solution:
- Character growth:
- New equilibrium:

## Chapter Outline
1. Chapter 1: [Title] - [World introduction]
2. Chapter 2: [Title] - [Characters and conflict]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for futuristic science fiction stories"
            },
            {
                "id": "historical",
                "name": "Historical Fiction",
                "content": """# Historical Fiction Template

## Historical Setting
### Time Period
- Exact dates:
- Major historical events:
- Social conditions:
- Political climate:

### Location
- Country/region:
- Cities/towns:
- Geography:
- Architecture:

### Daily Life
- Social classes:
- Occupations:
- Food and clothing:
- Transportation:
- Entertainment:

## Main Characters
### Protagonist
- Name:
- Social class:
- Occupation:
- Education level:
- Personal goals:

### Historical Figures
- Real people involved:
- Their roles in story:
- Accuracy vs. fiction:

## Historical Accuracy
### Research Areas
- Political events:
- Social customs:
- Technology:
- Language/dialect:
- Cultural attitudes:

### Anachronisms to Avoid
- Modern concepts:
- Incorrect technology:
- Wrong social attitudes:

## Plot Integration
### Historical Events
- How they affect characters:
- Character roles in events:
- Personal vs. historical stakes:

## Chapter Outline
1. Chapter 1: [Title] - [Setting establishment]
2. Chapter 2: [Title] - [Character in historical context]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for historical fiction set in past eras"
            },
            {
                "id": "comedy",
                "name": "Comedy Novel",
                "content": """# Comedy Novel Template

## Comedic Style
### Type of Humor
- Satirical:
- Absurdist:
- Romantic comedy:
- Dark comedy:
- Parody:

### Target
- What/who are you poking fun at?
- Social issues:
- Human nature:
- Specific groups/professions:

## Main Characters
### Comic Protagonist
- Name:
- Personality flaws (source of humor):
- Misunderstandings they create:
- How they grow:

### Supporting Cast
- Straight man/woman:
- Comic relief:
- Foils:
- Eccentric characters:

## Comedic Situations
### Running Gags
- Recurring jokes:
- Character quirks:
- Situational comedy:

### Set Pieces
- Major comedic scenes:
- Physical comedy:
- Dialogue-based humor:
- Ironic situations:

## Plot Structure
### Setup (Chapters 1-3)
- Normal world:
- Character introduction:
- Comedic premise:

### Complications (Chapters 4-8)
- Misunderstandings multiply:
- Situations escalate:
- Characters react:

### Resolution (Chapters 9-12)
- Truth revealed:
- Lessons learned:
- Happy ending:

## Chapter Outline
1. Chapter 1: [Title] - [Setup and first laugh]
2. Chapter 2: [Title] - [Complications begin]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for humorous fiction and satire"
            },
            {
                "id": "memoir",
                "name": "Biography/Memoir",
                "content": """# Biography/Memoir Template

## Overview
### Subject
- Full name:
- Birth/death dates:
- Significance:
- Why their story matters:

### Scope
- Time period covered:
- Key life phases:
- Major themes:

## Life Phases
### Early Life
- Family background:
- Childhood experiences:
- Education:
- Formative events:

### Career/Achievements
- Professional life:
- Major accomplishments:
- Challenges overcome:
- Impact on others:

### Personal Life
- Relationships:
- Family:
- Personal struggles:
- Character development:

### Legacy
- Lasting impact:
- What they're remembered for:
- Lessons learned:

## Research Sources
### Primary Sources
- Letters/diaries:
- Interviews:
- Official documents:
- Photographs:

### Secondary Sources
- Biographies:
- Historical records:
- News articles:
- Academic papers:

## Narrative Structure
### Chronological vs. Thematic
- Timeline approach:
- Theme-based chapters:
- Flashbacks/forwards:

## Chapter Outline
1. Chapter 1: [Title] - [Early life]
2. Chapter 2: [Title] - [Formative period]
...
""",
                "document_type": "novel",
                "is_system": True,
                "preview_text": "A template for personal stories and biographies"
            }
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"Error in get_templates: {e}")
        return []

# Goals endpoints  
@router.get("/goals")
async def get_writing_goals(
    user_id: int = Depends(get_current_user_id_from_documents)
):
    """Get user's writing goals (placeholder implementation)"""
    try:
        # TODO: Implement writing goals functionality
        return {
            "success": True,
            "goals": [],
            "count": 0,
            "message": "Writing goals feature coming soon"
        }
    except Exception as e:
        logger.error(f"Error in get_writing_goals: {e}")
        return {
            "success": True,
            "goals": [],
            "count": 0
        }