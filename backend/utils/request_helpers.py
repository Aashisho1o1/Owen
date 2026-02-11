"""
Shared request helper functions.
"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Extract client IP from common proxy/CDN headers with safe fallback."""
    forwarded_headers = [
        "X-Forwarded-For",
        "X-Real-IP",
        "CF-Connecting-IP",
        "X-Client-IP",
    ]

    for header_name in forwarded_headers:
        header_value = request.headers.get(header_name)
        if header_value:
            ip = header_value.split(",")[0].strip()
            if ip:
                return ip

    if request.client and request.client.host:
        return request.client.host
    return "unknown"
