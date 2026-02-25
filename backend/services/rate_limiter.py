import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from utils.request_helpers import get_client_ip as extract_client_ip

logger = logging.getLogger(__name__)

class SimpleRateLimiter:
    """Simple rate limiting for MVP"""
    
    def __init__(self, block_duration: timedelta = timedelta(minutes=30)):
        # Basic rate limits
        self.limits = {
            'general': {'requests': 30, 'window': 60},   # 30 req/min
            'auth': {'requests': 4, 'window': 300},      # 4 auth/5min
            'chat': {'requests': 8, 'window': 60},       # 8 chat/min
            'grammar': {'requests': 20, 'window': 60},   # 20 grammar/min
        }
        
        # Storage for request counts
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.block_duration = block_duration
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        ip_address = extract_client_ip(request)
        return ip_address if ip_address else "unknown"

    def is_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now() - block_time < self.block_duration:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False
    
    def check_rate_limit(self, request: Request, endpoint_type: str = "general") -> bool:
        """
        Simple rate limit check
        
        Args:
            request: FastAPI request object
            endpoint_type: Type of endpoint (general, auth, chat, grammar)
        
        Returns:
            True if request is allowed, raises HTTPException if blocked
        """
        ip_address = self.get_client_ip(request)
        
        # Check if IP is blocked
        if self.is_blocked(ip_address):
            logger.warning(f"Blocked IP attempted request: {ip_address}")
            raise HTTPException(
                status_code=429,
                detail="IP address is temporarily blocked due to too many requests"
            )
        
        # Get rate limit for endpoint type
        limit = self.limits.get(endpoint_type, self.limits['general'])
        
        # Create key for this IP and endpoint
        key = f"{ip_address}:{endpoint_type}"
        
        # Check rate limit
        now = time.time()
        window_start = now - limit['window']
        
        # Get request timestamps
        requests = self.request_counts[key]
        
        # Remove old requests
        while requests and requests[0] <= window_start:
            requests.popleft()
        
        # Check if limit exceeded
        if len(requests) >= limit['requests']:
            logger.warning(f"Rate limit exceeded for {ip_address} on {endpoint_type}")
            
            # Block IP if too many violations
            violations_key = f"{ip_address}:violations"
            violations = self.request_counts[violations_key]
            violations.append(now)
            
            # Clean old violations
            violation_window = now - 600  # 10 minutes
            while violations and violations[0] <= violation_window:
                violations.popleft()
            
            # Block if more than 5 violations in 10 minutes
            if len(violations) > 5:
                self.blocked_ips[ip_address] = datetime.now()
                logger.warning(f"IP blocked for repeated violations: {ip_address}")
                raise HTTPException(
                    status_code=429,
                    detail="IP address blocked due to repeated rate limit violations"
                )
            
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {limit['window']} seconds."
            )
        
        # Record this request
        requests.append(now)
        
        # Cleanup old data periodically (every 5 minutes)
        if not hasattr(self, 'last_cleanup_time'):
            self.last_cleanup_time = now
        if now - self.last_cleanup_time >= 300:
            self._cleanup_old_data()
            self.last_cleanup_time = now
        
        return True
    
    def _cleanup_old_data(self):
        """Clean up old rate limiting data"""
        now = time.time()
        keys_to_remove = []
        
        for key, requests in self.request_counts.items():
            # Remove requests older than 1 hour
            cutoff = now - 3600
            while requests and requests[0] < cutoff:
                requests.popleft()
            
            # Remove empty queues
            if not requests:
                keys_to_remove.append(key)
        before_cleanup = len(self.request_counts)
        for key in keys_to_remove:
            del self.request_counts[key]
        after_cleanup = len(self.request_counts)
        logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit entries (before: {before_cleanup}, after: {after_cleanup})")

# Global instance
rate_limiter = SimpleRateLimiter()

# Helper function for easy use
async def check_rate_limit(request: Request, endpoint_type: str = "general"):
    """Check rate limit for request"""
    return rate_limiter.check_rate_limit(request, endpoint_type) 
