"""
Helper Functions for DOG Writer

This module contains reusable utility functions that can be used across
different parts of the application to avoid code duplication and maintain
consistency.
"""

from services.database import get_db_service
from typing import Optional, Dict, Any

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user information by user ID.
    
    This is a helper function that can be used across different modules
    to fetch user data without duplicating the database query logic.
    
    Args:
        user_id (int): The unique identifier for the user
        
    Returns:
        Optional[Dict[str, Any]]: User data dictionary or None if not found
    """
    db_service = get_db_service()
    return db_service.execute_query(
        "SELECT id, username, email, name, created_at FROM users WHERE id = %s",
        (user_id,),
        fetch='one'
    )

def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0 
 