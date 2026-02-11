from fastapi import APIRouter, HTTPException, Depends, Request
import json
import re
import logging
import time
from typing import List, Optional, Union

# Import security services
from services.auth_service import auth_service
from services.validation_service import input_validator
from services.rate_limiter import check_rate_limit

# Import centralized rate limiting dependency
from dependencies import check_chat_rate_limit
from utils.error_responses import error_response

# Change relative imports to absolute imports
from models.schemas import (
    ChatRequest, ChatResponse, UserFeedbackRequest, 
    EnhancedChatResponse, SuggestionOption, AcceptSuggestionRequest,
    ChatMessage
)
from services.llm_service import LLMService
from services.database import db_service
from services.character_voice_service import CharacterVoiceService

# Import centralized authentication dependency
from dependencies import get_current_user_id

# Initialize services
llm_service = LLMService()
# character_voice_service = CharacterVoiceService()  # REMOVE eager init
character_voice_service: Optional[CharacterVoiceService] = None  # Lazy init placeholder

# Guest quota configuration - shared with story generation
GUEST_DAILY_LIMIT = 2  # Maximum chat interactions per 24h for guests


def get_character_voice_service() -> CharacterVoiceService:
    """Lazily initialize and return CharacterVoiceService instance"""
    global character_voice_service
    if character_voice_service is None:
        character_voice_service = CharacterVoiceService()
    return character_voice_service

async def generate_llm_response(prompt: str, provider: str) -> str:
    """
    Generate LLM response with provider-specific input formatting.
    
    Args:
        prompt: The prompt to send to the LLM
        provider: LLM provider (Google Gemini, OpenAI GPT, etc.)
        
    Returns:
        Generated response text
    """
    if provider == "Google Gemini":
        prompts = [{"role": "user", "parts": [prompt]}]
        return await llm_service.generate_with_selected_llm(prompts, provider)
    if provider == "OpenAI GPT":
        return await llm_service.generate_with_selected_llm(prompt, provider)

    response_result = await llm_service.generate_with_selected_llm(prompt, provider)
    if isinstance(response_result, dict) and "text" in response_result:
        return response_result["text"]
    return str(response_result)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

