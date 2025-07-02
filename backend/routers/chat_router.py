from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import re
import logging

# Import security services
from services.auth_service import auth_service, AuthenticationError
from services.validation_service import input_validator

# Import the new production rate limiter
from services.rate_limiter import check_rate_limit

# Change relative imports to absolute imports
from models.schemas import (
    ChatRequest, ChatResponse, UserFeedbackRequest, 
    EnhancedChatResponse, SuggestionOption, AcceptSuggestionRequest
)
from services.llm_service import LLMService
from services.database import db_service

# Import centralized authentication dependency
from dependencies import get_current_user_id

# Initialize services
llm_service = LLMService()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    user_id: int = Depends(get_current_user_id)
):
    """Enhanced chat endpoint with personalized, culturally-aware feedback and security."""
    try:
        # PRODUCTION RATE LIMITING: Use distributed rate limiter
        # This prevents abuse across multiple Railway instances
        await check_rate_limit(request, "chat")
        
        logger.info(f"🛡️ Rate limit check passed for user {user_id}")
        
        # Validate and sanitize all input data
        validated_message = input_validator.validate_chat_message(request.message)
        validated_editor_text = input_validator.validate_text_input(request.editor_text or "")
        validated_llm_provider = input_validator.validate_llm_provider(request.llm_provider)
        
        # SECURITY: Additional length checks for expensive operations
        total_input_length = len(validated_message) + len(validated_editor_text)
        if total_input_length > 15000:  # Reasonable limit for LLM processing
            raise HTTPException(
                status_code=400,
                detail="Input too long. Please reduce the length of your message and editor content."
            )
        
        # DEBUG: Log what content is being sent to AI
        logger.info(f"🔍 CHAT DEBUG - User ID: {user_id}")
        logger.info(f"📝 Message: {validated_message[:200]}..." if len(validated_message) > 200 else f"📝 Message: {validated_message}")
        logger.info(f"📄 Editor text length: {len(validated_editor_text)} chars")
        if validated_editor_text and len(validated_editor_text) > 0:
            editor_preview = validated_editor_text[:300] + "..." if len(validated_editor_text) > 300 else validated_editor_text
            logger.info(f"📄 Editor content preview: {editor_preview}")
        logger.info(f"🎭 Author persona: {request.author_persona}")
        logger.info(f"🎯 Help focus: {request.help_focus}")
        logger.info(f"🤖 AI Mode: {request.ai_mode}")

        
        # Simplified user preferences - handle both Pydantic model and dict cases
        user_preferences = request.user_preferences
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
        if request.highlighted_text:
            highlighted_text = input_validator.validate_text_input(request.highlighted_text)
            logger.info(f"📝 User highlighted text received: {highlighted_text[:100]}..." if len(highlighted_text) > 100 else f"📝 User highlighted text: {highlighted_text}")
        
        # DEPRECATED: Old method of extracting from message - keeping as fallback
        elif "improve this text:" in validated_message and '"' in validated_message:
            parts = validated_message.split('"')
            if len(parts) >= 3:
                highlighted_text = input_validator.validate_text_input(parts[1])
                logger.warning("⚠️ Using deprecated method to extract highlighted text from message")
        
        # Use the simplified prompt assembly system with AI mode
        final_prompt = llm_service.assemble_chat_prompt(
            user_message=validated_message,
            editor_text=validated_editor_text,
            author_persona=request.author_persona,
            help_focus=request.help_focus,
            user_corrections=user_corrections,
            highlighted_text=highlighted_text,
            ai_mode=request.ai_mode
        )
        
        # Generate response using selected LLM
        response_text = None
        thinking_trail = None

        if validated_llm_provider == "Google Gemini":
            # Format prompt for Gemini (expects list of dicts)
            prompts = [
                {"role": "user", "parts": [final_prompt]}
            ]
            response_text = await llm_service.generate_with_selected_llm(prompts, validated_llm_provider)
        elif validated_llm_provider == "OpenAI GPT":
            # Format prompt for OpenAI (simple string)
            response_text = await llm_service.generate_with_selected_llm(final_prompt, validated_llm_provider)
        else: # Anthropic Claude or other
            response_result = await llm_service.generate_with_selected_llm(final_prompt, validated_llm_provider)
            
            if isinstance(response_result, dict) and "text" in response_result:
                response_text = response_result["text"]
                thinking_trail = response_result.get("thinking_trail")
            else:
                print(f"Unexpected response_result structure from {validated_llm_provider}: {type(response_result)}")
                # Avoid circular reference by converting to string safely
                response_text = json.dumps({"dialogue_response": f"Error: Received unexpected response structure from LLM service for {validated_llm_provider}."})
                thinking_trail = "Error retrieving thinking trail."

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
                            print(f"Regex found potential JSON, but failed to parse: {json_match.group(0)}")
                            ai_response_dict = {"dialogue_response": cleaned_text}
                    else:
                        print(f"Response is not JSON and regex failed. Using raw text: {cleaned_text[:200]}...")
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
            if request.feedback_on_previous:
                validated_feedback = input_validator.validate_text_input(request.feedback_on_previous)
                db_service.add_user_feedback(
                    user_id=user_id,
                    original_message=validated_message,
                    ai_response=sanitized_response,
                    user_feedback=validated_feedback,
                    correction_type="general"  # Could be enhanced to detect type
                )
            
            return ChatResponse(
                dialogue_response=sanitized_response,
                thinking_trail=thinking_trail
            )
        except Exception as json_error:
            print(f"JSON parsing error in main chat: {json_error}. Raw response: {str(response_text)[:200]}...")
            return ChatResponse(
                dialogue_response=str(response_text) if response_text else "Error: Could not parse the AI's response.",
                thinking_trail=thinking_trail
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (like authentication errors and rate limits)
        raise
    except Exception as e:
        print(f"General error in /api/chat: {e}")
        error_dialogue = "Error: Failed to generate response. An unexpected error occurred."
        if hasattr(e, 'detail') and e.detail:
            error_dialogue = f"Error: {e.detail}"
        elif str(e):
            error_dialogue = f"Error: {str(e)}"
            
        return ChatResponse(
            dialogue_response=error_dialogue,
            thinking_trail=None
        )

@router.post("/feedback")
async def submit_user_feedback(
    request: UserFeedbackRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Submit user feedback on AI responses for continuous improvement."""
    try:
        # Apply rate limiting for feedback submission
        await check_rate_limit(request, "general")
        
        # Validate all feedback data
        validated_original = input_validator.validate_text_input(request.original_message)
        validated_ai_response = input_validator.validate_text_input(request.ai_response)
        validated_feedback = input_validator.validate_text_input(request.user_feedback)
        
        # Validate correction type
        allowed_types = ['grammar', 'style', 'tone', 'general']
        if request.correction_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid correction type. Must be one of: {allowed_types}")
        
        success = db_service.add_user_feedback(
            user_id=user_id,
            original_message=validated_original,
            ai_response=validated_ai_response,
            user_feedback=validated_feedback,
            correction_type=request.correction_type
        )
        
        if success:
            return {"status": "success", "message": "Feedback recorded successfully"}
        else:
            return {"status": "error", "message": "Failed to record feedback"}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting user feedback: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/preferences")
async def get_user_preferences(request: Request, user_id: int = Depends(get_current_user_id)):
    """Get user preferences for the authenticated user."""
    try:
        # Apply rate limiting  
        await check_rate_limit(request, "general")
        
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
            
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while retrieving user preferences.",
            "preferences": None
        }

@router.post("/suggestions", response_model=EnhancedChatResponse)
async def generate_suggestions(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Generate multiple actionable suggestions for selected text in Co-Edit mode"""
    try:
        # PRODUCTION RATE LIMITING: Stricter limits for expensive AI suggestions
        await check_rate_limit(request, "chat")  # Use chat limits for suggestions
        
        logger.info(f"🛡️ Suggestions rate limit check passed for user {user_id}")
        
        # Validate inputs
        validated_message = input_validator.validate_chat_message(request.message)
        highlighted_text = input_validator.validate_suggestion_text(request.highlighted_text or "")
        
        # Check if we have highlighted text
        if not highlighted_text or not highlighted_text.strip():
            return EnhancedChatResponse(
                dialogue_response="Please select some text first, and I'll provide multiple improvement options.",
                suggestions=[],
                has_suggestions=False
            )
        
        # Check if we're in Co-Edit mode (suggestions only make sense in Co-Edit)
        if request.ai_mode != "co-edit":
            return EnhancedChatResponse(
                dialogue_response="Multiple suggestions are available in Co-Edit mode. Switch to Co-Edit mode to get actionable text improvements.",
                suggestions=[],
                has_suggestions=False
            )
        
        logger.info(f"🎯 Generating suggestions for user {user_id}")
        logger.info(f"📝 Highlighted text: {highlighted_text[:100]}...")
        logger.info(f"💬 User message: {validated_message}")
        
        # Generate multiple suggestions using the enhanced LLM service
        suggestions_response = await llm_service.generate_multiple_suggestions(
            highlighted_text=highlighted_text,
            user_message=validated_message,
            author_persona=request.author_persona,
            help_focus=request.help_focus,
            llm_provider=request.llm_provider
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
        logger.error(f"Error generating suggestions: {e}")
        return EnhancedChatResponse(
            dialogue_response=f"I encountered an error generating suggestions: {str(e)}",
            suggestions=[],
            has_suggestions=False
        )

@router.post("/accept-suggestion")
async def accept_suggestion(
    request: AcceptSuggestionRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Accept and apply a suggestion to the editor content"""
    try:
        # Apply rate limiting for suggestion acceptance
        await check_rate_limit(request, "general")
        
        # Validate inputs - use suggestion-specific validation for text content
        original_text = input_validator.validate_suggestion_text(request.original_text)
        suggested_text = input_validator.validate_suggestion_text(request.suggested_text)
        editor_content = input_validator.validate_suggestion_text(request.editor_content)
        
        logger.info(f"📝 User {user_id} accepting suggestion {request.suggestion_id}")
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
                    "suggestion_id": request.suggestion_id,
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
        logger.error(f"Error accepting suggestion: {e}")
        return {
            "success": False,
            "error": str(e),
            "updated_content": request.editor_content
        }

 