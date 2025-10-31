"""
Minimal schemas for competition backend
Essential Pydantic models only
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# === AUTH SCHEMAS ===

class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

# === CHARACTER VOICE SCHEMAS ===

class DialogueSegment(BaseModel):
    speaker: str
    text: str
    confidence: float = 1.0

class VoiceAnalysisRequest(BaseModel):
    text: str = Field(min_length=10, description="Text containing dialogue")

class VoiceAnalysisResult(BaseModel):
    character_name: str
    is_consistent: bool
    confidence_score: float
    voice_traits: Dict[str, Any]
    issues: List[str] = []
    suggestions: List[str] = []
    flagged_text: Optional[str] = None

class VoiceAnalysisResponse(BaseModel):
    results: List[VoiceAnalysisResult]
    characters_analyzed: int
    dialogue_segments_found: int
    processing_time_ms: int

class CharacterProfile(BaseModel):
    id: int
    character_name: str
    dialogue_samples: List[str]
    voice_traits: Dict[str, Any]
    sample_count: int
    last_updated: str

class CharacterProfilesResponse(BaseModel):
    profiles: List[CharacterProfile]
