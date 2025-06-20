"""
Simple Security Logging Service for MVP

Basic security event logging with essential monitoring.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import Request

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Basic security event types for MVP"""
    AUTH_FAILURE = "auth_failure"
    AUTH_SUCCESS = "auth_success"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_REQUEST = "suspicious_request"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

class SecuritySeverity(Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Simple security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: SecurityEventType
    severity: SecuritySeverity
    ip_address: str
    user_agent: str
    user_id: Optional[str]
    endpoint: str
    method: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        return data

class SimpleSecurityMonitor:
    """Simple security monitoring for MVP"""
    
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.max_events = 1000  # Keep last 1000 events
        self.blocked_ips: Dict[str, datetime] = {}
    
    def get_client_info(self, request: Request) -> Dict[str, str]:
        """Extract basic client information from request"""
        # Get IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.headers.get("X-Real-IP", 
                request.client.host if request.client else "unknown")
        
        # Get user agent
        user_agent = request.headers.get("User-Agent", "unknown")
        
        return {
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    
    def log_security_event(self, request: Request, event_type: SecurityEventType,
                          severity: SecuritySeverity, details: Dict[str, Any],
                          user_id: Optional[str] = None) -> SecurityEvent:
        """Log a security event"""
        client_info = self.get_client_info(request)
        
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=severity,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            details=details
        )
        
        self.events.append(event)
        
        # Limit memory usage
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events//2:]
        
        # Log to standard logger
        log_level = logging.WARNING if severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL] else logging.INFO
        logger.log(log_level, 
                  f"Security Event: {event_type.value} from {client_info['ip_address']} - {details}")
        
        return event
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if an IP address is currently blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.utcnow() - block_time < timedelta(hours=1):
                return True
            else:
                del self.blocked_ips[ip_address]
        return False
    
    def get_recent_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Get recent security events"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [event for event in self.events if event.timestamp > cutoff]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get basic security metrics"""
        recent_events = self.get_recent_events(24)
        
        event_counts = {}
        for event_type in SecurityEventType:
            event_counts[event_type.value] = len([
                e for e in recent_events if e.event_type == event_type
            ])
        
        severity_counts = {}
        for severity in SecuritySeverity:
            severity_counts[severity.value] = len([
                e for e in recent_events if e.severity == severity
            ])
        
        return {
            "total_events_24h": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "events_by_type": event_counts,
            "events_by_severity": severity_counts,
            "last_updated": datetime.utcnow().isoformat()
        }

# Global instance
security_monitor = SimpleSecurityMonitor()

# Helper functions
def log_auth_failure(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log authentication failure"""
    return security_monitor.log_security_event(
        request, SecurityEventType.AUTH_FAILURE, SecuritySeverity.MEDIUM, details, user_id
    )

def log_suspicious_request(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log suspicious request"""
    return security_monitor.log_security_event(
        request, SecurityEventType.SUSPICIOUS_REQUEST, SecuritySeverity.HIGH, details, user_id
    )

def log_unauthorized_access(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log unauthorized access attempt"""
    return security_monitor.log_security_event(
        request, SecurityEventType.UNAUTHORIZED_ACCESS, SecuritySeverity.HIGH, details, user_id
    ) 