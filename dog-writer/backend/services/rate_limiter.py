"""
Advanced Rate Limiting Service

Provides multi-tier rate limiting with IP-based, user-based, and endpoint-specific limits.
Includes DDoS protection, suspicious activity detection, and automatic blocking.
"""

import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from fastapi import HTTPException, Request
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    window_seconds: int
    burst_limit: int = None  # Allow burst requests
    
@dataclass
class SecurityEvent:
    """Security event for monitoring"""
    timestamp: datetime
    ip_address: str
    event_type: str
    severity: str
    details: str

class AdvancedRateLimiter:
    """
    Advanced rate limiting with multiple protection layers:
    
    1. Global rate limiting (prevent DDoS)
    2. Per-IP rate limiting (prevent abuse)
    3. Per-user rate limiting (authenticated users)
    4. Per-endpoint rate limiting (protect expensive operations)
    5. Suspicious activity detection
    6. Automatic IP blocking
    """
    
    def __init__(self):
        # Rate limit configurations
        self.limits = {
            # Global limits (all requests)
            'global': RateLimit(requests=1000, window_seconds=60),
            
            # Per-IP limits
            'ip_general': RateLimit(requests=100, window_seconds=60, burst_limit=20),
            'ip_auth': RateLimit(requests=10, window_seconds=300),  # 10 auth attempts per 5 min
            'ip_grammar': RateLimit(requests=50, window_seconds=60),
            'ip_chat': RateLimit(requests=30, window_seconds=60),
            
            # Per-user limits (authenticated)
            'user_general': RateLimit(requests=200, window_seconds=60),
            'user_grammar': RateLimit(requests=100, window_seconds=60),
            'user_chat': RateLimit(requests=60, window_seconds=60),
            
            # Expensive operations
            'comprehensive_grammar': RateLimit(requests=10, window_seconds=300),
            'ai_generation': RateLimit(requests=20, window_seconds=300),
        }
        
        # Storage for rate limiting data
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_ips: Dict[str, List[SecurityEvent]] = defaultdict(list)
        
        # Security monitoring
        self.security_events: List[SecurityEvent] = []
        self.max_security_events = 1000
        
        # Cleanup intervals
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def get_client_ip(self, request: Request) -> str:
        """Extract real client IP from request"""
        # Check for forwarded headers (Railway, Cloudflare, etc.)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _create_key(self, identifier: str, limit_type: str) -> str:
        """Create a unique key for rate limiting"""
        return f"{limit_type}:{identifier}"
    
    def _is_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now() - block_time < timedelta(hours=1):  # 1 hour block
                return True
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip_address]
        return False
    
    def _record_security_event(self, ip_address: str, event_type: str, 
                              severity: str, details: str):
        """Record security event for monitoring"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            ip_address=ip_address,
            event_type=event_type,
            severity=severity,
            details=details
        )
        
        self.security_events.append(event)
        self.suspicious_ips[ip_address].append(event)
        
        # Limit memory usage
        if len(self.security_events) > self.max_security_events:
            self.security_events = self.security_events[-self.max_security_events//2:]
        
        logger.warning(f"Security event: {event_type} from {ip_address} - {details}")
    
    def _detect_suspicious_activity(self, ip_address: str) -> bool:
        """Detect suspicious patterns in IP activity"""
        if ip_address not in self.suspicious_ips:
            return False
        
        events = self.suspicious_ips[ip_address]
        recent_events = [
            e for e in events 
            if datetime.now() - e.timestamp < timedelta(minutes=15)
        ]
        
        # Suspicious patterns
        if len(recent_events) > 20:  # Too many events in 15 minutes
            return True
        
        # Multiple different attack types
        event_types = set(e.event_type for e in recent_events)
        if len(event_types) > 3:
            return True
        
        # High severity events
        high_severity = [e for e in recent_events if e.severity == 'high']
        if len(high_severity) > 5:
            return True
        
        return False
    
    def _check_rate_limit(self, key: str, limit: RateLimit) -> Tuple[bool, int]:
        """Check if request exceeds rate limit"""
        now = time.time()
        window_start = now - limit.window_seconds
        
        # Get request timestamps for this key
        requests = self.request_counts[key]
        
        # Remove old requests outside the window
        while requests and requests[0] <= window_start:
            requests.popleft()
        
        # Check if limit exceeded
        current_count = len(requests)
        
        # Handle burst limits
        if limit.burst_limit and current_count < limit.burst_limit:
            # Allow burst requests
            requests.append(now)
            return True, limit.requests - current_count - 1
        
        if current_count >= limit.requests:
            return False, 0
        
        # Record this request
        requests.append(now)
        return True, limit.requests - current_count - 1
    
    async def check_rate_limit(self, request: Request, endpoint_type: str = "general",
                              user_id: Optional[str] = None) -> bool:
        """
        Comprehensive rate limit check
        
        Args:
            request: FastAPI request object
            endpoint_type: Type of endpoint (general, auth, grammar, chat, etc.)
            user_id: User ID if authenticated
        
        Returns:
            True if request is allowed, raises HTTPException if blocked
        """
        ip_address = self.get_client_ip(request)
        
        # Cleanup old data periodically
        if time.time() - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_old_data()
        
        # Check if IP is blocked
        if self._is_blocked(ip_address):
            self._record_security_event(
                ip_address, "blocked_request", "high",
                f"Request from blocked IP to {endpoint_type}"
            )
            raise HTTPException(
                status_code=429,
                detail="IP address is temporarily blocked due to suspicious activity"
            )
        
        # Check global rate limit
        global_key = self._create_key("global", "global")
        global_allowed, global_remaining = self._check_rate_limit(
            global_key, self.limits['global']
        )
        
        if not global_allowed:
            self._record_security_event(
                ip_address, "global_rate_limit", "medium",
                f"Global rate limit exceeded from {ip_address}"
            )
            raise HTTPException(
                status_code=429,
                detail="Server is experiencing high load. Please try again later."
            )
        
        # Check IP-specific rate limits
        ip_limit_key = f"ip_{endpoint_type}"
        if ip_limit_key in self.limits:
            ip_key = self._create_key(ip_address, ip_limit_key)
            ip_allowed, ip_remaining = self._check_rate_limit(
                ip_key, self.limits[ip_limit_key]
            )
            
            if not ip_allowed:
                self._record_security_event(
                    ip_address, f"ip_rate_limit_{endpoint_type}", "medium",
                    f"IP rate limit exceeded for {endpoint_type}"
                )
                
                # Check for suspicious activity
                if self._detect_suspicious_activity(ip_address):
                    self.blocked_ips[ip_address] = datetime.now()
                    self._record_security_event(
                        ip_address, "ip_blocked", "high",
                        "IP blocked due to suspicious activity pattern"
                    )
                
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for {endpoint_type}. Try again in {self.limits[ip_limit_key].window_seconds} seconds."
                )
        
        # Check user-specific rate limits (if authenticated)
        if user_id:
            user_limit_key = f"user_{endpoint_type}"
            if user_limit_key in self.limits:
                user_key = self._create_key(user_id, user_limit_key)
                user_allowed, user_remaining = self._check_rate_limit(
                    user_key, self.limits[user_limit_key]
                )
                
                if not user_allowed:
                    self._record_security_event(
                        ip_address, f"user_rate_limit_{endpoint_type}", "low",
                        f"User {user_id} rate limit exceeded for {endpoint_type}"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail=f"User rate limit exceeded for {endpoint_type}. Try again later."
                    )
        
        return True
    
    async def _cleanup_old_data(self):
        """Clean up old rate limiting data to prevent memory leaks"""
        now = time.time()
        cutoff_time = now - 3600  # Keep data for 1 hour
        
        # Clean up request counts
        keys_to_remove = []
        for key, requests in self.request_counts.items():
            # Remove old requests
            while requests and requests[0] <= cutoff_time:
                requests.popleft()
            
            # Remove empty deques
            if not requests:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_counts[key]
        
        # Clean up old security events
        cutoff_datetime = datetime.now() - timedelta(hours=24)
        self.security_events = [
            e for e in self.security_events 
            if e.timestamp > cutoff_datetime
        ]
        
        # Clean up suspicious IPs data
        for ip in list(self.suspicious_ips.keys()):
            self.suspicious_ips[ip] = [
                e for e in self.suspicious_ips[ip]
                if e.timestamp > cutoff_datetime
            ]
            if not self.suspicious_ips[ip]:
                del self.suspicious_ips[ip]
        
        self.last_cleanup = now
        logger.info("Rate limiter cleanup completed")
    
    def get_security_stats(self) -> Dict:
        """Get security statistics for monitoring"""
        recent_events = [
            e for e in self.security_events
            if datetime.now() - e.timestamp < timedelta(hours=1)
        ]
        
        return {
            "total_blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "recent_security_events": len(recent_events),
            "active_rate_limits": len(self.request_counts),
            "security_events_by_type": {
                event_type: len([e for e in recent_events if e.event_type == event_type])
                for event_type in set(e.event_type for e in recent_events)
            }
        }

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

# FastAPI dependency
async def check_rate_limit(request: Request, endpoint_type: str = "general",
                          user_id: Optional[str] = None):
    """FastAPI dependency for rate limiting"""
    return await rate_limiter.check_rate_limit(request, endpoint_type, user_id) 