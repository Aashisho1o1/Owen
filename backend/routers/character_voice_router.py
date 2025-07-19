"""
Character Voice Consistency Router

API endpoints for character voice consistency detection in fiction writing.
Provides real-time analysis, character profile management, and voice consistency feedback.
"""

import time
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

# CRITICAL FIX: Make dependencies import resilient to database failures
try:
    from dependencies import get_current_user_id
    DEPENDENCIES_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Dependencies import failed: {e}")
    print("🔧 Character voice router will use fallback authentication")
    DEPENDENCIES_AVAILABLE = False
    
    # Fallback dependency function
    def get_current_user_id():
        """Fallback authentication dependency"""
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authentication service unavailable")

# CRITICAL FIX: Make CharacterVoiceService import resilient to database failures
try:
    from services.character_voice_service import SimpleCharacterVoiceService as CharacterVoiceService
    CHARACTER_VOICE_SERVICE_AVAILABLE = True
    print("✅ SimpleCharacterVoiceService imported successfully")
except Exception as e:
    print(f"⚠️ SimpleCharacterVoiceService import failed: {e}")
    print("🔧 Character voice router will use fallback service")
    CHARACTER_VOICE_SERVICE_AVAILABLE = False
    
    # Fallback CharacterVoiceService
    class CharacterVoiceService:
        def __init__(self):
            pass
        
        async def analyze_text_for_voice_consistency(self, *args, **kwargs):
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Voice analysis service unavailable - database connection required")
from models.schemas import (
    VoiceConsistencyRequest, VoiceConsistencyResponse, VoiceConsistencyResult,
    CharacterVoiceProfilesResponse, CharacterVoiceProfile, DeleteCharacterProfileRequest
)
from services.rate_limiter import SimpleRateLimiter
from services.security_logger import SecurityLogger, SecurityEventType, SecuritySeverity

logger = logging.getLogger(__name__)

print("✅ Character voice router module loaded successfully!")
print(f"🔧 Service availability: Dependencies={DEPENDENCIES_AVAILABLE}, CharacterVoice={CHARACTER_VOICE_SERVICE_AVAILABLE}")

router = APIRouter(prefix="/api/character-voice", tags=["character-voice"])
print(f"✅ Character voice router created with prefix: {router.prefix}")

# Initialize services
character_voice_service = None  # Will be initialized lazily
rate_limiter = SimpleRateLimiter()
security_logger = SecurityLogger()

def get_character_voice_service():
    """Get character voice service instance with lazy initialization"""
    global character_voice_service
    if character_voice_service is None:
        try:
            print("🔧 Initializing CharacterVoiceService...")
            character_voice_service = CharacterVoiceService()
            print("✅ CharacterVoiceService initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize CharacterVoiceService: {e}")
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
            raise Exception(f"Character voice service initialization failed: {e}")
    return character_voice_service

