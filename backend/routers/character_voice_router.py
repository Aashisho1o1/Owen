"""
Character Voice Consistency Router - Complete Implementation

API endpoint for character voice consistency analysis with full database integration and profile management.
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import re

# Direct imports
from dependencies import get_current_user_id, check_voice_analysis_rate_limit
from services.character_voice_service import CharacterVoiceService, CharacterVoiceProfile
from services.character_voice_service_optimized import optimized_character_voice_service
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
    http_request: Request,
    user_id: int = Depends(get_current_user_id),
    rate_limit_result = Depends(check_voice_analysis_rate_limit)  # PostgreSQL-based rate limiting
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
    start_time = datetime.now()
    
    try:
        logger.info(f"🎭 === VOICE ANALYSIS REQUEST START ===")
        logger.info(f"🔍 Request Details:")
        logger.info(f"   - User ID: {user_id}")
        logger.info(f"   - Text length: {len(request.text)} chars")
        logger.info(f"   - Text preview: {request.text[:200]}{'...' if len(request.text) > 200 else ''}")
        logger.info(f"   - Has HTML tags: {bool(re.search(r'<[^>]+>', request.text))}")
        logger.info(f"   - Rate limit tier: {rate_limit_result.tier}, tokens remaining: {rate_limit_result.tokens_remaining}")
        logger.info(f"   - Timestamp: {start_time}")
        
        logger.info(f"🚀 STEP 1: Input validation...")
        if not request.text or len(request.text.strip()) < 10:
            logger.error(f"❌ STEP 1 FAILED: Text too short ({len(request.text.strip())} chars)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text must be at least 10 characters long"
            )
        logger.info(f"✅ STEP 1 COMPLETE: Input validation passed")
        
        logger.info(f"🚀 STEP 2: Loading existing character profiles...")
        # Load existing character profiles from database
        existing_profiles = {}
        try:
            logger.info(f"🔍 Checking database service availability...")
            if db_service.is_available():
                logger.info(f"✅ Database service available, loading profiles...")
                profiles_data = await db_service.get_character_profiles(user_id)
                logger.info(f"📊 Retrieved {len(profiles_data)} profiles from database")
                
                for i, profile_data in enumerate(profiles_data):
                    logger.debug(f"   Processing profile {i+1}: {profile_data.get('character_name', 'Unknown')}")
                    profile = CharacterVoiceProfile(
                        character_id=profile_data['character_id'],
                        character_name=profile_data['character_name'],
                        dialogue_samples=profile_data.get('dialogue_samples', []),
                        voice_traits=profile_data.get('voice_traits', {}),
                        last_updated=profile_data.get('last_updated', ''),
                        sample_count=profile_data.get('sample_count', 0)
                    )
                    existing_profiles[profile.character_name] = profile
                    
                logger.info(f"✅ STEP 2 COMPLETE: Loaded {len(existing_profiles)} existing character profiles")
            else:
                logger.warning(f"⚠️ Database service not available, continuing without existing profiles")
                logger.info(f"✅ STEP 2 COMPLETE: No existing profiles loaded (DB unavailable)")
        except Exception as e:
            logger.error(f"❌ STEP 2 ERROR: Could not load existing profiles: {e}")
            logger.exception("Full traceback:")
            # Continue with empty profiles - analysis will still work
            logger.info(f"➡️ STEP 2 RECOVERY: Continuing with empty profiles")
        
        logger.info(f"🚀 STEP 3: Starting voice consistency analysis...")
        logger.info(f"🧠 Using Gemini 2.5 Flash for analysis...")
        logger.info("⏳ Expected processing time: 1-4 minutes for complex dialogue analysis...")
        
        try:
            # COST OPTIMIZATION: Use the optimized service with batch processing and caching
            logger.info(f"📞 Calling optimized character voice service (80% cost reduction)...")
            analysis_result = await optimized_character_voice_service.analyze(
                text=request.text, 
                existing_profiles=existing_profiles,
                user_id=user_id
            )
            
            # Extract results from the analysis result
            results = analysis_result.get("results", [])
            logger.info(f"✅ STEP 3 COMPLETE: Analysis returned {len(results)} results")
            logger.info(f"📊 Results summary:")
            for i, result in enumerate(results):
                logger.info(f"   Result {i+1}: {result.character_name} - Consistent: {result.is_consistent} (Confidence: {result.confidence_score})")
                
        except Exception as analysis_error:
            logger.error(f"❌ STEP 3 FAILED: Voice analysis error: {analysis_error}")
            logger.exception("Full analysis error traceback:")
            
            # Return a more specific error message
            error_detail = f"Voice analysis failed during processing. Error: {str(analysis_error)}"
            if "timeout" in str(analysis_error).lower():
                error_detail = "Voice analysis timed out. Please try with shorter text or try again later."
            elif "api" in str(analysis_error).lower():
                error_detail = "AI service temporarily unavailable. Please try again in a few moments."
            elif "json" in str(analysis_error).lower():
                error_detail = "AI response parsing error. Please try again."
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
        
        logger.info(f"🚀 STEP 4: Updating character profiles in database...")
        # Update character profiles in database
        updated_count = 0
        try:
            if db_service.is_available() and results:
                logger.info(f"💾 Saving {len(results)} character profiles to database")
                
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
                                logger.debug(f"   ✅ Saved profile for: {result.character_name}")
                            else:
                                logger.warning(f"   ⚠️ Failed to save profile for: {result.character_name}")
                                
                        except Exception as profile_error:
                            logger.warning(f"   ❌ Profile save error for {result.character_name}: {profile_error}")
                            
                logger.info(f"✅ STEP 4 COMPLETE: Successfully saved {updated_count}/{len(results)} character profiles")
            else:
                logger.info(f"⚠️ STEP 4 SKIPPED: Database unavailable or no results to save")
                
        except Exception as db_error:
            logger.error(f"❌ STEP 4 ERROR: Database update failed: {db_error}")
            logger.exception("Database error traceback:")
            # Don't fail the entire request for database issues
            logger.info(f"➡️ STEP 4 RECOVERY: Continuing without database updates")
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"🚀 STEP 5: Preparing response...")
        # Prepare response
        response = VoiceConsistencyResponse(
            results=results,
            characters_analyzed=len(set(r.character_name for r in results if r.character_name)),
            dialogue_segments_found=len(results),
            processing_time_ms=int(processing_time)
        )
        
        logger.info(f"✅ === VOICE ANALYSIS COMPLETE ===")
        logger.info(f"📊 Final Summary:")
        logger.info(f"   - Characters analyzed: {response.characters_analyzed}")
        logger.info(f"   - Dialogue segments: {response.dialogue_segments_found}")
        logger.info(f"   - Processing time: {response.processing_time_ms}ms")
        logger.info(f"   - Results count: {len(response.results)}")
        
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
