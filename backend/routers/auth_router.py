"""
Authentication Router

Secure authentication endpoints for user registration, login, profile management,
and session handling with proper rate limiting and security measures.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

# Import our services and models
from services.auth_service import (
    auth_service, get_current_user_id, rate_limiter, 
    AuthenticationError, security
)
from services.database_service import db_service
from services.validation_service import ValidationError, input_validator
from models.schemas import (
    UserRegistrationRequest, UserLoginRequest, UserLoginResponse,
    UserProfileResponse, ChangePasswordRequest, UpdateProfileRequest,
    TokenRefreshRequest, TokenRefreshResponse, UserPreferences
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
)

def get_client_ip(request: Request) -> str:
    """Extract client IP for rate limiting"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@router.post("/register", response_model=UserLoginResponse)
async def register_user(request: Request, user_data: UserRegistrationRequest):
    """Register a new user account with comprehensive validation"""
    client_ip = get_client_ip(request)
    
    # Rate limiting for registration attempts
    if rate_limiter.is_rate_limited(f"register:{client_ip}"):
        raise HTTPException(
            status_code=429, 
            detail="Too many registration attempts. Please try again later."
        )
    
    try:
        # Validate input data
        username = input_validator.validate_text_input(user_data.username)
        email = input_validator.validate_text_input(user_data.email)
        
        # Check if username already exists
        if db_service.username_exists(username):
            rate_limiter.record_attempt(f"register:{client_ip}")
            raise HTTPException(
                status_code=409,
                detail="Username already exists. Please choose a different username."
            )
        
        # Check if email already exists
        if db_service.email_exists(email):
            rate_limiter.record_attempt(f"register:{client_ip}")
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Please use a different email or sign in."
            )
        
        # Hash password securely
        password_hash = auth_service.hash_password(user_data.password)
        
        # Create user account
        user_id = db_service.create_user_account(
            username=username,
            email=email,
            password_hash=password_hash,
            display_name=user_data.display_name
        )
        
        if not user_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user account. Please try again."
            )
        
        # Generate tokens
        access_token = auth_service.create_access_token(user_id)
        refresh_token = auth_service.create_refresh_token(user_id)
        
        # Update last login
        db_service.update_user_last_login(user_id)
        
        # Get user profile data
        user_account = db_service.get_user_by_id(user_id)
        user_preferences = db_service.get_user_preferences(user_id) or UserPreferences()
        
        logger.info(f"Successfully registered user: {username}")
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=UserProfileResponse(
                user_id=user_id,
                username=user_account['username'],
                email=user_account['email'],
                display_name=user_account['display_name'],
                created_at=user_account['created_at'],
                preferences=user_preferences,
                onboarding_completed=user_preferences.onboarding_completed
            )
        )
        
    except ValidationError as e:
        rate_limiter.record_attempt(f"register:{client_ip}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        rate_limiter.record_attempt(f"register:{client_ip}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during registration. Please try again."
        )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: Request, login_data: UserLoginRequest):
    """Authenticate user and return access tokens"""
    client_ip = get_client_ip(request)
    
    # Rate limiting for login attempts
    if rate_limiter.is_rate_limited(f"login:{client_ip}"):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again later."
        )
    
    try:
        # Validate input
        username_or_email = input_validator.validate_text_input(login_data.username)
        
        # Try to find user by username or email
        user_account = None
        if "@" in username_or_email:
            user_account = db_service.get_user_by_email(username_or_email)
        else:
            user_account = db_service.get_user_by_username(username_or_email)
        
        # Verify user exists and password is correct
        if not user_account or not auth_service.verify_password(
            login_data.password, user_account['password_hash']
        ):
            rate_limiter.record_attempt(f"login:{client_ip}")
            raise HTTPException(
                status_code=401,
                detail="Invalid username/email or password."
            )
        
        # Check if account is active
        if not user_account['is_active']:
            rate_limiter.record_attempt(f"login:{client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated. Please contact support."
            )
        
        user_id = user_account['user_id']
        
        # Generate tokens with extended expiry if remember_me is True
        if login_data.remember_me:
            # Extend refresh token to 30 days for "remember me"
            auth_service.refresh_token_expire_days = 30
        
        access_token = auth_service.create_access_token(user_id)
        refresh_token = auth_service.create_refresh_token(user_id)
        
        # Reset refresh token expiry back to default
        auth_service.refresh_token_expire_days = 7
        
        # Update last login
        db_service.update_user_last_login(user_id)
        
        # Get user preferences
        user_preferences = db_service.get_user_preferences(user_id) or UserPreferences()
        
        logger.info(f"Successful login: {user_account['username']}")
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user=UserProfileResponse(
                user_id=user_id,
                username=user_account['username'],
                email=user_account['email'],
                display_name=user_account['display_name'],
                created_at=user_account['created_at'],
                preferences=user_preferences,
                onboarding_completed=user_preferences.onboarding_completed
            )
        )
        
    except ValidationError as e:
        rate_limiter.record_attempt(f"login:{client_ip}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        rate_limiter.record_attempt(f"login:{client_ip}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during login. Please try again."
        )

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(token_data: TokenRefreshRequest):
    """Refresh access token using refresh token"""
    try:
        # Decode and validate refresh token
        payload = auth_service.decode_token(token_data.refresh_token)
        
        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user still exists and is active
        user_account = db_service.get_user_by_id(user_id)
        if not user_account or not user_account['is_active']:
            raise HTTPException(status_code=401, detail="User account not found or inactive")
        
        # Generate new access token
        new_access_token = auth_service.create_access_token(user_id)
        
        return TokenRefreshResponse(
            access_token=new_access_token,
            expires_in=auth_service.access_token_expire_minutes * 60
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str = Depends(get_current_user_id)):
    """Get current user's profile information"""
    try:
        user_account = db_service.get_user_by_id(user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_preferences = db_service.get_user_preferences(user_id) or UserPreferences()
        
        return UserProfileResponse(
            user_id=user_id,
            username=user_account['username'],
            email=user_account['email'],
            display_name=user_account['display_name'],
            created_at=user_account['created_at'],
            preferences=user_preferences,
            onboarding_completed=user_preferences.onboarding_completed
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update user profile information"""
    try:
        # Validate email if provided
        if profile_data.email:
            # Check if email is already taken by another user
            existing_user = db_service.get_user_by_email(profile_data.email)
            if existing_user and existing_user['user_id'] != user_id:
                raise HTTPException(
                    status_code=409,
                    detail="Email already in use by another account"
                )
        
        # Update user profile
        success = db_service.update_user_profile_info(
            user_id=user_id,
            display_name=profile_data.display_name,
            email=profile_data.email
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        # Return updated profile
        return await get_user_profile(user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Change user password"""
    try:
        # Get current user account
        user_account = db_service.get_user_by_id(user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get full user data with password hash
        full_user_data = db_service.get_user_by_username(user_account['username'])
        if not full_user_data:
            raise HTTPException(status_code=404, detail="User credentials not found")
        
        # Verify current password
        if not auth_service.verify_password(
            password_data.current_password, 
            full_user_data['password_hash']
        ):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Hash new password
        new_password_hash = auth_service.hash_password(password_data.new_password)
        
        # Update password
        success = db_service.change_user_password(user_id, new_password_hash)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to change password")
        
        logger.info(f"Password changed for user: {user_account['username']}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.post("/logout")
async def logout_user(user_id: str = Depends(get_current_user_id)):
    """Logout user (client should discard tokens)"""
    try:
        # In a more sophisticated system, you might want to blacklist tokens
        # For now, we'll just return success - client should discard tokens
        
        user_account = db_service.get_user_by_id(user_id)
        if user_account:
            logger.info(f"User logged out: {user_account['username']}")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Don't fail logout even if there's an error
        return {"message": "Logged out successfully"}

# Health check endpoint for authentication service
@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "service": "authentication",
        "status": "healthy",
        "features": {
            "registration": True,
            "login": True,
            "jwt_tokens": True,
            "password_hashing": True,
            "rate_limiting": True,
            "profile_management": True
        }
    } 