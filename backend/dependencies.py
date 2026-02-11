"""
FastAPI Dependencies for DOG Writer

This module contains shared dependencies used across the application,
such as authentication, rate limiting, and database sessions, to ensure 
consistency and adherence to the DRY (Don't Repeat Yourself) principle.
"""

import logging
import time
from typing import Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service, AuthenticationError
from services.infra_service import infra_service, RateLimitResult
from utils.error_responses import error_response
from utils.request_helpers import get_client_ip

logger = logging.getLogger(__name__)

# Reusable security scheme using HTTP Bearer for JWT tokens.
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Union[str, int]:
    """
    FastAPI dependency to get the current user's ID from a JWT token.
    
    **Updated for Guest Support**: This now handles both regular user tokens 
    and guest session tokens, returning appropriate user identifiers for each.

    Engineering approach:
    1. Try to verify as regular user token first (most common case)
    2. If that fails with specific error, try guest token verification
    3. Return consistent user_id format for downstream code compatibility

    Returns:
        int: The authenticated user's unique ID (real user) or 
             str: Guest session identifier formatted as "guest_{session_id}"
    """
    if credentials is None or not credentials.credentials:
        logger.warning("Authentication attempt failed: No credentials provided.")
        raise error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_CREDENTIALS_MISSING",
            message="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        
        # First, try to verify as a regular user token (most common case)
        try:
            user_info = auth_service.verify_token(token)
            logger.info(f"Successfully authenticated user_id: {user_info['user_id']}")
            return user_info['user_id']
        except AuthenticationError as e:
            # CRITICAL FIX: Always try guest token verification on any auth failure
            # This ensures guest sessions work regardless of the specific error message
            try:
                guest_info = auth_service.verify_guest_token(token)
                # Return session_id as user_id for guests (maintains compatibility)
                guest_user_id = guest_info['session_id']
                logger.info(f"Successfully authenticated guest session: {guest_user_id}")
                return guest_user_id
            except AuthenticationError as guest_error:
                # Neither regular nor guest token worked - return original error for better debugging
                logger.debug(f"Guest token verification also failed: {guest_error}")
                raise e  # Raise the original user token error
        
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for token. Reason: {e}")
        raise error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_INVALID_TOKEN",
            message=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"An unexpected server error occurred during authentication: {e}", exc_info=True)
        raise error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="AUTH_VALIDATION_ERROR",
            message="Could not validate credentials due to a server error.",
        )

# New PostgreSQL-based rate limiting dependency
async def check_rate_limit_dependency(
    request: Request,
    endpoint: str = "general",
    user_id: Union[str, int] = Depends(get_current_user_id)
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
    fail_closed_endpoints = {"chat", "voice_analysis", "story_generation"}

    try:
        # Check rate limit using our new PostgreSQL-based service
        rate_limit_result = await infra_service.check_rate_limit(user_id, endpoint)
        
        if not rate_limit_result.allowed:
            logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")

            # Get client IP for logging
            client_ip = get_client_ip(request)
            logger.info("Rate limit denied request from ip=%s endpoint=%s", client_ip, endpoint)

            retry_after = max(0, rate_limit_result.reset_time - int(time.time()))
            raise error_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                code="RATE_LIMIT_EXCEEDED",
                message=f"You have exceeded the rate limit for {endpoint}. Please try again later.",
                meta={
                    "retry_after": retry_after,
                    "tokens_remaining": rate_limit_result.tokens_remaining,
                    "reset_time": rate_limit_result.reset_time,
                    "tier": rate_limit_result.tier,
                    "endpoint": endpoint
                },
                headers={
                    "Retry-After": str(retry_after),
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
        if endpoint in fail_closed_endpoints:
            raise error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="RATE_LIMIT_UNAVAILABLE",
                message="Rate limiter is temporarily unavailable for this endpoint. Please try again shortly.",
                meta={"endpoint": endpoint}
            )

        logger.warning(
            "Rate limiter unavailable for non-expensive endpoint=%s user_id=%s; failing open",
            endpoint,
            user_id
        )
        # Fail open for non-expensive endpoints
        return RateLimitResult(
            allowed=True,
            tokens_remaining=0,
            reset_time=int(time.time()) + 60,
            tier="free",
            endpoint=endpoint
        )

# Convenience functions for specific endpoints
async def check_chat_rate_limit(request: Request, user_id: Union[str, int] = Depends(get_current_user_id)) -> RateLimitResult:
    """Rate limit dependency specifically for chat endpoints"""
    return await check_rate_limit_dependency(request, "chat", user_id)

async def check_voice_analysis_rate_limit(request: Request, user_id: Union[str, int] = Depends(get_current_user_id)) -> RateLimitResult:
    """Rate limit dependency specifically for voice analysis endpoints"""
    return await check_rate_limit_dependency(request, "voice_analysis", user_id)

async def check_grammar_rate_limit(request: Request, user_id: Union[str, int] = Depends(get_current_user_id)) -> RateLimitResult:
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
