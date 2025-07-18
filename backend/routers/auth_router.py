"""
Authentication Router
Handles all authentication-related endpoints including registration, login, token refresh, and user profile.
Extracted from main.py as part of God File refactoring.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, Dict, Any

# Import models from centralized schemas
from models.schemas import (
    UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
)

# Import services
from services.auth_service import auth_service, AuthenticationError
from services.database import db_service, DatabaseError

# Import production rate limiter
from services.rate_limiter import check_rate_limit

# Import centralized authentication dependency
from dependencies import get_current_user_id

# Import helper functions
from utils.helpers import get_user_by_id

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, request: Request) -> TokenResponse:
    """Register a new user account"""
    try:
        # Apply strict rate limiting for registration to prevent abuse
        await check_rate_limit(request, "auth")
        
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        # Use auth service for registration
        result = auth_service.register_user(
            username=user_data.email.split('@')[0],
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        logger.info(f"New user registered: {user_data.email}")
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            token_type=result['token_type'],
            expires_in=1800,
            user={
                "id": result['user']['id'],
                "name": result['user']['name'],
                "email": result['user']['email'],
                "created_at": result['user']['created_at']
            }
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error during registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected registration error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, request: Request) -> TokenResponse:
    """Authenticate user and return tokens"""
    try:
        # Apply strict rate limiting for login to prevent brute force attacks
        await check_rate_limit(request, "auth")
        
        logger.info(f"Login attempt for email: {login_data.email}")
        
        result = auth_service.login_user(login_data.email, login_data.password)
        
        logger.info(f"User logged in successfully: {login_data.email}")
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            token_type=result['token_type'],
            expires_in=1800,
            user={
                "id": result['user']['id'],
                "name": result['user']['name'],
                "email": result['user']['email']
            }
        )
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for {login_data.email}: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {type(e).__name__}: {e}")
        
        # Provide more specific error messages
        error_message = "Login failed"
        if "database" in str(e).lower():
            error_message = "Database connection error. Please try again."
        elif "timeout" in str(e).lower():
            error_message = "Login request timed out. Please try again."
        elif "connection" in str(e).lower():
            error_message = "Connection error. Please check your internet connection."
        else:
            error_message = "An unexpected error occurred during login. Please try again."
        
        raise HTTPException(status_code=500, detail=error_message)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, request: Request) -> TokenResponse:
    """Refresh access token using refresh token"""
    try:
        # Apply rate limiting for token refresh
        await check_rate_limit(request, "auth")
        
        result = auth_service.refresh_access_token(refresh_data.refresh_token)
        
        return TokenResponse(
            access_token=result['access_token'],
            refresh_token=refresh_data.refresh_token,
            token_type=result['token_type'],
            expires_in=1800,
            user={}
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/logout")
async def logout(request: Request, user_id: int = Depends(get_current_user_id)):
    """Logout user"""
    try:
        # Apply rate limiting for logout
        await check_rate_limit(request, "general")
        
        logger.info(f"User {user_id} logged out")
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/profile")
async def get_profile(request: Request, user_id: int = Depends(get_current_user_id)):
    """Get user profile information"""
    try:
        # Apply rate limiting for profile access
        await check_rate_limit(request, "general")
        
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get basic document count only
        try:
            doc_stats = db_service.execute_query(
                "SELECT COUNT(*) as total_documents FROM documents WHERE user_id = %s",
                (user_id,),
                fetch='one'
            )
            user['total_documents'] = doc_stats['total_documents'] if doc_stats else 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            user['total_documents'] = 0
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile") 