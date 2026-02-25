"""
Security Middleware for DOG Writer

Implements comprehensive security headers, rate limiting, and security protections
following OWASP best practices and security standards.
"""

import time
import logging
import ipaddress
from typing import Dict
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

        # Rate limiting storage (in production with multiple instances, use Redis)
        self.rate_limit_storage: Dict[str, list] = {}
        # blocked_ips maps IP -> block timestamp for auto-expiry
        self.blocked_ips: Dict[str, float] = {}
        self.block_duration = 1800  # 30 minutes

        # Conservative default limits for cost and abuse control
        self.rate_limit_requests = 60
        self.rate_limit_window = 60     # seconds
        self.block_threshold = 120
        self.max_request_size = 10 * 1024 * 1024

        # Allow a small burst for initial page load while keeping abuse resistance high
        self.burst_allowance = 10
        self.burst_window = 15          # 15 seconds burst window

        # Security headers configuration
        self.security_headers = {
            # Core Content Security
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",

            # Referrer and Cross-Origin Policies
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "cross-origin",

            # Enhanced Permissions Policy
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

            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self'; "
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

            # 1. Check if IP is blocked (with auto-expiry)
            if self._is_blocked(client_ip):
                logger.warning(f"Blocked IP attempted access: {client_ip}")
                response = JSONResponse(
                    status_code=429,
                    content={"error": "IP temporarily blocked due to excessive requests"}
                )
                self._add_security_headers(response)
                return response

            # 2. Rate limiting
            if not self._check_rate_limit(client_ip):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                response = JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded. Please try again later."}
                )
                self._add_security_headers(response)
                return response

            # 3. Request size validation
            if not await self._validate_request_size(request):
                logger.warning(f"Request size exceeded limit from IP: {client_ip}")
                response = JSONResponse(
                    status_code=413,
                    content={"error": "Request too large"}
                )
                self._add_security_headers(response)
                return response

            # 4. Security headers check
            if not self._validate_request_headers(request):
                logger.warning(f"Suspicious request headers from IP: {client_ip}")
                response = JSONResponse(
                    status_code=400,
                    content={"error": "Invalid request headers"}
                )
                self._add_security_headers(response)
                return response

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
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
            self._add_security_headers(response)
            return response

    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address from behind a reverse proxy.

        On Railway (and most PaaS), the app sits behind a reverse proxy.
        X-Forwarded-For contains: client, proxy1, proxy2, ...
        The rightmost entry is added by the trusted proxy and is most reliable.
        We use the last entry to prevent IP spoofing via client-set headers.
        """
        # X-Forwarded-For: use the rightmost (proxy-appended) IP
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            # Rightmost IP is the one added by the trusted reverse proxy
            ips = [ip.strip() for ip in xff.split(",")]
            # Use the last IP (added by the reverse proxy closest to us)
            ip = ips[-1]
            if self._is_valid_ip(ip):
                return ip

        # Fallback to client host (direct connection IP)
        return request.client.host if request.client else "unknown"

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _is_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked, with auto-expiry"""
        if client_ip in self.blocked_ips:
            blocked_at = self.blocked_ips[client_ip]
            if time.time() - blocked_at < self.block_duration:
                return True
            # Block expired — auto-unblock
            del self.blocked_ips[client_ip]
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

        # Check burst allowance first (for initial page loads)
        recent_requests = [req_time for req_time in requests
                          if current_time - req_time < self.burst_window]

        if len(recent_requests) >= self.burst_allowance:
            logger.warning(f"Burst limit exceeded for IP: {client_ip} ({len(recent_requests)} requests in {self.burst_window}s)")
            return False

        # Check if within overall rate limit
        if len(requests) >= self.rate_limit_requests:
            # Check if should block IP
            if len(requests) >= self.block_threshold:
                self.blocked_ips[client_ip] = current_time
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
        """Validate request headers for suspicious patterns.

        Only checks non-standard headers to avoid false positives
        from legitimate User-Agent strings like "JavaScriptCore".
        """
        suspicious_patterns = [
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "eval(",
            "document.cookie"
        ]

        # Standard headers that may legitimately contain pattern substrings
        skip_headers = {
            "user-agent", "referer", "accept", "accept-language",
            "accept-encoding", "content-type", "authorization",
            "cookie", "host", "origin", "connection", "cache-control",
            "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site",
            "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
        }

        for header_name, header_value in request.headers.items():
            if header_name.lower() in skip_headers:
                continue
            header_value_lower = header_value.lower()
            for pattern in suspicious_patterns:
                if pattern in header_value_lower:
                    logger.warning(f"Suspicious pattern '{pattern}' in header '{header_name}'")
                    return False

        return True

    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value

        # Add server header obfuscation
        response.headers["Server"] = "DOG-Writer/1.0"

        # Remove potentially sensitive headers
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
            del self.blocked_ips[ip]
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
            del self.blocked_ips[ip]
            cleared = True
        if cleared:
            logger.info(f"Rate limiting data cleared for IP: {ip}")
        return cleared
