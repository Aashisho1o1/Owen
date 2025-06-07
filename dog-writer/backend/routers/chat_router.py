from fastapi import APIRouter, HTTPException
import json
import re

# Change relative imports to absolute imports
from models.schemas import (
    ChatRequest, ChatResponse, WritingSampleRequest, WritingSampleResponse,
    UserFeedbackRequest, OnboardingRequest, OnboardingResponse
)
from services.llm_service import LLMService
from services.database_service import db_service

# Initialize services
llm_service = LLMService()

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with personalized, culturally-aware feedback."""
    try:
        # Handle user session and preferences
        user_id = "default_user"  # In production, extract from auth token
        user_preferences = request.user_preferences
        
        # If no preferences provided, try to load from database
        if not user_preferences:
            user_preferences = db_service.get_user_preferences(user_id)
            if not user_preferences:
                # Create default preferences for new user
                user_preferences = db_service.create_default_preferences(user_id)
        
        # Extract user message and check for highlighted text
        highlighted_text = None
        message = request.message
        if "improve this text:" in request.message and '"' in request.message:
            parts = request.message.split('"')
            if len(parts) >= 3:
                highlighted_text = parts[1]
        
        # Use the new modular prompt assembly system
        final_prompt = llm_service.assemble_chat_prompt(
            user_message=message,
            editor_text=request.editor_text,
            author_persona=request.author_persona,
            help_focus=request.help_focus,
            english_variant=request.english_variant or user_preferences.english_variant,
            user_style_profile=user_preferences.writing_style_profile,
            user_corrections=user_preferences.user_corrections,
            highlighted_text=highlighted_text
        )
        
        # Generate response using selected LLM
        response_text = None
        thinking_trail = None

        if request.llm_provider == "Google Gemini":
            # Format prompt for Gemini (expects list of dicts)
            prompts = [
                {"role": "user", "parts": [final_prompt]}
            ]
            response_text = await llm_service.generate_with_selected_llm(prompts, request.llm_provider)
        else: # Anthropic Claude
            response_result = await llm_service.generate_with_selected_llm(final_prompt, request.llm_provider)
            
            if isinstance(response_result, dict) and "text" in response_result:
                response_text = response_result["text"]
                thinking_trail = response_result.get("thinking_trail")
            else:
                print(f"Unexpected response_result structure from Claude: {response_result}")
                response_text = json.dumps({"dialogue_response": "Error: Received unexpected response structure from LLM service for Claude."})
                thinking_trail = response_result.get("thinking_trail", "Error retrieving thinking trail.") if isinstance(response_result, dict) else "Unknown error in thinking trail."

        # Parse the JSON response
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
            
            # Store user feedback if provided
            if request.feedback_on_previous:
                db_service.add_user_feedback(
                    user_id=user_id,
                    original_message=message,
                    ai_response=ai_response_dict["dialogue_response"],
                    user_feedback=request.feedback_on_previous,
                    correction_type="general"  # Could be enhanced to detect type
                )
            
            return ChatResponse(
                dialogue_response=ai_response_dict["dialogue_response"],
                thinking_trail=thinking_trail
            )
        except Exception as json_error:
            print(f"JSON parsing error in main chat: {json_error}. Raw response: {str(response_text)[:200]}...")
            return ChatResponse(
                dialogue_response=str(response_text)[:1000] if response_text else "Error: Could not parse the AI's response.",
                thinking_trail=thinking_trail
            )
            
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
async def analyze_writing_sample(request: WritingSampleRequest):
    """Analyze a user's writing sample to create a personalized style profile."""
    try:
        user_id = request.user_id or "default_user"
        
        # Analyze the writing style using LLM
        style_profile = await llm_service.analyze_writing_style(request.writing_sample)
        
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
        
    except Exception as e:
        print(f"Error analyzing writing sample: {e}")
        return WritingSampleResponse(
            style_profile={},
            success=False,
            error=str(e)
        )

@router.post("/feedback")
async def submit_user_feedback(request: UserFeedbackRequest):
    """Submit user feedback on AI responses for continuous improvement."""
    try:
        user_id = "default_user"  # In production, extract from auth token
        
        success = db_service.add_user_feedback(
            user_id=user_id,
            original_message=request.original_message,
            ai_response=request.ai_response,
            user_feedback=request.user_feedback,
            correction_type=request.correction_type
        )
        
        if success:
            return {"status": "success", "message": "Feedback recorded successfully"}
        else:
            return {"status": "error", "message": "Failed to record feedback"}
            
    except Exception as e:
        print(f"Error submitting user feedback: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(request: OnboardingRequest):
    """Complete user onboarding and save initial preferences."""
    try:
        user_id = "default_user"  # In production, extract from auth token
        
        success = db_service.complete_onboarding(
            user_id=user_id,
            writing_type=request.writing_type,
            feedback_style=request.feedback_style,
            primary_goal=request.primary_goal,
            english_variant=request.english_variant
        )
        
        if success:
            user_preferences = db_service.get_user_preferences(user_id)
            return OnboardingResponse(
                success=True,
                user_preferences=user_preferences,
                message="Onboarding completed successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save onboarding preferences")
            
    except Exception as e:
        print(f"Error completing onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences")
async def get_user_preferences():
    """Get current user preferences."""
    try:
        user_id = "default_user"  # In production, extract from auth token
        preferences = db_service.get_user_preferences(user_id)
        
        if preferences:
            return {"status": "success", "preferences": preferences}
        else:
            # Create default preferences
            preferences = db_service.create_default_preferences(user_id)
            return {"status": "success", "preferences": preferences}
            
    except Exception as e:
        print(f"Error retrieving user preferences: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/style-options")
async def get_style_options():
    """Get available English variants."""
    return {
        "english_variants": [
            {"value": "standard", "label": "Standard English"},
            {"value": "indian", "label": "Indian English"},
            {"value": "british", "label": "British English"},
            {"value": "american", "label": "American English"}
        ]
    } 