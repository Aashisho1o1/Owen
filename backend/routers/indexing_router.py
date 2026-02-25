"""
Indexing Router - API endpoints for document indexing and contextual retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from dependencies import get_current_user_id
from services.indexing.hybrid_indexer import get_hybrid_indexer

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/indexing", tags=["indexing"])

# Initialize indexer lazily to avoid blocking app startup on model downloads
indexer = None

def get_indexer():
    global indexer
    if indexer is None:
        indexer = get_hybrid_indexer(collection_name="documents")
    return indexer


# Request/Response models
class IndexDocumentRequest(BaseModel):
    doc_id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None

class IndexFolderRequest(BaseModel):
    documents: List[Dict[str, Any]]  # List of {doc_id, text, metadata}

class ContextualFeedbackRequest(BaseModel):
    highlighted_text: str
    doc_id: str
    context_window: Optional[int] = 500

class ConsistencyCheckRequest(BaseModel):
    statement: str
    doc_id: str
    check_type: Optional[str] = 'all'

class WritingSuggestionsRequest(BaseModel):
    context: str
    suggestion_type: Optional[str] = 'all'

class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = 'hybrid'
    filters: Optional[Dict[str, Any]] = None

# Endpoints

@router.post("/index-document")
async def index_document(
    request: IndexDocumentRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Index a single document for enhanced contextual understanding
    """
    try:
        # Add user metadata
        if request.metadata is None:
            request.metadata = {}
        request.metadata['user_id'] = current_user_id

        # Index document
        result = await get_indexer().index_document(
            doc_id=request.doc_id,
            text=request.text,
            metadata=request.metadata
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail="Indexing failed")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to index document {request.doc_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.post("/index-folder")
async def index_folder(
    request: IndexFolderRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Index multiple related documents (e.g., chapters in a book)
    """
    try:
        # Prepare documents with user ID
        documents = []
        for doc in request.documents:
            metadata = doc.get('metadata', {})
            metadata['user_id'] = current_user_id
            documents.append((
                doc['doc_id'],
                doc['text'],
                metadata
            ))

        # Index folder
        result = await get_indexer().index_folder(documents)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to index folder: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.post("/contextual-feedback")
async def get_contextual_feedback(
    request: ContextualFeedbackRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get contextual feedback for highlighted text
    """
    try:
        feedback = await get_indexer().get_contextual_feedback(
            highlighted_text=request.highlighted_text,
            doc_id=request.doc_id,
            context_window=request.context_window
        )

        return feedback

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contextual feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.post("/check-consistency")
async def check_consistency(
    request: ConsistencyCheckRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Check consistency of a statement against the knowledge base
    """
    try:
        result = await get_indexer().check_consistency(
            statement=request.statement,
            doc_id=request.doc_id,
            check_type=request.check_type
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check consistency: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.post("/writing-suggestions")
async def get_writing_suggestions(
    request: WritingSuggestionsRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get AI-powered writing suggestions based on context
    """
    try:
        suggestions = await get_indexer().get_writing_suggestions(
            context=request.context,
            suggestion_type=request.suggestion_type
        )

        return suggestions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get writing suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.post("/search")
async def search(
    request: SearchRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Unified search across vector store and knowledge graph
    """
    try:
        # Add user filter
        if request.filters is None:
            request.filters = {}
        request.filters['user_id'] = current_user_id

        results = get_indexer().search(
            query=request.query,
            search_type=request.search_type,
            filters=request.filters
        )

        return {
            'query': request.query,
            'search_type': request.search_type,
            'results': results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.get("/document-stats/{doc_id}")
async def get_document_stats(
    doc_id: str,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Get indexing statistics for a document
    """
    try:
        stats = get_indexer().get_document_stats(doc_id)

        # Verify user owns this document
        if 'metadata' in stats and stats['metadata'].get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document stats for {doc_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

@router.get("/export-graph")
async def export_knowledge_graph(
    format: str = 'json',
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Export the knowledge graph for visualization
    """
    try:
        graph_data = get_indexer().export_knowledge_graph(format)

        return {
            'format': format,
            'graph': graph_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export knowledge graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred")

# Health check endpoint
@router.get("/health")
async def indexing_health():
    """
    Check if indexing service is healthy
    """
    if indexer is None:
        return {
            'status': 'not_initialized',
            'indexed_documents': 0,
            'graph_nodes': 0,
            'graph_edges': 0
        }

    return {
        'status': 'healthy',
        'indexed_documents': len(indexer.indexed_documents),
        'graph_nodes': indexer.graph_builder.graph.number_of_nodes() if indexer.graph_builder.graph else 0,
        'graph_edges': indexer.graph_builder.graph.number_of_edges() if indexer.graph_builder.graph else 0
    }
