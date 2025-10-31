"""
Character Voice Router - Essential endpoints only
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from models.schemas import (
    VoiceAnalysisRequest,
    VoiceAnalysisResponse,
    CharacterProfilesResponse,
    VoiceAnalysisResult
)
from services.character_voice_service import character_voice_service
from services.database import db_service
from services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Dependency to get current user from JWT
async def get_current_user(authorization: Optional[str] = Header(None)) -> int:
    """Extract user ID from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = authorization.replace("Bearer ", "")
    payload = auth_service.decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return int(payload['sub'])

@router.post("/analyze", response_model=VoiceAnalysisResponse)
async def analyze_voice_consistency(
    request: VoiceAnalysisRequest,
    user_id: int = Depends(get_current_user)
):
    """
    Analyze text for character voice consistency.

    Uses Gemini to:
    1. Extract dialogue and identify speakers
    2. Analyze voice traits for each character
    3. Compare against stored profiles
    4. Update profiles in database
    """
    start_time = datetime.now()

    logger.info(f"🎭 Voice analysis request from user {user_id}")
    logger.info(f"📝 Text length: {len(request.text)} chars")

    try:
        # Run analysis
        analysis_result = await character_voice_service.analyze(
            request.text,
            user_id
        )

        # Convert results to schema
        results = [
            VoiceAnalysisResult(**result)
            for result in analysis_result.get("results", [])
        ]

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        response = VoiceAnalysisResponse(
            results=results,
            characters_analyzed=analysis_result.get("characters_analyzed", 0),
            dialogue_segments_found=analysis_result.get("dialogue_segments_found", 0),
            processing_time_ms=int(processing_time)
        )

        logger.info(f"✅ Analysis complete: {len(results)} characters, {processing_time:.0f}ms")
        return response

    except Exception as e:
        logger.error(f"❌ Voice analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/profiles", response_model=CharacterProfilesResponse)
async def get_character_profiles(
    user_id: int = Depends(get_current_user)
):
    """Get all character profiles for the current user."""
    try:
        if not db_service.is_available():
            return CharacterProfilesResponse(profiles=[])

        profiles = await db_service.get_character_profiles(user_id)

        logger.info(f"📚 Retrieved {len(profiles)} profiles for user {user_id}")
        return CharacterProfilesResponse(profiles=profiles)

    except Exception as e:
        logger.error(f"❌ Get profiles failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profiles: {str(e)}"
        )

@router.delete("/profiles/{character_name}")
async def delete_character_profile(
    character_name: str,
    user_id: int = Depends(get_current_user)
):
    """Delete a specific character profile."""
    try:
        if not db_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable"
            )

        success = await db_service.delete_character_profile(user_id, character_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile '{character_name}' not found"
            )

        logger.info(f"🗑️ Deleted profile: {character_name} for user {user_id}")
        return {"success": True, "message": f"Profile '{character_name}' deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete profile failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )
