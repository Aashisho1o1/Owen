"""
Infrastructure Service - Cost Optimization Layer

This service provides clean abstractions for:
1. PostgreSQL-based rate limiting (Token Bucket + Sliding Window)
2. LLM response caching with intelligent TTL
3. Usage analytics and cost tracking
4. Future Redis migration support

Design Philosophy:
- Repository pattern for easy backend swapping
- Atomic operations for race condition safety  
- Industry-standard algorithms (Token Bucket, LRU)
- Cost-aware caching with different TTL strategies

References:
- Token Bucket: https://en.wikipedia.org/wiki/Token_bucket
- Sliding Window: https://blog.mansueli.com/rate-limiting-supabase-requests-with-postgresql-and-pgheaderkit
- GCRA Algorithm: https://builders.ramp.com/post/rate-limiting-with-redis
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps

from services.database import get_db_service, DatabaseError

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Cache types with different TTL strategies"""
    CHAT = "chat"                    # 5 min - conversations change
    VOICE_ANALYSIS = "voice_analysis"  # 1 hour - characters don't change often  
    GRAMMAR = "grammar"              # 30 min - text doesn't change much
    EMBEDDING = "embedding"          # 24 hours - vectors are expensive to compute

@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    tokens_remaining: int
    reset_time: int
    tier: str
    endpoint: str

@dataclass
class CacheResult:
    """Result of cache operation"""
    hit: bool
    data: Optional[Any]
    key: str
    ttl_seconds: int
    cache_type: str

@dataclass 
class UsageMetrics:
    """Usage tracking metrics"""
    user_id: int
    endpoint: str
    tokens_used: int
    estimated_cost_cents: int
    processing_time_ms: int
    cache_hit: bool
    llm_provider: Optional[str] = None

class RateLimiter:
    """
    PostgreSQL-based rate limiter using Token Bucket + Sliding Window algorithm.
    
    Features:
    - Atomic operations (no race conditions)
    - Flexible tier-based limits (free, premium, enterprise)
    - Burst allowance for legitimate traffic spikes
    - Automatic cleanup of old data
    
    Algorithm: Token Bucket with 1-minute sliding windows
    - Each user gets N tokens per minute based on their tier
    - Tokens are consumed atomically using PostgreSQL upsert
    - Reset time is calculated based on current window
    """
    
    def __init__(self):
        self.db = get_db_service()
        logger.info("🛡️ RateLimiter initialized with PostgreSQL backend")
    
    async def check_limit(self, user_id: int, endpoint: str, tier: str = "free") -> RateLimitResult:
        """
        Check if user is within rate limits for endpoint.
        
        Args:
            user_id: User identifier
            endpoint: API endpoint (chat, voice_analysis, grammar, auth)
            tier: User tier (free, premium, enterprise)
        
        Returns:
            RateLimitResult with decision and metadata
            
        Raises:
            DatabaseError: If rate limit check fails
        """
        try:
            # Call PostgreSQL function for atomic rate limit check
            result = await asyncio.to_thread(
                self.db.execute_query,
                "SELECT * FROM check_rate_limit(%s, %s, %s)",
                (user_id, endpoint, tier),
                fetch='one'
            )
            
            if not result:
                logger.error(f"Rate limit check returned no result for user {user_id}")
                # Fail open - allow request but log error
                return RateLimitResult(
                    allowed=True,
                    tokens_remaining=0,
                    reset_time=int(time.time()) + 60,
                    tier=tier,
                    endpoint=endpoint
                )
            
            rate_limit_result = RateLimitResult(
                allowed=result['allowed'],
                tokens_remaining=result['tokens_remaining'],
                reset_time=result['reset_time'],
                tier=tier,
                endpoint=endpoint
            )
            
            if not rate_limit_result.allowed:
                logger.warning(f"Rate limit exceeded: user={user_id}, endpoint={endpoint}, tier={tier}")
            else:
                logger.debug(f"Rate limit OK: user={user_id}, endpoint={endpoint}, tokens_remaining={rate_limit_result.tokens_remaining}")
            
            return rate_limit_result
            
        except Exception as e:
            logger.error(f"Rate limit check failed for user {user_id}: {e}")
            # Fail open - allow request but log error for monitoring
            return RateLimitResult(
                allowed=True,
                tokens_remaining=0,
                reset_time=int(time.time()) + 60,
                tier=tier,
                endpoint=endpoint
            )
    
    async def get_user_tier(self, user_id: int) -> str:
        """
        Get user's rate limiting tier.
        For MVP, everyone is 'free'. Later, check user subscription.
        """
        # TODO: Implement actual tier checking based on user subscription
        # For now, everyone gets free tier
        return "free"

