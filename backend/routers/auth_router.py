"""
Minimal Auth Router - Register and Login
"""

import logging
from fastapi import APIRouter, HTTPException, status
from models.schemas import UserRegister, UserLogin, TokenResponse
from services.auth_service import auth_service
from services.database import db_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user."""
    if not db_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )

    # Check if user exists
    existing_user = await db_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = auth_service.hash_password(user.password)

    # Create user
    user_id = await db_service.create_user(user.email, password_hash)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    # Create token
    access_token = auth_service.create_access_token(user_id, user.email)

    logger.info(f"✅ User registered: {user.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
    if not db_service.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )

    # Get user
    user = await db_service.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not auth_service.verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create token
    access_token = auth_service.create_access_token(user['id'], user['email'])

    logger.info(f"✅ User logged in: {credentials.email}")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user['id']
    )
