"""
Document Routes for DOG Writer API
PostgreSQL-based document management with modern REST API design.
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.auth_service import get_current_user_id, AuthenticationError
from services.document_service import document_service, DocumentError

logger = logging.getLogger(__name__)

router = APIRouter()

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
    user_id: int = Depends(get_current_user_id)
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
        logger.error(f"Unexpected error in create_document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/")
async def get_user_documents(
    user_id: int = Depends(get_current_user_id),
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

@router.get("/{document_id}/versions")
async def get_document_versions(
    document_id: str,
    user_id: int = Depends(get_current_user_id),
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
    user_id: int = Depends(get_current_user_id)
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
    user_id: int = Depends(get_current_user_id)
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
    user_id: int = Depends(get_current_user_id)
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
            "user_id": user_id,
            "database_type": "postgresql",
            "error": str(e),
            "message": "System check failed"
        } 