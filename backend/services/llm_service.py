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

# ROBUST IMPORT: Handle cases where LLM services are not available
SERVICES_AVAILABLE = False
gemini_service = None
openai_service = None

try:
    from .llm.base_service import get_prompt_template, PromptLibrary, LLMError
    logger.info("✅ LLM base service imported successfully")
    
    # Try importing Gemini service (may fail if google-generativeai not available)
    try:
        from .llm.gemini_service import gemini_service
        logger.info("✅ Gemini service imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ Gemini service not available: {e}")
        gemini_service = None
    except Exception as e:
        logger.error(f"❌ Unexpected error importing Gemini service: {e}")
        gemini_service = None
    
    # Try importing OpenAI service
    try:
        from .llm.openai_service import openai_service
        logger.info("✅ OpenAI service imported successfully")
    except ImportError as e:
        logger.warning(f"⚠️ OpenAI service not available: {e}")
        openai_service = None
    except Exception as e:
        logger.error(f"❌ Unexpected error importing OpenAI service: {e}")
        openai_service = None
    
    SERVICES_AVAILABLE = True
    logger.info("🚀 LLM services coordination layer initialized")
    
except ImportError as e:
    logger.warning(f"⚠️ LLM services not available: {e}")
    SERVICES_AVAILABLE = False
    
    # Fallback for when new services aren't available yet
    class LLMError(Exception):
        pass
    
    logger.warning("🔧 Using fallback LLM service configuration")

