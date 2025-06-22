"""
Helper Utilities
Common utility functions used across the application.
Extracted from main.py as part of God File refactoring.
"""

from typing import Optional
from services.database import db_service

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user details by ID"""
    try:
        result = db_service.execute_query(
            "SELECT id, username, name, email, created_at FROM users WHERE id = %s AND is_active = TRUE",
            (user_id,),
            fetch='one'
        )
        return dict(result) if result else None
    except Exception:
        return None

def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0 
 