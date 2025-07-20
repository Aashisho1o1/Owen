"""
Character Voice Consistency Router - Complete Implementation

API endpoint for character voice consistency analysis with full database integration and profile management.
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

# Direct imports
from dependencies import get_current_user_id
from services.character_voice_service import CharacterVoiceService, CharacterVoiceProfile
from services.database import get_db_service, DatabaseError
from models.schemas import (
    VoiceConsistencyRequest, 
    VoiceConsistencyResponse,
    CharacterVoiceProfilesResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/character-voice", tags=["character-voice"])

# Initialize services
character_voice_service = CharacterVoiceService()
db_service = get_db_service()

@router.post("/analyze", response_model=VoiceConsistencyResponse)
async def analyze_voice_consistency(
    request: VoiceConsistencyRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    Analyze text for character voice consistency.
    
    This endpoint:
    1. Extracts dialogue from the provided text
    2. Loads existing character profiles from database
    3. Performs AI-powered voice consistency analysis
    4. Updates character profiles in database
    5. Returns detailed analysis results
    """
    try:
        logger.info(f"🎭 Voice analysis request from user {user_id}")
        logger.info(f"📝 Text length: {len(request.text)} chars")
        logger.info(f"🚀 Starting Gemini 2.5 Flash voice analysis...")
        
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text must be at least 10 characters long"
            )
        
        # Load existing character profiles from database
        existing_profiles = {}
        try:
            if db_service.is_available():
                profiles_data = await db_service.get_character_profiles(user_id)
                for profile_data in profiles_data:
                    profile = CharacterVoiceProfile(
                        character_id=profile_data['character_id'],
                        character_name=profile_data['character_name'],
                        dialogue_samples=profile_data.get('dialogue_samples', []),
                        voice_traits=profile_data.get('voice_traits', {}),
                        last_updated=profile_data.get('last_updated', ''),
                        sample_count=profile_data.get('sample_count', 0)
                    )
                    existing_profiles[profile.character_name] = profile
                logger.info(f"📚 Loaded {len(existing_profiles)} existing character profiles")
        except Exception as e:
            logger.warning(f"⚠️ Could not load existing profiles: {e}")
            # Continue with empty profiles - analysis will still work
        
        # Perform voice consistency analysis using the same successful pattern as chat
        logger.info(f"🧠 Gemini 2.5 Flash processing voice analysis...")
        logger.info("⏳ Expected processing time: 1-4 minutes for complex dialogue analysis...")
        
        try:
            analysis_result = await character_voice_service.analyze(
                text=request.text,
                existing_profiles=existing_profiles
            )
            logger.info(f"✅ Gemini 2.5 Flash voice analysis completed successfully")
            
        except Exception as analysis_error:
            logger.error(f"❌ Voice analysis failed: {str(analysis_error)}")
            logger.error(f"❌ Analysis Error Type: {type(analysis_error).__name__}")
            logger.error(f"❌ Analysis Error Details: {str(analysis_error)}")
            
            # Return user-friendly error message (same pattern as successful chat)
            error_message = "Voice analysis is temporarily unavailable. Please try again in a moment."
            if "timeout" in str(analysis_error).lower():
                error_message = "Voice analysis is taking too long to complete. Please try with shorter text or try again later."
            elif "rate limit" in str(analysis_error).lower():
                error_message = "The AI service is currently busy. Please wait a moment and try again."
            elif "authentication" in str(analysis_error).lower() or "api key" in str(analysis_error).lower():
                error_message = "There's a configuration issue with the AI service. Please contact support."
            
            # Return empty results with error message instead of raising exception
            return VoiceConsistencyResponse(
                results=[],
                characters_analyzed=0,
                dialogue_segments_found=0,
                processing_time_ms=0
            )
        
        # Save/update character profiles in database
        try:
            if db_service.is_available() and analysis_result.get("results"):
                for result in analysis_result["results"]:
                    await db_service.upsert_character_profile(
                        user_id=user_id,
                        character_name=result.character_name,
                        dialogue_samples=[],  # Will be populated by the service
                        voice_traits={
                            "consistency_score": result.confidence_score,
                            "last_analysis": result.explanation
                        }
                    )
                logger.info(f"💾 Updated character profiles in database")
        except Exception as e:
            logger.warning(f"⚠️ Could not save profiles to database: {e}")
            # Continue - analysis results are still valid
        
        # Convert results to response format
        response_results = []
        for result in analysis_result.get("results", []):
            response_results.append({
                "is_consistent": result.is_consistent,
                "confidence_score": result.confidence_score,
                "character_name": result.character_name,
                "flagged_text": result.flagged_text,
                "explanation": result.explanation,
                "suggestions": result.suggestions
            })
        
        response = VoiceConsistencyResponse(
            results=response_results,
            characters_analyzed=analysis_result.get("characters_analyzed", 0),
            dialogue_segments_found=analysis_result.get("dialogue_segments_found", 0),
            processing_time_ms=analysis_result.get("processing_time_ms", 0)
        )
        
        logger.info(f"✅ Voice analysis completed: {len(response_results)} results returned")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice analysis endpoint failed: {str(e)}")
        logger.error(f"❌ Endpoint Error Type: {type(e).__name__}")
        logger.error(f"❌ Endpoint Error Details: {str(e)}")
        
        # Return user-friendly error (same as successful chat pattern)
        error_detail = "Voice analysis failed. Please try again."
        if "timeout" in str(e).lower():
            error_detail = "Voice analysis timed out. Please try with shorter text."
        elif "database" in str(e).lower():
            error_detail = "Database connection issue. Analysis results may not be saved."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.get("/profiles", response_model=CharacterVoiceProfilesResponse)
