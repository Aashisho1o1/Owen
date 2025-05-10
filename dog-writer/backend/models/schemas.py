from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    editor_text: str
    author_persona: str
    help_focus: str
    chat_history: List[ChatMessage]
    llm_provider: str = "Google Gemini"  # Default to Gemini if not specified

class ChatResponse(BaseModel):
    dialogue_response: str
    thinking_trail: Optional[str] = None

class CheckpointRequest(BaseModel):
    editor_text: str
    chat_history: List[ChatMessage]

class CheckpointResponse(BaseModel):
    status: str
    message: str

# --- New Models for Manga Feature ---
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