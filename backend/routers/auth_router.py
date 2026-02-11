"""
Authentication Router
Handles all authentication-related endpoints including registration, login, token refresh, and user profile.
Extracted from main.py as part of God File refactoring.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request

# Import models from centralized schemas
from models.schemas import (
    UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
)

# Import services
from services.auth_service import auth_service, AuthenticationError
from services.enhanced_validation import DetailedAuthenticationError
from services.database import get_db_service, DatabaseError

# Import production rate limiter
from services.rate_limiter import check_rate_limit

# Import centralized authentication dependency
from dependencies import get_current_user_id

# Import helper functions
from utils.helpers import get_user_by_id
from utils.error_responses import error_response

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
    except DetailedAuthenticationError as e:
        logger.error(f"Detailed authentication error during registration: {e}")
        raise error_response(
            status_code=400,
            code="REGISTRATION_VALIDATION_FAILED",
            message="Registration validation failed.",
            meta=e.to_dict()
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error during registration: {e}")
        raise error_response(
            status_code=400,
            code="REGISTRATION_FAILED",
            message=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise error_response(
            status_code=500,
            code="DATABASE_ERROR",
            message="Registration failed due to a database error."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected registration error: {type(e).__name__}: {e}")
        raise error_response(
            status_code=500,
            code="REGISTRATION_FAILED",
            message="Registration failed due to an internal server error."
        )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, request: Request) -> TokenResponse:
    """Authenticate user and return tokens"""
    try:
        logger.debug("Login endpoint called for email=%s", login_data.email)

        # Apply strict rate limiting for login to prevent brute force attacks
        await check_rate_limit(request, "auth")
        logger.debug("Login rate limit check passed")
        
        logger.info(f"Login attempt for email: {login_data.email}")
        
        result = auth_service.login_user(login_data.email, login_data.password)
        logger.debug("auth_service.login_user completed successfully")
        
        response = TokenResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            token_type=result['token_type'],
            expires_in=7200,  # 2 hours (120 minutes * 60 seconds) to match ACCESS_TOKEN_EXPIRE_MINUTES
            user={
                "id": result['user']['id'],
                "name": result['user']['name'],
                "email": result['user']['email']
            }
        )
        
        logger.info(f"User logged in successfully: {login_data.email}")
        return response
        
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for {login_data.email}: {str(e)}")
        raise error_response(
            status_code=401,
            code="INVALID_CREDENTIALS",
            message=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {type(e).__name__}: {e}")
        raise error_response(
            status_code=500,
            code="LOGIN_FAILED",
            message="An unexpected error occurred during login. Please try again."
        )

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
            expires_in=7200,  # 2 hours to match ACCESS_TOKEN_EXPIRE_MINUTES
            user={}
        )
    except AuthenticationError as e:
        raise error_response(
            status_code=401,
            code="TOKEN_REFRESH_FAILED",
            message=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise error_response(
            status_code=500,
            code="TOKEN_REFRESH_FAILED",
            message="Token refresh failed."
        )

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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise error_response(
            status_code=500,
            code="LOGOUT_FAILED",
            message="Logout failed."
        )

@router.post("/guest", response_model=TokenResponse)
async def create_guest_session(request: Request) -> TokenResponse:
    """
    Create a guest session for trying the app without registration.
    
    Engineering benefits:
    1. Zero-friction user onboarding
    2. IP-based rate limiting prevents abuse  
    3. 24-hour session allows meaningful evaluation
    4. Device binding prevents token sharing
    5. Same token format as regular auth (UI consistency)
    
    Security measures:
    - Rate limited: 10 guest sessions per IP per hour
    - Device fingerprinting prevents token sharing
    - Short session duration (24 hours)
    - Separate from user accounts (data isolation)
    """
    try:
        # Apply rate limiting for guest creation
        await check_rate_limit(request, "auth")
        
        # Extract client information for security
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(f"Guest session creation request from IP: {client_ip}")
        
        # Create guest session using auth service
        result = auth_service.create_guest_session(
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Return in same format as regular login (UI compatibility)
        response = TokenResponse(
            access_token=result['access_token'],
            refresh_token="",  # Guests don't get refresh tokens
            token_type=result['token_type'],
            expires_in=result['expires_in'],
            user=result['user']
        )
        
        logger.info(f"Guest session created successfully: {result['session_id']}")
        return response
        
    except AuthenticationError as e:
        logger.warning(f"Guest session creation failed: {e}")
        raise error_response(
            status_code=400,
            code="GUEST_SESSION_FAILED",
            message=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected guest session error: {type(e).__name__}: {e}")
        raise error_response(
            status_code=500,
            code="GUEST_SESSION_FAILED",
            message="Guest session creation failed."
        )

@router.post("/cleanup-guests")
async def cleanup_expired_guests(request: Request):
    """
    Cleanup expired guest sessions and associated data.
    
    Engineering purpose:
    1. Aggressive data cleanup (delete after 24 hours)
    2. Cost optimization (reduce storage usage)
    3. Privacy compliance (don't retain guest data)
    4. Database performance (prevent table bloat)
    
    This endpoint should be called:
    - Via cron job every hour
    - On server startup
    - Manually for maintenance
    """
    try:
        # Apply rate limiting for cleanup operations
        await check_rate_limit(request, "general")
        
        # Initialize database service
        db_service = get_db_service()
        
        # Call the database cleanup function we created in the migration
        result = db_service.execute_query(
            "SELECT * FROM cleanup_expired_guests(100)",  # Process 100 at a time
            fetch='one'
        )
        
        deleted_sessions = result.get('deleted_sessions', 0) if result else 0
        deleted_analytics = result.get('deleted_analytics', 0) if result else 0
        
        logger.info(f"Guest cleanup completed: {deleted_sessions} sessions, {deleted_analytics} analytics records deleted")
        
        return {
            "success": True,
            "deleted_sessions": deleted_sessions,
            "deleted_analytics": deleted_analytics,
            "message": f"Cleanup completed: {deleted_sessions} expired guest sessions removed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Guest cleanup error: {e}")
        raise error_response(
            status_code=500,
            code="GUEST_CLEANUP_FAILED",
            message="Cleanup operation failed."
        )

@router.get("/guest-quota")
async def get_guest_quota(user_id = Depends(get_current_user_id)):
    """
    Get guest quota information for frontend display.
    
    Returns quota status for guest users, or null for regular users.
    Used by frontend to show usage meters and upgrade prompts.
    """
    try:
        # Only return quota for guest sessions
        if isinstance(user_id, str):  # Guest sessions are UUID strings
            quota_info = auth_service.get_guest_quota(user_id, daily_limit=2)
            return {
                "is_guest": True,
                "quota": quota_info,
                "upgrade_message": f"You've used {quota_info['used']}/{quota_info['limit']} free AI interactions today."
            }
        else:
            # Regular users don't have quotas
            return {
                "is_guest": False,
                "quota": None,
                "upgrade_message": None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching guest quota: {e}")
        raise error_response(
            status_code=500,
            code="GUEST_QUOTA_FETCH_FAILED",
            message="Failed to get quota information."
        )

@router.get("/profile")
async def get_profile(request: Request, user_id = Depends(get_current_user_id)):
    """
    Get user profile information.
    
    **Updated for Guest Support**: Now handles both regular users and guest sessions.
    """
    try:
        # Apply rate limiting for profile access
        await check_rate_limit(request, "general")
        
        # Handle guest sessions differently
        if isinstance(user_id, str):
            # Guest session - return synthetic profile
            logger.info(f"Profile request for guest session: {user_id}")
            return {
                "id": f"guest_{user_id[:8]}",
                "username": f"Guest {user_id[:8]}",
                "email": "guest@trial.session",
                "name": "Guest User", 
                "type": "guest",
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "email_verified": False,
                "total_documents": 0,  # Guests start with no documents
                "session_expires_in": "24 hours",
                "features_available": [
                    "chat_assistance",
                    "voice_consistency_analysis", 
                    "grammar_checking",
                    "document_creation"
                ],
                "upgrade_benefits": [
                    "Unlimited documents",
                    "Extended AI assistance",
                    "Data persistence",
                    "Advanced features"
                ]
            }
        
        # Regular user profile
        user = get_user_by_id(user_id)
        if not user:
            raise error_response(
                status_code=404,
                code="USER_NOT_FOUND",
                message="User not found."
            )
        
        # Get basic document count only
        try:
            # Initialize database service
            db_service = get_db_service()
            
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
        raise error_response(
            status_code=500,
            code="PROFILE_FETCH_FAILED",
            message="Failed to get profile."
        )
