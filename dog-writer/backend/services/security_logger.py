"""
Security Logging and Monitoring Service

Provides comprehensive security event logging, monitoring, and alerting
for detecting and responding to security incidents.
"""

import logging
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import Request
import os

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
if not security_logger.handlers:
    handler = logging.FileHandler("security.log")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)

class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHENTICATION_SUCCESS = "auth_success"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_REQUEST = "suspicious_request"
    INPUT_VALIDATION_FAILURE = "input_validation_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    IP_BLOCKED = "ip_blocked"
    MALICIOUS_FILE_UPLOAD = "malicious_file_upload"
    API_ABUSE = "api_abuse"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"

class SecuritySeverity(Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: SecurityEventType
    severity: SecuritySeverity
    ip_address: str
    user_agent: str
    user_id: Optional[str]
    endpoint: str
    method: str
    request_id: str
    details: Dict[str, Any]
    risk_score: int  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        return data

class SecurityMonitor:
    """
    Security monitoring and logging service
    
    Features:
    - Real-time security event logging
    - Risk scoring and threat assessment
    - Automated alerting for critical events
    - Security metrics and reporting
    - Incident response coordination
    """
    
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.max_events = 10000  # Keep last 10k events in memory
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_patterns: Dict[str, int] = {}
        
        # Risk scoring weights
        self.risk_weights = {
            SecurityEventType.AUTHENTICATION_FAILURE: 10,
            SecurityEventType.RATE_LIMIT_EXCEEDED: 15,
            SecurityEventType.SUSPICIOUS_REQUEST: 20,
            SecurityEventType.INPUT_VALIDATION_FAILURE: 25,
            SecurityEventType.SQL_INJECTION_ATTEMPT: 80,
            SecurityEventType.XSS_ATTEMPT: 70,
            SecurityEventType.BRUTE_FORCE_ATTEMPT: 60,
            SecurityEventType.DATA_BREACH_ATTEMPT: 90,
            SecurityEventType.API_ABUSE: 40,
        }
    
    def get_client_info(self, request: Request) -> Dict[str, str]:
        """Extract client information from request"""
        # Get real IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.client.host if request.client else "unknown"
        
        # Get user agent
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Get or create request ID
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        return {
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_id": request_id,
            "endpoint": str(request.url.path),
            "method": request.method
        }
    
    def calculate_risk_score(self, event_type: SecurityEventType, 
                           ip_address: str, details: Dict[str, Any]) -> int:
        """Calculate risk score for security event"""
        base_score = self.risk_weights.get(event_type, 10)
        
        # Increase score for repeat offenders
        recent_events = self.get_recent_events_by_ip(ip_address, hours=1)
        repeat_multiplier = min(len(recent_events) * 0.1, 2.0)  # Max 2x multiplier
        
        # Increase score for suspicious patterns
        pattern_score = 0
        if "sql_keywords" in details:
            pattern_score += 20
        if "script_tags" in details:
            pattern_score += 15
        if "path_traversal" in details:
            pattern_score += 25
        
        final_score = int((base_score + pattern_score) * (1 + repeat_multiplier))
        return min(final_score, 100)  # Cap at 100
    
    def log_security_event(self, request: Request, event_type: SecurityEventType,
                          severity: SecuritySeverity, details: Dict[str, Any],
                          user_id: Optional[str] = None) -> SecurityEvent:
        """Log a security event"""
        client_info = self.get_client_info(request)
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(
            event_type, client_info["ip_address"], details
        )
        
        # Create security event
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
            user_id=user_id,
            endpoint=client_info["endpoint"],
            method=client_info["method"],
            request_id=client_info["request_id"],
            details=details,
            risk_score=risk_score
        )
        
        # Store event
        self.events.append(event)
        
        # Limit memory usage
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events//2:]
        
        # Log to file
        log_data = event.to_dict()
        security_logger.warning(f"SECURITY_EVENT: {json.dumps(log_data)}")
        
        # Handle high-risk events
        if risk_score >= 70 or severity == SecuritySeverity.CRITICAL:
            self._handle_high_risk_event(event)
        
        return event
    
    def _handle_high_risk_event(self, event: SecurityEvent):
        """Handle high-risk security events"""
        # Auto-block IP for critical events
        if event.severity == SecuritySeverity.CRITICAL or event.risk_score >= 80:
            self.blocked_ips[event.ip_address] = datetime.now()
            security_logger.critical(
                f"AUTO_BLOCKED IP {event.ip_address} due to {event.event_type.value}"
            )
        
        # Alert for immediate attention
        alert_data = {
            "alert_type": "HIGH_RISK_SECURITY_EVENT",
            "event_id": event.event_id,
            "ip_address": event.ip_address,
            "event_type": event.event_type.value,
            "risk_score": event.risk_score,
            "timestamp": event.timestamp.isoformat()
        }
        
        security_logger.critical(f"SECURITY_ALERT: {json.dumps(alert_data)}")
        
        # In production, you would send this to your alerting system
        # (Slack, PagerDuty, email, etc.)
    
    def get_recent_events_by_ip(self, ip_address: str, hours: int = 24) -> List[SecurityEvent]:
        """Get recent security events for an IP address"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.events
            if event.ip_address == ip_address and event.timestamp > cutoff_time
        ]
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            # Auto-unblock after 24 hours
            if datetime.now() - block_time > timedelta(hours=24):
                del self.blocked_ips[ip_address]
                return False
            return True
        return False
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring dashboard"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self.events if e.timestamp > last_hour]
        daily_events = [e for e in self.events if e.timestamp > last_24h]
        
        # Event counts by type
        event_counts = {}
        for event_type in SecurityEventType:
            event_counts[event_type.value] = len([
                e for e in daily_events if e.event_type == event_type
            ])
        
        # Top attacking IPs
        ip_counts = {}
        for event in daily_events:
            ip_counts[event.ip_address] = ip_counts.get(event.ip_address, 0) + 1
        
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Risk distribution
        risk_distribution = {
            "low": len([e for e in daily_events if e.risk_score < 30]),
            "medium": len([e for e in daily_events if 30 <= e.risk_score < 70]),
            "high": len([e for e in daily_events if e.risk_score >= 70])
        }
        
        return {
            "total_events_24h": len(daily_events),
            "events_last_hour": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "event_counts_by_type": event_counts,
            "top_attacking_ips": top_ips,
            "risk_distribution": risk_distribution,
            "average_risk_score": sum(e.risk_score for e in daily_events) / len(daily_events) if daily_events else 0
        }
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        events = [e for e in self.events if e.timestamp > cutoff_time]
        
        if not events:
            return {"message": "No security events in the specified time period"}
        
        # Critical events
        critical_events = [e for e in events if e.severity == SecuritySeverity.CRITICAL]
        
        # Most targeted endpoints
        endpoint_counts = {}
        for event in events:
            endpoint_counts[event.endpoint] = endpoint_counts.get(event.endpoint, 0) + 1
        
        top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "report_period_hours": hours,
            "total_events": len(events),
            "critical_events": len(critical_events),
            "unique_ips": len(set(e.ip_address for e in events)),
            "most_targeted_endpoints": top_endpoints,
            "critical_event_details": [e.to_dict() for e in critical_events[:10]],
            "metrics": self.get_security_metrics()
        }

# Global security monitor instance
security_monitor = SecurityMonitor()

# Security logging helpers
def log_auth_failure(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log authentication failure"""
    return security_monitor.log_security_event(
        request, SecurityEventType.AUTHENTICATION_FAILURE,
        SecuritySeverity.MEDIUM, details, user_id
    )

def log_suspicious_request(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log suspicious request"""
    return security_monitor.log_security_event(
        request, SecurityEventType.SUSPICIOUS_REQUEST,
        SecuritySeverity.HIGH, details, user_id
    )

def log_input_validation_failure(request: Request, details: Dict[str, Any], user_id: Optional[str] = None):
    """Log input validation failure"""
    return security_monitor.log_security_event(
        request, SecurityEventType.INPUT_VALIDATION_FAILURE,
        SecuritySeverity.MEDIUM, details, user_id
    ) 