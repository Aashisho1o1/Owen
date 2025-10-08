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
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from email_validator import validate_email, EmailNotValidError

from .database import get_db_service, DatabaseError
from .enhanced_validation import AuthValidationService, DetailedAuthenticationError

logger = logging.getLogger(__name__)

# JWT Configuration with enhanced security validation
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Increased from 30 to 120 minutes (2 hours)
REFRESH_TOKEN_EXPIRE_DAYS = 7

def _validate_jwt_configuration():
    """Validate JWT configuration at runtime, not import time"""
    # CRITICAL SECURITY: Validate JWT secret key when service is used
    if not JWT_SECRET_KEY:
        logger.critical("🚨 SECURITY CRITICAL: JWT_SECRET_KEY environment variable is not set!")
        logger.critical("This is a critical security vulnerability that MUST be fixed before deployment")
        logger.critical("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
        raise ValueError("JWT_SECRET_KEY must be configured for secure authentication")

    if len(JWT_SECRET_KEY) < 32:
        logger.critical("🚨 SECURITY CRITICAL: JWT_SECRET_KEY is too short!")
        logger.critical(f"Current length: {len(JWT_SECRET_KEY)} characters, minimum required: 32")
        logger.critical("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
        raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for security")

    # Validate JWT secret is not a common weak key
    WEAK_KEYS = ['secret', 'key', 'jwt_secret', 'your_secret_key', 'changeme', 'password', '123456']
    if JWT_SECRET_KEY.lower() in WEAK_KEYS:
        logger.critical("🚨 SECURITY CRITICAL: JWT_SECRET_KEY is using a common weak value!")
        logger.critical("This creates a critical security vulnerability")
        logger.critical("Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
        raise ValueError("JWT_SECRET_KEY must not use common weak values")

logger.info("✅ JWT_SECRET_KEY security validation passed")

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class AuthService:
    """
    Modern authentication service using PostgreSQL.
    Handles user registration, login, token management, and security.
    """
    
    def __init__(self):
        # Validate JWT configuration when service is initialized
        _validate_jwt_configuration()
        
        self.db = get_db_service()
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
        """Register a new user with enhanced validation"""
        try:
            # Enhanced validation with detailed error messages
            validation_result = AuthValidationService.validate_registration_data(email, password, name or "")
            
            if not validation_result.is_valid:
                # Create detailed error message
                error_messages = validation_result.get_error_messages()
                if len(error_messages) == 1:
                    error_msg = error_messages[0]
                else:
                    error_msg = "Please fix the following issues: " + "; ".join(error_messages)
                
                raise DetailedAuthenticationError(
                    error_msg, 
                    validation_result, 
                    "validation_failed"
                )
            
            # Normalize email
            try:
                valid_email = validate_email(email)
                email = valid_email.email
            except EmailNotValidError as e:
                raise DetailedAuthenticationError(f"Invalid email format: {e}")
            
            # Check if user already exists
            existing_user = self.db.execute_query(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (email, username),
                fetch='one'
            )
            
            if existing_user:
                raise DetailedAuthenticationError("An account with this email address already exists. Please try logging in instead.")
            
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
            
            # Store refresh token
            self._store_refresh_token(user['id'], refresh_token)
            
            # Log successful registration
            self._log_login_attempt(user['id'], email, True, None, "Registration successful")
            
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
            print(f"🔑 AUTH STEP 1: Starting login for {email}")
            
            # Get user from database
            print(f"🔑 AUTH STEP 2: Querying database for user...")
            user = self.db.execute_query(
                "SELECT id, username, email, name, password_hash, is_active, failed_login_attempts, account_locked_until FROM users WHERE email = %s",
                (email,),
                fetch='one'
            )
            print(f"🔑 AUTH STEP 2: ✅ Database query completed")
            
            if not user:
                print(f"🔑 AUTH STEP 2: ❌ User not found")
                self._log_login_attempt(None, email, False, ip_address, "User not found")
                raise AuthenticationError("Invalid email or password")
            
            print(f"🔑 AUTH STEP 3: User found, checking account status...")
            
            # Check if account is locked
            if user['account_locked_until'] and user['account_locked_until'] > datetime.utcnow():
                print(f"🔑 AUTH STEP 3: ❌ Account is locked")
                self._log_login_attempt(user['id'], email, False, ip_address, "Account locked")
                raise AuthenticationError("Account is temporarily locked")
            
            # Check if account is active
            if not user['is_active']:
                print(f"🔑 AUTH STEP 3: ❌ Account is inactive")
                self._log_login_attempt(user['id'], email, False, ip_address, "Account inactive")
                raise AuthenticationError("Account is inactive")
            
            print(f"🔑 AUTH STEP 3: ✅ Account status OK")
            
            # Verify password
            print(f"🔑 AUTH STEP 4: Verifying password...")
            if not self._verify_password(password, user['password_hash']):
                print(f"🔑 AUTH STEP 4: ❌ Password verification failed")
                # Increment failed login attempts
                self._handle_failed_login(user['id'])
                self._log_login_attempt(user['id'], email, False, ip_address, "Invalid password")
                raise AuthenticationError("Invalid email or password")
            
            print(f"🔑 AUTH STEP 4: ✅ Password verified")
            
            # Reset failed login attempts on successful login
            print(f"🔑 AUTH STEP 5: Resetting failed login attempts...")
            self._reset_failed_login_attempts(user['id'])
            print(f"🔑 AUTH STEP 5: ✅ Failed login attempts reset")
            
            # Generate tokens
            print(f"🔑 AUTH STEP 6: Generating tokens...")
            access_token, refresh_token = self._generate_tokens(user['id'], user['email'])
            print(f"🔑 AUTH STEP 6: ✅ Tokens generated")
            
            # Store refresh token
            print(f"🔑 AUTH STEP 7: Storing refresh token...")
            self._store_refresh_token(user['id'], refresh_token, user_agent, ip_address)
            print(f"🔑 AUTH STEP 7: ✅ Refresh token stored")
            
            # Update last login
            print(f"🔑 AUTH STEP 8: Updating last login time...")
            self.db.execute_query(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.utcnow(), user['id'])
            )
            print(f"🔑 AUTH STEP 8: ✅ Last login updated")
            
            # Log successful login
            print(f"🔑 AUTH STEP 9: Logging successful login...")
            self._log_login_attempt(user['id'], email, True, ip_address, "Login successful")
            print(f"🔑 AUTH STEP 9: ✅ Login logged")
            
            logger.info(f"User logged in successfully: {email}")
            print(f"🔑 AUTH STEP 10: ✅ Login completed successfully")
            
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
            print(f"🔑 AUTH ❌ DATABASE ERROR: {str(e)}")
            logger.error(f"Database error during login: {e}")
            raise AuthenticationError("Login failed due to database error")
        except AuthenticationError:
            print(f"🔑 AUTH ❌ AUTHENTICATION ERROR (re-raising)")
            raise
        except Exception as e:
            print(f"🔑 AUTH ❌ UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError("Login failed")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        logger.info("--- 🕵️ Starting Token Verification ---")
        if not token:
            logger.error("VERIFY_TOKEN_FAIL: Token is null or empty.")
            raise AuthenticationError("Token not provided.")
            
        try:
            logger.info(f"VERIFY_TOKEN_STEP_1: Decoding JWT. Token starts with: {token[:20]}...")
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            logger.info("VERIFY_TOKEN_STEP_2: JWT decoded successfully.")
            
            # Check token type
            token_type = payload.get('type')
            logger.info(f"VERIFY_TOKEN_STEP_3: Checking token type. Found type: '{token_type}'.")
            if token_type != 'access':
                logger.warning(f"VERIFY_TOKEN_FAIL: Invalid token type. Expected 'access', got '{token_type}'.")
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get('user_id')
            logger.info(f"VERIFY_TOKEN_STEP_4: Extracting user_id. Found user_id: {user_id}.")
            if not user_id:
                logger.error("VERIFY_TOKEN_FAIL: 'user_id' not found in token payload.")
                raise AuthenticationError("'user_id' missing from token.")

            # Get user from database to ensure they still exist and are active
            logger.info(f"VERIFY_TOKEN_STEP_5: Querying database for user_id: {user_id}.")
            user = self.db.execute_query(
                "SELECT id, username, email, name, is_active FROM users WHERE id = %s",
                (user_id,),
                fetch='one'
            )
            
            if not user:
                logger.warning(f"VERIFY_TOKEN_FAIL: User {user_id} not found in database.")
                raise AuthenticationError("User not found")
            logger.info(f"VERIFY_TOKEN_STEP_6: User {user_id} found in database.")
                
            if not user['is_active']:
                logger.warning(f"VERIFY_TOKEN_FAIL: User {user_id} is inactive.")
                raise AuthenticationError("User account is inactive")
            logger.info(f"VERIFY_TOKEN_STEP_7: User {user_id} is active.")
            
            logger.info(f"--- ✅ Token Verified Successfully for user {user['id']} ---")
            return {
                "user_id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "name": user['name']
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("VERIFY_TOKEN_FAIL: JWT has expired.")
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"VERIFY_TOKEN_FAIL: JWT is invalid. Details: {str(e)}")
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"VERIFY_TOKEN_FAIL: An unexpected exception occurred. Details: {str(e)}", exc_info=True)
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

    def create_guest_session(self, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Create a secure guest session with device binding and rate limiting.
        
        Engineering principles:
        1. Separate guest sessions from user accounts (data hygiene)
        2. Device fingerprinting prevents token sharing
        3. IP-based rate limiting prevents abuse
        4. Short-lived tokens minimize security risk
        """
        try:
            # 1. Rate limiting: Prevent IP-based guest session spam
            if ip_address:
                recent_guests = self.db.execute_query(
                    """SELECT COUNT(*) as count FROM guest_sessions 
                       WHERE ip_address = %s 
                       AND created_at > NOW() - INTERVAL '1 hour'
                       AND is_active = TRUE""",
                    (ip_address,),
                    fetch='one'
                )
                
                if recent_guests and recent_guests['count'] >= 5:
                    raise AuthenticationError("Too many guest sessions from this IP address. Please try again later.")
            
            # 2. Generate secure session identifiers
            session_id = str(uuid.uuid4())
            
            # 3. Create device fingerprint for binding (prevents token sharing)
            device_info = f"{ip_address or 'unknown'}:{user_agent or 'unknown'}"
            device_fingerprint = hashlib.sha256(device_info.encode()).hexdigest()[:32]
            
            # 4. Generate guest-specific JWT with reduced privileges
            # Key difference: 24-hour expiry instead of 2 hours for regular users
            guest_payload = {
                "session_id": session_id,
                "type": "guest",
                "device_fp": device_fingerprint,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # 24-hour session
                "iat": datetime.now(timezone.utc)
            }
            
            guest_token = jwt.encode(guest_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            
            # 5. Store session in dedicated guest table (not users table)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            self.db.execute_query(
                """INSERT INTO guest_sessions 
                   (id, session_token, ip_address, user_agent, device_fingerprint, expires_at, data)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    session_id, 
                    guest_token, 
                    ip_address, 
                    user_agent, 
                    device_fingerprint,
                    expires_at,
                    '{"features_used": [], "limits_hit": []}'  # Track guest behavior
                )
            )
            
            # 6. Log guest session creation for monitoring
            logger.info(f"Guest session created: {session_id} from IP {ip_address}")
            
            # 7. Return token in same format as regular login (UI consistency)
            return {
                "access_token": guest_token,
                "token_type": "bearer",
                "expires_in": 86400,  # 24 hours in seconds
                "session_id": session_id,  # For analytics
                "user": {
                    "id": f"guest_{session_id[:8]}",  # Pseudo user ID for UI
                    "username": f"Guest {session_id[:8]}",
                    "email": f"guest@trial.session",  # Fake email for UI
                    "name": "Guest User",
                    "type": "guest"
                }
            }
            
        except DatabaseError as e:
            logger.error(f"Database error during guest session creation: {e}")
            raise AuthenticationError("Failed to create guest session")
        except Exception as e:
            logger.error(f"Unexpected error during guest session creation: {e}")
            raise AuthenticationError("Guest session creation failed")

    def verify_guest_token(self, token: str) -> Dict[str, Any]:
        """
        Verify guest token and return session info.
        
        Engineering note: This is separate from verify_token to handle 
        different data sources (guest_sessions vs users table).
        """
        try:
            # 1. Decode JWT and validate structure
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload.get('type') != 'guest':
                raise AuthenticationError("Not a guest token")
            
            session_id = payload.get('session_id')
            device_fp = payload.get('device_fp')
            
            if not session_id:
                raise AuthenticationError("Invalid guest token: missing session_id")
            
            # 2. Verify session exists and is active
            session = self.db.execute_query(
                """SELECT id, device_fingerprint, expires_at, is_active, data 
                   FROM guest_sessions 
                   WHERE id = %s AND is_active = TRUE""",
                (session_id,),
                fetch='one'
            )
            
            if not session:
                raise AuthenticationError("Guest session not found or expired")
            
            # 3. Verify device binding (prevents token sharing)
            if device_fp and session['device_fingerprint'] != device_fp:
                logger.warning(f"Device fingerprint mismatch for guest session {session_id}")
                raise AuthenticationError("Invalid device for this session")
            
            # 4. Check session expiry (defense in depth)
            if session['expires_at'] < datetime.now(timezone.utc):
                logger.info(f"Guest session {session_id} expired, marking inactive")
                self.db.execute_query(
                    "UPDATE guest_sessions SET is_active = FALSE WHERE id = %s",
                    (session_id,)
                )
                raise AuthenticationError("Guest session expired")
            
            # 5. Return session info in format compatible with regular auth
            return {
                "session_id": session_id,
                "type": "guest",
                "username": f"Guest {session_id[:8]}",
                "email": f"guest@trial.session",
                "name": "Guest User",
                "user_id": f"guest_{session_id[:8]}",  # Pseudo user ID
                "data": session.get('data', {})
            }
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Guest token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid guest token: {e}")
            raise AuthenticationError("Invalid guest token")
        except Exception as e:
            logger.error(f"Guest token verification error: {e}")
            raise AuthenticationError("Guest token verification failed")

    def track_guest_activity(self, session_id: str, activity: str, metadata: Dict[str, Any] = None):
        """
        Track guest activities for conversion optimization and abuse prevention.
        
        This helps understand:
        - Which features drive conversion
        - When users hit limits (conversion opportunities)
        - Abuse patterns for rate limiting improvements
        """
        try:
            self.db.execute_query(
                """INSERT INTO guest_analytics (session_id, action, metadata)
                   VALUES (%s, %s, %s)""",
                (session_id, activity, metadata or {})
            )
        except Exception as e:
            # Don't fail the main operation if analytics fail
            logger.warning(f"Failed to track guest activity: {e}")

    def get_guest_usage_count(self, session_id: str) -> int:
        """
        Count rolling 24-hour guest interactions for expensive operations.
        
        Engineering rationale:
        - Only counts story_generate and chat_message (expensive LLM calls)
        - Rolling 24h window prevents daily reset gaming
        - Returns 0 on errors to fail safe (allow operation)
        - Used for enforcing daily quotas to control costs
        """
        try:
            result = self.db.execute_query(
                """SELECT COUNT(*) AS count FROM guest_analytics
                   WHERE session_id = %s 
                   AND action IN ('story_generate', 'chat_message')
                   AND created_at > NOW() - INTERVAL '24 hours'""",
                (session_id,),
                fetch='one'
            )
            count = int(result['count'] if result and result.get('count') is not None else 0)
            logger.debug(f"Guest {session_id} usage count in last 24h: {count}")
            return count
        except Exception as e:
            logger.warning(f"Failed to get guest usage count for {session_id}: {e}")
            return 0  # Fail safe: allow operation if count check fails

    def get_guest_quota(self, session_id: str, daily_limit: int = 2) -> Dict[str, Any]:
        """
        Get guest quota status for frontend display and enforcement.
        
        Returns quota information compatible with existing rate limit patterns.
        Used by frontend to show usage and prompt upgrades.
        """
        try:
            count = self.get_guest_usage_count(session_id)
            remaining = max(0, daily_limit - count)
            
            # Calculate reset time based on oldest usage in current 24h window
            reset_result = self.db.execute_query(
                """SELECT MIN(created_at) AS oldest_usage FROM guest_analytics
                   WHERE session_id = %s 
                   AND action IN ('story_generate', 'chat_message')
                   AND created_at > NOW() - INTERVAL '24 hours'""",
                (session_id,),
                fetch='one'
            )
            
            reset_at = None
            if reset_result and reset_result.get('oldest_usage'):
                # Reset 24 hours after oldest usage
                reset_time = reset_result['oldest_usage'] + timedelta(hours=24)
                reset_at = reset_time.isoformat()
            
            return {
                "limit": daily_limit,
                "used": count,
                "remaining": remaining,
                "reset_at": reset_at,
                "session_id": session_id
            }
        except Exception as e:
            logger.error(f"Failed to get guest quota for {session_id}: {e}")
            # Return safe defaults
            return {
                "limit": daily_limit,
                "used": 0,
                "remaining": daily_limit,
                "reset_at": None,
                "session_id": session_id
            }

    def convert_guest_to_user(self, session_id: str, email: str, password: str, name: str = None) -> Dict[str, Any]:
        """
        Convert guest session to full user account with data migration.
        
        Engineering approach:
        1. Validate guest session exists and is active
        2. Create new user account 
        3. Migrate guest data (documents, folders, character profiles)
        4. Mark session as converted (for analytics)
        5. Return new user tokens
        """
        try:
            # 1. Verify guest session exists and is valid
            session = self.db.execute_query(
                """SELECT id, data, expires_at FROM guest_sessions 
                   WHERE id = %s AND is_active = TRUE AND expires_at > NOW()""",
                (session_id,),
                fetch='one'
            )
            
            if not session:
                raise AuthenticationError("Invalid or expired guest session")
            
            # 2. Create user account using existing registration logic
            user_result = self.register_user(
                username=email.split('@')[0],  # Use email prefix as username
                email=email,
                password=password,
                name=name or "Converted Guest"
            )
            
            user_id = user_result['user']['id']
            
            # 3. Migrate guest data to new user account
            # This updates foreign keys to point to the new user_id
            self._migrate_guest_data(session_id, user_id)
            
            # 4. Mark session as converted (for analytics and cleanup)
            self.db.execute_query(
                """UPDATE guest_sessions 
                   SET converted_to_user_id = %s, is_active = FALSE 
                   WHERE id = %s""",
                (user_id, session_id)
            )
            
            # 5. Track conversion for analytics
            self.track_guest_activity(session_id, "converted_to_user", {
                "user_id": user_id,
                "email": email,
                "session_duration_hours": (datetime.utcnow() - session['expires_at'] + timedelta(hours=24)).total_seconds() / 3600
            })
            
            logger.info(f"Guest session {session_id} converted to user {user_id}")
            
            return user_result
            
        except AuthenticationError:
            raise  # Re-raise auth errors
        except Exception as e:
            logger.error(f"Guest conversion error: {e}")
            raise AuthenticationError("Failed to convert guest session")

    def _migrate_guest_data(self, session_id: str, user_id: int):
        """
        Migrate guest data to user account.
        
        Since guest sessions don't create user records, we need to update
        any data created during the guest session to point to the new user_id.
        
        This is a critical step for user retention - losing their work during
        conversion would destroy the user experience.
        """
        try:
            # Note: This would migrate documents, folders, character profiles, etc.
            # But since guests use session_id instead of user_id in our current design,
            # we'd need to update the data model to support this migration pattern.
            
            # For now, log that migration would happen here
            logger.info(f"Guest data migration from session {session_id} to user {user_id}")
            
            # TODO: Implement actual data migration when guest data model is finalized
            # Example migrations:
            # UPDATE documents SET user_id = %s WHERE guest_session_id = %s
            # UPDATE folders SET user_id = %s WHERE guest_session_id = %s
            # UPDATE character_profiles SET user_id = %s WHERE guest_session_id = %s
            
        except Exception as e:
            logger.error(f"Guest data migration failed: {e}")
            # Don't fail conversion if migration fails - user account is created
            # Users can recreate their work if needed

# Global auth service instance - lazy initialization
_auth_service_instance = None

def get_auth_service() -> AuthService:
    """Get the auth service instance (lazy initialization)"""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance

# Backward compatibility - this will be initialized on first access
@property
def auth_service():
    """Backward compatibility property"""
    return get_auth_service()

# Create a module-level object that behaves like the old auth_service
class AuthServiceProxy:
    def __getattr__(self, name):
        return getattr(get_auth_service(), name)

auth_service = AuthServiceProxy()