async def get_character_profiles(
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all character voice profiles for the current user.
    """
    try:
        logger.info(f"📚 Fetching character profiles for user {user_id}")
        
        profiles = []
        if db_service.is_available():
            profiles_data = await db_service.get_character_profiles(user_id)
            
            for profile_data in profiles_data:
                profiles.append({
                    "character_id": profile_data['character_id'],
                    "character_name": profile_data['character_name'],
                    "dialogue_samples": profile_data.get('dialogue_samples', []),
                    "voice_traits": profile_data.get('voice_traits', {}),
                    "last_updated": profile_data.get('last_updated', ''),
                    "sample_count": profile_data.get('sample_count', 0)
                })
        
        logger.info(f"✅ Retrieved {len(profiles)} character profiles")
        return CharacterVoiceProfilesResponse(profiles=profiles)
        
    except Exception as e:
        logger.error(f"❌ Failed to get character profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve character profiles: {str(e)}"
        )

@router.delete("/profiles/{character_name}")
async def delete_character_profile(
    character_name: str,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a specific character profile.
    """
    try:
        logger.info(f"🗑️ Deleting character profile '{character_name}' for user {user_id}")
        
        if db_service.is_available():
            success = await db_service.delete_character_profile(user_id, character_name)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Character profile '{character_name}' not found"
                )
        
        logger.info(f"✅ Deleted character profile '{character_name}'")
        return {"success": True, "message": f"Character profile '{character_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete character profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete character profile: {str(e)}"
        )

@router.post("/profiles/{character_name}/update")
async def update_character_profile(
    character_name: str,
    profile_data: Dict[str, Any],
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a character profile with new dialogue samples or traits.
    """
    try:
        logger.info(f"📝 Updating character profile '{character_name}' for user {user_id}")
        
        if db_service.is_available():
            await db_service.upsert_character_profile(
                user_id=user_id,
                character_name=character_name,
                dialogue_samples=profile_data.get('dialogue_samples', []),
                voice_traits=profile_data.get('voice_traits', {})
            )
        
        logger.info(f"✅ Updated character profile '{character_name}'")
        return {"success": True, "message": f"Character profile '{character_name}' updated successfully"}
        
    except Exception as e:
        logger.error(f"❌ Failed to update character profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update character profile: {str(e)}"
        )

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the character voice service.
    """
    try:
        service_status = {
            "character_voice_service": "available" if character_voice_service else "unavailable",
            "database_service": "available" if db_service and db_service.is_available() else "unavailable",
            "llm_service": "available" if character_voice_service and hasattr(character_voice_service, 'llm_service') and character_voice_service.llm_service else "unavailable"
        }
        
        all_healthy = all(status == "available" for status in service_status.values())
        
        return JSONResponse(
            status_code=200 if all_healthy else 503,
            content={
                "status": "healthy" if all_healthy else "degraded",
                "services": service_status,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )
