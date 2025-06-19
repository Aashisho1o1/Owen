"""
Folders API for DOG Writer
Document organization and folder management endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

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
        logger.error(f"Authentication error in folders route: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Invalid token or authentication error.")

router = APIRouter()

@router.get("/")
async def get_folders(user_id: int = Depends(get_current_user_id)):
    """Get user folders - returns array directly"""
    try:
        folders = document_service.get_user_folders(user_id)
        return folders  # Return direct array as frontend expects
    except Exception as e:
        logger.info(f"No folders found for user {user_id}: {e}")
        return []  # Return empty array if no folders or service unavailable 