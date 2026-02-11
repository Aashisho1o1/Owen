"""
Security Logger Service
Tracks security events and document access for audit purposes.
Addresses Claude Opus security recommendation.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from utils.request_helpers import get_client_ip  # Re-export shared helper for compatibility

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Types of security events to log"""
    DOCUMENT_ACCESS = "document_access"
    DOCUMENT_CREATE = "document_create"
    DOCUMENT_UPDATE = "document_update"
    DOCUMENT_DELETE = "document_delete"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    DANGEROUS_PATTERN = "dangerous_pattern"
    PROMPT_INJECTION = "prompt_injection"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class SecuritySeverity(Enum):
    """Security event severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityLogger:
    """Security event logging service"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        # Configure security logger with separate handler if needed
        if not self.logger.handlers:
            self._setup_security_logger()
    
    def _setup_security_logger(self):
        """Set up dedicated security logger"""
        # For MVP, use same handler as main logger
        # In production, this should write to a separate security log file
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        severity: SecuritySeverity,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        additional_context: Optional[str] = None
    ):
        """Log a security event"""
        try:
            security_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type.value,
                "severity": severity.value,
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details or {},
                "context": additional_context
            }
            
            # Log with appropriate level based on severity
            log_message = f"SECURITY_EVENT: {json.dumps(security_event)}"
            
            if severity == SecuritySeverity.CRITICAL:
                self.logger.critical(log_message)
            elif severity == SecuritySeverity.HIGH:
                self.logger.error(log_message)
            elif severity == SecuritySeverity.MEDIUM:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def log_document_access(
        self,
        document_id: str,
        user_id: int,
        action: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_details: Optional[str] = None
    ):
        """Log document access events"""
        event_type_map = {
            "read": SecurityEventType.DOCUMENT_ACCESS,
            "create": SecurityEventType.DOCUMENT_CREATE,
            "update": SecurityEventType.DOCUMENT_UPDATE,
            "delete": SecurityEventType.DOCUMENT_DELETE
        }
        
        event_type = event_type_map.get(action, SecurityEventType.DOCUMENT_ACCESS)
        severity = SecuritySeverity.LOW if success else SecuritySeverity.MEDIUM
        
        details = {
            "document_id": document_id,
            "action": action,
            "success": success
        }
        
        if error_details:
            details["error"] = error_details
            severity = SecuritySeverity.HIGH
        
        self.log_security_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            additional_context=f"Document {action} operation"
        )
    
    def log_authentication_event(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        failure_reason: Optional[str] = None,
        user_id: Optional[int] = None
    ):
        """Log authentication events"""
        event_type = SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILURE
        severity = SecuritySeverity.LOW if success else SecuritySeverity.MEDIUM
        
        details = {
            "email": email,
            "success": success
        }
        
        if failure_reason:
            details["failure_reason"] = failure_reason
            # Escalate severity for multiple failures or suspicious patterns
            if "multiple attempts" in failure_reason.lower() or "locked" in failure_reason.lower():
                severity = SecuritySeverity.HIGH
        
        self.log_security_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            additional_context="User authentication attempt"
        )
    
    def log_dangerous_pattern(
        self,
        pattern: str,
        input_sample: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log dangerous pattern detection"""
        self.log_security_event(
            event_type=SecurityEventType.DANGEROUS_PATTERN,
            severity=SecuritySeverity.HIGH,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "pattern": pattern,
                "input_sample": input_sample[:100]  # Limit sample size
            },
            additional_context="Dangerous pattern detected in user input"
        )
    
    def log_prompt_injection(
        self,
        pattern: str,
        input_sample: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log prompt injection attempts"""
        self.log_security_event(
            event_type=SecurityEventType.PROMPT_INJECTION,
            severity=SecuritySeverity.CRITICAL,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "pattern": pattern,
                "input_sample": input_sample[:100]  # Limit sample size
            },
            additional_context="Prompt injection attempt detected"
        )
    
    def log_rate_limit_exceeded(
        self,
        endpoint: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log rate limit violations"""
        self.log_security_event(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            severity=SecuritySeverity.MEDIUM,
            user_id=user_id,
            ip_address=ip_address,
            details={"endpoint": endpoint},
            additional_context="Rate limit exceeded"
        )
    
    def log_unauthorized_access(
        self,
        resource: str,
        attempted_action: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log unauthorized access attempts"""
        self.log_security_event(
            event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
            severity=SecuritySeverity.HIGH,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "resource": resource,
                "attempted_action": attempted_action
            },
            additional_context="Unauthorized access attempt"
        )

# Global security logger instance
security_logger = SecurityLogger()
