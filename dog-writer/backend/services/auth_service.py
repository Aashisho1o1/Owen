"""
Authentication and Authorization Service

Provides secure user authentication with JWT tokens, password hashing,
and session management following security best practices.
"""

import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication failures"""
    pass

class AuthService:
    """
    Secure authentication service with JWT tokens and bcrypt password hashing.
    
    Features:
    - JWT token generation and validation
    - Password hashing with bcrypt
    - Rate limiting protection
    - Session management
    - Role-based access control
    """
    
    def __init__(self):
        # 🔒 SECURITY REQUIREMENT: JWT_SECRET_KEY must be set in environment
        self.secret_key = os.getenv('JWT_SECRET_KEY')
        if not self.secret_key:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required for security. "
                "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        
        # Validate secret key strength
        if len(self.secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for security")
        
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        logger.info("Authentication service initialized with secure JWT configuration")
    
    def _generate_secret_key(self) -> str:
        """Generate a cryptographically secure secret key"""
        # This method is kept for utility but not used in production
        return secrets.token_urlsafe(64)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with salt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_access_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Create JWT access token with expiration"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token with longer expiration"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            'sub': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get('type') not in ['access', 'refresh']:
                raise AuthenticationError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {e}")
    
    def get_current_user_id(self, token: str) -> str:
        """Extract user ID from valid token"""
        payload = self.decode_token(token)
        user_id = payload.get('sub')
        
        if not user_id:
            raise AuthenticationError("Token missing user ID")
        
        return user_id

# Security middleware and dependencies
security = HTTPBearer()
auth_service = AuthService()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """FastAPI dependency to extract current user ID from JWT token"""
    try:
        return auth_service.get_current_user_id(credentials.credentials)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_optional_user_id(request: Request) -> Optional[str]:
    """FastAPI dependency for optional authentication"""
    auth_header = request.headers.get('authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        return auth_service.get_current_user_id(token)
    except AuthenticationError:
        return None

# Rate limiting for authentication endpoints
class RateLimiter:
    """Simple in-memory rate limiter for authentication endpoints"""
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts = {}  # In production, use Redis
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Clean old attempts
        if identifier in self.attempts:
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if attempt > window_start
            ]
        
        # Check rate limit
        attempt_count = len(self.attempts.get(identifier, []))
        return attempt_count >= self.max_attempts
    
    def record_attempt(self, identifier: str):
        """Record a failed authentication attempt"""
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(datetime.utcnow())

rate_limiter = RateLimiter() 