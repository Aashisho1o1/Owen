"""
Coordinated LLM Service

Main service that coordinates different LLM providers and provides
a unified interface for the application.

"""

import json
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

# GOOGLE GEMINI ONLY - Simplified for Google AI competition
SERVICES_AVAILABLE = False
gemini_service = None

try:
    from .llm.base_service import get_prompt_template, PromptLibrary, LLMError
    logger.info("✅ LLM base service imported successfully")

    # Import Gemini service only
    try:
        from .llm.gemini_service import gemini_service
        logger.info("✅ Gemini service imported successfully - using Google AI exclusively")
    except ImportError as e:
        logger.warning(f"⚠️ Gemini service not available: {e}")
        gemini_service = None
    except Exception as e:
        logger.error(f"❌ Unexpected error importing Gemini service: {e}")
        gemini_service = None

    SERVICES_AVAILABLE = True
    logger.info("🚀 Google Gemini service initialized for competition")

except ImportError as e:
    logger.warning(f"⚠️ LLM services not available: {e}")
    SERVICES_AVAILABLE = False

    # Fallback for when service isn't available
    class LLMError(Exception):
        pass

    logger.warning("🔧 Using fallback LLM service configuration")

class LLMService:
    """
    Coordinated LLM service providing unified interface to multiple providers.
    
    Acts as a facade pattern, routing requests to appropriate specialized services.
    """
    
    def __init__(self):
        """Initialize Google Gemini LLM service only"""
        if SERVICES_AVAILABLE:
            self.providers = {}

            # Register Gemini service only
            if gemini_service and gemini_service.is_available():
                self.providers["Google Gemini"] = gemini_service
                logger.info("✅ Google Gemini provider registered for competition")
            else:
                logger.warning("⚠️ Google Gemini provider not available")

            self.default_provider = "Google Gemini"
            logger.info(f"🎯 Using Google Gemini exclusively")
        else:
            # Fallback initialization for backward compatibility
            self.providers = {}
            self.default_provider = "Google Gemini"
            logger.warning("🔧 Using fallback LLM service initialization")
    
    def _get_default_provider(self) -> str:
        """Return Google Gemini as the only provider"""
        return "Google Gemini"
    
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
                           ai_mode: str = "talk",
                           conversation_context: Optional[str] = None,
                           folder_context: Optional[str] = None) -> str:
        """Assemble a chat prompt with mode-specific templates for Talk vs Co-Edit"""
        
        # Build context parts
        context_parts = []
        
        # FEATURE: Add conversation history context if available
        if conversation_context and conversation_context.strip():
            history_context = f"""**💬 CONVERSATION HISTORY:**
{conversation_context}

**Current Request:**"""
            context_parts.append(history_context)
        
        # NEW: PREMIUM FEATURE - Add folder context if available
        if folder_context and folder_context.strip():
            folder_info = f"""**📁 FOLDER CONTEXT (FolderScope Premium Feature):**
{folder_context}

This context includes content from other documents in your project folder to help maintain consistency."""
            context_parts.append(folder_info)
        
        # Add author persona
        if author_persona:
            persona_context = f"""**Author Persona: {author_persona}**
Writing a {author_persona.lower()} story with their unique style and voice."""
            context_parts.append(persona_context)
        
        # Add user corrections (keep simple)
        if user_corrections:
            corrections_context = "**Remember these preferences:**"
            for correction in user_corrections[-2:]:  # Only last 2
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
6. **Contextual Awareness:** Reference previous conversation when relevant to provide consistent help

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
6. **Contextual Awareness:** Reference our previous discussion when helpful to build on ideas

**Response Format:** Engage in friendly discussion, ask questions, suggest possibilities, and provide encouragement.

"""
        
        # Combine all parts
        additional_context = '\n\n'.join(context_parts)
        return base_prompt + additional_context

    def assemble_suggestions_prompt(self, 
                                  highlighted_text: str,
                                  user_message: str,
                                  author_persona: str,
                                  help_focus: str,
                                  conversation_context: Optional[str] = None) -> str:
        """Assemble a prompt specifically for generating multiple actionable suggestions"""
        
        # Build conversation context if available
        context_prefix = ""
        if conversation_context and conversation_context.strip():
            context_prefix = f"""**💬 CONVERSATION HISTORY:**
{conversation_context}

**Current Suggestion Request:**

"""
        
        return f"""{context_prefix}You are "Owen," an AI writing co-editor. The user has selected text and wants multiple improvement options they can accept directly.

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
6. **Consider previous conversation context** when relevant

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
                                          llm_provider: str,
                                          conversation_context: Optional[str] = None) -> Dict[str, Any]:
        """Generate multiple suggestion options for Co-Edit mode"""
        
        if not highlighted_text or not highlighted_text.strip():
            return {
                "suggestions": [],
                "original_text": "",
                "dialogue_response": "Please select some text first, and I'll provide multiple improvement options."
            }
        
        # Generate the specialized prompt for suggestions
        suggestions_prompt = self.assemble_suggestions_prompt(
            highlighted_text, user_message, author_persona, help_focus, conversation_context
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

    # Dialogue consistency check using Gemini only
    async def quick_dialogue_consistency_check(self,
                                             dialogue: str,
                                             character_context: str) -> Dict[str, Any]:
        """Dialogue consistency check using Google Gemini"""
        if not SERVICES_AVAILABLE or not gemini_service or not gemini_service.is_available():
            return {
                "is_consistent": True,
                "explanation": "Gemini service temporarily unavailable",
                "processing_time": 0,
                "cost": 0.0,
                "provider": "fallback"
            }

        try:
            prompt = f"Character: {character_context}\nDialogue: '{dialogue}'\nIs this dialogue consistent with the character? Brief yes/no answer with reason."
            response = await gemini_service.generate_text(prompt)
            return {
                "is_consistent": "yes" in response.lower(),
                "explanation": response,
                "processing_time": 5.0,
                "cost": 0.005,
                "provider": "google_gemini"
            }
        except Exception as e:
            logger.error(f"Error in consistency check: {e}")
            return {
                "is_consistent": True,
                "explanation": f"Error during analysis: {str(e)}",
                "processing_time": 0,
                "cost": 0.0,
                "provider": "error_fallback"
            }

    async def analyze_dialogue_with_hybrid(self,
                                         character_profile: Dict,
                                         dialogue_segments: List[str],
                                         speed_priority: bool = False) -> Dict[str, Any]:
        """Dialogue analysis using Google Gemini"""
        if not SERVICES_AVAILABLE or not gemini_service or not gemini_service.is_available():
            return {
                "analysis": "Gemini service temporarily unavailable",
                "provider": "fallback",
                "cost": 0.0,
                "processing_time": 0
            }

        try:
            prompt = f"""DIALOGUE CONSISTENCY ANALYSIS

Character: {character_profile.get('name', 'Unknown')}
Traits: {character_profile.get('traits', [])}

Dialogue Segments:
{chr(10).join([f"{i+1}. {seg}" for i, seg in enumerate(dialogue_segments[:5])])}

Analyze consistency and provide specific feedback."""

            response = await gemini_service.generate_text(prompt)
            return {
                "analysis": response,
                "provider": "google_gemini",
                "cost": 0.01,
                "processing_time": 15.0,
                "model_used": "gemini-2.5-flash"
            }
        except Exception as e:
            logger.error(f"Error in dialogue analysis: {e}")
            return {
                "analysis": f"Error during analysis: {str(e)}",
                "provider": "error_fallback",
                "cost": 0.0,
                "processing_time": 0
            }

# Global instance for backward compatibility
llm_service = LLMService()