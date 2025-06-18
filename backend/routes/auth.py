"""
Authentication Routes for DOG Writer
Modern PostgreSQL-based authentication with JWT tokens and security best practices.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
import re

from services.auth_service import auth_service, AuthenticationError

logger = logging.getLogger(__name__)

security = HTTPBearer()
router = APIRouter()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    username: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Name must be less than 100 characters')
        return v.strip()
    
    @validator('username')
    def validate_username(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v.strip()) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common weak passwords
        weak_passwords = [
            'password', 'password123', '12345678', 'qwerty123', 'abc123456',
            'password1', 'welcome123', 'admin123', 'user1234', 'letmein123'
        ]
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')
        
        return v

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str]
    created_at: str
    onboarding_completed: bool = False

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Utility functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        return auth_service.verify_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication endpoints
@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        result = auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        result = auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            user=result["user"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        result = auth_service.refresh_access_token(refresh_data.refresh_token)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=refresh_data.refresh_token,  # Keep the same refresh token
            token_type=result["token_type"],
            user={}  # Don't return user data for refresh
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user = auth_service.get_user_by_id(current_user["user_id"])
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"].isoformat(),
            onboarding_completed=user.get("onboarding_completed", False)
        )
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@router.put("/profile")
async def update_user_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    # Note: This would require implementing update_user in auth_service
    # For now, return a placeholder response
    return {
        "success": True,
        "message": "Profile update functionality coming soon"
    }

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password"""
    # Note: This would require implementing change_password in auth_service
    # For now, return a placeholder response
    return {
        "success": True,
        "message": "Password change functionality coming soon"
    }

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (revoke tokens)"""
    # Note: This would require implementing token revocation in auth_service
    # For now, return success (client should discard tokens)
    return {
        "success": True,
        "message": "Logged out successfully"
    } 