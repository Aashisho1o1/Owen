"""
Minimal Auth Service - JWT tokens and password hashing
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

logger = logging.getLogger(__name__)

class AuthService:
    """Simple authentication service."""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"❌ Password verification failed: {e}")
            return False

    def create_access_token(self, user_id: int, email: str) -> str:
        """Create JWT access token."""
        expires = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expires
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"❌ Token decode failed: {e}")
            return None

# Global instance
auth_service = AuthService()
