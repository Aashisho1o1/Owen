"""
Character Voice Consistency Router

API endpoints for character voice consistency detection in fiction writing.
Provides real-time analysis, character profile management, and voice consistency feedback.
"""

import time
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from ..dependencies import get_current_user_id
from ..services.character_voice_service import CharacterVoiceService
from ..models.schemas import (
    VoiceConsistencyRequest, VoiceConsistencyResponse, VoiceConsistencyResult,
    CharacterVoiceProfilesResponse, DeleteCharacterProfileRequest
)
from ..services.rate_limiter import SimpleRateLimiter
from ..services.security_logger import SecurityLogger, SecurityEventType, SecuritySeverity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/character-voice", tags=["character-voice"])

# Initialize services
character_voice_service = None  # Will be initialized lazily
rate_limiter = SimpleRateLimiter()
security_logger = SecurityLogger()

def get_character_voice_service():
    """Get character voice service instance with lazy initialization"""
    global character_voice_service
    if character_voice_service is None:
        character_voice_service = CharacterVoiceService()
    return character_voice_service

@router.post("/analyze", response_model=VoiceConsistencyResponse)
async def analyze_voice_consistency(
    request: VoiceConsistencyRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id)
):
    """
    Analyze text for character voice consistency issues
    
    This endpoint analyzes the provided text for dialogue and checks if characters
    speak consistently with their established voice patterns.
    """
    start_time = time.time()
    
    try:
        # Rate limiting
        client_ip = http_request.client.host
        if not rate_limiter.check_rate_limit(http_request, "character_voice_analysis"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Log analysis request
        security_logger.log_security_event(
            SecurityEventType.DOCUMENT_ACCESS,
            SecuritySeverity.LOW,
            user_id=user_id,
            ip_address=client_ip,
            details={
                "action": "voice_consistency_analysis",
                "text_length": len(request.text),
                "document_id": request.document_id
            }
        )
        
        # Perform voice consistency analysis
        results = await get_character_voice_service().analyze_text_for_voice_consistency(
            text=request.text,
            user_id=user_id,
            document_id=request.document_id
        )
        
        # Convert service results to API response format
        api_results = []
        characters_analyzed = set()
        
        for result in results:
            api_result = VoiceConsistencyResult(
                is_consistent=result.is_consistent,
                confidence_score=result.confidence_score,
                similarity_score=result.similarity_score,
                character_name=result.character_name,
                flagged_text=result.flagged_text,
                explanation=result.explanation,
                suggestions=result.suggestions,
                analysis_method=result.analysis_method
            )
            api_results.append(api_result)
            characters_analyzed.add(result.character_name)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Create response
        response = VoiceConsistencyResponse(
            results=api_results,
            characters_analyzed=len(characters_analyzed),
            dialogue_segments_found=len(results),
            processing_time_ms=processing_time
        )
        
        # Log successful analysis
        logger.info(f"Voice consistency analysis completed for user {user_id}: "
                   f"{len(results)} segments, {len(characters_analyzed)} characters, "
                   f"{processing_time}ms")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice consistency analysis: {str(e)}")
        security_logger.log_security_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecuritySeverity.HIGH,
            user_id=user_id,
            ip_address=client_ip,
            details={"error": str(e), "endpoint": "analyze_voice_consistency"}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during voice analysis"
        )

