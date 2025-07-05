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
    
    # Enhanced dangerous patterns based on OWASP guidelines
    DANGEROUS_PATTERNS = [
        # XSS Prevention
        r'<script[^>]*>.*?</script>',  # Script tags
        r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
        r'<object[^>]*>.*?</object>',  # Object tags
        r'<embed[^>]*>',               # Embed tags
        r'javascript:',                # Javascript URLs
        r'vbscript:',                  # VBScript URLs
        r'data:text/html',             # Data URLs with HTML
        r'data:application/javascript', # Data URLs with JS
        
        # Event handlers (comprehensive list)
        r'onload\s*=', r'onerror\s*=', r'onclick\s*=', r'onmouseover\s*=',
        r'onfocus\s*=', r'onblur\s*=', r'onchange\s*=', r'onsubmit\s*=',
        r'onkeydown\s*=', r'onkeyup\s*=', r'onmousedown\s*=', r'onmouseup\s*=',
        
        # SQL Injection Prevention
        r'DROP\s+TABLE', r'DELETE\s+FROM', r'INSERT\s+INTO', r'UPDATE\s+.*SET',
        r'UNION\s+SELECT', r'OR\s+1\s*=\s*1', r'AND\s+1\s*=\s*1',
        r';\s*--', r'/\*.*\*/', r'EXEC\s*\(', r'SP_EXECUTESQL',
        r'xp_cmdshell', r'sp_makewebtask',
        
        # NoSQL Injection
        r'\$where', r'\$ne', r'\$gt', r'\$lt', r'\$regex', r'\$in',
        
        # LDAP Injection
        r'\*\)', r'\|\|', r'&\|', r'\(\|',
        
        # Command Injection
        r';\s*cat\s+', r';\s*ls\s+', r';\s*dir\s+', r';\s*rm\s+', r';\s*del\s+',
        r'`.*`', r'\$\(.*\)', r'&&', r'\|\|', r';\s*wget', r';\s*curl',
        
        # Path Traversal
        r'\.\./.*', r'\.\.\\.*', r'/etc/passwd', r'/etc/shadow',
        r'C:\\Windows\\System32', r'\.\./', r'\.\.\\',
        
        # Server-Side Template Injection
        r'\{\{.*\}\}', r'\{\%.*\%\}', r'\$\{.*\}',
    ]
    
    # Enhanced prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything\s+above',
        r'new\s+instructions',
        r'override\s+your\s+instructions',
        r'you\s+are\s+now\s+a',
        r'act\s+as\s+if',
        r'pretend\s+to\s+be',
        r'simulate\s+being',
        r'roleplay\s+as',
        r'jailbreak',
        r'developer\s+mode',
        r'admin\s+mode',
        r'god\s+mode',
        r'debug\s+mode',
        r'maintenance\s+mode',
        r'bypass\s+safety',
        r'disable\s+safety',
        r'ignore\s+safety',
        r'forget\s+your\s+guidelines',
        r'new\s+persona',
        r'different\s+persona',
        r'switch\s+to',
        r'change\s+to',
        r'become\s+[a-z]+',
    ]
    
    def __init__(self):
        self.max_text_length = 10000
        self.max_message_length = 2000
    
    def validate_text_input(self, text: str, max_length: Optional[int] = None) -> str:
        """Enhanced text validation and sanitization with comprehensive security checks"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Check for null bytes and control characters
        if '\x00' in text:
            raise ValidationError("Input contains null bytes which are not allowed")
        
        # Remove or replace dangerous Unicode characters
        text = self._sanitize_unicode(text)
        
        # Check length after sanitization
        max_len = max_length or self.max_text_length
        if len(text) > max_len:
            raise ValidationError(f"Text too long. Maximum {max_len} characters allowed")
        
        # Check for dangerous patterns
        self._check_dangerous_patterns(text)
        
        # Enhanced HTML escape with additional protections
        sanitized_text = html.escape(text, quote=True)
        
        # Additional sanitization for URLs and special characters
        sanitized_text = self._sanitize_special_chars(sanitized_text)
        
        return sanitized_text.strip()
    
    def validate_suggestion_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Validate suggestion text without HTML escaping (for plain text editor content)"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Check for null bytes and control characters
        if '\x00' in text:
            raise ValidationError("Input contains null bytes which are not allowed")
        
        # Remove or replace dangerous Unicode characters
        text = self._sanitize_unicode(text)
        
        # Check length after sanitization
        max_len = max_length or 100000
        if len(text) > max_len:
            raise ValidationError(f"Text too long. Maximum {max_len} characters allowed")
        
        # Check for dangerous patterns (but allow some HTML-like content for rich text)
        self._check_dangerous_patterns(text)
        
        # NO HTML ESCAPING - keep original text for editor content
        # Just normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _sanitize_unicode(self, text: str) -> str:
        """Sanitize dangerous Unicode characters"""
        # Remove or replace problematic Unicode characters
        dangerous_unicode = [
            '\u202e',  # Right-to-left override
            '\u200e',  # Left-to-right mark
            '\u200f',  # Right-to-left mark
            '\ufeff',  # Zero-width no-break space
            '\u2028',  # Line separator
            '\u2029',  # Paragraph separator
        ]
        
        for char in dangerous_unicode:
            text = text.replace(char, '')
        
        # Normalize Unicode to prevent encoding attacks
        import unicodedata
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def _sanitize_special_chars(self, text: str) -> str:
        """Additional sanitization for special characters and sequences"""
        # Replace multiple consecutive whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove any remaining problematic character sequences
        problematic_sequences = [
            r'<!--.*?-->',  # HTML comments
            r'<!\[CDATA\[.*?\]\]>',  # CDATA sections
        ]
        
        for pattern in problematic_sequences:
            text = re.sub(pattern, '', text, flags=re.DOTALL)
        
        return text
    
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
        """Check for dangerous patterns with enhanced security logging"""
        text_lower = text.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # SECURITY: Log potential attack attempts for security monitoring
                logger.error(f"🚨 SECURITY ALERT: Dangerous pattern detected - Pattern: {pattern}")
                logger.error(f"🚨 SECURITY ALERT: Input sample: {text[:100]}...")
                # Store security event for further analysis
                self._log_security_event("dangerous_pattern", {"pattern": pattern, "input_sample": text[:100]})
                raise ValidationError("Input contains potentially dangerous content")
    
    def _check_prompt_injection(self, text: str):
        """Check for prompt injection patterns with enhanced security logging"""
        text_lower = text.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # SECURITY: Log potential prompt injection attempts
                logger.error(f"🚨 SECURITY ALERT: Prompt injection attempt - Pattern: {pattern}")
                logger.error(f"🚨 SECURITY ALERT: Input sample: {text[:100]}...")
                # Store security event for further analysis
                self._log_security_event("prompt_injection", {"pattern": pattern, "input_sample": text[:100]})
                raise ValidationError("Input appears to contain prompt injection attempt")
    
    def _log_security_event(self, event_type: str, details: dict):
        """Log security events for monitoring and analysis"""
        try:
            # Simple file-based logging for MVP (should be enhanced for production)
            import json
            from datetime import datetime
            
            security_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "details": details,
                "severity": "HIGH"
            }
            
            # Log to application logs
            logger.critical(f"SECURITY_EVENT: {json.dumps(security_event)}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

    def validate_llm_response(self, text: str, max_length: Optional[int] = None) -> str:
        """Validate LLM response text with relaxed length limits"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Check for null bytes and control characters
        if '\x00' in text:
            raise ValidationError("Input contains null bytes which are not allowed")
        
        # Remove or replace dangerous Unicode characters
        text = self._sanitize_unicode(text)
        
        # Much higher limit for LLM responses (50KB instead of 10KB)
        max_len = max_length or 50000  # 50,000 characters for LLM responses
        if len(text) > max_len:
            raise ValidationError(f"LLM response too long. Maximum {max_len} characters allowed")
        
        # Skip dangerous pattern checks for trusted LLM responses
        # (LLM responses are from our trusted AI providers, not user input)
        
        # Just normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

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