def build_conversation_context(chat_history: List[ChatMessage], max_history: int = 5) -> str:
    """Build conversation context from chat history using sliding window approach"""
    if not chat_history:
        return ""
    
    # Keep last N exchanges (sliding window)
    recent_history = chat_history[-max_history:]
    
    if not recent_history:
        return ""
    
    context_parts = []
    for msg in recent_history:
        role = "Human" if msg.role == "user" else "Assistant"
        # Truncate very long messages to keep context manageable
        content = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
        context_parts.append(f"{role}: {content}")
    
    return "\n".join(context_parts)

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    http_request: Request,
    user_id: Union[str, int] = Depends(get_current_user_id),  # Accept both guest UUIDs and user IDs
    rate_limit_result = Depends(check_chat_rate_limit)
):
    """Enhanced chat endpoint with personalized, culturally-aware feedback and security."""
    try:
        logger.debug("Chat endpoint reached for user_id=%s", user_id)
        
        # GUEST QUOTA ENFORCEMENT: Check daily limits for cost control
        if isinstance(user_id, str):  # Guest sessions are UUID strings
            usage_count = auth_service.get_guest_usage_count(user_id)
            if usage_count >= GUEST_DAILY_LIMIT:
                logger.info(f"Guest {user_id} hit daily chat limit: {usage_count}/{GUEST_DAILY_LIMIT}")
                quota_info = auth_service.get_guest_quota(user_id, GUEST_DAILY_LIMIT)
                raise error_response(
                    status_code=402,  # Payment Required - perfect for quota limits
                    code="GUEST_LIMIT_REACHED",
                    message=f"You've used your {GUEST_DAILY_LIMIT} free daily AI chats. Sign up for unlimited access!",
                    meta={"quota": quota_info}
                )
            logger.info(f"Guest {user_id} chat interaction: {usage_count + 1}/{GUEST_DAILY_LIMIT}")
        
        # ENHANCED DEBUGGING: Log authentication success
        logger.debug("Authentication successful for user_id=%s", user_id)
        
        # ENHANCED DEBUGGING: Log request details for debugging
        request_info = {
            'user_id': user_id,
            'voice_guard': chat_request.voice_guard,
            'ai_mode': chat_request.ai_mode,
            'message_length': len(chat_request.message),
            'editor_text_length': len(chat_request.editor_text or ""),
            'has_highlighted_text': bool(chat_request.highlighted_text),
            'llm_provider': chat_request.llm_provider
        }
        logger.debug("Request info: %s", request_info)
        
        # Shared dependency-based rate limiting.
        logger.debug(
            "Rate limit check passed for user=%s tier=%s tokens_remaining=%s",
            user_id,
            rate_limit_result.tier,
            rate_limit_result.tokens_remaining
        )
        
        # ENHANCED DEBUGGING: Log LLM service availability
        available_providers = llm_service.get_available_providers()
        logger.debug("Available LLM providers: %s", available_providers)
        
        # Validate and sanitize all input data
        validated_message = input_validator.validate_chat_message(chat_request.message)
        validated_editor_text = input_validator.validate_text_input(chat_request.editor_text or "")
        validated_llm_provider = input_validator.validate_llm_provider(chat_request.llm_provider)
        
        # ENHANCED DEBUGGING: Verify the requested provider is available
        if validated_llm_provider not in available_providers:
            logger.error(f"❌ Requested LLM provider '{validated_llm_provider}' not available. Available: {available_providers}")
            raise error_response(
                status_code=400,
                code="INVALID_LLM_PROVIDER",
                message=f"LLM provider '{validated_llm_provider}' is not available.",
                meta={"available_providers": available_providers}
            )
        
        # SECURITY: Additional length checks for expensive operations
        total_input_length = len(validated_message) + len(validated_editor_text)
        if total_input_length > 100000:  # Increased limit to align with validation service
            raise error_response(
                status_code=400,
                code="INPUT_TOO_LONG",
                message="Input too long. Please reduce the length of your message and editor content."
            )
        
        # DEBUG: Log what content is being sent to AI
        logger.debug("Chat request user_id=%s", user_id)
        logger.debug("Message preview: %s", f"{validated_message[:200]}..." if len(validated_message) > 200 else validated_message)
        logger.debug("Editor text length: %s chars", len(validated_editor_text))
        if validated_editor_text and len(validated_editor_text) > 0:
            editor_preview = validated_editor_text[:300] + "..." if len(validated_editor_text) > 300 else validated_editor_text
            logger.debug("Editor content preview: %s", editor_preview)
        logger.debug("Author persona: %s", chat_request.author_persona)
        logger.debug("Help focus: %s", chat_request.help_focus)
        logger.debug("AI mode: %s", chat_request.ai_mode)
        logger.debug("LLM provider: %s", validated_llm_provider)
        
        # NEW: Log premium features usage
        logger.debug("Voice guard: %s", bool(chat_request.voice_guard))

        
        # Simplified user preferences - handle both Pydantic model and dict cases
        user_preferences = chat_request.user_preferences
        if user_preferences is None:
            user_corrections = []
        elif hasattr(user_preferences, 'user_corrections'):
            # It's a Pydantic UserPreferences model
            user_corrections = user_preferences.user_corrections or []
        elif isinstance(user_preferences, dict):
            # It's a dictionary (fallback case)
            user_corrections = user_preferences.get("user_corrections", [])
        else:
            # Unknown type, default to empty list
            user_corrections = []
        
        # Get highlighted text directly from request - this is the user's selection
        highlighted_text = None
        if chat_request.highlighted_text:
            highlighted_text = input_validator.validate_suggestion_text(chat_request.highlighted_text)
            logger.debug("Highlighted text length: %s", len(highlighted_text))
        
        # DEPRECATED: Old method of extracting from message - keeping as fallback
        elif "improve this text:" in validated_message and '"' in validated_message:
            parts = validated_message.split('"')
            if len(parts) >= 3:
                highlighted_text = input_validator.validate_suggestion_text(parts[1])
                logger.warning("⚠️ Using deprecated method to extract highlighted text from message")
        
        # FEATURE: Build conversation context from chat history
        conversation_context = build_conversation_context(chat_request.chat_history)
        if conversation_context:
            logger.debug("Using conversation context with %s messages", len(chat_request.chat_history))
        
        # Use the simplified prompt assembly system with AI mode
        logger.debug("Assembling prompt for provider=%s", validated_llm_provider)
        final_prompt = llm_service.assemble_chat_prompt(
            user_message=validated_message,
            editor_text=validated_editor_text,
            author_persona=chat_request.author_persona,
            help_focus=chat_request.help_focus,
            user_corrections=user_corrections,
            highlighted_text=highlighted_text,
            ai_mode=chat_request.ai_mode,
            conversation_context=conversation_context
        )
        
        logger.debug("Prompt assembled successfully (length=%s chars)", len(final_prompt))
        
        # Generate response using selected LLM
        response_text = None
        thinking_trail = None

        logger.info(f"🚀 Generating response with {validated_llm_provider}...")
        
        try:
            start_time = time.time()
            response_text = await generate_llm_response(final_prompt, validated_llm_provider)
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"✅ Response received (length: {len(response_text) if response_text else 0} chars, time: {processing_time_ms}ms)")
        
        except Exception as llm_error:
            logger.error("LLM generation failed for provider=%s", validated_llm_provider, exc_info=True)
            
            # Return user-friendly error message
            error_message = f"I'm having trouble connecting to the AI service ({validated_llm_provider}). Please try again in a moment."
            if "timeout" in str(llm_error).lower():
                error_message = f"The AI service ({validated_llm_provider}) is taking too long to respond. Please try a shorter message or try again later."
            elif "rate limit" in str(llm_error).lower():
                error_message = f"The AI service ({validated_llm_provider}) is currently busy. Please wait a moment and try again."
            elif "authentication" in str(llm_error).lower() or "api key" in str(llm_error).lower():
                error_message = f"There's a configuration issue with the AI service ({validated_llm_provider}). Please contact support."
            
            return ChatResponse(
                dialogue_response=error_message,
                thinking_trail=None
            )

        # Parse and validate the JSON response
        try:
            ai_response_dict = {}
            if response_text:
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```") and cleaned_text.endswith("```"):
                    json_text = cleaned_text.split("```")[1]
                    if json_text.startswith("json"):
                        json_text = json_text[4:].strip()
                    ai_response_dict = json.loads(json_text)
                elif cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                    ai_response_dict = json.loads(cleaned_text)
                else:
                    json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', cleaned_text, re.DOTALL)
                    if json_match:
                        try:
                            ai_response_dict = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Regex found potential JSON, but failed to parse: {json_match.group(0)}")
                            ai_response_dict = {"dialogue_response": cleaned_text}
                    else:
                        logger.info(f"ℹ️ Response is not JSON, using raw text: {cleaned_text[:200]}...")
                        ai_response_dict = {"dialogue_response": cleaned_text}
            else:
                ai_response_dict = {"dialogue_response": "Error: AI response was empty."}

            if "dialogue_response" not in ai_response_dict:
                dialogue_content = ai_response_dict.get("text", str(ai_response_dict))
                ai_response_dict["dialogue_response"] = dialogue_content if isinstance(dialogue_content, str) else "Error: AI response format was incorrect (missing dialogue_response)."
            
            # Validate AI response length but don't HTML escape since it's from our trusted LLM
            response_text = ai_response_dict["dialogue_response"]
            if len(response_text) > 10000:  # Reasonable limit for AI responses
                response_text = response_text[:10000] + "... [Response truncated]"
            sanitized_response = response_text
            
            # Store user feedback if provided
            if chat_request.feedback_on_previous:
                validated_feedback = input_validator.validate_text_input(chat_request.feedback_on_previous)
                db_service.add_user_feedback(
                    user_id=user_id,
                    original_message=validated_message,
                    ai_response=sanitized_response,
                    user_feedback=validated_feedback,
                    correction_type="general"  # Could be enhanced to detect type
                )
            
            # VOICE CONSISTENCY ANALYSIS: Check if editor text contains dialogue
            voice_analysis_results = []
            if validated_editor_text and len(validated_editor_text) > 100:
                try:
                    # Analyze editor text for voice consistency using the correct method name
                    voice_results = await get_character_voice_service().analyze(
                        text=validated_editor_text
                    )
                    
                    # Robust type checking for voice_results
                    if voice_results is None:
                        logger.warning("⚠️ Voice analysis returned None, skipping voice consistency check")
                    elif isinstance(voice_results, str):
                        logger.warning(f"⚠️ Voice analysis returned unexpected string: {voice_results[:200]}")
                    elif not isinstance(voice_results, dict):
                        logger.warning(f"⚠️ Voice analysis returned unexpected type: {type(voice_results)}")
                    elif 'results' not in voice_results:
                        logger.warning(f"⚠️ Voice analysis missing 'results' key: {voice_results.keys()}")
                    else:
                        # Add voice consistency feedback to response if issues found
                        try:
                            inconsistent_characters = [r for r in voice_results['results'] if hasattr(r, 'is_consistent') and not r.is_consistent]
                            if inconsistent_characters:
                                voice_feedback = f"\n\n💬 **Voice Consistency Note:** I noticed some potential voice inconsistencies in your writing:\n"
                                for result in inconsistent_characters[:2]:  # Limit to 2 for brevity
                                    if hasattr(result, 'character_name') and hasattr(result, 'explanation'):
                                        voice_feedback += f"• **{result.character_name}**: {result.explanation}\n"
                                
                                # Add voice feedback to the response
                                sanitized_response += voice_feedback
                                
                                logger.info(f"🎭 Voice consistency analysis: {len(inconsistent_characters)} inconsistencies found for user {user_id}")
                        except Exception as result_processing_error:
                            logger.error(f"❌ Error processing voice consistency results: {result_processing_error}")
                            logger.error(f"❌ Voice results type: {type(voice_results)}")
                            logger.error(f"❌ Voice results content: {str(voice_results)[:500]}")
                    
                except Exception as voice_error:
                    logger.error(f"❌ Voice consistency analysis error: {voice_error}")
                    logger.error(f"❌ Voice error type: {type(voice_error)}")
                    logger.exception("Voice consistency analysis full traceback:")
                    # Don't fail the chat if voice analysis fails
                    pass
            
            logger.info(f"🎉 Chat response generated successfully for user {user_id}")
            
            # GUEST ANALYTICS: Track successful chat interaction for quota enforcement
            if isinstance(user_id, str):  # Guest sessions
                auth_service.track_guest_activity(user_id, "chat_message", {
                    "message_length": len(chat_request.message),
                    "response_length": len(sanitized_response),
                    "llm_provider": validated_llm_provider,
                    "ai_mode": chat_request.ai_mode,
                    "author_persona": chat_request.author_persona
                })
            
            return ChatResponse(
                dialogue_response=sanitized_response,
                thinking_trail=thinking_trail
            )
        except Exception as json_error:
            logger.error(f"❌ JSON parsing error in main chat: {json_error}. Raw response: {str(response_text)[:200]}...")
            return ChatResponse(
                dialogue_response="I generated a response, but it couldn't be formatted correctly. Please try again.",
                thinking_trail=thinking_trail
            )
            
    except HTTPException as http_error:
        # Re-raise HTTP exceptions (like authentication errors and rate limits)
        logger.error(f"❌ HTTP Exception in chat endpoint: {http_error.status_code} - {http_error.detail}")
        raise
    except Exception as e:
        logger.error("General error in /api/chat", exc_info=True)
        return ChatResponse(
            dialogue_response="Error: Failed to generate response. An unexpected error occurred.",
            thinking_trail=None
        )

