"""
Authentication Routes for Owen AI Writer
Secure user registration, login, and profile management
Following security best practices with JWT tokens
"""

import os
import bcrypt
import jwt
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
import sqlite3
import logging
import re

logger = logging.getLogger(__name__)

# Security configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'auth.db')

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str  # Make name required instead of username
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 100:
            raise ValueError('Name must be less than 100 characters')
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
    email: str  # Use email for login
    password: str
    remember_me: bool = False

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str]
    created_at: str
    preferences: Dict[str, Any]
    onboarding_completed: bool = False

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
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
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, name, created_at, preferences, onboarding_completed
            FROM users WHERE id = ?
        """, (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "name": user_data[3],
            "created_at": user_data[4],
            "preferences": user_data[5] if user_data[5] else "{}",
            "onboarding_completed": bool(user_data[6])
        }
    
    finally:
        conn.close()


# Authentication endpoints
@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("""
            SELECT email FROM users WHERE email = ?
        """, (user_data.email,))
        
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Auto-generate username from email
        username = user_data.email.split('@')[0].lower()
        # Ensure username is unique by adding number if needed
        base_username = username
        counter = 1
        while True:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                break
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (username, name, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (
            username,  # Use auto-generated username
            user_data.name,
            user_data.email,
            password_hash
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Create tokens
        token_data = {"sub": user_id, "username": username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token in refresh_tokens table
        refresh_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        cursor.execute("""
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, refresh_token, refresh_expires))
        
        conn.commit()
        
        logger.info(f"New user registered: {username} (ID: {user_id})")
        
        # Get user profile for response
        user_profile = {
            "user_id": str(user_id),
            "username": username,
            "email": user_data.email,
            "display_name": user_data.name,
            "created_at": datetime.utcnow().isoformat(),
            "preferences": {
                "onboarding_completed": False,
                "user_corrections": [],
                "writing_style_profile": {},
                "writing_type": None,
                "feedback_style": None,
                "primary_goal": None
            },
            "onboarding_completed": False
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
    finally:
        conn.close()

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Find user by email
        cursor.execute("""
            SELECT id, username, password_hash FROM users 
            WHERE email = ?
        """, (login_data.email,))
        
        user_data = cursor.fetchone()
        if not user_data or not verify_password(login_data.password, user_data[2]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_id, username = user_data[0], user_data[1]
        
        # Create tokens
        token_data = {"sub": user_id, "username": username}
        
        # Adjust token expiry if remember_me is true
        if login_data.remember_me:
            access_expire = timedelta(days=7)  # Extended access token
            refresh_expire_days = 90  # Extended refresh token
        else:
            access_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_expire_days = REFRESH_TOKEN_EXPIRE_DAYS
        
        access_token = create_access_token(token_data, access_expire)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token in refresh_tokens table
        refresh_expires = datetime.utcnow() + timedelta(days=refresh_expire_days)
        cursor.execute("""
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, refresh_token, refresh_expires))
        
        conn.commit()
        
        logger.info(f"User logged in: {username}")
        
        # Get user profile for response
        cursor.execute("""
            SELECT name, email, created_at, preferences, onboarding_completed
            FROM users WHERE id = ?
        """, (user_id,))
        
        user_row = cursor.fetchone()
        preferences = json.loads(user_row[3]) if user_row[3] else {}
        user_profile = {
            "user_id": str(user_id),
            "username": username,
            "email": user_row[1],
            "display_name": user_row[0],
            "created_at": user_row[2],
            "preferences": {
                "onboarding_completed": bool(user_row[4]),
                "user_corrections": preferences.get("user_corrections", []),
                "writing_style_profile": preferences.get("writing_style_profile", {}),
                "writing_type": preferences.get("writing_type"),
                "feedback_style": preferences.get("feedback_style"),
                "primary_goal": preferences.get("primary_goal")
            },
            "onboarding_completed": bool(user_row[4])
        }
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_expire.total_seconds()) if login_data.remember_me else ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    finally:
        conn.close()

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        # Verify refresh token in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT token_hash, expires_at FROM refresh_tokens 
                WHERE user_id = ? AND token_hash = ? AND revoked = FALSE
            """, (user_id, refresh_data.refresh_token))
            
            token_data = cursor.fetchone()
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Check if refresh token is expired
            expires_at = datetime.fromisoformat(token_data[1])
            if datetime.utcnow() > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token expired"
                )
            
            # Create new access token
            token_data = {"sub": user_id, "username": username}
            access_token = create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_data.refresh_token,  # Keep same refresh token
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    import json
    
    try:
        preferences = json.loads(current_user["preferences"])
    except (json.JSONDecodeError, TypeError):
        preferences = {}
    
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"],
        preferences=preferences,
        onboarding_completed=current_user["onboarding_completed"]
    )

@router.put("/profile")
async def update_user_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if profile_data.name is not None:
            updates.append("name = ?")
            params.append(profile_data.name)
        
        if profile_data.email is not None:
            # Check if email is already in use
            cursor.execute("""
                SELECT id FROM users WHERE email = ? AND id != ?
            """, (profile_data.email, current_user["id"]))
            
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            
            updates.append("email = ?")
            params.append(profile_data.email)
        
        if updates:
            params.append(current_user["id"])
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )
    finally:
        conn.close()

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get current password hash
        cursor.execute("""
            SELECT password_hash FROM users WHERE id = ?
        """, (current_user["id"],))
        
        current_hash = cursor.fetchone()[0]
        
        # Verify current password
        if not verify_password(password_data.current_password, current_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password (using same validation as registration)
        try:
            UserRegistration.validate_password(password_data.new_password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Update password
        new_hash = hash_password(password_data.new_password)
        cursor.execute("""
            UPDATE users SET password_hash = ? WHERE id = ?
        """, (new_hash, current_user["id"]))
        
        conn.commit()
        
        logger.info(f"Password changed for user: {current_user['username']}")
        
        return {"success": True, "message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
    finally:
        conn.close()

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (invalidate refresh token)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users SET refresh_token = NULL, refresh_token_expires = NULL
            WHERE id = ?
        """, (current_user["id"],))
        
        conn.commit()
        
        logger.info(f"User logged out: {current_user['username']}")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
    finally:
        conn.close() 