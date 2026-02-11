"""
Character Voice Consistency Router - Complete Implementation

API endpoint for character voice consistency analysis with full database integration and profile management.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime

# Direct imports
from dependencies import get_current_user_id, check_voice_analysis_rate_limit
from services.character_voice_service import CharacterVoiceService, CharacterVoiceProfile
from services.database import get_db_service
from models.schemas import (
    VoiceConsistencyRequest, 
    VoiceConsistencyResponse,
    CharacterVoiceProfilesResponse
)
from utils.error_responses import error_response

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/character-voice", tags=["character-voice"])

# Lazy initialization to prevent import-time errors
character_voice_service = None
db_service = None

def get_character_voice_service() -> CharacterVoiceService:
    """Lazily initialize and return CharacterVoiceService instance"""
    global character_voice_service
    if character_voice_service is None:
        character_voice_service = CharacterVoiceService()
    return character_voice_service

def get_db_service_instance():
    """Lazily initialize and return database service instance"""
    global db_service
    if db_service is None:
        db_service = get_db_service()
    return db_service

@router.post("/analyze", response_model=VoiceConsistencyResponse)
async def analyze_voice_consistency(
    request: VoiceConsistencyRequest,
    user_id: int = Depends(get_current_user_id),
    rate_limit_result = Depends(check_voice_analysis_rate_limit)
):
    """
    Analyze text for character voice consistency.
    
    This endpoint:
    1. Applies rate limiting
    2. Extracts dialogue from the provided text
    3. Loads existing character profiles from database
    4. Performs AI-powered voice consistency analysis
    5. Updates character profiles in database
    6. Returns detailed analysis results
    """
    start_time = datetime.now()
    
    try:
        logger.info(
            "Voice analysis request started for user %s (tier=%s, tokens_remaining=%s, text_length=%s)",
            user_id,
            rate_limit_result.tier,
            rate_limit_result.tokens_remaining,
            len(request.text),
        )

        if not request.text or len(request.text.strip()) < 10:
            logger.warning("Voice analysis request rejected: text too short for user %s", user_id)
            raise error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="VOICE_TEXT_TOO_SHORT",
                message="Text must be at least 10 characters long"
            )

        # Load existing character profiles from database
        existing_profiles = {}
        try:
            db_service = get_db_service_instance()
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
                logger.info("Loaded %s existing character profiles for user %s", len(existing_profiles), user_id)
            else:
                logger.warning("Database service unavailable; continuing without existing profiles")
        except Exception:
            logger.exception("Could not load existing character profiles; continuing with empty set")
            # Continue with empty profiles - analysis will still work
        
        try:
            # Call the character voice service
            character_service = get_character_voice_service()
            analysis_result = await character_service.analyze(
                request.text, 
                existing_profiles
            )
            
            # Extract results from the analysis result
            results = analysis_result.get("results", [])
            logger.info("Voice analysis produced %s results for user %s", len(results), user_id)
                
        except Exception as analysis_error:
            logger.exception("Voice analysis processing failed for user %s", user_id)
            
            # Return a specific, non-leaky error message
            error_code = "VOICE_ANALYSIS_FAILED"
            error_detail = "Voice analysis failed during processing. Please try again."
            if "timeout" in str(analysis_error).lower():
                error_code = "VOICE_ANALYSIS_TIMEOUT"
                error_detail = "Voice analysis timed out. Please try with shorter text or try again later."
            elif "api" in str(analysis_error).lower():
                error_code = "VOICE_SERVICE_UNAVAILABLE"
                error_detail = "AI service temporarily unavailable. Please try again in a few moments."
            elif "json" in str(analysis_error).lower():
                error_code = "VOICE_ANALYSIS_PARSE_FAILED"
                error_detail = "AI response parsing error. Please try again."
            
            raise error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=error_code,
                message=error_detail
            )
        
        # Update character profiles in database
        updated_count = 0
        try:
            db_service = get_db_service_instance()
            if db_service.is_available() and results:
                for result in results:
                    if result.character_name and result.character_name.strip():
                        try:
                            # Prepare dialogue samples and voice traits
                            dialogue_samples = [result.flagged_text] if result.flagged_text else []
                            voice_traits = {
                                "consistency_score": result.confidence_score,
                                "is_consistent": result.is_consistent,
                                "last_analysis": datetime.now().isoformat(),
                                "analysis_method": result.analysis_method if hasattr(result, 'analysis_method') else "llm_validated",
                                "suggestions": result.suggestions[:3] if result.suggestions else []  # Store top 3 suggestions
                            }
                            
                            # Use upsert to handle both insert and update cases
                            success = await db_service.upsert_character_profile(
                                user_id=user_id,
                                character_name=result.character_name,
                                dialogue_samples=dialogue_samples,
                                voice_traits=voice_traits
                            )
                            
                            if success:
                                updated_count += 1
                            else:
                                logger.warning("Failed to save character profile for '%s'", result.character_name)
                                
                        except Exception as profile_error:
                            logger.warning("Error saving character profile '%s': %s", result.character_name, profile_error)

                logger.info("Saved %s/%s character profiles for user %s", updated_count, len(results), user_id)
            else:
                logger.debug("Skipping character profile persistence; database unavailable or no results")
                
        except Exception:
            logger.exception("Failed to persist character profiles for user %s", user_id)
            # Don't fail the entire request for database issues
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response = VoiceConsistencyResponse(
            results=results,
            characters_analyzed=len(set(r.character_name for r in results if r.character_name)),
            dialogue_segments_found=len(results),
            processing_time_ms=int(processing_time)
        )
        
        logger.info(
            "Voice analysis completed for user %s (characters=%s, segments=%s, results=%s, duration_ms=%s)",
            user_id,
            response.characters_analyzed,
            response.dialogue_segments_found,
            len(response.results),
            response.processing_time_ms,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Voice analysis endpoint failed for user %s", user_id)
        
        # Return user-friendly error (same as successful chat pattern)
        error_code = "VOICE_ANALYSIS_FAILED"
        error_detail = "Voice analysis failed. Please try again."
        if "timeout" in str(e).lower():
            error_code = "VOICE_ANALYSIS_TIMEOUT"
            error_detail = "Voice analysis timed out. Please try with shorter text."
        elif "database" in str(e).lower():
            error_code = "DATABASE_UNAVAILABLE"
            error_detail = "Database connection issue. Analysis results may not be saved."
        
        raise error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=error_code,
            message=error_detail
        )

@router.get("/profiles", response_model=CharacterVoiceProfilesResponse)
async def get_character_profiles(
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all character voice profiles for the current user.
    """
    try:
        logger.info("Fetching character profiles for user %s", user_id)
        
        profiles = []
        profiles_data = []
        db_service = get_db_service_instance()
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
        
        logger.info("Retrieved %s character profiles for user %s", len(profiles), user_id)
        return CharacterVoiceProfilesResponse(
            profiles=profiles,
            total_characters=len(profiles)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character profiles: {str(e)}")
        raise error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="VOICE_PROFILES_FETCH_FAILED",
            message="Failed to retrieve character profiles."
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
        logger.info("Deleting character profile '%s' for user %s", character_name, user_id)
        
        db_service = get_db_service_instance()
        if not db_service.is_available():
            raise error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="DATABASE_UNAVAILABLE",
                message="Database service is temporarily unavailable."
            )

        success = await db_service.delete_character_profile(user_id, character_name)
        if not success:
            raise error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                code="VOICE_PROFILE_NOT_FOUND",
                message=f"Character profile '{character_name}' not found."
            )
        
        logger.info("Deleted character profile '%s' for user %s", character_name, user_id)
        return {"success": True, "message": f"Character profile '{character_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete character profile: {str(e)}")
        raise error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="VOICE_PROFILE_DELETE_FAILED",
            message="Failed to delete character profile."
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
        logger.info("Updating character profile '%s' for user %s", character_name, user_id)
        
        db_service = get_db_service_instance()
        if not db_service.is_available():
            raise error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="DATABASE_UNAVAILABLE",
                message="Database service is temporarily unavailable."
            )

        await db_service.upsert_character_profile(
            user_id=user_id,
            character_name=character_name,
            dialogue_samples=profile_data.get('dialogue_samples', []),
            voice_traits=profile_data.get('voice_traits', {})
        )
        
        logger.info("Updated character profile '%s' for user %s", character_name, user_id)
        return {"success": True, "message": f"Character profile '{character_name}' updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character profile: {str(e)}")
        raise error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="VOICE_PROFILE_UPDATE_FAILED",
            message="Failed to update character profile."
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
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
        
    except Exception as e:
        # Log full exception details server-side without exposing them to the client
        logger.exception(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Internal health check failure",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
