from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class UserPreferences(BaseModel):
    """User preferences for personalized writing assistance."""
    english_variant: str = "standard"  # "standard", "indian", "british", "american"
    writing_style_profile: Optional[Dict[str, Any]] = None  # Analyzed writing style
    onboarding_completed: bool = False
    user_corrections: List[str] = Field(default_factory=list)  # User feedback history
    
    # Onboarding questions
    writing_type: Optional[str] = None  # "fiction", "non-fiction", "academic", "business"
    feedback_style: Optional[str] = None  # "gentle", "clear", "direct"
    primary_goal: Optional[str] = None  # "grammar", "storytelling", "voice"

class WritingSampleRequest(BaseModel):
    """Request to analyze a user's writing sample."""
    writing_sample: str
    user_id: Optional[str] = None  # For storing the analysis

class WritingSampleResponse(BaseModel):
    """Response with analyzed writing style profile."""
    style_profile: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    editor_text: str
    author_persona: str
    help_focus: str
    chat_history: List[ChatMessage]
    llm_provider: str = "Google Gemini"  # Default to Gemini if not specified
    
    # NEW: Enhanced fields for personalized assistance
    user_preferences: Optional[UserPreferences] = None
    feedback_on_previous: Optional[str] = None  # User feedback on previous response
    english_variant: str = "standard"  # Override for this specific request

class ChatResponse(BaseModel):
    dialogue_response: str
    thinking_trail: Optional[str] = None

class UserFeedbackRequest(BaseModel):
    """Request to store user feedback on AI responses."""
    original_message: str
    ai_response: str
    user_feedback: str  # What the user said about the response
    correction_type: str  # "style", "grammar", "tone", "cultural", "other"

class CheckpointRequest(BaseModel):
    editor_text: str
    chat_history: List[ChatMessage]

class CheckpointResponse(BaseModel):
    status: str
    message: str

# User onboarding schemas
class OnboardingRequest(BaseModel):
    """User's responses to onboarding questions."""
    writing_type: str  # "fiction", "non-fiction", "academic", "business"
    feedback_style: str  # "gentle", "clear", "direct"
    primary_goal: str  # "grammar", "storytelling", "voice"
    english_variant: str = "standard"

class OnboardingResponse(BaseModel):
    """Response after saving onboarding preferences."""
    success: bool = True
    user_preferences: UserPreferences
    message: str = "Onboarding completed successfully"

# NEW: Writing Session Management Schemas

class SessionStartRequest(BaseModel):
    """Request to start a new writing session."""
    user_id: Optional[str] = None
    content_length: int = 0  # Current length of editor content

class SessionStartResponse(BaseModel):
    """Response with new session ID."""
    session_id: str
    success: bool = True
    message: str = "Writing session started"

class ActivityUpdateRequest(BaseModel):
    """Request to update session activity."""
    session_id: str
    activity_type: str  # "typing", "editing", "scrolling", "thinking_pause"
    content_length: int = 0
    timestamp: Optional[str] = None

class ActivityUpdateResponse(BaseModel):
    """Response for activity update."""
    success: bool = True
    message: str = "Activity recorded"

class SessionEndRequest(BaseModel):
    """Request to end a writing session."""
    session_id: str
    total_active_seconds: int
    total_keystrokes: int = 0
    total_words: int = 0
    focus_lost_intervals: List[Dict[str, Any]] = Field(default_factory=list)

class SessionEndResponse(BaseModel):
    """Response after ending session."""
    success: bool = True
    session_summary: Dict[str, Any] = Field(default_factory=dict)
    message: str = "Writing session ended"

class LiveSessionData(BaseModel):
    """Real-time session data for frontend."""
    session_id: str
    is_active: bool
    current_active_seconds: int
    session_start_time: str
    last_activity_time: str
    current_focus_score: float = 0.0

# Analytics Schemas

class DailyStat(BaseModel):
    """Daily writing statistics."""
    date: str  # YYYY-MM-DD
    day_name: str  # Monday, Tuesday, etc.
    active_minutes: int
    sessions: int
    focus_score: float  # 0-100 percentage

class WeeklyAnalyticsRequest(BaseModel):
    """Request for weekly analytics."""
    user_id: Optional[str] = None
    week_offset: int = 0  # 0 = current week, -1 = last week

class WeeklyAnalyticsResponse(BaseModel):
    """Comprehensive weekly writing analytics."""
    week_start: str
    week_end: str
    total_minutes: int
    total_hours: float
    total_sessions: int
    total_keystrokes: int
    total_words: int
    active_days: int
    avg_daily_minutes: float
    longest_session_minutes: int
    avg_focus_score: float  # Percentage
    most_productive_day: DailyStat
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_percentage: float
    daily_breakdown: List[DailyStat]
    insights: List[str]
    success: bool = True

class TimerPreferences(BaseModel):
    """User preferences for the writing timer."""
    timer_visible: bool = True
    activity_bridge_timeout: int = 30  # seconds
    grace_period_on_blur: int = 5  # seconds
    session_end_timeout: int = 1800  # 30 minutes in seconds
    show_analytics_notifications: bool = True
    analytics_frequency: str = "weekly"  # "daily", "weekly", "monthly"

# --- Existing Models for Manga Feature ---
class MangaStoryRequest(BaseModel):
    story_text: str
    author_persona: str # To pass to script generator for context

class MangaPanelDialogue(BaseModel):
    character: str
    speech: str

class MangaPanel(BaseModel):
    panel_number: int
    description: str # Detailed visual description for DALL-E
    dialogue: List[MangaPanelDialogue] = Field(default_factory=list)
    image_url: Optional[str] = None # To be populated by DALL-E

class MangaPage(BaseModel):
    title: str
    page_number: int
    character_designs: Dict[str, str] = Field(default_factory=dict) # CharacterName: Description
    panels: List[MangaPanel] = Field(default_factory=list)

class MangaScriptResponse(BaseModel):
    manga_page: Optional[MangaPage] = None
    error: Optional[str] = None 
    warning: Optional[str] = None  # Add warning field for non-fatal issues 

# Database models for user data persistence
class UserProfile(BaseModel):
    """User profile stored in database."""
    user_id: str = Field(description="Unique user identifier")
    preferences: UserPreferences
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserFeedback(BaseModel):
    """User feedback stored in database."""
    feedback_id: str = Field(description="Unique feedback identifier")
    user_id: str
    original_message: str
    ai_response: str
    user_feedback: str
    correction_type: str
    timestamp: Optional[str] = None 