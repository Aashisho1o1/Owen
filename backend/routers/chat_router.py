from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import re
import logging

# Import security services
from services.auth_service import auth_service, AuthenticationError
from services.validation_service import input_validator

# Change relative imports to absolute imports
from models.schemas import (
    ChatRequest, ChatResponse, UserFeedbackRequest
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
        # CRITICAL SECURITY: Rate limiting for chat requests
        # This prevents abuse and protects against DoS attacks on expensive LLM calls
        from datetime import datetime, timedelta
        import time
        
        # Simple in-memory rate limiting (should be moved to Redis in production)
        if not hasattr(chat, '_user_requests'):
            chat._user_requests = {}
        
        now = time.time()
        minute_ago = now - 60  # 1 minute window
        
        # Clean old requests
        if user_id in chat._user_requests:
            chat._user_requests[user_id] = [req_time for req_time in chat._user_requests[user_id] if req_time > minute_ago]
        else:
            chat._user_requests[user_id] = []
        
        # Check rate limit (max 10 requests per minute)
        if len(chat._user_requests[user_id]) >= 10:
            logger.warning(f"🚨 SECURITY: Rate limit exceeded for user {user_id}")
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please wait before sending another message."
            )
        
        # Record this request
        chat._user_requests[user_id].append(now)
        
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
        
        # Use the simplified prompt assembly system
        final_prompt = llm_service.assemble_chat_prompt(
            user_message=validated_message,
            editor_text=validated_editor_text,
            author_persona=request.author_persona,
            help_focus=request.help_focus,
            user_corrections=user_corrections,
            highlighted_text=highlighted_text
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
        # Re-raise HTTP exceptions (like authentication errors)
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
async def get_user_preferences(user_id: int = Depends(get_current_user_id)):
    """Get user preferences for the authenticated user."""
    try:
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

 