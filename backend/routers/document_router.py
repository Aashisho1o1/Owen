"""
Document Router
Handles all document-related endpoints including CRUD operations and auto-save.
Extracted from main.py as part of God File refactoring.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request

# Import models from centralized schemas
from models.schemas import (
    DocumentCreate, DocumentUpdate, DocumentFromTemplateCreate, DocumentStatus
)

# Import services
from services.database import db_service, DatabaseError

# Import production rate limiter
from services.rate_limiter import check_rate_limit

# Import centralized authentication dependency
from dependencies import get_current_user_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
)

# Helper function
def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0

@router.get("")
async def get_documents(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    folder_id: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    offset: Optional[int] = Query(0)
):
    """Get user documents with optional filtering"""
    try:
        # Apply rate limiting for document listing
        await check_rate_limit(request, "general")
        
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

@router.post("/from-template")
async def create_document_from_template(
    doc_data: DocumentFromTemplateCreate, 
    request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new document from a template"""
    try:
        # Apply rate limiting for document creation
        await check_rate_limit(request, "general")
        
        logger.info(f"Creating document from template: {doc_data.template_id}")
        
        # Import templates store from main.py (this should be moved to a service)
        from main import templates_store
        
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

@router.post("")
async def create_document(doc_data: DocumentCreate, request: Request, user_id: int = Depends(get_current_user_id)):
    """Create a new document"""
    try:
        # Apply rate limiting for document creation
        await check_rate_limit(request, "general")
        
        logger.info(f"Creating document: {doc_data.title}")
        
        doc_id = str(uuid.uuid4())
        content = doc_data.content
        
        # Use template content if provided
        if doc_data.template_id:
            from main import templates_store
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

@router.get("/{document_id}")
async def get_document(document_id: str, request: Request, user_id: int = Depends(get_current_user_id)):
    """Get a specific document by ID"""
    try:
        # Apply rate limiting for document access
        await check_rate_limit(request, "general")
        
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

@router.put("/{document_id}")
async def update_document(
    document_id: str, 
    doc_data: DocumentUpdate, 
    request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """Update a document"""
    try:
        # Apply rate limiting for document updates
        await check_rate_limit(request, "general")
        
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
            return await get_document(document_id, request, user_id)
        
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

@router.delete("/{document_id}")
async def delete_document(document_id: str, request: Request, user_id: int = Depends(get_current_user_id)):
    """Delete a document"""
    try:
        # Apply rate limiting for document deletion
        await check_rate_limit(request, "general")
        
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

@router.put("/{document_id}/auto-save")
async def auto_save_document(
    document_id: str, 
    request: Request,
    user_id: int = Depends(get_current_user_id),
    content: str = Query(...)
):
    """Auto-save document content"""
    try:
        # Apply rate limiting for auto-save (more lenient for frequent saves)
        await check_rate_limit(request, "general")
        
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
 