class LLMService:
    """
    Coordinated LLM service providing unified interface to multiple providers.
    
    Acts as a facade pattern, routing requests to appropriate specialized services.
    """
    
    def __init__(self):
        """Initialize the coordinated LLM service"""
        if SERVICES_AVAILABLE:
            self.providers = {}
            
            # Add Gemini if available
            if gemini_service and gemini_service.is_available():
                self.providers["Google Gemini"] = gemini_service
                logger.info("✅ Google Gemini provider registered")
            else:
                logger.warning("⚠️ Google Gemini provider not available")
            
            # Add OpenAI if available  
            if openai_service and openai_service.is_available():
                self.providers["OpenAI GPT"] = openai_service
                logger.info("✅ OpenAI GPT provider registered")
            else:
                logger.warning("⚠️ OpenAI GPT provider not available")
            
            self.default_provider = self._get_default_provider()
            logger.info(f"🎯 Default LLM provider: {self.default_provider}")
        else:
            # Fallback initialization for backward compatibility
            self.providers = {}
            self.default_provider = "Google Gemini"
            logger.warning("🔧 Using fallback LLM service initialization")
    
    def _get_default_provider(self) -> str:
        """Determine the best available provider"""
        if not SERVICES_AVAILABLE or not self.providers:
            logger.warning("⚠️ No LLM providers available, defaulting to Google Gemini")
            return "Google Gemini"
            
        # Prefer Gemini first, then OpenAI
        for provider_name in ["Google Gemini", "OpenAI GPT"]:
            if provider_name in self.providers:
                service = self.providers[provider_name]
                if service.is_available():
                    logger.info(f"✅ Selected {provider_name} as default provider")
                    return provider_name
        
        # If no services are actually available, still return a name
        if self.providers:
            first_provider = list(self.providers.keys())[0]
            logger.warning(f"⚠️ No fully available providers, defaulting to {first_provider}")
            return first_provider
        
        logger.warning("⚠️ No LLM providers registered!")
        return "Google Gemini"  # Fallback name
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        if not SERVICES_AVAILABLE:
            return ["Google Gemini"]  # Fallback
            
        available = []
        for name, service in self.providers.items():
            if service and service.is_available():
                available.append(name)
        
        if not available:
            logger.warning("⚠️ No LLM providers are currently available")
            return ["Google Gemini"]  # Return something so UI doesn't break
        
        return available
    
    async def generate_with_selected_llm(self, prompt: Union[str, List[Dict[str, Any]]], 
                                        llm_provider: str) -> Union[str, Dict[str, Any]]:
        """Generate response using the specified LLM provider"""
        if not SERVICES_AVAILABLE:
            # Fallback behavior
            logger.warning("⚠️ LLM services temporarily unavailable")
            return "LLM services temporarily unavailable. Please check your environment configuration."
            
        if llm_provider not in self.providers:
            available_providers = list(self.providers.keys())
            error_msg = f"Unknown LLM provider: {llm_provider}. Available: {available_providers}"
            logger.error(error_msg)
            raise LLMError(error_msg)
        
        service = self.providers[llm_provider]
        if not service.is_available():
            error_msg = f"LLM provider {llm_provider} is not available"
            logger.error(error_msg)
            raise LLMError(error_msg)
        
        try:
            # Handle both string prompts and conversation history
            if isinstance(prompt, str):
                return await service.generate_text(prompt)
            elif isinstance(prompt, list):
                return await service.generate_with_conversation_history(prompt)
            else:
                raise LLMError("Prompt must be either a string or list of messages")
        except Exception as e:
            logger.error(f"Error generating response with {llm_provider}: {e}")
            raise LLMError(f"Failed to generate response with {llm_provider}: {str(e)}")
    
    def assemble_chat_prompt(self, 
                           user_message: str,
                           editor_text: str,
                           author_persona: str,
                           help_focus: str,
                           user_corrections: Optional[List] = None,
                           highlighted_text: Optional[str] = None,
                           ai_mode: str = "talk") -> str:
        """Assemble a chat prompt with mode-specific templates for Talk vs Co-Edit"""
        
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
        
        # MODE-SPECIFIC PROMPTS: Different behavior for Talk vs Co-Edit
        if ai_mode == "co-edit":
            # CO-EDIT MODE: Direct editing, actionable feedback, similar style/tone
            base_prompt = """You are "Owen," an AI writing co-editor. Your goal is to provide direct, actionable text improvements that writers can accept immediately.

**Co-Edit Mode Principles:**
1. **Direct Improvements:** Provide specific text rewrites and edits ready for acceptance
2. **Match Style:** Mirror the author's tone, voice, and writing style closely
3. **Similar Length:** Keep suggestions roughly the same length as the original
4. **Actionable:** Focus on concrete changes rather than abstract advice
5. **Preserve Voice:** Enhance clarity while maintaining the author's unique voice

**Response Format:** Provide specific text improvements, rewrites, or direct edits that can be immediately implemented.

"""
        else:
            # TALK MODE: Conversational, brainstorming, ideation-focused
            base_prompt = """You are "Owen," a thoughtful AI writing companion. Your goal is friendly discussion, brainstorming, and ideation to help writers explore their ideas.

**Talk Mode Principles:**
1. **Conversational:** Use phrases like "Here's a thought" or "What if we tried"
2. **Brainstorming:** Focus on exploring ideas, possibilities, and creative directions
3. **Questions:** Ask thoughtful questions to help the writer think deeper
4. **Supportive:** Encourage exploration and creative risk-taking
5. **Preserve Authenticity:** Respect the author's unique style and vocabulary

**Response Format:** Engage in friendly discussion, ask questions, suggest possibilities, and provide encouragement.

"""
        
        # Combine all parts
        additional_context = '\n\n'.join(context_parts)
        return base_prompt + additional_context

    def assemble_suggestions_prompt(self, 
                                  highlighted_text: str,
                                  user_message: str,
                                  author_persona: str,
                                  help_focus: str) -> str:
        """Assemble a prompt specifically for generating multiple actionable suggestions"""
        
        return f"""You are "Owen," an AI writing co-editor. The user has selected text and wants multiple improvement options they can accept directly.

**CRITICAL: You must respond with a JSON object containing multiple suggestions.**

**Selected Text:** "{highlighted_text}"
**User Request:** {user_message}
**Author Style:** {author_persona}
**Focus Area:** {help_focus}

**Your Task:** Provide 3-4 different ways to improve this text. Each suggestion should:
1. **Preserve the author's voice and style**
2. **Be roughly the same length** (±20% of original)
3. **Be immediately usable** - no placeholder text
4. **Address the user's specific request**
5. **Maintain the original meaning** while enhancing clarity/style

**Response Format (JSON only):**
{{
  "suggestions": [
    {{
      "id": "option_1",
      "text": "Your first rewrite option here",
      "type": "clarity_improvement",
      "confidence": 0.9,
      "explanation": "Brief explanation of what this version improves"
    }},
    {{
      "id": "option_2", 
      "text": "Your second rewrite option here",
      "type": "style_enhancement",
      "confidence": 0.85,
      "explanation": "Brief explanation of this approach"
    }},
    {{
      "id": "option_3",
      "text": "Your third rewrite option here", 
      "type": "conciseness",
      "confidence": 0.8,
      "explanation": "Brief explanation of this variation"
    }}
  ],
  "original_text": "{highlighted_text}",
  "dialogue_response": "I've prepared several ways to improve your selected text. Each option maintains your {author_persona.lower()} style while addressing {help_focus.lower()}. Choose the one that feels most natural to you, or use them as inspiration for your own revision."
}}

**Important:** Respond ONLY with valid JSON. No additional text before or after."""

    async def generate_multiple_suggestions(self,
                                          highlighted_text: str,
                                          user_message: str,
                                          author_persona: str,
                                          help_focus: str,
                                          llm_provider: str) -> Dict[str, Any]:
        """Generate multiple suggestion options for Co-Edit mode"""
        
        if not highlighted_text or not highlighted_text.strip():
            return {
                "suggestions": [],
                "original_text": "",
                "dialogue_response": "Please select some text first, and I'll provide multiple improvement options."
            }
        
        # Generate the specialized prompt for suggestions
        suggestions_prompt = self.assemble_suggestions_prompt(
            highlighted_text, user_message, author_persona, help_focus
        )
        
        try:
            # Get response from LLM
            response = await self.generate_with_selected_llm(suggestions_prompt, llm_provider)
            
            # Parse JSON response
            if isinstance(response, str):
                import json
                import re
                
                # Clean the response to extract JSON
                cleaned_response = response.strip()
                
                # Remove markdown code blocks if present
                if cleaned_response.startswith("```"):
                    lines = cleaned_response.split('\n')
                    cleaned_response = '\n'.join(lines[1:-1])
                
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed_response = json.loads(json_str)
                    
                    # Validate the response structure
                    if "suggestions" in parsed_response:
                        # Add unique IDs if missing
                        for i, suggestion in enumerate(parsed_response["suggestions"]):
                            if "id" not in suggestion:
                                suggestion["id"] = f"suggestion_{i+1}"
                        
                        return parsed_response
            
            # Fallback if JSON parsing fails
            logger.warning("Failed to parse suggestions JSON, using fallback")
            return {
                "suggestions": [{
                    "id": "fallback_1",
                    "text": highlighted_text,  # Return original as fallback
                    "type": "original",
                    "confidence": 1.0,
                    "explanation": "Original text (AI response parsing failed)"
                }],
                "original_text": highlighted_text,
                "dialogue_response": "I encountered an issue generating multiple options. Please try rephrasing your request."
            }
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {
                "suggestions": [],
                "original_text": highlighted_text,
                "dialogue_response": f"I encountered an error generating suggestions: {str(e)}"
            }

# Global instance for backward compatibility
llm_service = LLMService()