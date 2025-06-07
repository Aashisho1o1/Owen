"""
Input Validation and Sanitization Service

Provides comprehensive input validation, sanitization, and security checks
to prevent injection attacks and ensure data integrity.
"""

import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, ValidationError
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """
    Comprehensive input validation and sanitization service.
    
    Features:
    - HTML/XSS prevention
    - SQL injection protection
    - Length and format validation
    - Content filtering
    - Prompt injection detection
    """
    
    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    ALLOWED_ATTRIBUTES = {}
    
    # Dangerous patterns that might indicate injection attempts
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # Javascript URLs
        r'vbscript:',                # VBScript URLs
        r'onload\s*=',               # Event handlers
        r'onerror\s*=',
        r'onclick\s*=',
        r'eval\s*\(',                # Code execution
        r'setTimeout\s*\(',
        r'setInterval\s*\(',
        r'Function\s*\(',
        r'import\s+',                # Python imports
        r'__import__\s*\(',
        r'exec\s*\(',                # Python exec
        r'eval\s*\(',                # Python eval
        r'DROP\s+TABLE',             # SQL injection
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'UPDATE\s+.*SET',
        r'UNION\s+SELECT',
        r'OR\s+1\s*=\s*1',
    ]
    
    # Prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'new\s+instructions',
        r'system\s*:\s*you\s+are',
        r'assistant\s*:\s*i\s+will',
        r'pretend\s+to\s+be',
        r'act\s+as\s+if',
        r'roleplay\s+as',
    ]
    
    def __init__(self):
        self.max_text_length = 10000  # Maximum text input length
        self.max_message_length = 2000  # Maximum chat message length
        self.max_filename_length = 255
    
    def validate_text_input(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Validate and sanitize text input.
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length (uses default if None)
        
        Returns:
            Sanitized text
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Check length
        max_len = max_length or self.max_text_length
        if len(text) > max_len:
            raise ValidationError(f"Text too long. Maximum {max_len} characters allowed")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(text)
        
        # HTML escape for safety
        sanitized = html.escape(text)
        
        # Additional sanitization with bleach for HTML content
        sanitized = bleach.clean(
            sanitized,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return sanitized.strip()
    
    def validate_chat_message(self, message: str) -> str:
        """Validate chat message with specific rules"""
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")
        
        # Check for prompt injection attempts
        self._check_prompt_injection(message)
        
        return self.validate_text_input(message, self.max_message_length)
    
    def validate_filename(self, filename: str) -> str:
        """Validate filename for file uploads"""
        if not filename:
            raise ValidationError("Filename cannot be empty")
        
        if len(filename) > self.max_filename_length:
            raise ValidationError(f"Filename too long. Maximum {self.max_filename_length} characters")
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Only allow alphanumeric, dots, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
            raise ValidationError("Invalid filename characters")
        
        return filename
    
    def validate_user_id(self, user_id: str) -> str:
        """Validate user ID format"""
        if not user_id:
            raise ValidationError("User ID cannot be empty")
        
        # UUID format validation
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, user_id.lower()):
            raise ValidationError("Invalid user ID format")
        
        return user_id.lower()
    
    def validate_json_data(self, data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
        """Validate JSON data structure"""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        # Check required fields
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {missing_fields}")
        
        # Recursively validate string values
        validated_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                validated_data[key] = self.validate_text_input(value)
            elif isinstance(value, (int, float, bool, type(None))):
                validated_data[key] = value
            elif isinstance(value, (list, dict)):
                # For complex structures, apply basic validation
                validated_data[key] = self._validate_complex_data(value)
            else:
                raise ValidationError(f"Unsupported data type for field {key}")
        
        return validated_data
    
    def _validate_complex_data(self, data: Union[List, Dict]) -> Union[List, Dict]:
        """Validate complex nested data structures"""
        if isinstance(data, list):
            return [
                self.validate_text_input(item) if isinstance(item, str) else item
                for item in data[:100]  # Limit list size
            ]
        elif isinstance(data, dict):
            return {
                key: self.validate_text_input(value) if isinstance(value, str) else value
                for key, value in list(data.items())[:50]  # Limit dict size
            }
        return data
    
    def _check_dangerous_patterns(self, text: str):
        """Check for dangerous patterns in text"""
        text_lower = text.lower()
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                raise ValidationError("Input contains potentially dangerous content")
    
    def _check_prompt_injection(self, text: str):
        """Check for prompt injection attempts"""
        text_lower = text.lower()
        
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential prompt injection detected: {pattern}")
                raise ValidationError("Input appears to contain prompt injection attempt")
    
    def validate_llm_provider(self, provider: str) -> str:
        """Validate LLM provider selection"""
        allowed_providers = ['Google Gemini', 'Anthropic Claude', 'OpenAI GPT']
        
        if provider not in allowed_providers:
            raise ValidationError(f"Invalid LLM provider. Allowed: {allowed_providers}")
        
        return provider
    
    def validate_english_variant(self, variant: str) -> str:
        """Validate English variant selection"""
        allowed_variants = ['standard', 'indian', 'british', 'american']
        
        if variant not in allowed_variants:
            raise ValidationError(f"Invalid English variant. Allowed: {allowed_variants}")
        
        return variant

# Global validator instance
input_validator = InputValidator()

def validate_request_data(data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
    """
    FastAPI dependency for request validation.
    
    Usage:
        @router.post("/endpoint")
        async def endpoint(validated_data: Dict = Depends(validate_request_data)):
            # validated_data is now safe to use
    """
    try:
        return input_validator.validate_json_data(data, required_fields)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Pydantic models for structured validation
class ChatMessageModel(BaseModel):
    """Pydantic model for chat message validation"""
    message: str
    editor_text: Optional[str] = ""
    author_persona: Optional[str] = "Ernest Hemingway"
    help_focus: Optional[str] = "Dialogue Writing"
    llm_provider: Optional[str] = "Google Gemini"
    english_variant: Optional[str] = "standard"
    
    @validator('message')
    def validate_message(cls, v):
        return input_validator.validate_chat_message(v)
    
    @validator('editor_text')
    def validate_editor_text(cls, v):
        if v:
            return input_validator.validate_text_input(v)
        return v
    
    @validator('llm_provider')
    def validate_llm_provider(cls, v):
        return input_validator.validate_llm_provider(v)
    
    @validator('english_variant')
    def validate_english_variant(cls, v):
        return input_validator.validate_english_variant(v)

class UserFeedbackModel(BaseModel):
    """Pydantic model for user feedback validation"""
    original_message: str
    ai_response: str
    user_feedback: str
    correction_type: str
    
    @validator('*')
    def validate_text_fields(cls, v):
        if isinstance(v, str):
            return input_validator.validate_text_input(v)
        return v 