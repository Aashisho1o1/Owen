"""
FastAPI Dependencies for DOG Writer

This module contains shared dependencies used across the application,
such as authentication and database sessions, to ensure consistency and
adherence to the DRY (Don't Repeat Yourself) principle.
"""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service, AuthenticationError

logger = logging.getLogger(__name__)

# Reusable security scheme using HTTP Bearer for JWT tokens.
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    FastAPI dependency to get the current user's ID from a JWT token.

    This function serves as the single source of truth for user authentication
    on all protected routes. It ensures that every protected endpoint
    goes through the same validation logic.

    It extracts the token from the 'Authorization: Bearer <token>' header,
    verifies its signature and expiration, and checks if the user exists
    and is active in the database.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is missing, malformed, invalid,
              expired, or the associated user is not found or inactive.
            - 500 Internal Server Error: For any other unexpected errors
              during the authentication process.

    Returns:
        int: The authenticated user's unique ID.
    """
    if credentials is None or not credentials.credentials:
        logger.warning("Authentication attempt failed: No credentials provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user_info = auth_service.verify_token(token)
        logger.info(f"Successfully authenticated user_id: {user_info['user_id']}")
        return user_info['user_id']
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for token. Reason: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"An unexpected server error occurred during authentication: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials due to a server error.",
        ) 