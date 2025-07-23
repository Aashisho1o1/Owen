"""
FastAPI Dependencies for DOG Writer

This module contains shared dependencies used across the application,
such as authentication, rate limiting, and database sessions, to ensure 
consistency and adherence to the DRY (Don't Repeat Yourself) principle.
"""

import logging
import time
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service, AuthenticationError
from services.infra_service import infra_service, RateLimitResult

logger = logging.getLogger(__name__)

# Reusable security scheme using HTTP Bearer for JWT tokens.
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    FastAPI dependency to get the current user's ID from a JWT token.

    This function serves as the single source of truth for user authentication
    on all protected routes. It ensures that every protected endpoint
    goes through the same validation logic.

    It extracts the token from the 'Authorization: Bearer <token>' header,
    verifies its signature and expiration, and checks if the user exists
    and is active in the database.

    Raises:
        HTTPException: 
            - 401 Unauthorized: If the token is missing, malformed, invalid,
              expired, or the associated user is not found or inactive.
            - 500 Internal Server Error: For any other unexpected errors
              during the authentication process.

    Returns:
        int: The authenticated user's unique ID.
    """
    if credentials is None or not credentials.credentials:
        logger.warning("Authentication attempt failed: No credentials provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user_info = auth_service.verify_token(token)
        logger.info(f"Successfully authenticated user_id: {user_info['user_id']}")
        return user_info['user_id']
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for token. Reason: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"An unexpected server error occurred during authentication: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials due to a server error.",
        ) 

# New PostgreSQL-based rate limiting dependency
async def check_rate_limit_dependency(
    request: Request,
    endpoint: str = "general",
    user_id: int = Depends(get_current_user_id)
) -> RateLimitResult:
    """
    FastAPI dependency for PostgreSQL-based rate limiting.
    
    This replaces the old memory-based rate limiter with a proper 
    database-backed solution that works across multiple Railway instances.
    
    Args:
        request: FastAPI request object (for IP extraction if needed)
        endpoint: Endpoint type (chat, voice_analysis, grammar, auth)
        user_id: Authenticated user ID
        
    Returns:
        RateLimitResult with rate limit status
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    try:
        # Check rate limit using our new PostgreSQL-based service
        rate_limit_result = await infra_service.check_rate_limit(user_id, endpoint)
        
        if not rate_limit_result.allowed:
            logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")
            
            # Get client IP for logging
            client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            if not client_ip:
                client_ip = request.headers.get("X-Real-IP", "")
            if not client_ip:
                client_ip = request.client.host if request.client else "unknown"
            
            # Enhanced error response with rate limit info
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"You have exceeded the rate limit for {endpoint}. Please try again later.",
                    "retry_after": rate_limit_result.reset_time - int(time.time()),
                    "tokens_remaining": rate_limit_result.tokens_remaining,
                    "reset_time": rate_limit_result.reset_time,
                    "tier": rate_limit_result.tier,
                    "endpoint": endpoint
                },
                headers={
                    "Retry-After": str(rate_limit_result.reset_time - int(time.time())),
                    "X-RateLimit-Limit": "varies-by-tier",
                    "X-RateLimit-Remaining": str(rate_limit_result.tokens_remaining),
                    "X-RateLimit-Reset": str(rate_limit_result.reset_time)
                }
            )
        
        logger.debug(f"Rate limit OK for user {user_id} on {endpoint}: {rate_limit_result.tokens_remaining} tokens remaining")
        return rate_limit_result
        
    except HTTPException:
        # Re-raise HTTP exceptions (rate limit exceeded)
        raise
    except Exception as e:
        logger.error(f"Rate limit check failed for user {user_id}: {e}")
        # Fail open - allow request but log error for monitoring
        # This prevents rate limiting failures from breaking the app
        return RateLimitResult(
            allowed=True,
            tokens_remaining=0,
            reset_time=int(time.time()) + 60,
            tier="free",
            endpoint=endpoint
        )

# Convenience functions for specific endpoints
async def check_chat_rate_limit(request: Request, user_id: int = Depends(get_current_user_id)) -> RateLimitResult:
    """Rate limit dependency specifically for chat endpoints"""
    return await check_rate_limit_dependency(request, "chat", user_id)

async def check_voice_analysis_rate_limit(request: Request, user_id: int = Depends(get_current_user_id)) -> RateLimitResult:
    """Rate limit dependency specifically for voice analysis endpoints"""
    return await check_rate_limit_dependency(request, "voice_analysis", user_id)

async def check_grammar_rate_limit(request: Request, user_id: int = Depends(get_current_user_id)) -> RateLimitResult:
    """Rate limit dependency specifically for grammar endpoints"""
    return await check_rate_limit_dependency(request, "grammar", user_id)

async def check_auth_rate_limit(request: Request) -> bool:
    """
    Rate limit dependency for auth endpoints (no user_id required).
    Uses IP-based rate limiting for unauthenticated requests.
    """
    try:
        # For auth endpoints, we don't have a user_id yet
        # Use IP-based rate limiting (fall back to old system for now)
        from services.rate_limiter import check_rate_limit
        return await check_rate_limit(request, "auth")
    except Exception as e:
        logger.error(f"Auth rate limit check failed: {e}")
        return True  # Fail open 