@router.post("/feedback")
async def submit_user_feedback(
    feedback_request: UserFeedbackRequest,
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """Submit user feedback on AI responses for continuous improvement."""
    try:
        # Apply rate limiting for feedback submission
        await check_rate_limit(http_request, "general")
        
        # Validate all feedback data
        validated_original = input_validator.validate_text_input(feedback_request.original_message)
        validated_ai_response = input_validator.validate_text_input(feedback_request.ai_response)
        validated_feedback = input_validator.validate_text_input(feedback_request.user_feedback)
        
        # Validate correction type
        allowed_types = ['grammar', 'style', 'tone', 'general']
        if feedback_request.correction_type not in allowed_types:
            raise error_response(
                status_code=400,
                code="INVALID_CORRECTION_TYPE",
                message="Invalid correction type.",
                meta={"allowed_types": allowed_types}
            )
        
        success = db_service.add_user_feedback(
            user_id=user_id,
            original_message=validated_original,
            ai_response=validated_ai_response,
            user_feedback=validated_feedback,
            correction_type=feedback_request.correction_type
        )
        
        if success:
            return {"status": "success", "message": "Feedback recorded successfully"}
        else:
            raise error_response(
                status_code=500,
                code="FEEDBACK_PERSIST_FAILED",
                message="Failed to record feedback."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting user feedback", exc_info=True)
        raise error_response(
            status_code=500,
            code="FEEDBACK_SUBMISSION_FAILED",
            message="An internal error occurred while submitting feedback."
        )

@router.get("/preferences")
async def get_user_preferences(http_request: Request, user_id: int = Depends(get_current_user_id)):
    """Get user preferences for the authenticated user."""
    try:
        # Apply rate limiting  
        await check_rate_limit(http_request, "general")
        
        preferences = db_service.get_user_preferences(user_id)
        
        if preferences:
            return {
                "status": "success",
                "preferences": preferences
            }
        else:
            # Create default preferences for new user
            default_preferences = db_service.create_default_preferences(user_id)
            return {
                "status": "success", 
                "preferences": default_preferences
            }
            
    except Exception:
        logger.error("Error getting user preferences", exc_info=True)
        raise error_response(
            status_code=500,
            code="PREFERENCES_FETCH_FAILED",
            message="An internal error occurred while retrieving user preferences."
        )

@router.post("/suggestions", response_model=EnhancedChatResponse)
async def generate_suggestions(
    suggestion_request: ChatRequest,
    http_request: Request,
    user_id: int = Depends(get_current_user_id),
    rate_limit_result = Depends(check_chat_rate_limit)  # Use chat limits for suggestions
):
    """Generate multiple actionable suggestions for selected text in Co-Edit mode"""
    try:
        # PRODUCTION RATE LIMITING: Now handled by dependency injection
        logger.info(f"🛡️ Suggestions rate limit check passed for user {user_id} (tokens remaining: {rate_limit_result.tokens_remaining})")
        
        # Validate inputs
        validated_message = input_validator.validate_chat_message(suggestion_request.message)
        highlighted_text = input_validator.validate_suggestion_text(suggestion_request.highlighted_text or "")
        
        # Check if we have highlighted text
        if not highlighted_text or not highlighted_text.strip():
            return EnhancedChatResponse(
                dialogue_response="Please select some text first, and I'll provide multiple improvement options.",
                suggestions=[],
                has_suggestions=False
            )
        
        # Check if we're in Co-Edit mode (suggestions only make sense in Co-Edit)
        if suggestion_request.ai_mode != "co-edit":
            return EnhancedChatResponse(
                dialogue_response="Multiple suggestions are available in Co-Edit mode. Switch to Co-Edit mode to get actionable text improvements.",
                suggestions=[],
                has_suggestions=False
            )
        
        logger.info(f"🎯 Generating suggestions for user {user_id}")
        logger.info(f"📝 Highlighted text: {highlighted_text[:100]}...")
        logger.info(f"💬 User message: {validated_message}")
        
        # FEATURE: Build conversation context for suggestions too
        conversation_context = build_conversation_context(suggestion_request.chat_history)
        if conversation_context:
            logger.info(f"💬 Using conversation context for suggestions with {len(suggestion_request.chat_history)} messages")
        
        # Generate multiple suggestions using the enhanced LLM service
        suggestions_response = await llm_service.generate_multiple_suggestions(
            highlighted_text=highlighted_text,
            user_message=validated_message,
            author_persona=suggestion_request.author_persona,
            help_focus=suggestion_request.help_focus,
            llm_provider=suggestion_request.llm_provider,
            conversation_context=conversation_context
        )
        
        # Convert to our schema format
        suggestion_objects = []
        for suggestion_data in suggestions_response.get("suggestions", []):
            suggestion_objects.append(SuggestionOption(
                id=suggestion_data.get("id", f"suggestion_{len(suggestion_objects)+1}"),
                text=suggestion_data.get("text", ""),
                type=suggestion_data.get("type", "improvement"),
                confidence=suggestion_data.get("confidence", 0.8),
                explanation=suggestion_data.get("explanation", "")
            ))
        
        return EnhancedChatResponse(
            dialogue_response=suggestions_response.get("dialogue_response", "Here are multiple options for improving your text:"),
            suggestions=suggestion_objects,
            original_text=highlighted_text,
            has_suggestions=len(suggestion_objects) > 0
        )
        
    except Exception as e:
        logger.error("Error generating suggestions", exc_info=True)
        return EnhancedChatResponse(
            dialogue_response="I encountered an error generating suggestions. Please try again.",
            suggestions=[],
            has_suggestions=False
        )

@router.post("/accept-suggestion")
async def accept_suggestion(
    suggestion_request: AcceptSuggestionRequest,
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """Accept and apply a suggestion to the editor content"""
    try:
        # Apply rate limiting for suggestion acceptance
        await check_rate_limit(http_request, "general")
        
        # Validate inputs - use suggestion-specific validation for text content
        original_text = input_validator.validate_suggestion_text(suggestion_request.original_text)
        suggested_text = input_validator.validate_suggestion_text(suggestion_request.suggested_text)
        editor_content = input_validator.validate_suggestion_text(suggestion_request.editor_content)
        
        logger.info(f"📝 User {user_id} accepting suggestion {suggestion_request.suggestion_id}")
        logger.info(f"🔄 Replacing: {original_text[:50]}...")
        logger.info(f"✨ With: {suggested_text[:50]}...")
        logger.info(f"📄 Editor content length: {len(editor_content)} chars")
        
        # Enhanced text matching with multiple strategies
        def normalize_text(text: str) -> str:
            """Normalize text for better matching"""
            import html
            import re
            
            # Decode HTML entities first (in case they're already present)
            text = html.unescape(text)
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            return text
        
        def clean_text_for_replacement(text: str) -> str:
            """Clean text specifically for replacement operations"""
            import html
            import re
            
            # Decode any HTML entities that might be present
            text = html.unescape(text)
            # Normalize whitespace but preserve line breaks
            text = re.sub(r'[ \t]+', ' ', text)  # Only collapse spaces and tabs
            text = re.sub(r'\n+', '\n', text)   # Collapse multiple newlines
            return text.strip()

        def find_text_with_fuzzy_matching(original: str, content: str) -> tuple[bool, str]:
            """Find text using multiple matching strategies"""
            
            # Clean both texts for better matching
            cleaned_original = clean_text_for_replacement(original)
            cleaned_content = clean_text_for_replacement(content)
            cleaned_suggested = clean_text_for_replacement(suggested_text)
            
            # Strategy 1: Exact match with cleaned text
            if cleaned_original in cleaned_content:
                logger.info("✅ Found exact match with cleaned text")
                return True, cleaned_content.replace(cleaned_original, cleaned_suggested, 1)
            
            # Strategy 2: Normalized text matching
            normalized_original = normalize_text(cleaned_original)
            normalized_content = normalize_text(cleaned_content)
            
            if normalized_original in normalized_content:
                logger.info("✅ Found normalized match")
                # Find the actual position in the cleaned content
                import re
                # Create a pattern that matches the original text with flexible whitespace
                pattern = re.escape(normalized_original).replace(r'\ ', r'\s+')
                match = re.search(pattern, cleaned_content, re.IGNORECASE)
                if match:
                    # Replace the matched text with the suggestion
                    return True, cleaned_content[:match.start()] + cleaned_suggested + cleaned_content[match.end():]
            
            # Strategy 3: Case-insensitive matching
            original_lower = cleaned_original.lower()
            content_lower = cleaned_content.lower()
            
            if original_lower in content_lower:
                logger.info("✅ Found case-insensitive match")
                # Find the actual case-sensitive position
                start_idx = content_lower.find(original_lower)
                if start_idx != -1:
                    end_idx = start_idx + len(cleaned_original)
                    return True, cleaned_content[:start_idx] + cleaned_suggested + cleaned_content[end_idx:]
            
            # Strategy 4: Partial matching with similarity threshold
            from difflib import SequenceMatcher
            
            # Split content into sentences/chunks and find best match
            import re
            sentences = re.split(r'[.!?]+', cleaned_content)
            best_match_ratio = 0
            best_match_sentence = None
            best_match_idx = -1
            
            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if len(sentence) > 10:  # Only consider substantial sentences
                    ratio = SequenceMatcher(None, cleaned_original.lower(), sentence.lower()).ratio()
                    if ratio > best_match_ratio and ratio > 0.7:  # 70% similarity threshold
                        best_match_ratio = ratio
                        best_match_sentence = sentence
                        best_match_idx = i
            
            if best_match_sentence and best_match_ratio > 0.7:
                logger.info(f"✅ Found partial match with {best_match_ratio:.2%} similarity")
                # Replace the best matching sentence
                sentences[best_match_idx] = cleaned_suggested
                return True, '.'.join(sentences)
            
            return False, content
        
        # Log the exact texts for debugging
        logger.info(f"🔍 Original text (len={len(original_text)}): '{original_text}'")
        logger.info(f"🔍 Editor content preview: '{editor_content[:200]}...'")
        logger.info(f"🔍 Looking for exact match...")
        
        # Try enhanced text matching
        found, updated_content = find_text_with_fuzzy_matching(original_text, editor_content)
        
        if found:
            logger.info("✅ Text replacement successful")
            return {
                "success": True,
                "updated_content": updated_content,
                "replacement_info": {
                    "original_text": original_text,
                    "suggested_text": suggested_text,
                    "suggestion_id": suggestion_request.suggestion_id,
                    "replacement_method": "enhanced_matching"
                }
            }
        else:
            # Enhanced error reporting
            logger.error(f"❌ Text not found using any matching strategy")
            logger.error(f"🔍 Original text chars: {[ord(c) for c in original_text[:20]]}")
            logger.error(f"🔍 Editor content sample chars: {[ord(c) for c in editor_content[:50]]}")
            
            return {
                "success": False,
                "error": f"Original text not found in editor content. Text: '{original_text[:100]}...' not found in content of length {len(editor_content)}",
                "updated_content": editor_content,
                "debug_info": {
                    "original_text_length": len(original_text),
                    "editor_content_length": len(editor_content),
                    "original_text_preview": original_text[:100],
                    "editor_content_preview": editor_content[:200]
                }
            }
            
    except Exception as e:
        logger.error("Error accepting suggestion:", exc_info=True)
        return {
            "success": False,
            "error": "An internal error has occurred. Please try again later.",
            "updated_content": suggestion_request.editor_content
        }

@router.get("/debug")
async def debug_chat_service(user_id: int = Depends(get_current_user_id)):
    """Debug endpoint to test authentication and LLM service availability"""
    try:
        logger.info(f"🔍 Debug endpoint called by user {user_id}")
        
        # Test LLM service availability
        available_providers = llm_service.get_available_providers()
        
        # Test each provider's detailed status
        provider_details = {}
        for provider in ["Google Gemini", "OpenAI GPT"]:
            try:
                if provider == "Google Gemini":
                    from services.llm.gemini_service import gemini_service
                    provider_details[provider] = gemini_service.get_model_info()
                elif provider == "OpenAI GPT":
                    from services.llm.openai_service import openai_service
                    provider_details[provider] = openai_service.get_model_info()
            except Exception as e:
                provider_details[provider] = {"error": str(e), "available": False}
        
        return {
            "status": "success",
            "user_id": user_id,
            "authentication": "working",
            "available_providers": available_providers,
            "provider_details": provider_details,
            "llm_service_status": "initialized",
            "timestamp": "2025-01-04T04:00:00Z"
        }
        
    except Exception as e:
        logger.error("❌ Debug endpoint error:", exc_info=True)
        return {
            "status": "error",
            "error": "An internal error has occurred. Please try again later.",
            "error_type": "unknown",
            "authentication": "unknown"
        }

 
