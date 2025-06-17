"""
Useful decorators for the DOG Writer backend.
"""

import logging
from functools import wraps
from fastapi import HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

def handle_exceptions():
    """
    A decorator to catch common exceptions in API routes and return a
    standardized error response.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as he:
                logger.warning(f"HTTP Exception in {func.__name__}: {he.detail}")
                raise he
            except Exception as e:
                logger.error(f"Unhandled exception in {func.__name__}: {e}", exc_info=True)
                return JSONResponse(
                    status_code=500,
                    content={"detail": "An unexpected server error occurred."}
                )
        return wrapper
    return decorator 