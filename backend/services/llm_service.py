"""
Coordinated LLM Service

Main service that coordinates different LLM providers and provides
a unified interface for the application.

OPTIMIZATION BENEFITS:
- Reduced from 658 lines to ~150 lines
- Separated concerns (each LLM has its own service)
- Better error handling and logging
- Cleaner prompt management
- Easier testing and maintenance
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

# Import specialized services
try:
    from .llm.base_service import get_prompt_template, PromptLibrary, LLMError
    from .llm.gemini_service import gemini_service
    from .llm.openai_service import openai_service
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LLM services not available: {e}")
    SERVICES_AVAILABLE = False
    
    # Fallback for when new services aren't available yet
    class LLMError(Exception):
        pass

class LLMService:
    """
    Coordinated LLM service providing unified interface to multiple providers.
    
    Acts as a facade pattern, routing requests to appropriate specialized services.
    """
    
    def __init__(self):
        """Initialize the coordinated LLM service"""
        if SERVICES_AVAILABLE:
            self.providers = {
                "Google Gemini": gemini_service,
                "OpenAI GPT": openai_service,
            }
            self.default_provider = self._get_default_provider()
        else:
            # Fallback initialization for backward compatibility
            self.providers = {}
            self.default_provider = "Google Gemini"
            logger.warning("Using fallback LLM service initialization")
    
    def _get_default_provider(self) -> str:
        """Determine the best available provider"""
        if not SERVICES_AVAILABLE:
            return "Google Gemini"
            
        for name, service in self.providers.items():
            if service.is_available():
                return name
        
        logger.warning("No LLM providers available!")
        return "Google Gemini"  # Fallback
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        if not SERVICES_AVAILABLE:
            return ["Google Gemini"]
            
        return [name for name, service in self.providers.items() if service.is_available()]
    
    async def generate_with_selected_llm(self, prompt: Union[str, List[Dict[str, Any]]], 
                                        llm_provider: str) -> Union[str, Dict[str, Any]]:
        """Generate response using the specified LLM provider"""
        if not SERVICES_AVAILABLE:
            # Fallback behavior
            return "LLM services temporarily unavailable"
            
        if llm_provider not in self.providers:
            raise LLMError(f"Unknown LLM provider: {llm_provider}")
        
        service = self.providers[llm_provider]
        if not service.is_available():
            raise LLMError(f"LLM provider {llm_provider} is not available")
        
        # Handle both string prompts and conversation history
        if isinstance(prompt, str):
            return await service.generate_text(prompt)
        elif isinstance(prompt, list):
            return await service.generate_with_conversation_history(prompt)
        else:
            raise LLMError("Prompt must be either a string or list of messages")
    
    def assemble_chat_prompt(self, 
                           user_message: str,
                           editor_text: str,
                           author_persona: str,
                           help_focus: str,
                           user_corrections: Optional[List] = None,
                           highlighted_text: Optional[str] = None) -> str:
        """Assemble a simplified chat prompt for MVP"""
        
        # Build context parts
        context_parts = []
        
        # Add author persona
        if author_persona:
            persona_context = f"""**Author Persona: {author_persona}**
Writing a {author_persona.lower()} story with their unique style and voice."""
            context_parts.append(persona_context)
        
        # Add user corrections (keep simple)
        if user_corrections:
            corrections_context = "**Remember these preferences:**"
            for correction in user_corrections[-3:]:  # Only last 3
                corrections_context += f"\n- {correction}"
            context_parts.append(corrections_context)
        
        # PRIORITY: Add highlighted text if available
        if highlighted_text and highlighted_text.strip():
            highlight_context = f"""**🎯 SELECTED TEXT FOR ANALYSIS:**
The user has highlighted this text for your attention:
"{highlighted_text}"

Please focus your response on this selected text."""
            context_parts.append(highlight_context)
        
        # Add current task context
        task_context = f"""**Current Task:**
Help Focus: {help_focus}
User Message: {user_message}"""
        
        # Only include full editor content if no highlighted text
        if not highlighted_text or not highlighted_text.strip():
            task_context += f"""
Full Editor Content: {editor_text[:300]}{'...' if len(editor_text) > 300 else ''}"""
        else:
            task_context += f"""
Editor Context: {len(editor_text)} characters total"""
        
        context_parts.append(task_context)
        
        # Simplified Owen prompt - no multi-lingual complexity
        base_prompt = """You are "Owen," a thoughtful AI writing companion. Help writers strengthen their unique voice.

**Core Principles:**
1. **Respect:** Use phrases like "Here's a thought" or "What if we tried". Never claim definitively "better."
2. **Preserve Authenticity:** Identify and preserve the author's unique style and vocabulary.
3. **Explain Why:** Provide reasoning behind suggestions from a craft perspective.

"""
        
        # Combine all parts
        additional_context = '\n\n'.join(context_parts)
        return base_prompt + additional_context

# Global instance for backward compatibility
llm_service = LLMService()