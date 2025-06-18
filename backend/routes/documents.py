"""
Document Management API Routes for DOG Writer

RESTful API endpoints for document CRUD operations, version control,
folder organization, and advanced features.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os

from services.document_service import document_service, Document, DocumentVersion, DocumentError
from services.auth_service import verify_token
from utils.decorators import handle_exceptions

router = APIRouter(prefix="/api/documents", tags=["documents"])
security = HTTPBearer()

# Request/Response Models
class CreateDocumentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(default="")
    document_type: str = Field(default="novel")
    folder_id: Optional[str] = None
    series_id: Optional[str] = None
    chapter_number: Optional[int] = None

class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    document_type: Optional[str] = None
    folder_id: Optional[str] = None
    series_id: Optional[str] = None
    chapter_number: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    document_type: str
    folder_id: Optional[str]
    series_id: Optional[str]
    chapter_number: Optional[int]
    status: str
    tags: List[str]
    is_favorite: bool
    word_count: int
    created_at: str
    updated_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total_count: int
    total_words: int

class VersionResponse(BaseModel):
    id: str
    document_id: str
    version_number: int
    title: str
    content: str
    word_count: int
    change_summary: str
    is_auto_save: bool
    created_at: str

# Helper Functions
def get_current_user_id(token: str = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    try:
        print(f"🔍 DEBUG: Received token: {token.credentials[:50]}...")
        payload = verify_token(token.credentials)
        print(f"🔍 DEBUG: Token payload: {payload}")
        user_id = payload.get("sub")
        print(f"🔍 DEBUG: Extracted user_id: {user_id}")
        return str(user_id)
    except Exception as e:
        print(f"❌ DEBUG: Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def document_to_response(doc: Document) -> DocumentResponse:
    """Convert Document dataclass to response model"""
    return DocumentResponse(
        id=doc.id,
        user_id=doc.user_id,
        title=doc.title,
        content=doc.content,
        document_type=doc.document_type,
        folder_id=doc.folder_id,
        series_id=doc.series_id,
        chapter_number=doc.chapter_number,
        status=doc.status,
        tags=doc.tags or [],
        is_favorite=doc.is_favorite,
        word_count=doc.word_count,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
        updated_at=doc.updated_at.isoformat() if doc.updated_at else ""
    )

def version_to_response(version: DocumentVersion) -> VersionResponse:
    """Convert DocumentVersion dataclass to response model"""
    return VersionResponse(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        title=version.title,
        content=version.content,
        word_count=version.word_count,
        change_summary=version.change_summary,
        is_auto_save=version.is_auto_save,
        created_at=version.created_at.isoformat()
    )

# Document CRUD Endpoints

@router.get("/", response_model=DocumentListResponse)
@handle_exceptions()
async def get_documents(
    user_id: str = Depends(get_current_user_id),
    folder_id: Optional[str] = Query(None),
    series_id: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all documents for the authenticated user with optional filtering"""
    documents = document_service.get_user_documents(
        user_id=user_id,
        folder_id=folder_id,
        series_id=series_id,
        document_type=document_type
    )
    
    # Apply pagination
    total_count = len(documents)
    paginated_docs = documents[offset:offset + limit]
    
    # Calculate total word count
    total_words = sum(doc.word_count for doc in documents)
    
    return DocumentListResponse(
        documents=[document_to_response(doc) for doc in paginated_docs],
        total_count=total_count,
        total_words=total_words
    )

@router.get("/{document_id}", response_model=DocumentResponse)
@handle_exceptions()
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific document by ID"""
    document = document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify ownership
    if document.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return document_to_response(document)

@router.post("/", response_model=DocumentResponse, status_code=201)
@handle_exceptions()
async def create_document(
    request: CreateDocumentRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new document"""
    document = document_service.create_document(
        user_id=user_id,
        title=request.title,
        content=request.content,
        document_type=request.document_type,
        folder_id=request.folder_id,
        series_id=request.series_id,
        chapter_number=request.chapter_number
    )
    
    return document_to_response(document)

@router.get("/stats/overview")
@handle_exceptions()
async def get_document_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get overview statistics for user's documents"""
    documents = document_service.get_user_documents(user_id)
    
    total_documents = len(documents)
    total_words = sum(doc.word_count for doc in documents)
    
    # Group by document type
    type_counts = {}
    for doc in documents:
        type_counts[doc.document_type] = type_counts.get(doc.document_type, 0) + 1
    
    return {
        "total_documents": total_documents,
        "total_words": total_words,
        "document_types": type_counts,
        "average_words_per_document": total_words // total_documents if total_documents > 0 else 0
    }

@router.get("/debug/system-status")
@handle_exceptions()
async def debug_system_status(
    user_id: str = Depends(get_current_user_id)
):
    """Debug endpoint to check system status and database connectivity"""
    try:
        # Test database connectivity
        test_docs = document_service.get_user_documents(user_id)
        
        # Get database configuration
        DATABASE_URL = os.getenv("DATABASE_URL")
        db_type = "postgresql" if DATABASE_URL else "sqlite"
        
        return {
            "status": "healthy",
            "user_id": user_id,
            "database_type": db_type,
            "database_url_present": bool(DATABASE_URL),
            "document_service_db_type": document_service.db_type,
            "document_service_config": document_service.db_config,
            "user_documents_count": len(test_docs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "user_id": user_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        } 