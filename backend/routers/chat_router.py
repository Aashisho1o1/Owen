from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import re
import logging

# Import security services
from services.auth_service import auth_service, AuthenticationError
from services.validation_service import ChatMessageModel, UserFeedbackModel, input_validator

# Change relative imports to absolute imports
from models.schemas import (
    ChatRequest, ChatResponse, WritingSampleRequest, WritingSampleResponse,
    UserFeedbackRequest, OnboardingRequest, OnboardingResponse
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
        # Validate and sanitize all input data
        validated_message = input_validator.validate_chat_message(request.message)
        validated_editor_text = input_validator.validate_text_input(request.editor_text or "")
        validated_llm_provider = input_validator.validate_llm_provider(request.llm_provider)

        
        # Get user preferences - now user_id comes from JWT token
        user_preferences = request.user_preferences
        
        # If no preferences provided, try to load from database
        if not user_preferences:
            user_preferences = db_service.get_user_preferences(user_id)
            if not user_preferences:
                # Create default preferences for new user
                user_preferences = db_service.create_default_preferences(user_id)
        
        # Extract highlighted text safely
        highlighted_text = None
        if "improve this text:" in validated_message and '"' in validated_message:
            parts = validated_message.split('"')
            if len(parts) >= 3:
                highlighted_text = input_validator.validate_text_input(parts[1])
        
        # Use the new modular prompt assembly system
        final_prompt = llm_service.assemble_chat_prompt(
            user_message=validated_message,
            editor_text=validated_editor_text,
            author_persona=request.author_persona,
            help_focus=request.help_focus,
            user_style_profile=user_preferences.writing_style_profile,
            user_corrections=user_preferences.user_corrections,
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
                            ai_response_dict = {"dialogue_response": cleaned_text[:1000]}
                    else:
                        print(f"Response is not JSON and regex failed. Using raw text: {cleaned_text[:200]}...")
                        ai_response_dict = {"dialogue_response": cleaned_text[:1000]}
            else:
                ai_response_dict = {"dialogue_response": "Error: AI response was empty."}

            if "dialogue_response" not in ai_response_dict:
                dialogue_content = ai_response_dict.get("text", str(ai_response_dict))
                ai_response_dict["dialogue_response"] = dialogue_content if isinstance(dialogue_content, str) else "Error: AI response format was incorrect (missing dialogue_response)."
            
            # Validate and sanitize the AI response
            sanitized_response = input_validator.validate_text_input(ai_response_dict["dialogue_response"])
            
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
                dialogue_response=str(response_text)[:1000] if response_text else "Error: Could not parse the AI's response.",
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

@router.post("/analyze-writing", response_model=WritingSampleResponse)
async def analyze_writing_sample(
    request: WritingSampleRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Analyze a user's writing sample to create a personalized style profile."""
    try:
        # Validate writing sample
        validated_sample = input_validator.validate_text_input(request.writing_sample)
        
        # Analyze the writing style using LLM
        style_profile = await llm_service.analyze_writing_style(validated_sample)
        
        # Save the style profile to database
        if not style_profile.get("error"):
            success = db_service.save_writing_style_profile(user_id, style_profile)
            if not success:
                return WritingSampleResponse(
                    style_profile=style_profile,
                    success=False,
                    error="Failed to save style profile to database"
                )
        
        return WritingSampleResponse(
            style_profile=style_profile,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error analyzing writing sample: {e}")
        return WritingSampleResponse(
            style_profile={},
            success=False,
            error=str(e)
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

@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Complete user onboarding and save initial preferences."""
    try:
        # Validate onboarding data
        validated_writing_type = input_validator.validate_text_input(request.writing_type)
        validated_feedback_style = input_validator.validate_text_input(request.feedback_style)
        validated_primary_goal = input_validator.validate_text_input(request.primary_goal)
        
        success = db_service.complete_onboarding(
            user_id=user_id,
            writing_type=validated_writing_type,
            feedback_style=validated_feedback_style,
            primary_goal=validated_primary_goal
        )
        
        if success:
            # Get updated preferences
            user_preferences = db_service.get_user_preferences(user_id)
            
            return OnboardingResponse(
                success=True,
                message="Onboarding completed successfully",
                user_preferences=user_preferences
            )
        else:
            return OnboardingResponse(
                success=False,
                message="Failed to complete onboarding"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing onboarding: {e}")
        return OnboardingResponse(
            success=False,
            message="An internal error occurred while completing onboarding."
        )

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

 