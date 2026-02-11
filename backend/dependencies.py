"""
FastAPI Dependencies for DOG Writer

This module contains shared dependencies used across the application,
such as authentication, rate limiting, and database sessions, to ensure 
consistency and adherence to the DRY (Don't Repeat Yourself) principle.
"""

import logging
import time
from dataclasses import dataclass
from typing import Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import auth_service, AuthenticationError
from services.rate_limiter import check_rate_limit
from utils.error_responses import error_response
from utils.request_helpers import get_client_ip

logger = logging.getLogger(__name__)

# Reusable security scheme using HTTP Bearer for JWT tokens.
security = HTTPBearer()


@dataclass
class RateLimitResult:
    """Lightweight result model used by existing endpoint dependencies."""
    allowed: bool
    tokens_remaining: int
    reset_time: int
    tier: str
    endpoint: str

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
            # Always try guest token verification on auth failure
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

async def check_rate_limit_dependency(
    request: Request,
    endpoint: str = "general",
    user_id: Union[str, int] = Depends(get_current_user_id)
) -> RateLimitResult:
    """
    FastAPI dependency for shared endpoint rate limiting.
    
    Args:
        request: FastAPI request object (for IP extraction if needed)
        endpoint: Endpoint type (chat, voice_analysis, grammar, auth)
        user_id: Authenticated user ID
        
    Returns:
        RateLimitResult with rate limit status metadata
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    fail_closed_endpoints = {"chat", "voice_analysis", "story_generation"}
    endpoint_alias = {
        "voice_analysis": "chat",
        "story_generation": "chat",
    }
    limiter_endpoint = endpoint_alias.get(endpoint, endpoint)

    try:
        await check_rate_limit(request, limiter_endpoint)
        return RateLimitResult(
            allowed=True,
            tokens_remaining=-1,
            reset_time=int(time.time()) + 60,
            tier="free",
            endpoint=endpoint,
        )
    except HTTPException as exc:
        logger.warning("Rate limit exceeded for user=%s endpoint=%s", user_id, endpoint)
        client_ip = get_client_ip(request)
        logger.info("Rate limit denied request from ip=%s endpoint=%s", client_ip, endpoint)
        message = exc.detail if isinstance(exc.detail, str) else f"Rate limit exceeded for {endpoint}"
        raise error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            meta={"endpoint": endpoint},
        )
    except Exception as exc:
        logger.error("Rate limit check failed for user %s: %s", user_id, exc)
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
            tokens_remaining=-1,
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
        return await check_rate_limit(request, "auth")
    except Exception as e:
        logger.error(f"Auth rate limit check failed: {e}")
        return True  # Fail open 
