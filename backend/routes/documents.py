"""
Simplified Documents API for DOG Writer
Essential document management with clean, simple endpoints.
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

# Simple request models
class DocumentCreateRequest(BaseModel):
    title: str
    content: str = ""
    document_type: str = "novel"

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

router = APIRouter()

@router.post("/")
async def create_document(
    request: DocumentCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new document"""
    try:
        document = document_service.create_document(
            user_id=user_id,
            title=request.title,
            content=request.content,
            document_type=request.document_type
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
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's documents"""
    try:
        documents = document_service.get_user_documents(
            user_id=user_id,
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
    user_id: int = Depends(get_current_user_id)
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
    user_id: int = Depends(get_current_user_id)
):
    """Update a document"""
    try:
        document = document_service.update_document(
            document_id=document_id,
            user_id=user_id,
            title=request.title,
            content=request.content
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
    user_id: int = Depends(get_current_user_id)
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

# Simple endpoints for frontend compatibility
@router.get("/folders")
async def get_folders(user_id: int = Depends(get_current_user_id)):
    """Get user folders (simplified)"""
    return {"success": True, "folders": []}

@router.get("/series")
async def get_series(user_id: int = Depends(get_current_user_id)):
    """Get user series (simplified)"""
    return {"success": True, "series": []}

@router.get("/templates")
async def get_templates(user_id: int = Depends(get_current_user_id)):
    """Get document templates (simplified)"""
    return {
        "success": True, 
        "templates": [
            {
                "id": "blank",
                "name": "Blank Document",
                "description": "Start with a blank document",
                "content": ""
            },
            {
                "id": "novel",
                "name": "Novel",
                "description": "Basic novel template",
                "content": "Chapter 1\n\n"
            },
            {
                "id": "short-story",
                "name": "Short Story", 
                "description": "Short story template",
                "content": "# Title\n\n"
            }
        ]
    }

@router.get("/goals")
async def get_goals(user_id: int = Depends(get_current_user_id)):
    """Get writing goals (simplified)"""
    return {"success": True, "goals": []}