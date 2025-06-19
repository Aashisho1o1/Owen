"""
Documents API for DOG Writer - Frontend Compatible
Fixed to match exact frontend expectations and data structures.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from pydantic import BaseModel

from services.auth_service import auth_service, AuthenticationError
from services.document_service import document_service, DocumentError

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided.")
    try:
        token = credentials.credentials
        user_data = auth_service.verify_token(token)
        return user_data["user_id"]
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Authentication error in documents route: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token or authentication error.")

# Request models matching frontend expectations
class DocumentCreateRequest(BaseModel):
    title: str
    content: str = ""
    document_type: str = "novel"
    folder_id: Optional[str] = None
    series_id: Optional[str] = None
    chapter_number: Optional[int] = None

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None

class CreateFromTemplateRequest(BaseModel):
    template_id: str
    title: str
    folder_id: Optional[str] = None

router = APIRouter()

# Documents endpoints (return direct objects as frontend expects)
@router.post("/")
async def create_document(
    request: DocumentCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new document - returns Document object directly"""
    try:
        document = document_service.create_document(
            user_id=user_id,
            title=request.title,
            content=request.content,
            document_type=request.document_type,
            folder_id=request.folder_id,
            series_id=request.series_id
        )
        
        # Return direct Document object as frontend expects
        return {
            "id": document["id"],
            "title": document["title"],
            "content": request.content,
            "document_type": document["document_type"],
            "word_count": document["word_count"],
            "created_at": document["created_at"],
            "updated_at": document["created_at"],
            "user_id": str(user_id),
            "folder_id": request.folder_id,
            "series_id": request.series_id,
            "chapter_number": request.chapter_number,
            "status": "draft",
            "is_favorite": False,
            "tags": []
        }
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def get_user_documents(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's documents - returns DocumentsResponse format"""
    try:
        documents = document_service.get_user_documents(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Format for frontend DocumentsResponse interface
        formatted_documents = []
        for doc in documents:
            formatted_documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "content": doc.get("content", ""),
                "document_type": doc["document_type"],
                "word_count": doc["word_count"],
                "created_at": doc["created_at"],
                "updated_at": doc["updated_at"],
                "user_id": str(user_id),
                "folder_id": doc.get("folder_id"),
                "series_id": doc.get("series_id"),
                "chapter_number": doc.get("chapter_number"),
                "status": doc.get("status", "draft"),
                "is_favorite": doc.get("is_favorite", False),
                "tags": doc.get("tags", [])
            })
        
        return {
            "documents": formatted_documents,
            "total": len(formatted_documents)
        }
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_user_documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific document - returns Document object directly"""
    try:
        doc = document_service.get_document(document_id, user_id)
        
        # Return direct Document object as frontend expects
        return {
            "id": doc["id"],
            "title": doc["title"],
            "content": doc["content"],
            "document_type": doc["document_type"],
            "word_count": doc["word_count"],
            "created_at": doc["created_at"],
            "updated_at": doc["updated_at"],
            "user_id": str(user_id),
            "folder_id": doc.get("folder_id"),
            "series_id": doc.get("series_id"),
            "chapter_number": doc.get("chapter_number"),
            "status": doc.get("status", "draft"),
            "is_favorite": doc.get("is_favorite", False),
            "tags": doc.get("tags", [])
        }
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Update a document - returns Document object directly"""
    try:
        document = document_service.update_document(
            document_id=document_id,
            user_id=user_id,
            title=request.title,
            content=request.content,
            tags=request.tags,
            is_favorite=request.is_favorite
        )
        
        # Return direct Document object as frontend expects
        return {
            "id": document["id"],
            "title": document["title"],
            "content": document["content"],
            "document_type": document["document_type"],
            "word_count": document["word_count"],
            "created_at": document["created_at"],
            "updated_at": document["updated_at"],
            "user_id": str(user_id),
            "folder_id": document.get("folder_id"),
            "series_id": document.get("series_id"),
            "chapter_number": document.get("chapter_number"),
            "status": document.get("status", "draft"),
            "is_favorite": document.get("is_favorite", False),
            "tags": document.get("tags", [])
        }
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a document"""
    try:
        success = document_service.delete_document(document_id, user_id)
        return {"success": success, "message": "Document deleted successfully"}
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Template functionality
@router.post("/from-template")
async def create_from_template(
    request: CreateFromTemplateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create document from template"""
    try:
        # Get template content
        templates = {
            "blank": "",
            "novel": "Chapter 1\n\n",
            "short-story": "# Title\n\n",
            "romance": "# Romance Novel\n\nChapter 1\n\n",
            "fantasy": "# Fantasy Epic\n\nChapter 1: The Beginning\n\n",
            "thriller": "# Thriller\n\nChapter 1: The Hook\n\n"
        }
        
        content = templates.get(request.template_id, "")
        
        document = document_service.create_document(
            user_id=user_id,
            title=request.title,
            content=content,
            document_type="novel",
            folder_id=request.folder_id
        )
        
        # Return direct Document object
        return {
            "id": document["id"],
            "title": document["title"],
            "content": content,
            "document_type": document["document_type"],
            "word_count": document["word_count"],
            "created_at": document["created_at"],
            "updated_at": document["created_at"],
            "user_id": str(user_id),
            "folder_id": request.folder_id,
            "series_id": None,
            "chapter_number": None,
            "status": "draft",
            "is_favorite": False,
            "tags": []
        }
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_from_template: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Folders endpoint (required by frontend)
@router.get("/folders")
async def get_folders(user_id: int = Depends(get_current_user_id)):
    """Get user folders - returns array directly"""
    try:
        folders = document_service.get_user_folders(user_id)
        return folders  # Return direct array as frontend expects
    except Exception as e:
        logger.info(f"No folders found for user {user_id}: {e}")
        return []  # Return empty array if no folders or service unavailable

# Series endpoint (required by frontend)  
@router.get("/series")
async def get_series(user_id: int = Depends(get_current_user_id)):
    """Get user series - returns array directly"""
    return []  # Simple implementation for now

# Templates endpoint (required by frontend)
@router.get("/templates")
async def get_templates(user_id: int = Depends(get_current_user_id)):
    """Get document templates - returns array matching DocumentTemplate interface"""
    return [
        {
            "id": "blank",
            "name": "Blank Document",
            "content": "",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Start with a blank document"
        },
        {
            "id": "novel",
            "name": "Novel",
            "content": "Chapter 1\n\n",
            "document_type": "novel", 
            "is_system": True,
            "preview_text": "Basic novel template with chapter structure"
        },
        {
            "id": "short-story",
            "name": "Short Story",
            "content": "# Title\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Short story template"
        },
        {
            "id": "romance",
            "name": "Romance Novel",
            "content": "# Romance Novel\n\nChapter 1\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Romance novel template with romantic elements"
        },
        {
            "id": "fantasy", 
            "name": "Fantasy Epic",
            "content": "# Fantasy Epic\n\nChapter 1: The Beginning\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Fantasy template for epic adventures"
        },
        {
            "id": "thriller",
            "name": "Thriller",
            "content": "# Thriller\n\nChapter 1: The Hook\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Thriller template for suspenseful stories"
        }
    ]

# Goals endpoint (required by frontend)
@router.get("/goals")
async def get_goals(user_id: int = Depends(get_current_user_id)):
    """Get writing goals - returns array directly"""
    return []  # Simple implementation for now