class CacheProvider:
    """
    PostgreSQL-based cache for expensive LLM responses.
    
    Features:
    - Intelligent TTL based on cache type
    - Cost-aware caching (expensive operations cached longer)
    - Automatic cleanup of expired entries
    - JSON storage for complex data structures
    - Cache hit rate tracking for optimization
    
    Cache Strategy:
    - Chat responses: 5 min (conversations change frequently)
    - Voice analysis: 1 hour (character profiles stable)
    - Grammar checks: 30 min (text doesn't change much)
    - Embeddings: 24 hours (vectors expensive to compute)
    """
    
    def __init__(self):
        self.db = get_db_service()
        
        # TTL strategies by cache type
        self.ttl_config = {
            CacheType.CHAT: 300,           # 5 minutes
            CacheType.VOICE_ANALYSIS: 3600, # 1 hour  
            CacheType.GRAMMAR: 1800,       # 30 minutes
            CacheType.EMBEDDING: 86400,    # 24 hours
        }
        
        logger.info("💾 CacheProvider initialized with PostgreSQL backend")
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate deterministic cache key from function arguments.
        
        This creates a unique key based on function name and arguments,
        ensuring cache hits for identical requests.
        """
        # Create deterministic string from all arguments
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_hash[:16]}"
    
    async def get(self, key: str) -> CacheResult:
        """
        Get cached data by key.
        
        Returns:
            CacheResult with hit status and data
        """
        try:
            result = await asyncio.to_thread(
                self.db.execute_query,
                """
                SELECT response, cache_type, ttl_seconds, 
                       EXTRACT(EPOCH FROM (inserted_at + (ttl_seconds || ' seconds')::INTERVAL - NOW())) as ttl_remaining
                FROM llm_cache 
                WHERE key = %s 
                AND inserted_at > NOW() - (ttl_seconds || ' seconds')::INTERVAL
                """,
                (key,),
                fetch='one'
            )
            
            if result and result['ttl_remaining'] > 0:
                logger.debug(f"Cache HIT: {key} (TTL remaining: {int(result['ttl_remaining'])}s)")
                return CacheResult(
                    hit=True,
                    data=result['response'],
                    key=key,
                    ttl_seconds=result['ttl_seconds'],
                    cache_type=result['cache_type']
                )
            else:
                logger.debug(f"Cache MISS: {key}")
                return CacheResult(
                    hit=False,
                    data=None,
                    key=key,
                    ttl_seconds=0,
                    cache_type=""
                )
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return CacheResult(
                hit=False,
                data=None,
                key=key,
                ttl_seconds=0,
                cache_type=""
            )
    
    async def set(self, key: str, data: Any, cache_type: CacheType, user_id: int, token_count: int = 0) -> bool:
        """
        Store data in cache with appropriate TTL.
        
        Args:
            key: Cache key
            data: Data to cache (will be JSON serialized)
            cache_type: Type of cache (determines TTL)
            user_id: User who owns this cache entry
            token_count: Number of tokens for cost tracking
        
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            ttl_seconds = self.ttl_config.get(cache_type, 3600)
            
            await asyncio.to_thread(
                self.db.execute_query,
                """
                INSERT INTO llm_cache (key, response, cache_type, ttl_seconds, user_id, token_count)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    response = EXCLUDED.response,
                    inserted_at = NOW(),
                    ttl_seconds = EXCLUDED.ttl_seconds,
                    token_count = EXCLUDED.token_count
                """,
                (key, json.dumps(data), cache_type.value, ttl_seconds, user_id, token_count),
                fetch='none'
            )
            
            logger.debug(f"Cache SET: {key} (TTL: {ttl_seconds}s, type: {cache_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def cached_call(self, cache_type: CacheType, ttl_override: Optional[int] = None):
        """
        Decorator for caching expensive function calls.
        
        Usage:
            @cache_provider.cached_call(CacheType.VOICE_ANALYSIS)
            async def expensive_llm_call(text: str, user_id: int) -> dict:
                return await llm_service.analyze(text)
        
        The decorator will:
        1. Generate cache key from function name and arguments
        2. Check cache for existing result
        3. If miss, execute function and cache result
        4. Return cached or fresh result
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user_id for cache ownership
                user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 and isinstance(args[1], int) else 1)
                
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, *args, **kwargs)
                
                # Check cache first
                cache_result = await self.get(cache_key)
                if cache_result.hit:
                    logger.info(f"🎯 Cache HIT for {func.__name__}: {cache_key[:20]}...")
                    return cache_result.data
                
                # Cache miss - execute function
                logger.info(f"💸 Cache MISS for {func.__name__}: {cache_key[:20]}... (executing expensive operation)")
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    processing_time = int((time.time() - start_time) * 1000)
                    
                    # Estimate token count for cost tracking
                    estimated_tokens = len(str(result)) // 4  # Rough estimate: 4 chars per token
                    
                    # Store in cache
                    await self.set(cache_key, result, cache_type, user_id, estimated_tokens)
                    
                    logger.info(f"✅ Cached result for {func.__name__} (processing_time: {processing_time}ms)")
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in cached function {func.__name__}: {e}")
                    raise
                    
            return wrapper
        return decorator

class UsageAnalytics:
    """
    Usage analytics and cost tracking service.
    
    Features:
    - Real-time cost tracking
    - Daily/monthly usage summaries  
    - Cache hit rate monitoring
    - Budget alerts and limits
    - Cost optimization insights
    """
    
    def __init__(self):
        self.db = get_db_service()
        logger.info("📊 UsageAnalytics initialized")
    
    async def record_usage(self, metrics: UsageMetrics) -> bool:
        """
        Record API usage for cost tracking and optimization.
        
        This is called after every expensive operation to track:
        - Token usage and estimated costs
        - Processing times for performance monitoring
        - Cache hit rates for optimization
        - Per-user and per-endpoint usage patterns
        """
        try:
            await asyncio.to_thread(
                self.db.execute_query,
                "SELECT record_api_usage(%s, %s, %s, %s, %s, %s, %s)",
                (
                    metrics.user_id,
                    metrics.endpoint,
                    metrics.llm_provider,
                    metrics.tokens_used,
                    metrics.estimated_cost_cents,
                    metrics.cache_hit,
                    metrics.processing_time_ms
                ),
                fetch='none'
            )
            
            logger.debug(f"Usage recorded: user={metrics.user_id}, endpoint={metrics.endpoint}, cost={metrics.estimated_cost_cents}¢")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record usage metrics: {e}")
            return False
    
    async def get_user_daily_usage(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get user's usage summary for a specific date.
        """
        if not date:
            date = datetime.now()
        
        try:
            result = await asyncio.to_thread(
                self.db.execute_query,
                """
                SELECT * FROM daily_usage_summary 
                WHERE user_id = %s AND date_bucket = %s
                ORDER BY total_cost_cents DESC
                """,
                (user_id, date.date()),
                fetch='all'
            )
            
            return {
                'date': date.date(),
                'user_id': user_id,
                'endpoints': result or [],
                'total_cost_cents': sum(row['total_cost_cents'] for row in result) if result else 0,
                'total_requests': sum(row['total_requests'] for row in result) if result else 0,
                'cache_hit_rate': sum(row['cache_hit_rate'] * row['total_requests'] for row in result) / sum(row['total_requests'] for row in result) if result and sum(row['total_requests'] for row in result) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily usage for user {user_id}: {e}")
            return {'date': date.date(), 'user_id': user_id, 'endpoints': [], 'total_cost_cents': 0, 'total_requests': 0}

class InfraService:
    """
    Main infrastructure service that coordinates all cost optimization features.
    
    This service provides a single entry point for:
    - Rate limiting
    - Caching  
    - Usage analytics
    - Cost monitoring
    
    It's designed to be easily swappable between PostgreSQL and Redis backends.
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.cache = CacheProvider()
        self.analytics = UsageAnalytics()
        
        logger.info("🏗️ InfraService initialized with PostgreSQL backend")
    
    async def check_rate_limit(self, user_id: int, endpoint: str) -> RateLimitResult:
        """Check rate limits for user and endpoint"""
        tier = await self.rate_limiter.get_user_tier(user_id)
        return await self.rate_limiter.check_limit(user_id, endpoint, tier)
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired cache entries and old rate limit data.
        Should be called periodically (every 10 minutes).
        """
        try:
            cache_deleted = await asyncio.to_thread(
                self.rate_limiter.db.execute_query,
                "SELECT cleanup_expired_cache()",
                fetch='one'
            )
            
            rate_limit_deleted = await asyncio.to_thread(
                self.rate_limiter.db.execute_query,
                "SELECT cleanup_old_rate_limits()",
                fetch='one'
            )
            
            cleanup_stats = {
                'cache_entries_deleted': cache_deleted['cleanup_expired_cache'] if cache_deleted else 0,
                'rate_limit_entries_deleted': rate_limit_deleted['cleanup_old_rate_limits'] if rate_limit_deleted else 0
            }
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {'cache_entries_deleted': 0, 'rate_limit_entries_deleted': 0}

# Global service instances
infra_service = InfraService()

# Convenience exports for easy importing
rate_limiter = infra_service.rate_limiter
cache_provider = infra_service.cache
usage_analytics = infra_service.analytics 