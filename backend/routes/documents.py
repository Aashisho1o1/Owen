"""
Simple Documents API for DOG Writer
Minimal, working document management.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from services.auth_service import auth_service

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    try:
        token = credentials.credentials
        user_data = auth_service.verify_token(token)
        return user_data["user_id"]
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication required")

# Simple request models
class DocumentCreateRequest(BaseModel):
    title: str
    content: str = ""
    document_type: str = "novel"
    folder_id: Optional[str] = None

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class CreateFromTemplateRequest(BaseModel):
    template_id: str
    title: str
    folder_id: Optional[str] = None

router = APIRouter()

# In-memory storage for development/testing
documents_store = {}

@router.post("/")
async def create_document(
    request: DocumentCreateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new document - ultra simple"""
    try:
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        document = {
            "id": doc_id,
            "title": request.title,
            "content": request.content,
            "document_type": request.document_type,
            "word_count": len(request.content.split()) if request.content else 0,
            "created_at": now,
            "updated_at": now,
            "user_id": str(user_id),
            "folder_id": request.folder_id,
            "series_id": None,
            "chapter_number": None,
            "status": "draft",
            "is_favorite": False,
            "tags": []
        }
        
        # Store in memory (for now)
        documents_store[doc_id] = document
        
        logger.info(f"Created document {doc_id} for user {user_id}")
        return document
        
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@router.get("/")
async def get_user_documents(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's documents - ultra simple"""
    try:
        # Filter documents for this user
        user_docs = [
            doc for doc in documents_store.values() 
            if doc["user_id"] == str(user_id)
        ]
        
        # Apply pagination
        paginated_docs = user_docs[offset:offset + limit]
        
        return {
            "documents": paginated_docs,
            "total": len(user_docs)
        }
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documents")

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific document"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
            
        document = documents_store[document_id]
        
        # Check ownership
        if document["user_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
            
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Update a document"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
            
        document = documents_store[document_id]
        
        # Check ownership
        if document["user_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        if request.title is not None:
            document["title"] = request.title
        if request.content is not None:
            document["content"] = request.content
            document["word_count"] = len(request.content.split()) if request.content else 0
            
        document["updated_at"] = datetime.utcnow().isoformat()
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a document"""
    try:
        if document_id not in documents_store:
            raise HTTPException(status_code=404, detail="Document not found")
            
        document = documents_store[document_id]
        
        # Check ownership
        if document["user_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="Access denied")
            
        del documents_store[document_id]
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.post("/from-template")
async def create_from_template(
    request: CreateFromTemplateRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Create document from template - ultra simple"""
    try:
        # Simple templates
        templates = {
            "blank": "",
            "novel": "Chapter 1\n\n",
            "short-story": "# Title\n\n",
            "romance": "# Romance Novel\n\nChapter 1\n\n",
            "fantasy": "# Fantasy Epic\n\nChapter 1: The Beginning\n\n",
            "thriller": "# Thriller\n\nChapter 1: The Hook\n\n"
        }
        
        content = templates.get(request.template_id, "")
        
        # Create document using same logic as create_document
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        document = {
            "id": doc_id,
            "title": request.title,
            "content": content,
            "document_type": "novel",
            "word_count": len(content.split()) if content else 0,
            "created_at": now,
            "updated_at": now,
            "user_id": str(user_id),
            "folder_id": request.folder_id,
            "series_id": None,
            "chapter_number": None,
            "status": "draft",
            "is_favorite": False,
            "tags": []
        }
        
        documents_store[doc_id] = document
        
        logger.info(f"Created document from template {request.template_id}")
        return document
        
    except Exception as e:
        logger.error(f"Error creating from template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document from template")