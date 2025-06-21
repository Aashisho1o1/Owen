"""
Simple Input Validation Service for MVP

Basic input validation and sanitization for essential security.
"""

import re
import html
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class SimpleInputValidator:
    """Simple input validation for MVP"""
    
    # Basic dangerous patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # Javascript URLs
        r'onload\s*=',               # Event handlers
        r'onerror\s*=',
        r'onclick\s*=',
        r'DROP\s+TABLE',             # SQL injection
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'UNION\s+SELECT',
        r'OR\s+1\s*=\s*1',
        r';\s*--',                   # SQL comments
    ]
    
    # Basic prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'new\s+instructions',
        r'override\s+your\s+instructions',
        r'you\s+are\s+now\s+a',
    ]
    
    def __init__(self):
        self.max_text_length = 10000
        self.max_message_length = 2000
    
    def validate_text_input(self, text: str, max_length: Optional[int] = None) -> str:
        """Basic text validation and sanitization"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Check length
        max_len = max_length or self.max_text_length
        if len(text) > max_len:
            raise ValidationError(f"Text too long. Maximum {max_len} characters allowed")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(text)
        
        # Basic HTML escape
        return html.escape(text).strip()
    
    def validate_chat_message(self, message: str) -> str:
        """Validate chat message"""
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        # Check for prompt injection attempts
        self._check_prompt_injection(message)
        
        return self.validate_text_input(message, self.max_message_length)
    
    def validate_user_id(self, user_id: str) -> str:
        """Validate user ID format (UUID)"""
        if not user_id:
            raise ValidationError("User ID cannot be empty")
        
        # Basic UUID format validation
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, user_id.lower()):
            raise ValidationError("Invalid user ID format")
        
        return user_id.lower()
    
    def validate_llm_provider(self, provider: str) -> str:
        """Validate LLM provider name"""
        if not provider:
            raise ValidationError("LLM provider cannot be empty")
        
        # Updated to match actual provider names used by LLM service and frontend
        valid_providers = ["Google Gemini", "OpenAI GPT"]
        if provider not in valid_providers:
            raise ValidationError(f"Invalid LLM provider. Must be one of: {valid_providers}")
        
        return provider
    
    def _check_dangerous_patterns(self, text: str):
        """Check for basic dangerous patterns"""
        text_lower = text.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                raise ValidationError("Input contains potentially dangerous content")
    
    def _check_prompt_injection(self, text: str):
        """Check for basic prompt injection patterns"""
        text_lower = text.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Prompt injection attempt detected: {pattern}")
                raise ValidationError("Input appears to contain prompt injection attempt")

# Global instance
input_validator = SimpleInputValidator()

# Helper functions
def validate_request_data(data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
    """Validate request data"""
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid data format")
    
    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {missing_fields}"
            )
    
    return data

def validate_chat_input(message: str, editor_text: str = "") -> Dict[str, str]:
    """Validate chat input data"""
    try:
        validated_message = input_validator.validate_chat_message(message)
        validated_editor = input_validator.validate_text_input(editor_text or "")
        
        return {
            "message": validated_message,
            "editor_text": validated_editor
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) 