@router.post("/analyze", response_model=VoiceConsistencyResponse)
async def analyze_voice_consistency(
    request: VoiceConsistencyRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id)  # Require authentication
):
    """
    Analyze text for character voice consistency issues
    
    This endpoint analyzes the provided text for dialogue and checks if characters
    speak consistently with their established voice patterns.
    
    Requires user authentication to maintain character profiles.
    """
    start_time = time.time()
    client_ip = http_request.client.host
    effective_user_id = user_id
    
    # ENHANCED: Add detailed logging at every step
    logger.info(f"🎭 === VOICE ANALYSIS REQUEST START ===")
    logger.info(f"👤 User ID: {effective_user_id}")
    logger.info(f"🌐 Client IP: {client_ip}")
    logger.info(f"📝 Text length: {len(request.text)} characters")
    logger.info(f"📄 Document ID: {request.document_id}")
    logger.info(f"📝 Text preview: {request.text[:200]}...")
    
    try:
        # STEP 1: Rate limiting
        logger.info(f"🚦 STEP 1: Checking rate limits...")
        if not rate_limiter.check_rate_limit(http_request, "character_voice_analysis"):
            logger.warning(f"❌ Rate limit exceeded for user {effective_user_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        logger.info(f"✅ STEP 1: Rate limit check passed")
        
        # STEP 2: Security logging
        logger.info(f"🔒 STEP 2: Logging security event...")
        security_logger.log_security_event(
            SecurityEventType.DOCUMENT_ACCESS,
            SecuritySeverity.LOW,
            user_id=effective_user_id,
            ip_address=client_ip,
            details={
                "action": "voice_consistency_analysis",
                "text_length": len(request.text),
                "document_id": request.document_id
            }
        )
        logger.info(f"✅ STEP 2: Security event logged")
        
        # STEP 3: Get service instance
        logger.info(f"🔧 STEP 3: Getting character voice service instance...")
        try:
            service = get_character_voice_service()
            logger.info(f"✅ STEP 3: Service instance obtained successfully")
        except Exception as e:
            logger.error(f"❌ STEP 3: Failed to get service instance: {str(e)}")
            logger.exception("Service initialization error:")
            raise HTTPException(
                status_code=503,
                detail=f"Voice analysis service unavailable: {str(e)}"
            )
        
        # STEP 4: Call service method
        logger.info(f"🔍 STEP 4: Calling voice consistency analysis...")
        logger.info(f"🔍 Calling: service.analyze_text_for_voice_consistency(text={len(request.text)}chars, user_id={effective_user_id}, document_id={request.document_id})")
        
        try:
            results = await service.analyze_text_for_voice_consistency(
                text=request.text,
                user_id=effective_user_id,
                document_id=request.document_id
            )
            logger.info(f"✅ STEP 4: Service call completed successfully")
            logger.info(f"📊 Service returned {len(results)} results")
        except Exception as e:
            logger.error(f"❌ STEP 4: Service call failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.exception("Service method error:")
            raise HTTPException(
                status_code=500,
                detail=f"Voice analysis failed: {str(e)}"
            )
        
        # STEP 5: Convert results
        logger.info(f"🔄 STEP 5: Converting service results to API format...")
        api_results = []
        characters_analyzed = set()
        
        for i, result in enumerate(results):
            logger.info(f"🔄 Converting result {i+1}: {result.character_name} - {'Consistent' if result.is_consistent else 'Inconsistent'}")
            
            try:
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
                logger.info(f"✅ Result {i+1} converted successfully")
            except Exception as e:
                logger.error(f"❌ Failed to convert result {i+1}: {str(e)}")
                logger.exception("Result conversion error:")
                # Continue with other results instead of failing
                continue
        
        logger.info(f"✅ STEP 5: Result conversion completed")
        
        # STEP 6: Create response
        logger.info(f"📦 STEP 6: Creating API response...")
        processing_time = int((time.time() - start_time) * 1000)
        
        try:
            response = VoiceConsistencyResponse(
                results=api_results,
                characters_analyzed=len(characters_analyzed),
                dialogue_segments_found=len(results),
                processing_time_ms=processing_time
            )
            logger.info(f"✅ STEP 6: Response created successfully")
        except Exception as e:
            logger.error(f"❌ STEP 6: Failed to create response: {str(e)}")
            logger.exception("Response creation error:")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create response: {str(e)}"
            )
        
        # STEP 7: Final logging and return
        logger.info(f"📤 STEP 7: Sending response...")
        logger.info(f"📤 Response details: {len(api_results)} results, {len(characters_analyzed)} characters, {processing_time}ms")
        logger.info(f"🎭 === VOICE ANALYSIS REQUEST COMPLETE ===")
        
        return response
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions without modification
        logger.error(f"❌ HTTP Exception: {http_exc.status_code} - {http_exc.detail}")
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"❌ === UNEXPECTED ERROR IN VOICE ANALYSIS ===")
        logger.error(f"❌ Error: {str(e)}")
        logger.error(f"❌ Error Type: {type(e).__name__}")
        logger.error(f"❌ Error Module: {getattr(type(e), '__module__', 'unknown')}")
        
        # Log full traceback
        import traceback
        full_traceback = traceback.format_exc()
        logger.error(f"❌ Full Traceback:\n{full_traceback}")
        
        # Log context information
        logger.error(f"❌ Context: user_id={effective_user_id}, text_length={len(request.text) if request else 'unknown'}")
        
        # Log to security system
        try:
            security_logger.log_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY,
                SecuritySeverity.HIGH,
                user_id=effective_user_id,
                ip_address=client_ip,
                details={
                    "error": str(e), 
                    "error_type": type(e).__name__,
                    "endpoint": "analyze_voice_consistency",
                    "text_length": len(request.text) if request else 0,
                    "traceback": full_traceback
                }
            )
        except Exception as security_log_error:
            logger.error(f"❌ Failed to log security event: {security_log_error}")
        
        # Return generic error to client
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
        logger.error(f"❌ Error checking character voice service health: {str(e)}")
        logger.error(f"❌ Error Type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Health Check Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=503,
            content={
                "service": "character_voice_consistency",
                "status": "error",
                "timestamp": time.time(),
                "message": f"Service health check failed: {str(e)}",
                "error_type": type(e).__name__,
                "debug_info": traceback.format_exc() if logger.level <= 10 else None  # Only in debug mode
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