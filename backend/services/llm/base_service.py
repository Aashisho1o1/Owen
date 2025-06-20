"""
Base LLM Service

Provides common functionality and interfaces for all LLM providers.
This follows the Strategy pattern for different LLM implementations.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Base exception for LLM operations"""
    pass

class BaseLLMService(ABC):
    """
    Abstract base class for all LLM services.
    
    Provides common functionality like API key management,
    error handling, and prompt templates.
    """
    
    def __init__(self, api_key_env: str):
        """Initialize with the environment variable name for the API key"""
        load_dotenv()
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            logger.warning(f"No API key found for {api_key_env}")
            self.available = False
        else:
            self.available = True
            logger.info(f"✅ {self.__class__.__name__} initialized successfully")
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM provider"""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured data using the LLM provider"""
        pass
    
    def is_available(self) -> bool:
        """Check if the service is available (has API key)"""
        return self.available
    
    def safe_api_key_display(self) -> str:
        """Return safely displayable portion of API key for logging"""
        if not self.api_key:
            return "Not configured"
        return f"{self.api_key[:8]}..."

class PromptTemplate:
    """
    Manages reusable prompt templates with variable substitution.
    
    Separates prompt content from logic for better maintainability.
    """
    
    def __init__(self, template: str):
        self.template = template
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise LLMError(f"Missing template variable: {e}")
    
    @classmethod
    def from_file(cls, filepath: str) -> 'PromptTemplate':
        """Load template from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return cls(f.read())
        except FileNotFoundError:
            raise LLMError(f"Template file not found: {filepath}")

class PromptLibrary:
    """
    Centralized collection of all prompt templates.
    
    This eliminates hardcoded prompts scattered throughout the codebase.
    """
    
    # Base system prompt for Owen - simplified for MVP
    OWEN_BASE = """You are "Owen," a thoughtful and respectful AI writing companion. Your primary goal is to help writers strengthen their own unique voice, not to replace it with a generic one.

**Your Core Principles:**
1. **Humility and Respect:** Use phrases like "Here's a thought," "Another perspective could be," "What if we tried," or "I notice...". Never claim a suggestion is definitively "better."
2. **Preserve Authenticity:** Identify and preserve the author's unique style, tone, and vocabulary.
3. **Offer Perspectives:** Explain the *effect* of different choices, not just provide rewrites.
4. **Distinguish Style from Error:** Differentiate between deliberate stylistic choices and genuine errors.
5. **Focus on "Why":** Explain reasoning behind suggestions from a craft perspective.

{additional_context}
"""
    
    # Manga generation prompt
    MANGA_SCRIPT = """Convert this story into a manga script format with {num_panels} panels.

Story: {story_text}
Author Persona: {author_persona}

Return JSON with:
- title: Short manga title
- page_number: 1
- character_designs: {{character_name: description}}
- panels: [{{panel_number, description, dialogue: [{{character, speech}}]}}]

Focus on visual storytelling, dynamic scenes, and character expressions suitable for manga format.
"""

def get_prompt_template(name: str, **kwargs) -> str:
    """
    Get a formatted prompt template.
    
    Args:
        name: Template name from PromptLibrary
        **kwargs: Variables to substitute in template
    
    Returns:
        Formatted prompt string
    """
    template_map = {
        'owen_base': PromptLibrary.OWEN_BASE,
        'manga_script': PromptLibrary.MANGA_SCRIPT,
    }
    
    if name not in template_map:
        raise LLMError(f"Unknown template: {name}")
    
    template = PromptTemplate(template_map[name])
    return template.format(**kwargs)

def clean_json_response(response_text: str) -> str:
    """
    Clean a response that might contain JSON in markdown format
    
    Args:
        response_text: The raw response text
        
    Returns:
        Cleaned JSON string
    """
    if not response_text:
        return ""
        
    cleaned_text = response_text.strip()
    
    # Handle markdown code blocks
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]  # Remove ```json
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]  # Remove ```
        
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]  # Remove closing ```
        
    return cleaned_text.strip()

def log_api_error(provider: str, error: Exception, context: str = "") -> None:
    """
    Log API errors consistently
    
    Args:
        provider: The LLM provider name
        error: The exception
        context: Additional context about the operation
    """
    logger.error(f"{provider} API Error{' in ' + context if context else ''}: {str(error)}")

def get_env_var(name: str, required: bool = False) -> Optional[str]:
    """
    Get environment variable with proper error handling
    
    Args:
        name: Environment variable name
        required: Whether the variable is required
        
    Returns:
        The environment variable value or None if not found
        
    Raises:
        ValueError: If required is True and the variable is not found
    """
    value = os.getenv(name)
    if required and not value:
        error_msg = f"Required environment variable {name} not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    if not value:
        logger.warning(f"Environment variable {name} not found")
        
    return value 