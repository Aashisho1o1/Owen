from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Union
import logging

from services.llm_service import LLMService
from services.validation_service import input_validator
from services.auth_service import auth_service
from dependencies import get_current_user_id, check_chat_rate_limit

logger = logging.getLogger(__name__)
llm_service = LLMService()

# Guest quota configuration
GUEST_DAILY_LIMIT = 2  # Maximum story generations per 24h for guests

router = APIRouter(
    prefix="/api/story-generator",
    tags=["story-generator"],
)

class StoryGenerateRequest(BaseModel):
    """Request to generate a short story"""
    story_spark: str = Field(..., min_length=1, max_length=500, description="Story idea or spark")
    reader_emotion: str = Field(..., min_length=1, max_length=100, description="Desired reader emotion")
    author_vibe: str = Field(..., min_length=1, max_length=100, description="Author style inspiration")
    story_length: str = Field(..., min_length=1, max_length=50, description="Story length preference")

class StoryGenerateResponse(BaseModel):
    """Response containing generated story"""
    story: str
    inputs: dict
    success: bool = True

@router.post("/generate", response_model=StoryGenerateResponse)
async def generate_story(
    request: StoryGenerateRequest,
    user_id: Union[str, int] = Depends(get_current_user_id),  # Accept both guest UUIDs and user IDs
    _rate_limit_result = Depends(check_chat_rate_limit)
):
    """
    Generate a complete short story based on user inputs.
    
    This endpoint:
    1. Validates all inputs using existing validation service
    2. Applies rate limiting using existing rate limiter
    3. Constructs a carefully crafted prompt for story generation
    4. Uses existing LLM service to generate the story
    5. Returns structured response with story and metadata
    """
    try:
        # GUEST QUOTA ENFORCEMENT: Check daily limits for cost control
        if isinstance(user_id, str):  # Guest sessions are UUID strings
            usage_count = auth_service.get_guest_usage_count(user_id)
            if usage_count >= GUEST_DAILY_LIMIT:
                logger.info(f"Guest {user_id} hit daily story limit: {usage_count}/{GUEST_DAILY_LIMIT}")
                quota_info = auth_service.get_guest_quota(user_id, GUEST_DAILY_LIMIT)
                raise HTTPException(
                    status_code=402,  # Payment Required - perfect for quota limits
                    detail={
                        "code": "GUEST_LIMIT_REACHED",
                        "message": f"You've used your {GUEST_DAILY_LIMIT} free daily stories. Sign up for unlimited access!",
                        "quota": quota_info
                    }
                )
            logger.info(f"Guest {user_id} story generation: {usage_count + 1}/{GUEST_DAILY_LIMIT}")
        
        # Validate inputs using existing validation service
        # This ensures consistency with other endpoints and security
        story_spark = input_validator.validate_text_input(request.story_spark, max_length=500)
        reader_emotion = input_validator.validate_text_input(request.reader_emotion, max_length=100)
        author_vibe = input_validator.validate_text_input(request.author_vibe, max_length=100)
        story_length = input_validator.validate_text_input(request.story_length, max_length=50)
        
        # Log the request for monitoring and debugging
        logger.info(f"Story generation request from user {user_id}: {story_spark[:50]}...")
        
        # Construct the story generation prompt
        # This prompt is designed to create viral, engaging micro-stories that hook users instantly
        prompt = f"""You are a master of viral micro-fiction. Create an instantly captivating story that will make readers gasp, laugh, or get chills. This needs to hook someone scrolling on their phone in 2 seconds.

🎯 STORY MISSION: {story_spark}
💫 READER REACTION TARGET: Make them feel {reader_emotion} - but INTENSE and IMMEDIATE
✍️ VOICE: Channel {author_vibe}'s most compelling, punchy style
📏 LENGTH: {story_length} - Every word must EARN its place

🔥 VIRAL STORY RULES:
• HOOK in the first 5 words - make it impossible to look away
• Create an "OH WOW" moment that makes people want to share
• End with impact - leave them wanting MORE
• Use vivid, sensory details that pop off the screen
• Make it feel like a movie trailer in text form
• Perfect for reading aloud - should sound amazing
• Create that "I need to show this to someone" feeling

📱 MOBILE-FIRST: Remember, they're reading this on their phone, probably while doing something else. GRAB their attention and don't let go.

🎬 THINK LIKE: A TikTok that went viral, a tweet that got 100k likes, a story people screenshot and send to friends.

Format your response as:
TITLE: [Punchy, intriguing title that makes people click]

[Your viral micro-story here - every word counts!]"""

        # Generate story using existing LLM service
        # We use Google Gemini as it's good for creative writing
        story_text = await llm_service.generate_with_selected_llm(prompt, "Google Gemini")
        
        # Log successful generation
        logger.info(f"Story generated successfully for user {user_id}, length: {len(story_text)} chars")
        
        # GUEST ANALYTICS: Track successful story generation for quota enforcement
        if isinstance(user_id, str):  # Guest sessions
            auth_service.track_guest_activity(user_id, "story_generate", {
                "story_length": len(story_text),
                "spark_category": story_spark[:50],  # First 50 chars for categorization
                "reader_emotion": reader_emotion,
                "author_vibe": author_vibe
            })
        
        # Return structured response
        return StoryGenerateResponse(
            story=story_text,
            inputs={
                "story_spark": story_spark,
                "reader_emotion": reader_emotion,
                "author_vibe": author_vibe,
                "story_length": story_length
            },
            success=True
        )
        
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Story generation error for user {user_id}: {str(e)}")
        
        # Return user-friendly error
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate story. Please try again with different inputs."
        )

@router.get("/health")
async def story_generator_health():
    """Health check endpoint for story generator service"""
    return {
        "status": "healthy",
        "service": "story-generator",
        "llm_available": llm_service.get_available_providers()
    } 