@router.get("/profiles", response_model=CharacterVoiceProfilesResponse)
async def get_character_profiles(
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """
    Get all character voice profiles for the current user
    
    Returns a list of all characters the system has learned voice patterns for,
    along with metadata about each character's voice profile.
    """
    try:
        # Rate limiting
        if not rate_limiter.check_rate_limit(http_request, "character_voice_profiles"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Get character profiles
        profiles_data = await get_character_voice_service().get_character_profiles(user_id)
        
        # Convert to API response format
        profiles = []
        for profile_data in profiles_data:
            profile = CharacterVoiceProfile(
                character_id=profile_data['character_id'],
                character_name=profile_data['character_name'],
                sample_count=profile_data['sample_count'],
                last_updated=profile_data['last_updated'],
                voice_characteristics=profile_data['voice_characteristics']
            )
            profiles.append(profile)
        
        response = CharacterVoiceProfilesResponse(
            profiles=profiles,
            total_characters=len(profiles)
        )
        
        logger.info(f"Retrieved {len(profiles)} character profiles for user {user_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving character profiles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving character profiles"
        )

@router.delete("/profiles/{character_name}")
async def delete_character_profile(
    character_name: str,
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """
    Delete a character voice profile
    
    Removes all stored voice data for the specified character.
    This action cannot be undone.
    """
    try:
        # Rate limiting
        if not rate_limiter.check_rate_limit(http_request, "character_voice_delete"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Validate character name
        if not character_name or not character_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Character name cannot be empty"
            )
        
        # Delete character profile
        success = await get_character_voice_service().delete_character_profile(
            user_id=user_id,
            character_name=character_name.strip()
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Character profile '{character_name}' not found"
            )
        
        # Log deletion
        security_logger.log_security_event(
            SecurityEventType.DOCUMENT_DELETE,
            SecuritySeverity.MEDIUM,
            user_id=user_id,
            ip_address=http_request.client.host,
            details={
                "action": "character_profile_deleted",
                "character_name": character_name
            }
        )
        
        logger.info(f"Character profile '{character_name}' deleted for user {user_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Character profile '{character_name}' deleted successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting character profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error deleting character profile"
        )

@router.post("/profiles/reset")
async def reset_all_character_profiles(
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """
    Reset all character voice profiles for the current user
    
    WARNING: This will delete all learned character voice patterns.
    This action cannot be undone.
    """
    try:
        # Rate limiting with stricter limits for destructive operations
        if not rate_limiter.check_rate_limit(http_request, "character_voice_reset"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Get all profiles first
        profiles_data = await get_character_voice_service().get_character_profiles(user_id)
        
        # Delete each profile
        deleted_count = 0
        for profile_data in profiles_data:
            success = await get_character_voice_service().delete_character_profile(
                user_id=user_id,
                character_name=profile_data['character_name']
            )
            if success:
                deleted_count += 1
        
        # Log reset operation
        security_logger.log_security_event(
            SecurityEventType.DOCUMENT_DELETE,
            SecuritySeverity.HIGH,
            user_id=user_id,
            ip_address=http_request.client.host,
            details={
                "action": "all_character_profiles_reset",
                "profiles_deleted": deleted_count
            }
        )
        
        logger.warning(f"All character profiles reset for user {user_id}: {deleted_count} profiles deleted")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"All character profiles reset successfully. {deleted_count} profiles deleted.",
                "profiles_deleted": deleted_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting character profiles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error resetting character profiles"
        )

@router.get("/health")
async def character_voice_health():
    """
    Health check for character voice consistency service
    
    Returns the current status of the voice analysis system including
    database connectivity, AI model availability, and service configuration.
    """
    try:
        health_status = await get_character_voice_service().get_service_health()
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "service": "character_voice_consistency",
                "status": health_status['status'],
                "timestamp": time.time(),
                "details": health_status
            }
        )
        
    except Exception as e:
        logger.error(f"Error checking character voice service health: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "character_voice_consistency",
                "status": "error",
                "timestamp": time.time(),
                "message": "An internal error occurred while checking service health."
            }
        )

@router.get("/stats")
async def get_voice_analysis_stats(
    http_request: Request,
    user_id: int = Depends(get_current_user_id)
):
    """
    Get statistics about voice analysis for the current user
    
    Returns information about character profiles, analysis history,
    and system performance metrics.
    """
    try:
        # Rate limiting
        if not rate_limiter.check_rate_limit(http_request, "character_voice_stats"):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Get character profiles
        profiles_data = await get_character_voice_service().get_character_profiles(user_id)
        
        # Calculate statistics
        total_characters = len(profiles_data)
        total_samples = sum(profile['sample_count'] for profile in profiles_data)
        
        # Get service health for additional stats
        health_status = await get_character_voice_service().get_service_health()
        
        stats = {
            "user_id": user_id,
            "total_characters": total_characters,
            "total_dialogue_samples": total_samples,
            "average_samples_per_character": total_samples / total_characters if total_characters > 0 else 0,
            "service_status": health_status['status'],
            "cache_size": health_status.get('cache_size', 0),
            "analysis_config": health_status.get('config', {}),
            "characters": [
                {
                    "name": profile['character_name'],
                    "sample_count": profile['sample_count'],
                    "last_updated": profile['last_updated']
                }
                for profile in profiles_data
            ]
        }
        
        return JSONResponse(
            status_code=200,
            content=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice analysis stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving statistics"
        ) 