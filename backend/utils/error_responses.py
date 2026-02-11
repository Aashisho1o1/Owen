"""
Centralized HTTP error response helpers.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException


def error_response(
    status_code: int,
    code: str,
    message: str,
    meta: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """Create a standardized HTTPException payload."""
    detail: Dict[str, Any] = {
        "code": code,
        "message": message
    }
    if meta:
        detail["meta"] = meta
    return HTTPException(status_code=status_code, detail=detail, headers=headers)
