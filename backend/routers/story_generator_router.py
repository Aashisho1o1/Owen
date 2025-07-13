from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
import logging

from services.llm_service import LLMService
from services.rate_limiter import check_rate_limit
from services.validation_service import input_validator
from dependencies import get_current_user_id

logger = logging.getLogger(__name__)
llm_service = LLMService()

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
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
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
        # Apply rate limiting - reuse existing chat rate limits
        await check_rate_limit(http_request, "chat")
        
        # Validate inputs using existing validation service
        # This ensures consistency with other endpoints and security
        story_spark = input_validator.validate_text_input(request.story_spark, max_length=500)
        reader_emotion = input_validator.validate_text_input(request.reader_emotion, max_length=100)
        author_vibe = input_validator.validate_text_input(request.author_vibe, max_length=100)
        story_length = input_validator.validate_text_input(request.story_length, max_length=50)
        
        # Log the request for monitoring and debugging
        logger.info(f"Story generation request from user {user_id}: {story_spark[:50]}...")
        
        # Construct the story generation prompt
        # This prompt is carefully designed to produce engaging, complete stories
        prompt = f"""Write a complete, engaging short story based on these specifications:

STORY CONCEPT: {story_spark}
TARGET EMOTION: The reader should feel {reader_emotion}
WRITING STYLE: Write in the style and voice of {author_vibe}
LENGTH: {story_length}

REQUIREMENTS:
- Create a complete story with beginning, middle, and end
- Include a compelling title
- Develop relatable characters
- Build to an emotionally satisfying conclusion
- Evoke {reader_emotion} in the reader through your narrative choices
- Match the distinctive voice and style of {author_vibe}
- Keep the length appropriate for {story_length}

Format your response as:
TITLE: [Your compelling title]

[Your complete story here]"""

        # Generate story using existing LLM service
        # We use Google Gemini as it's good for creative writing
        story_text = await llm_service.generate_with_selected_llm(prompt, "Google Gemini")
        
        # Log successful generation
        logger.info(f"Story generated successfully for user {user_id}, length: {len(story_text)} chars")
        
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