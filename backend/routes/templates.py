"""
Templates API for DOG Writer
Document templates for different writing genres and formats.
"""

import logging
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service, AuthenticationError

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    try:
        token = credentials.credentials
        user_data = auth_service.verify_token(token)
        return user_data["user_id"]
    except Exception:
        # For templates, we might allow anonymous access in the future
        return None

router = APIRouter()

@router.get("/")
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