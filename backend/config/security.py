"""
Security Configuration

Centralized security settings and configurations for the Owen AI Writer application.
This file contains all security-related constants, settings, and validation rules.
"""

import os
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', '')
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting Configuration
    GLOBAL_RATE_LIMIT: int = 1000  # requests per minute
    IP_RATE_LIMIT: int = 100       # requests per minute per IP
    USER_RATE_LIMIT: int = 200     # requests per minute per user
    AUTH_RATE_LIMIT: int = 10      # auth attempts per 5 minutes
    
    # Input Validation Limits
    MAX_TEXT_LENGTH: int = 10000
    MAX_MESSAGE_LENGTH: int = 5000
    MAX_FILENAME_LENGTH: int = 255
    MAX_JSON_SIZE: int = 1024 * 1024  # 1MB
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = None
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = None
    
    # Content Security Policy
    CSP_DIRECTIVES: List[str] = None
    
    # Blocked Patterns (for input validation)
    DANGEROUS_PATTERNS: List[str] = None
    
    # File Upload Security
    ALLOWED_FILE_EXTENSIONS: List[str] = None
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    def __post_init__(self):
        """Initialize complex configurations after dataclass creation"""
        
        # Validate JWT secret key
        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required. "
                "Generate one using: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        
        # Security Headers Configuration
        self.SECURITY_HEADERS = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
                "encrypted-media=(), fullscreen=(), picture-in-picture=()"
            )
        }
        
        # CORS Configuration
        self.ALLOWED_ORIGINS = [
            "https://frontend-production-88b0.up.railway.app",
            "https://owen-ai-writer.vercel.app",  # Add your production frontend URL
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:4173",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175", 
            "http://localhost:5176",
            "http://localhost:5177",
            "http://localhost:8080",
        ]
        
        # Content Security Policy
        self.CSP_DIRECTIVES = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://api.languagetool.org https://api.openai.com https://generativelanguage.googleapis.com",
            "media-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        
        # Dangerous Patterns for Input Validation
        self.DANGEROUS_PATTERNS = [
            # Script injection
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'data:application/javascript',
            
            # Event handlers
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'onfocus\s*=',
            r'onblur\s*=',
            r'onchange\s*=',
            r'onsubmit\s*=',
            
            # Code execution
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'Function\s*\(',
            r'import\s+',
            r'__import__\s*\(',
            r'exec\s*\(',
            
            # SQL injection
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*SET',
            r'UNION\s+SELECT',
            r'OR\s+1\s*=\s*1',
            r'AND\s+1\s*=\s*1',
            r';\s*--',
            r'/\*.*\*/',
            
            # HTML injection
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            
            # Path traversal
            r'\.\./.*',
            r'\.\.\\.*',
            r'/etc/passwd',
            r'/etc/shadow',
            r'C:\\Windows\\System32',
            
            # Command injection
            r';\s*cat\s+',
            r';\s*ls\s+',
            r';\s*dir\s+',
            r';\s*rm\s+',
            r';\s*del\s+',
            r'`.*`',
            r'\$\(.*\)',
        ]
        
        # Allowed File Extensions
        self.ALLOWED_FILE_EXTENSIONS = [
            '.txt', '.md', '.doc', '.docx', '.pdf',
            '.jpg', '.jpeg', '.png', '.gif', '.webp',
            '.mp3', '.wav', '.mp4', '.webm'
        ]

# Global security configuration instance
security_config = SecurityConfig()

# Security validation functions
def validate_file_upload(filename: str, file_size: int) -> bool:
    """Validate file upload security"""
    # Check file extension
    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    if file_ext not in security_config.ALLOWED_FILE_EXTENSIONS:
        return False
    
    # Check file size
    if file_size > security_config.MAX_FILE_SIZE:
        return False
    
    # Check filename for dangerous patterns
    for pattern in security_config.DANGEROUS_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return False
    
    return True

def get_csp_header() -> str:
    """Get Content Security Policy header value"""
    return "; ".join(security_config.CSP_DIRECTIVES)

def is_origin_allowed(origin: str) -> bool:
    """Check if origin is allowed for CORS"""
    return origin in security_config.ALLOWED_ORIGINS

# Environment-specific security settings
def get_security_level() -> str:
    """Get current security level based on environment"""
    env = os.getenv('RAILWAY_ENVIRONMENT', 'development')
    
    if env == 'production':
        return 'strict'
    elif env == 'staging':
        return 'moderate'
    else:
        return 'development'

def should_enforce_https() -> bool:
    """Check if HTTPS should be enforced"""
    return get_security_level() in ['strict', 'moderate']

def get_session_timeout() -> int:
    """Get session timeout based on security level"""
    security_level = get_security_level()
    
    if security_level == 'strict':
        return 15 * 60  # 15 minutes
    elif security_level == 'moderate':
        return 30 * 60  # 30 minutes
    else:
        return 60 * 60  # 1 hour

# Security monitoring thresholds
SECURITY_THRESHOLDS = {
    'max_failed_logins': 5,
    'max_requests_per_minute': 100,
    'max_suspicious_events': 10,
    'auto_block_threshold': 80,  # Risk score
    'alert_threshold': 70,       # Risk score
}

# Logging configuration
SECURITY_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SECURITY_LOG_FILE = 'security.log'
SECURITY_LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
SECURITY_LOG_BACKUP_COUNT = 5 