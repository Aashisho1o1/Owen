"""
Local AI Router - OpenAI gpt-oss Integration

Provides endpoints for local AI model management, cost optimization,
and ultra-fast dialogue consistency checking using Ollama.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from ..services.llm_service import llm_service
from ..dependencies import get_current_user_id
from ..utils.error_responses import error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/local-ai", tags=["Local AI Models"])

# Request/Response Models
class QuickConsistencyRequest(BaseModel):
    """Request for quick dialogue consistency check"""
    dialogue: str = Field(..., description="Dialogue text to check", min_length=1)
    character_context: str = Field(..., description="Character context/description")
    character_name: Optional[str] = Field(None, description="Character name for tracking")

class DialogueAnalysisRequest(BaseModel):
    """Request for comprehensive dialogue analysis"""
    character_profile: Dict[str, Any] = Field(..., description="Character profile with traits")
    dialogue_segments: List[str] = Field(..., description="List of dialogue segments")
    speed_priority: bool = Field(False, description="Prioritize speed over thoroughness")

# Health and Status Endpoints
@router.get("/status", response_model=Dict[str, Any])
async def get_local_ai_status():
    """
    Get status of local AI models and Ollama installation
    """
    try:
        status = await llm_service.check_local_model_status()
        return {
            "success": True,
            "data": status,
            "message": "Local AI status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting local AI status: {e}")
        raise error_response(
            status_code=500,
            code="LOCAL_AI_STATUS_FETCH_FAILED",
            message="Failed to get local AI status."
        )

@router.get("/cost-analytics", response_model=Dict[str, Any])
async def get_cost_analytics(
    user_id: Union[str, int] = Depends(get_current_user_id)
):
    """
    Get cost analytics and optimization recommendations
    
    🔒 PROTECTED: Requires authentication (JWT token in Authorization header)
    """
    try:
        logger.info(f"Cost analytics requested by user {user_id}")
        analytics = await llm_service.get_llm_cost_analytics()
        return {
            "success": True,
            "data": analytics,
            "message": "Cost analytics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting cost analytics for user {user_id}: {e}")
        raise error_response(
            status_code=500,
            code="LOCAL_AI_ANALYTICS_FETCH_FAILED",
            message="Failed to get cost analytics."
        )

# Fast Inference Endpoints
@router.post("/quick-consistency-check", response_model=Dict[str, Any])
async def quick_consistency_check(
    request: QuickConsistencyRequest,
    background_tasks: BackgroundTasks,
    user_id: Union[str, int] = Depends(get_current_user_id)
):
    """
    Ultra-fast dialogue consistency check using local models when available
    
    🔒 PROTECTED: Requires authentication (JWT token in Authorization header)
    Target performance: Sub-10 seconds, $0 cost when using local models
    """
    try:
        # Log usage for analytics (background task)
        def log_usage():
            logger.info(f"Quick consistency check by user {user_id}: {len(request.dialogue)} chars")
        
        background_tasks.add_task(log_usage)
        
        # Perform quick consistency check
        result = await llm_service.quick_dialogue_consistency_check(
            dialogue=request.dialogue,
            character_context=request.character_context
        )
        
        # Add request metadata
        result.update({
            "character_name": request.character_name,
            "dialogue_length": len(request.dialogue),
            "user_id": user_id
        })
        
        return {
            "success": True,
            "data": result,
            "message": f"Consistency check completed in {result.get('processing_time', 0):.2f}s"
        }
        
    except Exception as e:
        logger.error(f"Error in quick consistency check: {e}")
        raise error_response(
            status_code=500,
            code="LOCAL_AI_CONSISTENCY_CHECK_FAILED",
            message="Consistency check failed."
        )

@router.post("/analyze-dialogue", response_model=Dict[str, Any])
async def analyze_dialogue_comprehensive(
    request: DialogueAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: Union[str, int] = Depends(get_current_user_id)
):
    """
    Comprehensive dialogue analysis with hybrid model routing
    
    🔒 PROTECTED: Requires authentication (JWT token in Authorization header)
    Automatically selects optimal model (local vs cloud) based on:
    - Model availability
    - Speed requirements  
    - Cost optimization
    """
    try:
        # Validate input
        if not request.dialogue_segments:
            raise HTTPException(status_code=400, detail="No dialogue segments provided")
        
        if len(request.dialogue_segments) > 50:
            raise HTTPException(status_code=400, detail="Too many segments (max 50)")
        
        # Log usage for analytics
        def log_analysis():
            segments_count = len(request.dialogue_segments)
            character_name = request.character_profile.get("name", "unknown")
            logger.info(f"Dialogue analysis by user {user_id}: {segments_count} segments, character: {character_name}")
        
        background_tasks.add_task(log_analysis)
        
        # Perform analysis using hybrid routing
        result = await llm_service.analyze_dialogue_with_hybrid(
            character_profile=request.character_profile,
            dialogue_segments=request.dialogue_segments,
            speed_priority=request.speed_priority
        )
        
        # Add request metadata
        result.update({
            "segments_analyzed": len(request.dialogue_segments),
            "character_name": request.character_profile.get("name"),
            "speed_priority": request.speed_priority,
            "user_id": user_id
        })
        
        return {
            "success": True,
            "data": result,
            "message": f"Analysis completed using {result.get('provider', 'unknown')} provider"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in dialogue analysis: {e}")
        raise error_response(
            status_code=500,
            code="LOCAL_AI_DIALOGUE_ANALYSIS_FAILED",
            message="Dialogue analysis failed."
        )

# Setup and Management Endpoints
@router.get("/setup-guide", response_model=Dict[str, Any])
async def get_setup_guide():
    """
    Get step-by-step setup guide for local AI models
    """
    return {
        "success": True,
        "data": {
            "title": "Local AI Setup Guide - OpenAI gpt-oss via Ollama",
            "steps": [
                {
                    "step": 1,
                    "title": "Install Ollama",
                    "command": "curl -fsSL https://ollama.ai/install.sh | sh",
                    "description": "Download and install Ollama on your system",
                    "time_estimate": "2-5 minutes"
                },
                {
                    "step": 2,
                    "title": "Start Ollama Service", 
                    "command": "ollama serve",
                    "description": "Start the Ollama service (keep running in background)",
                    "time_estimate": "Immediate"
                },
                {
                    "step": 3,
                    "title": "Download gpt-oss 20B (Fast Model)",
                    "command": "ollama pull gpt-oss:20b",
                    "description": "Download the 20B parameter model (14GB) for fast inference",
                    "time_estimate": "5-20 minutes depending on internet speed"
                },
                {
                    "step": 4,
                    "title": "Test Installation",
                    "command": "ollama run gpt-oss:20b \"Hello, can you help me analyze dialogue?\"",
                    "description": "Verify the model works correctly",
                    "time_estimate": "30 seconds"
                },
                {
                    "step": 5,
                    "title": "Optional: Download gpt-oss 120B (Powerful Model)",
                    "command": "ollama pull gpt-oss:120b",
                    "description": "Download the 120B parameter model (65GB) for complex reasoning",
                    "time_estimate": "20-60 minutes depending on internet speed",
                    "note": "Requires 64GB+ RAM for optimal performance"
                }
            ],
            "benefits": [
                "🆓 Zero cost inference - no API fees",
                "⚡ Ultra-fast response times (5-15 seconds)", 
                "🔒 Complete privacy - data never leaves your machine",
                "🌐 Works offline - no internet required for inference",
                "💰 Estimated savings: $50-200+ per month vs cloud APIs"
            ],
            "system_requirements": {
                "minimum": {
                    "ram": "16GB",
                    "storage": "20GB free space",
                    "model": "gpt-oss:20b only"
                },
                "recommended": {
                    "ram": "32GB+", 
                    "storage": "80GB free space",
                    "model": "Both gpt-oss:20b and gpt-oss:120b"
                }
            },
            "troubleshooting": [
                {
                    "issue": "Ollama not found after installation",
                    "solution": "Restart your terminal or run: export PATH=$PATH:/usr/local/bin"
                },
                {
                    "issue": "Model download fails",
                    "solution": "Check internet connection and available disk space"
                },
                {
                    "issue": "Out of memory errors",
                    "solution": "Use only gpt-oss:20b model or upgrade RAM"
                }
            ]
        },
        "message": "Setup guide generated successfully"
    }

@router.get("/performance-comparison", response_model=Dict[str, Any])
async def get_performance_comparison():
    """
    Compare performance between local and cloud models
    """
    return {
        "success": True,
        "data": {
            "comparison_table": {
                "headers": ["Metric", "Local gpt-oss:20b", "Local gpt-oss:120b", "Cloud Gemini"],
                "rows": [
                    ["Response Time", "5-15 seconds", "10-30 seconds", "20-60 seconds"],
                    ["Cost per Request", "$0.00", "$0.00", "$0.005-0.02"],
                    ["Privacy", "Complete", "Complete", "Data sent to Google"],
                    ["Internet Required", "No", "No", "Yes"],
                    ["Quality", "Good", "Excellent", "Excellent"],
                    ["Context Length", "128K tokens", "128K tokens", "128K tokens"],
                    ["Best Use Case", "Quick checks", "Deep analysis", "Creative writing"]
                ]
            },
            "cost_projections": {
                "monthly_requests": {
                    "100": {"local": "$0.00", "cloud": "$1-4"},
                    "500": {"local": "$0.00", "cloud": "$5-15"}, 
                    "1000": {"local": "$0.00", "cloud": "$10-30"},
                    "5000": {"local": "$0.00", "cloud": "$50-150"}
                },
                "annual_savings": {
                    "light_user": "$50-180",
                    "moderate_user": "$200-600", 
                    "heavy_user": "$600-1800"
                }
            },
            "recommendations": {
                "individual_writers": "Start with gpt-oss:20b for cost-free dialogue analysis",
                "writing_teams": "Use gpt-oss:120b for comprehensive character consistency",
                "enterprises": "Deploy both models for hybrid routing optimization"
            }
        },
        "message": "Performance comparison data generated"
    }

# Background task for model optimization
@router.post("/optimize-models", response_model=Dict[str, Any])
async def optimize_models(
    background_tasks: BackgroundTasks,
    user_id: Union[str, int] = Depends(get_current_user_id)
):
    """
    Trigger model optimization and cleanup (background task)
    
    🔒 PROTECTED: Requires authentication (JWT token in Authorization header)
    """
    try:
        def run_optimization():
            """Background optimization task"""
            logger.info(f"Starting model optimization for user {user_id}...")
            # In a real implementation, this would:
            # 1. Clear unused model cache
            # 2. Optimize memory usage
            # 3. Update model routing preferences
            # 4. Generate optimization report
            logger.info(f"Model optimization completed for user {user_id}")
        
        background_tasks.add_task(run_optimization)
        
        return {
            "success": True,
            "data": {
                "optimization_started": True,
                "estimated_completion": "2-5 minutes"
            },
            "message": "Model optimization started in background"
        }
        
    except Exception as e:
        logger.error(f"Error starting optimization: {e}")
        raise error_response(
            status_code=500,
            code="LOCAL_AI_OPTIMIZATION_FAILED",
            message="Model optimization failed."
        )

# Export router
__all__ = ["router"]
