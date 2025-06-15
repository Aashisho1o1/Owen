"""
Analytics API Routes for DOG Writer
GDPR-compliant analytics endpoints with user consent management
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from ..services.analytics_service import analytics_service
from ..services.writing_analytics_service import writing_analytics_service
from ..services.auth_service import verify_token
from ..config.analytics_config import PrivacyLevel

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
security = HTTPBearer()

# Request/Response Models
class ConsentRequest(BaseModel):
    essential: bool = True
    analytics: bool = False
    comprehensive: bool = False

class ConsentResponse(BaseModel):
    user_id: str
    essential: bool
    analytics: bool
    comprehensive: bool
    updated_at: str

class WritingInsightsResponse(BaseModel):
    user_id: str
    writing_summary: Dict[str, Any]
    strengths: List[str]
    improvement_areas: List[str]
    recommendations: List[str]
    writing_style_summary: str

class AnalyticsSummaryResponse(BaseModel):
    user_id: str
    total_writing_sessions: int
    total_words_written: int
    average_typing_speed: float
    most_active_hours: List[int]
    writing_streak_days: int
    consent_status: Dict[str, Any]

class EventTrackingRequest(BaseModel):
    event_name: str
    properties: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None

class WritingSessionRequest(BaseModel):
    document_id: str
    content_before: str
    content_after: str
    session_duration_minutes: float

# Helper Functions
def get_current_user_id(token: str = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    try:
        payload = verify_token(token.credentials)
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# Consent Management Endpoints

@router.post("/consent", response_model=ConsentResponse)
async def set_user_consent(
    consent: ConsentRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Set user consent preferences for analytics tracking
    
    This endpoint allows users to control what level of analytics data
    is collected about their usage, ensuring GDPR compliance.
    """
    try:
        analytics_service.set_user_consent(
            user_id=user_id,
            essential=consent.essential,
            analytics=consent.analytics,
            comprehensive=consent.comprehensive
        )
        
        return ConsentResponse(
            user_id=user_id,
            essential=consent.essential,
            analytics=consent.analytics,
            comprehensive=consent.comprehensive,
            updated_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update consent: {str(e)}")

@router.get("/consent", response_model=ConsentResponse)
async def get_user_consent(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user consent preferences"""
    try:
        consent_data = analytics_service.user_consents.get(user_id, {
            "essential": True,
            "analytics": False,
            "comprehensive": False,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return ConsentResponse(
            user_id=user_id,
            essential=consent_data.get("essential", True),
            analytics=consent_data.get("analytics", False),
            comprehensive=consent_data.get("comprehensive", False),
            updated_at=consent_data.get("updated_at", datetime.utcnow().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get consent: {str(e)}")

# Writing Analytics Endpoints

@router.get("/writing/insights", response_model=WritingInsightsResponse)
async def get_writing_insights(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive writing insights and recommendations
    
    Provides personalized feedback on writing style, productivity,
    and areas for improvement based on user's writing history.
    """
    try:
        insights = writing_analytics_service.get_user_writing_insights(user_id)
        
        return WritingInsightsResponse(
            user_id=insights["user_id"],
            writing_summary=insights.get("writing_summary", {}),
            strengths=insights.get("strengths", []),
            improvement_areas=insights.get("improvement_areas", []),
            recommendations=insights.get("recommendations", []),
            writing_style_summary=insights.get("writing_style_summary", "")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get writing insights: {str(e)}")

@router.post("/writing/session")
async def track_writing_session(
    session_data: WritingSessionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Track a writing session for analytics
    
    Records writing activity including productivity metrics,
    style analysis, and content changes for personalized insights.
    """
    try:
        # Generate session ID
        session_id = f"session_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        # Track the writing session
        session_analysis = writing_analytics_service.track_writing_session(
            user_id=user_id,
            document_id=session_data.document_id,
            session_id=session_id,
            content_before=session_data.content_before,
            content_after=session_data.content_after,
            session_duration_minutes=session_data.session_duration_minutes
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "analysis": session_analysis,
            "message": "Writing session tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track writing session: {str(e)}")

@router.get("/writing/style-analysis")
async def analyze_writing_style(
    text: str = Query(..., description="Text content to analyze"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyze writing style of provided text
    
    Returns detailed analysis including readability, sentiment,
    complexity, and voice characteristics.
    """
    try:
        if len(text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Text must be at least 50 characters long")
        
        style_metrics = writing_analytics_service.analyze_writing_style(text)
        
        return {
            "analysis": {
                "readability_score": style_metrics.readability_score,
                "flesch_kincaid_grade": style_metrics.flesch_kincaid_grade,
                "avg_sentence_length": style_metrics.avg_sentence_length,
                "avg_word_length": style_metrics.avg_word_length,
                "vocabulary_diversity": style_metrics.vocabulary_diversity,
                "passive_voice_ratio": style_metrics.passive_voice_ratio,
                "sentiment_polarity": style_metrics.sentiment_polarity,
                "sentiment_subjectivity": style_metrics.sentiment_subjectivity,
                "complexity_score": style_metrics.complexity_score,
                "tone_analysis": style_metrics.tone_analysis,
                "writing_voice_indicators": style_metrics.writing_voice_indicators
            },
            "interpretation": {
                "readability": "Easy" if style_metrics.readability_score > 70 else "Moderate" if style_metrics.readability_score > 50 else "Difficult",
                "sentiment": "Positive" if style_metrics.sentiment_polarity > 0.1 else "Negative" if style_metrics.sentiment_polarity < -0.1 else "Neutral",
                "complexity": "High" if style_metrics.complexity_score > 12 else "Medium" if style_metrics.complexity_score > 8 else "Low"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze writing style: {str(e)}")

# General Analytics Endpoints

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    user_id: str = Depends(get_current_user_id)
):
    """Get comprehensive analytics summary for user"""
    try:
        summary = analytics_service.get_user_analytics_summary(user_id)
        
        return AnalyticsSummaryResponse(
            user_id=summary["user_id"],
            total_writing_sessions=summary.get("total_writing_sessions", 0),
            total_words_written=summary.get("total_words_written", 0),
            average_typing_speed=summary.get("average_typing_speed", 0.0),
            most_active_hours=summary.get("most_active_hours", []),
            writing_streak_days=summary.get("writing_streak_days", 0),
            consent_status=summary.get("consent_status", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")

@router.post("/track-event")
async def track_custom_event(
    event_data: EventTrackingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Track a custom analytics event
    
    Allows frontend to track specific user interactions
    that aren't automatically captured by middleware.
    """
    try:
        analytics_service.track_event(
            event_name=event_data.event_name,
            user_id=user_id,
            properties=event_data.properties,
            session_id=event_data.session_id
        )
        
        return {
            "success": True,
            "message": f"Event '{event_data.event_name}' tracked successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

# GDPR Compliance Endpoints

@router.get("/export-data")
async def export_user_data(
    user_id: str = Depends(get_current_user_id)
):
    """
    Export all analytics data for user (GDPR compliance)
    
    Returns all collected analytics data for the user
    in a structured format for data portability.
    """
    try:
        user_data = analytics_service.export_user_data(user_id)
        
        return {
            "export_data": user_data,
            "export_timestamp": datetime.utcnow().isoformat(),
            "format_version": "1.0"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")

@router.delete("/delete-data")
async def delete_user_data(
    user_id: str = Depends(get_current_user_id),
    confirm: bool = Query(False, description="Confirmation flag for data deletion")
):
    """
    Delete all analytics data for user (GDPR compliance)
    
    Permanently removes all analytics data associated with the user.
    This action cannot be undone.
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Data deletion requires explicit confirmation. Set confirm=true"
        )
    
    try:
        success = analytics_service.delete_user_data(user_id)
        
        if success:
            return {
                "success": True,
                "message": "All analytics data has been permanently deleted",
                "deleted_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user data")
            
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")

# Dashboard and Reporting Endpoints

@router.get("/dashboard")
async def get_analytics_dashboard(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in dashboard")
):
    """
    Get analytics dashboard data
    
    Returns comprehensive analytics data for dashboard visualization
    including writing patterns, productivity trends, and insights.
    """
    try:
        # Get writing insights
        writing_insights = writing_analytics_service.get_user_writing_insights(user_id)
        
        # Get analytics summary
        analytics_summary = analytics_service.get_user_analytics_summary(user_id)
        
        # Combine data for dashboard
        dashboard_data = {
            "user_id": user_id,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            
            # Writing metrics
            "writing_metrics": {
                "total_sessions": writing_insights.get("writing_summary", {}).get("total_sessions", 0),
                "average_typing_speed": writing_insights.get("writing_summary", {}).get("average_typing_speed", 0),
                "average_readability": writing_insights.get("writing_summary", {}).get("average_readability", 0),
                "average_complexity": writing_insights.get("writing_summary", {}).get("average_complexity", 0)
            },
            
            # Insights and recommendations
            "insights": {
                "strengths": writing_insights.get("strengths", []),
                "improvement_areas": writing_insights.get("improvement_areas", []),
                "recommendations": writing_insights.get("recommendations", []),
                "style_summary": writing_insights.get("writing_style_summary", "")
            },
            
            # Analytics summary
            "analytics": {
                "total_words_written": analytics_summary.get("total_words_written", 0),
                "writing_streak_days": analytics_summary.get("writing_streak_days", 0),
                "most_active_hours": analytics_summary.get("most_active_hours", [])
            },
            
            # Privacy status
            "privacy": {
                "consent_status": analytics_summary.get("consent_status", {}),
                "data_retention_days": 365,
                "anonymization_enabled": True
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.get("/privacy-info")
async def get_privacy_info():
    """
    Get information about analytics privacy practices
    
    Returns details about data collection, processing,
    and privacy protection measures.
    """
    return {
        "privacy_policy": {
            "data_collection": {
                "essential": "Basic functionality and error tracking",
                "analytics": "Usage patterns and feature popularity",
                "comprehensive": "Detailed writing analysis and personalization"
            },
            "data_processing": {
                "anonymization": "IP addresses and sensitive data are anonymized",
                "encryption": "All data is encrypted in transit and at rest",
                "retention": "Data is retained for 365 days unless deleted earlier"
            },
            "user_rights": {
                "consent": "Users can control what data is collected",
                "access": "Users can export all their data",
                "deletion": "Users can delete all their data permanently",
                "portability": "Data is provided in structured format"
            },
            "compliance": {
                "gdpr": "Fully compliant with GDPR requirements",
                "ccpa": "Compliant with California Consumer Privacy Act",
                "security": "SOC 2 Type II security standards"
            }
        },
        "contact": {
            "privacy_officer": "privacy@dogwriter.com",
            "data_protection": "dpo@dogwriter.com"
        }
    } 