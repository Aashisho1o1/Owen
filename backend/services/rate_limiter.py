"""
Simple Rate Limiting Service for MVP

Basic rate limiting with IP-based protection.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

class SimpleRateLimiter:
    """Simple rate limiting for MVP"""
    
    def __init__(self):
        # Basic rate limits
        self.limits = {
            'general': {'requests': 100, 'window': 60},  # 100 req/min
            'auth': {'requests': 5, 'window': 300},      # 5 auth/5min
            'chat': {'requests': 30, 'window': 60},      # 30 chat/min
            'grammar': {'requests': 50, 'window': 60},   # 50 grammar/min
        }
        
        # Storage for request counts
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"
    
    def is_blocked(self, ip_address: str) -> bool:
        """Check if IP is currently blocked"""
        if ip_address in self.blocked_ips:
            block_time = self.blocked_ips[ip_address]
            if datetime.now() - block_time < timedelta(minutes=30):  # 30 min block
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
        
        # Cleanup old data periodically
        if now % 300 < 1:  # Every 5 minutes
            self._cleanup_old_data()
        
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
        
        for key in keys_to_remove:
            del self.request_counts[key]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit entries")

# Global instance
rate_limiter = SimpleRateLimiter()

# Helper function for easy use
async def check_rate_limit(request: Request, endpoint_type: str = "general"):
    """Check rate limit for request"""
    return rate_limiter.check_rate_limit(request, endpoint_type) 