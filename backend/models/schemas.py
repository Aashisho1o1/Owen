from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re
from pydantic import field_validator
from enum import Enum

# === ENUMS ===
class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# === AUTHENTICATION SCHEMAS ===
class UserRegistrationRequest(BaseModel):
    """Request to register a new user account."""
    username: str = Field(min_length=3, max_length=50, description="Unique username")
    email: str = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name for the user")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserCreate(BaseModel):
    """User creation model for main.py compatibility"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, description="User's full name")

class UserLogin(BaseModel):
    """User login model"""
    email: str
    password: str

class UserLoginRequest(BaseModel):
    """Request to log in a user."""
    username: str = Field(description="Username or email")
    password: str = Field(description="User password")

class UserLoginResponse(BaseModel):
    """Response after successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int = 1800  # 30 minutes
    user: dict

class TokenRefreshRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    """Refresh token request model for main.py compatibility"""
    refresh_token: str

# === DOCUMENT SCHEMAS ===
class DocumentCreate(BaseModel):
    """Document creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template_id: Optional[str] = None
    folder_id: Optional[str] = None
    status: DocumentStatus = DocumentStatus.DRAFT

class DocumentUpdate(BaseModel):
    """Document update model"""
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[DocumentStatus] = None
    folder_id: Optional[str] = None

class DocumentFromTemplateCreate(BaseModel):
    """Create document from template model"""
    template_id: str = Field(..., description="Template ID to use")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    folder_id: Optional[str] = None

# === FOLDER SCHEMAS ===
class FolderCreate(BaseModel):
    """Folder creation model"""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    color: Optional[str] = "#3B82F6"

class FolderUpdate(BaseModel):
    """Folder update model"""
    name: Optional[str] = None
    color: Optional[str] = None

# === CHAT SCHEMAS (Core MVP Feature) ===
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class UserPreferences(BaseModel):
    """Minimal user preferences for MVP - no complex onboarding."""
    user_corrections: List[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str
    editor_text: str
    author_persona: str
    help_focus: str
    chat_history: List[ChatMessage]
    llm_provider: str = "Google Gemini"
    ai_mode: str = "talk"  # NEW: AI interaction mode - "talk" or "co-edit"
    user_preferences: Optional[UserPreferences] = None
    feedback_on_previous: Optional[str] = None
    highlighted_text: Optional[str] = None
    highlight_id: Optional[str] = None

class ChatResponse(BaseModel):
    dialogue_response: str
    thinking_trail: Optional[str] = None

class UserFeedbackRequest(BaseModel):
    """Request to store user feedback on AI responses."""
    original_message: str
    ai_response: str
    user_feedback: str
    correction_type: str  # "style", "grammar", "tone", "cultural", "other"

# === GRAMMAR CHECKING SCHEMAS (Core MVP Feature) ===
class GrammarCheckRequest(BaseModel):
    """Request for grammar checking"""
    text: str = Field(..., max_length=10000, description="Text to check for grammar and spelling")
    check_type: str = Field("real_time", description="Type of check: 'real_time' or 'comprehensive'")
    language: str = Field("en-US", description="Language code for checking")
    context: Optional[str] = Field(None, max_length=2000, description="Additional context for comprehensive checking")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty')
        return v
    
    @field_validator('check_type')
    @classmethod
    def validate_check_type(cls, v):
        if v not in ['real_time', 'comprehensive']:
            raise ValueError('check_type must be either "real_time" or "comprehensive"')
        return v

class GrammarIssueResponse(BaseModel):
    """Grammar issue response model"""
    start: int
    end: int
    issue_type: str
    severity: str
    message: str
    suggestions: List[str]
    confidence: float
    source: str

class GrammarCheckResponse(BaseModel):
    """Grammar check response"""
    text_length: int
    word_count: int
    issues: List[GrammarIssueResponse]
    check_type: str
    processing_time_ms: int
    cached: bool
    overall_score: Optional[int] = None
    style_notes: Optional[str] = None 