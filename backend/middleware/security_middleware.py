"""
Security Middleware for DOG Writer

Implements comprehensive security headers, rate limiting, and security protections
following OWASP best practices and security standards.
"""

import time
import hashlib
import logging
from typing import Dict, Set
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware implementing:
    - Security headers (OWASP recommendations)
    - Rate limiting per IP
    - Content Security Policy
    - Request validation
    - Security logging
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage: Dict[str, list] = {}
        self.blocked_ips: Set[str] = set()
        
        # Conservative default limits for cost and abuse control
        self.rate_limit_requests = 60
        self.rate_limit_window = 60     # seconds
        self.block_threshold = 120
        self.max_request_size = 10 * 1024 * 1024
        
        # Allow a small burst for initial page load while keeping abuse resistance high
        self.burst_allowance = 10
        self.burst_window = 15          # 15 seconds burst window
        
        # Enhanced security headers configuration (2025 OWASP standards)
        self.security_headers = {
            # Core Content Security
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer and Cross-Origin Policies
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "cross-origin",
            
            # Enhanced Permissions Policy (2025 update)
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=(), "
                "accelerometer=(), ambient-light-sensor=(), autoplay=(), "
                "encrypted-media=(), fullscreen=(), picture-in-picture=(), "
                "web-share=(), clipboard-read=(), clipboard-write=(), "
                "notifications=(), push=(), speaker-selection=(), "
                "screen-wake-lock=(), idle-detection=(), "
                "storage-access=(), display-capture=()"
            ),
            
            # Comprehensive Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https://api.languagetool.org https://api.openai.com https://generativelanguage.googleapis.com; "
                "media-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            ),
            
            # Transport Security
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Cache Control for sensitive data
            "Cache-Control": "no-cache, no-store, must-revalidate, private",
            "Pragma": "no-cache",
            "Expires": "0",
            
            # Rate limiting information
            "X-Rate-Limit-Policy": "60-per-minute-per-ip"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        try:
            # SPECIAL HANDLING FOR CORS PREFLIGHT REQUESTS
            # Allow OPTIONS requests (CORS preflight) to pass through with minimal checks
            if request.method == "OPTIONS":
                logger.debug(f"CORS preflight request from {client_ip} to {request.url.path}")
                response = await call_next(request)
                self._add_security_headers(response)
                return response
            
            # 1. Check if IP is blocked
            if client_ip in self.blocked_ips:
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                response = JSONResponse(
                    status_code=429,
                    content={"error": "IP temporarily blocked due to excessive requests"}
                )
                # CRITICAL FIX: Add CORS headers to blocked IP responses
                self._add_security_headers(response)
                return response
            
            # 2. Rate limiting
            if not self._check_rate_limit(client_ip):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                response = JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded. Please try again later."}
                )
                # CRITICAL FIX: Add CORS headers to rate-limited responses
                self._add_security_headers(response)
                return response
            
            # 3. Request size validation
            if not await self._validate_request_size(request):
                logger.warning(f"Request size exceeded limit from IP: {client_ip}")
                return JSONResponse(
                    status_code=413,
                    content={"error": "Request too large"}
                )
            
            # 4. Security headers check
            if not self._validate_request_headers(request):
                logger.warning(f"Suspicious request headers from IP: {client_ip}")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid request headers"}
                )
            
            # 5. Process request
            response = await call_next(request)
            
            # 6. Add security headers to response
            self._add_security_headers(response)
            
            # 7. Log security metrics
            processing_time = time.time() - start_time
            self._log_security_metrics(request, response, processing_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            # Don't expose internal errors
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address handling proxies"""
        # Check for forwarded headers (in order of trust)
        forwarded_headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "CF-Connecting-IP",  # Cloudflare
            "X-Client-IP"
        ]
        
        for header in forwarded_headers:
            if header in request.headers:
                # Take first IP from comma-separated list
                ip = request.headers[header].split(",")[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check and update rate limiting for client IP with burst allowance"""
        current_time = time.time()
        
        # Initialize IP tracking if not exists
        if client_ip not in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = []
        
        # Remove old requests outside the window
        requests = self.rate_limit_storage[client_ip]
        requests[:] = [req_time for req_time in requests 
                      if current_time - req_time < self.rate_limit_window]
        
        # FIXED: Check burst allowance first (for initial page loads)
        recent_requests = [req_time for req_time in requests 
                          if current_time - req_time < self.burst_window]
        
        if len(recent_requests) >= self.burst_allowance:
            logger.warning(f"Burst limit exceeded for IP: {client_ip} ({len(recent_requests)} requests in {self.burst_window}s)")
            return False
        
        # Check if within overall rate limit
        if len(requests) >= self.rate_limit_requests:
            # Check if should block IP
            if len(requests) >= self.block_threshold:
                self.blocked_ips.add(client_ip)
                logger.critical(f"IP blocked for excessive requests: {client_ip}")
            return False
        
        # Add current request
        requests.append(current_time)
        return True
    
    async def _validate_request_size(self, request: Request) -> bool:
        """Validate request size to prevent DoS attacks"""
        try:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                return False
            return True
        except (ValueError, TypeError):
            return True  # Allow if can't determine size
    
    def _validate_request_headers(self, request: Request) -> bool:
        """Validate request headers for suspicious patterns"""
        suspicious_patterns = [
            "script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "<script",
            "eval(",
            "document.cookie"
        ]
        
        # Check all header values
        for header_name, header_value in request.headers.items():
            header_value_lower = header_value.lower()
            for pattern in suspicious_patterns:
                if pattern in header_value_lower:
                    logger.warning(f"Suspicious pattern '{pattern}' in header '{header_name}': {header_value}")
                    return False
        
        return True
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        # Add server header obfuscation
        response.headers["Server"] = "DOG-Writer/1.0"
        
        # Remove potentially sensitive headers (use del instead of pop for MutableHeaders)
        sensitive_headers = ["X-Powered-By"]
        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]
    
    def _log_security_metrics(self, request: Request, response: Response, processing_time: float):
        """Log security-related metrics"""
        client_ip = self._get_client_ip(request)
        
        # Log based on response status
        if response.status_code >= 400:
            logger.warning(
                f"Security Alert - IP: {client_ip}, "
                f"Method: {request.method}, "
                f"Path: {request.url.path}, "
                f"Status: {response.status_code}, "
                f"Time: {processing_time:.3f}s"
            )
        
        # Log slow requests (potential DoS)
        if processing_time > 5.0:
            logger.warning(
                f"Slow Request - IP: {client_ip}, "
                f"Path: {request.url.path}, "
                f"Time: {processing_time:.3f}s"
            )
    
    def get_security_stats(self) -> Dict:
        """Get current security statistics"""
        return {
            "blocked_ips_count": len(self.blocked_ips),
            "tracked_ips_count": len(self.rate_limit_storage),
            "rate_limit_config": {
                "requests_per_minute": self.rate_limit_requests,
                "window_seconds": self.rate_limit_window,
                "block_threshold": self.block_threshold
            }
        }
    
    def unblock_ip(self, ip: str) -> bool:
        """Manually unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP unblocked: {ip}")
            return True
        return False
    
    def clear_rate_limits(self):
        """Clear all rate limiting data (admin function)"""
        self.rate_limit_storage.clear()
        self.blocked_ips.clear()
        logger.info("Security middleware data cleared")

    def clear_ip_rate_limit(self, ip: str) -> bool:
        """Clear rate limiting data for a specific IP address"""
        cleared = False
        if ip in self.rate_limit_storage:
            del self.rate_limit_storage[ip]
            cleared = True
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            cleared = True
        if cleared:
            logger.info(f"Rate limiting data cleared for IP: {ip}")
        return cleared


# Utility function to create security middleware
def create_security_middleware() -> SecurityMiddleware:
    """Factory function to create security middleware with default config"""
    return SecurityMiddleware 
