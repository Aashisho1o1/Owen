"""
Authentication Service for DOG Writer

Basic JWT token verification and user authentication.
Supports both session-based and JWT authentication.
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

# This service no longer needs to know about the database path directly.
# It will receive a connection from the service that calls it.
# However, for the standalone init_db script to work, we need a way to get the config.
# We will rely on the global configuration set in document_service.py for now.

# from services.document_service import DB_TYPE, DB_CONFIG
# This would be a better approach but causes circular imports.
# For now, the services will implicitly share the database configuration
# established in main.py and document_service.py

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

class AuthError(Exception):
    """Custom exception for authentication errors"""
    pass

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating JWT token: {e}")
        raise AuthError(f"Failed to create access token: {e}")

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise AuthError("Token has expired")
        
        # Ensure user ID is a string for consistency
        if "sub" in payload:
            payload["sub"] = str(payload["sub"])
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthError(f"Invalid token: {e}")
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise AuthError(f"Token verification failed: {e}")

def get_user_id_from_token(token: str) -> str:
    """Extract user ID from JWT token"""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthError("Token does not contain user ID")
        
        return str(user_id)  # Ensure it's a string
        
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Error extracting user ID from token: {e}")
        raise AuthError(f"Failed to extract user ID: {e}")

def create_user_token(user_id: str, username: str = None, email: str = None) -> str:
    """Create a JWT token for a user"""
    try:
        token_data = {
            "sub": user_id,  # Subject (user ID)
            "iat": datetime.utcnow(),  # Issued at
        }
        
        # Add optional claims
        if username:
            token_data["username"] = username
        if email:
            token_data["email"] = email
        
        return create_access_token(token_data)
        
    except Exception as e:
        logger.error(f"Error creating user token: {e}")
        raise AuthError(f"Failed to create user token: {e}")

def validate_user_access(token: str, required_user_id: str = None) -> Dict[str, Any]:
    """Validate user access and optionally check if token belongs to specific user"""
    try:
        payload = verify_token(token)
        token_user_id = payload.get("sub")
        
        if required_user_id and token_user_id != required_user_id:
            raise AuthError("Token does not belong to the required user")
        
        return payload
        
    except AuthError:
        raise
    except Exception as e:
        logger.error(f"Error validating user access: {e}")
        raise AuthError(f"Access validation failed: {e}")

# For development: create a temporary session-based auth
_session_users = {}  # In-memory session storage (for development only)

def create_session_user(user_id: str = None) -> str:
    """Create a temporary session user (for development)"""
    import uuid
    
    if not user_id:
        user_id = str(uuid.uuid4())
    
    session_token = create_user_token(user_id, f"user_{user_id[:8]}")
    _session_users[user_id] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "token": session_token
    }
    
    logger.info(f"Created session user: {user_id}")
    return session_token

def get_session_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get session user information"""
    return _session_users.get(user_id)

# Mock authentication for development
def mock_verify_token(token: str) -> Dict[str, Any]:
    """Mock token verification for development (when no real auth is implemented)"""
    if not token or token == "Bearer":
        # Create a default user for development
        return {
            "sub": "dev-user-001",
            "username": "developer",
            "email": "dev@dogwriter.com",
            "iat": datetime.utcnow().timestamp()
        }
    
    try:
        # First try real token verification
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise AuthError("Token has expired")
        
        # Ensure user ID is a string for consistency
        if "sub" in payload:
            payload["sub"] = str(payload["sub"])
        
        return payload
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, AuthError):
        # If real token verification fails, return default dev user
        logger.warning("Using mock authentication for development")
        return {
            "sub": "dev-user-001",
            "username": "developer", 
            "email": "dev@dogwriter.com",
            "iat": datetime.utcnow().timestamp()
        }

# Don't override in production - use real auth
if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
    # Use real authentication in production
    pass
else:
    # Use mock auth only in development
    verify_token = mock_verify_token 