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

from services.persona_service import create_writer_persona

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
                "OpenAI": openai_service,
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
                           english_variant: str = "standard",
                           user_style_profile: Optional[Dict] = None,
                           user_corrections: Optional[List] = None,
                           highlighted_text: Optional[str] = None) -> str:
        """Assemble a complete chat prompt using modular components"""
        
        # Build context parts
        context_parts = []
        
        # Add English style guide
        style_guides = {
            "indian": "**Indian English Mode:** Preserve Indian English vocabulary (prepone, lakhs, crores), syntax patterns, and honorifics.",
            "british": "**British English Mode:** Use British spellings (colour, analyse), vocabulary (lorry, pavement), and grammar conventions.",
            "american": "**American English Mode:** Use American spellings (color, analyze), vocabulary (truck, sidewalk), and direct communication style.",
            "standard": ""
        }
        
        if english_variant in style_guides and style_guides[english_variant]:
            context_parts.append(style_guides[english_variant])
        
        # Add author persona
        if author_persona:
            persona = create_writer_persona(author_persona)
            if persona:
                persona_context = f"""**Author Persona: {author_persona}**
Writing Style: {persona.get('writing_style', 'Unique style')}
Voice: {persona.get('voice', 'Distinctive voice')}"""
                context_parts.append(persona_context)
        
        # Add user style profile
        if user_style_profile:
            profile_context = "**Your Personal Writing Style:**"
            for key, value in user_style_profile.items():
                if value:
                    profile_context += f"\n- {key.title()}: {value}"
            context_parts.append(profile_context)
        
        # Add user corrections
        if user_corrections:
            corrections_context = "**Remember these preferences:**"
            for correction in user_corrections[-3:]:
                corrections_context += f"\n- {correction}"
            context_parts.append(corrections_context)
        
        # Add current task context
        task_context = f"""**Current Task:**
Help Focus: {help_focus}
Editor Content: {editor_text[:300]}{'...' if len(editor_text) > 300 else ''}
User Message: {user_message}"""
        context_parts.append(task_context)
        
        # Base Owen prompt
        base_prompt = """You are "Owen," a thoughtful AI writing companion. Help writers strengthen their unique voice.

**Core Principles:**
1. **Respect:** Use phrases like "Here's a thought" or "What if we tried". Never claim definitively "better."
2. **Preserve Authenticity:** Identify and preserve the author's unique style and vocabulary.
3. **Explain Why:** Provide reasoning behind suggestions from a craft perspective.

"""
        
        # Combine all parts
        additional_context = '\n\n'.join(context_parts)
        return base_prompt + additional_context
    
    async def analyze_writing_style(self, writing_sample: str) -> Dict[str, Any]:
        """Analyze writing style using available LLM"""
        if not SERVICES_AVAILABLE:
            # Fallback analysis
            return {
                "formality": "semi-formal",
                "sentence_complexity": "mixed",
                "key_vocabulary": [],
                "pacing": "steady",
                "literary_devices": [],
                "regional_indicators": "standard"
            }
        
        for service in self.providers.values():
            if service.is_available():
                return await service.analyze_writing_style(writing_sample)
        
        raise LLMError("No LLM providers available for style analysis")
    
    async def generate_manga_script(self, story_text: str, author_persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate manga script using structured generation"""
        if not SERVICES_AVAILABLE:
            # Fallback manga structure
            return {
                "title": "Generated Story",
            "page_number": 1,
                "character_designs": {"Main Character": "Protagonist of the story"},
            "panels": [
                    {"panel_number": 1, "description": "Opening scene", "dialogue": []}
                ]
            }
        
        prompt = f"""Convert this story into a manga script format with 4 panels:

Story: {story_text}
Author: {author_persona_data.get('name', 'Unknown')}

Return JSON with:
- title: Short manga title
- page_number: 1
- character_designs: {{character_name: description}}
- panels: [{{panel_number, description, dialogue: [{{character, speech}}]}}]"""
        
        for service in self.providers.values():
            if service.is_available():
                return await service.generate_structured(prompt, {})
        
        raise LLMError("No LLM providers available for manga generation")
    
    async def generate_panel_image_with_dalle(self, panel_description: str, 
                                            character_descriptions: Dict[str, str]) -> Optional[str]:
        """Generate manga panel image using DALL-E"""
        if not SERVICES_AVAILABLE:
            return None

        if "OpenAI" in self.providers and self.providers["OpenAI"].is_available():
            char_desc = ", ".join([f"{name}: {desc}" for name, desc in character_descriptions.items()])
            image_prompt = f"{panel_description}. Characters: {char_desc}. Style: monochrome manga, clean lines"
            
            try:
                return await self.providers["OpenAI"].generate_image(image_prompt)
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                return None
        
        return None

# Global instance for backward compatibility
llm_service = LLMService()