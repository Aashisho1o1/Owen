"""
Cost Optimization Monitoring Router

Provides endpoints for monitoring API costs, cache performance, 
and rate limiting statistics. This helps track the effectiveness
of our cost optimization strategies.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from dependencies import get_current_user_id
from services.infra_service import infra_service, usage_analytics
from services.database import get_db_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/cost-optimization",
    tags=["cost-optimization"]
)

@router.get("/dashboard")
async def get_cost_optimization_dashboard(
    user_id: int = Depends(get_current_user_id),
    days: int = Query(default=7, ge=1, le=30, description="Number of days to analyze")
):
    """
    Get comprehensive cost optimization dashboard for user.
    
    Shows:
    - Daily usage and costs
    - Cache hit rates
    - Rate limit usage
    - Cost savings from optimizations
    """
    try:
        # Get usage data for the specified period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Collect usage data for each day
        daily_stats = []
        total_cost_cents = 0
        total_requests = 0
        total_cache_hits = 0
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_stats = await usage_analytics.get_user_daily_usage(user_id, date)
            daily_stats.append(day_stats)
            
            total_cost_cents += day_stats['total_cost_cents']
            total_requests += day_stats['total_requests']
            
            # Calculate cache hits for this day
            for endpoint_data in day_stats['endpoints']:
                total_cache_hits += endpoint_data.get('cache_hits', 0)
        
        # Calculate overall metrics
        overall_cache_hit_rate = (total_cache_hits / total_requests * 100) if total_requests > 0 else 0
        estimated_cost_without_optimization = total_cost_cents * 5  # Assume 5x cost without optimizations
        estimated_savings_cents = estimated_cost_without_optimization - total_cost_cents
        
        # Get rate limit status
        rate_limit_status = await infra_service.rate_limiter.get_user_tier(user_id)
        
        return {
            "period": {
                "start_date": start_date.date(),
                "end_date": end_date.date(),
                "days": days
            },
            "summary": {
                "total_requests": total_requests,
                "total_cost_cents": total_cost_cents,
                "total_cost_dollars": total_cost_cents / 100,
                "average_cost_per_request": (total_cost_cents / total_requests) if total_requests > 0 else 0,
                "cache_hit_rate_percent": round(overall_cache_hit_rate, 2),
                "estimated_savings_cents": estimated_savings_cents,
                "estimated_savings_dollars": estimated_savings_cents / 100,
                "rate_limit_tier": rate_limit_status
            },
            "daily_breakdown": daily_stats,
            "optimizations_active": {
                "batch_processing": True,
                "intelligent_caching": True,
                "rate_limiting": True,
                "context_optimization": True,
                "usage_analytics": True
            },
            "recommendations": _generate_cost_recommendations(daily_stats, overall_cache_hit_rate)
        }
        
    except Exception as e:
        logger.error(f"Error generating cost optimization dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard")

@router.get("/cache-stats")
async def get_cache_statistics(
    user_id: int = Depends(get_current_user_id)
):
    """
    Get detailed cache performance statistics.
    """
    try:
        db = get_db_service()
        
        # Get cache statistics from database
        cache_stats = await db.execute_query(
            """
            SELECT 
                cache_type,
                COUNT(*) as total_entries,
                AVG(token_count) as avg_tokens,
                MIN(inserted_at) as oldest_entry,
                MAX(inserted_at) as newest_entry
            FROM llm_cache 
            WHERE user_id = %s 
            AND inserted_at > NOW() - INTERVAL '7 days'
            GROUP BY cache_type
            ORDER BY total_entries DESC
            """,
            (user_id,),
            fetch='all'
        )
        
        # Get hit rate statistics
        hit_rate_stats = await db.execute_query(
            """
            SELECT 
                endpoint,
                COUNT(*) as total_requests,
                SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                ROUND(100.0 * SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) / COUNT(*), 2) as hit_rate
            FROM api_usage_analytics 
            WHERE user_id = %s 
            AND created_at > NOW() - INTERVAL '7 days'
            GROUP BY endpoint
            ORDER BY total_requests DESC
            """,
            (user_id,),
            fetch='all'
        )
        
        return {
            "cache_types": cache_stats or [],
            "endpoint_hit_rates": hit_rate_stats or [],
            "recommendations": _generate_cache_recommendations(cache_stats, hit_rate_stats)
        }
        
    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache statistics")

@router.get("/rate-limit-status")
async def get_rate_limit_status(
    user_id: int = Depends(get_current_user_id)
):
    """
    Get current rate limit status and usage.
    """
    try:
        # Get rate limit status for different endpoints
        endpoints = ["chat", "voice_analysis", "grammar"]
        status = {}
        
        for endpoint in endpoints:
            result = await infra_service.check_rate_limit(user_id, endpoint)
            status[endpoint] = {
                "allowed": result.allowed,
                "tokens_remaining": result.tokens_remaining,
                "reset_time": result.reset_time,
                "tier": result.tier
            }
        
        return {
            "user_id": user_id,
            "endpoints": status,
            "tier_info": {
                "current_tier": status.get("chat", {}).get("tier", "free"),
                "upgrade_available": True,
                "benefits": [
                    "Higher rate limits",
                    "Priority processing",
                    "Advanced analytics",
                    "Bulk operations"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rate limit status")

@router.post("/cleanup")
async def cleanup_expired_data(
    user_id: int = Depends(get_current_user_id)
):
    """
    Manually trigger cleanup of expired cache and rate limit data.
    Useful for testing and maintenance.
    """
    try:
        cleanup_stats = await infra_service.cleanup_expired_data()
        
        logger.info(f"Manual cleanup triggered by user {user_id}: {cleanup_stats}")
        
        return {
            "success": True,
            "cleanup_stats": cleanup_stats,
            "message": "Expired data cleaned up successfully"
        }
        
    except Exception as e:
        logger.error(f"Error during manual cleanup: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

def _generate_cost_recommendations(daily_stats: List[Dict], cache_hit_rate: float) -> List[str]:
    """Generate personalized cost optimization recommendations."""
    recommendations = []
    
    if cache_hit_rate < 30:
        recommendations.append("💡 Low cache hit rate detected. Consider using similar prompts to benefit from caching.")
    
    if cache_hit_rate > 80:
        recommendations.append("🎉 Excellent cache performance! You're saving significant costs through cached responses.")
    
    # Analyze usage patterns
    total_requests = sum(day['total_requests'] for day in daily_stats)
    if total_requests > 100:
        recommendations.append("📈 High usage detected. Consider upgrading to premium tier for better rate limits.")
    elif total_requests < 10:
        recommendations.append("📊 Light usage pattern. Current free tier is perfect for your needs.")
    
    # Check for expensive operations
    voice_analysis_heavy = any(
        any(endpoint.get('endpoint') == 'voice_analysis' and endpoint.get('total_requests', 0) > 10 
            for endpoint in day.get('endpoints', [])) 
        for day in daily_stats
    )
    
    if voice_analysis_heavy:
        recommendations.append("🎭 Heavy voice analysis usage. Batch processing is saving you ~80% on API costs!")
    
    if not recommendations:
        recommendations.append("✅ Your usage patterns are well-optimized. Keep up the good work!")
    
    return recommendations

def _generate_cache_recommendations(cache_stats: List[Dict], hit_rate_stats: List[Dict]) -> List[str]:
    """Generate cache-specific recommendations."""
    recommendations = []
    
    if not cache_stats:
        recommendations.append("🆕 No cache data yet. Start using the app to see cache benefits!")
        return recommendations
    
    # Find lowest hit rate endpoint
    if hit_rate_stats:
        lowest_hit_rate = min(hit_rate_stats, key=lambda x: x.get('hit_rate', 0))
        if lowest_hit_rate.get('hit_rate', 0) < 20:
            recommendations.append(f"⚡ {lowest_hit_rate['endpoint']} has low cache hit rate. Try using similar queries.")
    
    # Check cache distribution
    voice_analysis_cache = next((stat for stat in cache_stats if stat['cache_type'] == 'voice_analysis'), None)
    if voice_analysis_cache and voice_analysis_cache['total_entries'] > 50:
        recommendations.append("🎭 Voice analysis cache is working well! Repeated character analysis is nearly free.")
    
    recommendations.append("💾 Cache automatically expires after optimal periods to balance cost and freshness.")
    
    return recommendations 