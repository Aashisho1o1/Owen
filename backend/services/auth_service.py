"""
Authentication Service for DOG Writer
PostgreSQL-based authentication with JWT tokens, secure password handling,
and comprehensive user management.
"""

import bcrypt
import jwt
import logging
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from email_validator import validate_email, EmailNotValidError

from .database import db_service, DatabaseError

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", None)
if not JWT_SECRET_KEY:
    JWT_SECRET_KEY = secrets.token_urlsafe(32)
    logger.warning("JWT_SECRET_KEY not found in environment - using temporary key (tokens will reset on restart)")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class AuthService:
    """
    Modern authentication service using PostgreSQL.
    Handles user registration, login, token management, and security.
    """
    
    def __init__(self):
        self.db = db_service
        logger.info("Auth service initialized with PostgreSQL")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_tokens(self, user_id: int, email: str) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        # Access token (short-lived)
        access_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        # Refresh token (long-lived)
        refresh_payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return access_token, refresh_token
    
    def _store_refresh_token(self, user_id: int, refresh_token: str, device_info: str = None, ip_address: str = None):
        """Store refresh token in database"""
        token_hash = bcrypt.hashpw(refresh_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        query = """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at, device_info, ip_address)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (user_id, token_hash, expires_at, device_info, ip_address))
    
    def register_user(self, username: str, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Skip email validation temporarily
            # try:
            #     valid_email = validate_email(email)
            #     email = valid_email.email
            # except EmailNotValidError as e:
            #     raise AuthenticationError(f"Invalid email: {e}")
            
            # Check if user already exists
            existing_user = self.db.execute_query(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (email, username),
                fetch='one'
            )
            
            if existing_user:
                raise AuthenticationError("User with this email or username already exists")
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Create user
            query = """
                INSERT INTO users (username, email, password_hash, name, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email, name, created_at
            """
            user = self.db.execute_query(
                query,
                (username, email, password_hash, name, datetime.utcnow()),
                fetch='one'
            )
            
            if not user:
                raise AuthenticationError("Failed to create user")
            
            # Generate tokens
            access_token, refresh_token = self._generate_tokens(user['id'], user['email'])
            
            # Skip refresh token storage temporarily
            # self._store_refresh_token(user['id'], refresh_token)
            
            # Skip login logs temporarily  
            # self._log_login_attempt(user['id'], email, True, None, "Registration successful")
            
            logger.info(f"User registered successfully: {email}")
            
            return {
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "name": user['name'],
                    "created_at": user['created_at'].isoformat()
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except DatabaseError as e:
            logger.error(f"Database error during registration: {e}")
            raise AuthenticationError("Registration failed due to database error")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise AuthenticationError("Registration failed")
    
    def login_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        try:
            # Get user from database
            user = self.db.execute_query(
                "SELECT id, username, email, name, password_hash, is_active, failed_login_attempts, account_locked_until FROM users WHERE email = %s",
                (email,),
                fetch='one'
            )
            
            if not user:
                self._log_login_attempt(None, email, False, ip_address, "User not found")
                raise AuthenticationError("Invalid email or password")
            
            # Check if account is locked
            if user['account_locked_until'] and user['account_locked_until'] > datetime.utcnow():
                self._log_login_attempt(user['id'], email, False, ip_address, "Account locked")
                raise AuthenticationError("Account is temporarily locked")
            
            # Check if account is active
            if not user['is_active']:
                self._log_login_attempt(user['id'], email, False, ip_address, "Account inactive")
                raise AuthenticationError("Account is inactive")
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                # Increment failed login attempts
                self._handle_failed_login(user['id'])
                self._log_login_attempt(user['id'], email, False, ip_address, "Invalid password")
                raise AuthenticationError("Invalid email or password")
            
            # Reset failed login attempts on successful login
            self._reset_failed_login_attempts(user['id'])
            
            # Generate tokens
            access_token, refresh_token = self._generate_tokens(user['id'], user['email'])
            
            # Store refresh token
            self._store_refresh_token(user['id'], refresh_token, user_agent, ip_address)
            
            # Update last login
            self.db.execute_query(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.utcnow(), user['id'])
            )
            
            # Log successful login
            self._log_login_attempt(user['id'], email, True, ip_address, "Login successful")
            
            logger.info(f"User logged in successfully: {email}")
            
            return {
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "name": user['name']
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except DatabaseError as e:
            logger.error(f"Database error during login: {e}")
            raise AuthenticationError("Login failed due to database error")
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError("Login failed")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            # Log token verification attempt
            logger.debug(f"Verifying token: {token[:20]}...")
            
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get('type') != 'access':
                logger.warning(f"Invalid token type: {payload.get('type')}")
                raise AuthenticationError("Invalid token type")
            
            # Get user from database to ensure they still exist and are active
            user = self.db.execute_query(
                "SELECT id, username, email, name, is_active FROM users WHERE id = %s",
                (payload['user_id'],),
                fetch='one'
            )
            
            if not user:
                logger.warning(f"User {payload['user_id']} not found in database")
                raise AuthenticationError("User not found")
                
            if not user['is_active']:
                logger.warning(f"User {payload['user_id']} is inactive")
                raise AuthenticationError("User account is inactive")
            
            logger.debug(f"Token verified successfully for user {user['id']}")
            return {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "name": user['name']
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise AuthenticationError("Token verification failed")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Generate new access token using refresh token"""
        try:
            logger.info("Attempting to refresh access token")
            payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload.get('type') != 'refresh':
                logger.warning("Invalid token type in refresh request")
                raise AuthenticationError("Invalid token type")
            
            user_id = payload['user_id']
            logger.info(f"Refresh token valid for user {user_id}")
            
            # Get all valid refresh tokens for this user
            stored_tokens = self.db.execute_query(
                "SELECT id, user_id, token_hash FROM refresh_tokens WHERE user_id = %s AND expires_at > %s AND revoked = FALSE",
                (user_id, datetime.utcnow()),
                fetch='all'
            )
            
            if not stored_tokens:
                logger.warning(f"No valid refresh tokens found for user {user_id}")
                raise AuthenticationError("No valid refresh tokens found")
            
            logger.info(f"Found {len(stored_tokens)} valid refresh tokens for user {user_id}")
            
            # Check if the provided refresh token matches any stored hash
            valid_token = None
            for stored_token in stored_tokens:
                if bcrypt.checkpw(refresh_token.encode('utf-8'), stored_token['token_hash'].encode('utf-8')):
                    valid_token = stored_token
                    logger.info(f"Refresh token verified for user {user_id}")
                    break
            
            if not valid_token:
                logger.warning(f"Refresh token verification failed for user {user_id}")
                raise AuthenticationError("Refresh token not found or expired")
            
            # Get user
            user = self.db.execute_query(
                "SELECT id, email, is_active FROM users WHERE id = %s",
                (user_id,),
                fetch='one'
            )
            
            if not user or not user['is_active']:
                logger.warning(f"User {user_id} not found or inactive during token refresh")
                raise AuthenticationError("User not found or inactive")
            
            # Generate new access token
            access_token, _ = self._generate_tokens(user['id'], user['email'])
            
            logger.info(f"New access token generated for user {user_id}")
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            raise AuthenticationError("Refresh token has expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid refresh token provided")
            raise AuthenticationError("Invalid refresh token")
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthenticationError("Token refresh failed")
    
    def _handle_failed_login(self, user_id: int):
        """Handle failed login attempt"""
        # Increment failed attempts
        self.db.execute_query(
            "UPDATE users SET failed_login_attempts = failed_login_attempts + 1, last_failed_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id)
        )
        
        # Check if account should be locked
        user = self.db.execute_query(
            "SELECT failed_login_attempts FROM users WHERE id = %s",
            (user_id,),
            fetch='one'
        )
        
        if user and user['failed_login_attempts'] >= 5:
            # Lock account for 15 minutes
            lock_until = datetime.utcnow() + timedelta(minutes=15)
            self.db.execute_query(
                "UPDATE users SET account_locked_until = %s WHERE id = %s",
                (lock_until, user_id)
            )
    
    def _reset_failed_login_attempts(self, user_id: int):
        """Reset failed login attempts after successful login"""
        self.db.execute_query(
            "UPDATE users SET failed_login_attempts = 0, account_locked_until = NULL WHERE id = %s",
            (user_id,)
        )
    
    def _log_login_attempt(self, user_id: Optional[int], email: str, success: bool, ip_address: str = None, failure_reason: str = None):
        """Log login attempt for security monitoring"""
        query = """
            INSERT INTO login_logs (user_id, email, success, ip_address, failure_reason, attempted_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.execute_query(query, (user_id, email, success, ip_address, failure_reason, datetime.utcnow()))
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self.db.execute_query(
            "SELECT id, username, email, name, created_at, is_active, email_verified FROM users WHERE id = %s",
            (user_id,),
            fetch='one'
        )
        return user

    def cleanup_expired_tokens(self):
        """Clean up expired refresh tokens"""
        try:
            deleted_count = self.db.execute_query(
                "DELETE FROM refresh_tokens WHERE expires_at < %s",
                (datetime.utcnow(),),
                fetch='none'
            )
            if deleted_count and deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired refresh tokens")
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")

    def revoke_user_tokens(self, user_id: int):
        """Revoke all refresh tokens for a user (useful for logout all devices)"""
        try:
            self.db.execute_query(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"Revoked all tokens for user {user_id}")
        except Exception as e:
            logger.error(f"Error revoking tokens for user {user_id}: {e}")

    def cleanup_expired_tokens(self):
        """Clean up expired refresh tokens"""
        try:
            deleted_count = self.db.execute_query(
                "DELETE FROM refresh_tokens WHERE expires_at < %s",
                (datetime.utcnow(),),
                fetch='none'
            )
            if deleted_count and deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired refresh tokens")
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {e}")

    def revoke_user_tokens(self, user_id: int):
        """Revoke all refresh tokens for a user (useful for logout all devices)"""
        try:
            self.db.execute_query(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"Revoked all tokens for user {user_id}")
        except Exception as e:
            logger.error(f"Error revoking tokens for user {user_id}: {e}")

# Global auth service instance
auth_service = AuthService()
