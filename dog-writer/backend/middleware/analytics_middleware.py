"""
Analytics Middleware for DOG Writer
Automatic tracking of user interactions and API usage with privacy compliance
"""

import time
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from services.analytics_service import analytics_service
from config.analytics_config import analytics_config, TRACKED_EVENTS

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic analytics tracking
    
    Features:
    - Automatic API endpoint tracking
    - Request/response time monitoring
    - Error tracking
    - User session management
    - Privacy-compliant data collection
    """
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health", 
            "/api/health", 
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/favicon.ico"
        ]
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and track analytics"""
        start_time = time.time()
        
        # Skip tracking for excluded paths
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Extract user information
        user_id = self._extract_user_id(request)
        session_id = self._get_or_create_session_id(request, user_id)
        
        # Track request start
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent", ""),
            "ip_address": self._get_client_ip(request),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Process request
        response = None
        error_occurred = False
        
        try:
            response = await call_next(request)
            
        except Exception as e:
            error_occurred = True
            logger.error(f"Request error: {e}")
            
            # Track API error
            analytics_service.track_event(
                "api_error",
                user_id=user_id,
                properties={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:200]  # Limit error message length
                },
                session_id=session_id
            )
            
            # Re-raise the exception
            raise
        
        finally:
            # Calculate response time
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Track successful API calls
            if not error_occurred and response:
                await self._track_api_call(
                    request, 
                    response, 
                    user_id, 
                    session_id, 
                    response_time_ms
                )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from tracking"""
        return any(excluded in path for excluded in self.exclude_paths)
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (JWT token, session, etc.)"""
        try:
            # Try to get from Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # This would decode JWT token to get user ID
                # For now, return None for anonymous tracking
                return None
            
            # Try to get from session or cookies
            # This would integrate with your auth system
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract user ID: {e}")
            return None
    
    def _get_or_create_session_id(self, request: Request, user_id: Optional[str]) -> str:
        """Get or create session ID for tracking"""
        # Try to get existing session ID from headers or cookies
        session_id = request.headers.get("x-session-id")
        
        if not session_id:
            # Generate new session ID
            session_id = str(uuid.uuid4())
        
        # Update session info
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "request_count": 0
            }
        
        # Update last activity
        self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
        self.active_sessions[session_id]["request_count"] += 1
        
        return session_id
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with privacy considerations"""
        if not analytics_config.anonymize_ip:
            # Get real IP if anonymization is disabled
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            return request.client.host if request.client else "unknown"
        else:
            # Return anonymized IP for privacy
            return "anonymized"
    
    async def _track_api_call(
        self, 
        request: Request, 
        response: Response, 
        user_id: Optional[str], 
        session_id: str, 
        response_time_ms: float
    ):
        """Track API call analytics"""
        try:
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            # Determine event name based on endpoint
            event_name = self._get_event_name_for_endpoint(endpoint, method)
            
            # Prepare analytics properties
            properties = {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "user_agent": request.headers.get("user-agent", "")[:100],  # Limit length
            }
            
            # Add specific tracking for document operations
            if "/api/documents" in endpoint:
                await self._track_document_operation(request, response, properties)
            
            # Add specific tracking for chat operations
            elif "/api/chat" in endpoint:
                await self._track_chat_operation(request, response, properties)
            
            # Track the event
            if event_name:
                analytics_service.track_event(
                    event_name,
                    user_id=user_id,
                    properties=properties,
                    session_id=session_id
                )
            
            # Track performance metrics
            analytics_service.track_event(
                "page_load_time",
                user_id=user_id,
                properties={
                    "endpoint": endpoint,
                    "response_time_ms": response_time_ms,
                    "status_code": status_code
                },
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
    
    def _get_event_name_for_endpoint(self, endpoint: str, method: str) -> Optional[str]:
        """Map API endpoints to analytics event names"""
        endpoint_mappings = {
            # Document operations
            ("/api/documents", "POST"): "document_created",
            ("/api/documents", "GET"): "documents_listed",
            ("/api/documents/", "PUT"): "document_saved",
            ("/api/documents/", "DELETE"): "document_deleted",
            
            # Chat operations
            ("/api/chat/message", "POST"): "ai_chat_message",
            ("/api/chat/basic", "GET"): "ai_chat_basic",
            
            # User operations
            ("/api/auth/login", "POST"): "user_login",
            ("/api/auth/logout", "POST"): "user_logout",
            ("/api/auth/register", "POST"): "user_signup",
        }
        
        # Check exact matches first
        key = (endpoint, method)
        if key in endpoint_mappings:
            return endpoint_mappings[key]
        
        # Check partial matches for dynamic routes
        for (pattern, pattern_method), event_name in endpoint_mappings.items():
            if pattern in endpoint and method == pattern_method:
                return event_name
        
        return None
    
    async def _track_document_operation(
        self, 
        request: Request, 
        response: Response, 
        properties: Dict[str, Any]
    ):
        """Add document-specific tracking properties"""
        try:
            # Extract document ID from URL if present
            path_parts = request.url.path.split("/")
            if len(path_parts) > 3 and path_parts[2] == "documents":
                document_id = path_parts[3] if len(path_parts) > 3 else None
                if document_id:
                    properties["document_id"] = document_id
            
            # For POST requests (document creation), try to get document info from response
            if request.method == "POST" and response.status_code == 201:
                # This would extract document info from response body if needed
                properties["operation"] = "create"
            elif request.method == "PUT":
                properties["operation"] = "update"
            elif request.method == "DELETE":
                properties["operation"] = "delete"
            elif request.method == "GET":
                properties["operation"] = "read"
                
        except Exception as e:
            logger.debug(f"Error tracking document operation: {e}")
    
    async def _track_chat_operation(
        self, 
        request: Request, 
        response: Response, 
        properties: Dict[str, Any]
    ):
        """Add chat-specific tracking properties"""
        try:
            # Add chat-specific properties
            properties["feature"] = "ai_chat"
            
            # Try to extract chat parameters from request body (if available)
            if request.method == "POST":
                # This would extract chat parameters like model, message length, etc.
                properties["operation"] = "send_message"
            
        except Exception as e:
            logger.debug(f"Error tracking chat operation: {e}")

class WritingSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for tracking writing sessions
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.writing_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Track writing session data"""
        
        # Only track document-related requests
        if "/api/documents" not in request.url.path:
            return await call_next(request)
        
        user_id = self._extract_user_id(request)
        session_id = request.headers.get("x-session-id", str(uuid.uuid4()))
        
        # Track writing session start/activity
        if request.method in ["POST", "PUT"]:
            await self._track_writing_activity(request, user_id, session_id)
        
        response = await call_next(request)
        return response
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        # This would integrate with your auth system
        return None
    
    async def _track_writing_activity(
        self, 
        request: Request, 
        user_id: Optional[str], 
        session_id: str
    ):
        """Track writing activity"""
        try:
            # This would extract writing data from request body
            # and track it using the writing analytics service
            
            analytics_service.track_event(
                "writing_session_start",
                user_id=user_id,
                properties={
                    "endpoint": request.url.path,
                    "method": request.method
                },
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error tracking writing activity: {e}")

# Middleware factory functions
def create_analytics_middleware(exclude_paths: Optional[list] = None):
    """Create analytics middleware with custom configuration"""
    def middleware_factory(app):
        return AnalyticsMiddleware(app, exclude_paths=exclude_paths)
    return middleware_factory

def create_writing_session_middleware():
    """Create writing session middleware"""
    def middleware_factory(app):
        return WritingSessionMiddleware(app)
    return middleware_factory 
Analytics Middleware for DOG Writer
Automatic tracking of user interactions and API usage with privacy compliance
"""

import time
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from services.analytics_service import analytics_service
from config.analytics_config import analytics_config, TRACKED_EVENTS

logger = logging.getLogger(__name__)

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic analytics tracking
    
    Features:
    - Automatic API endpoint tracking
    - Request/response time monitoring
    - Error tracking
    - User session management
    - Privacy-compliant data collection
    """
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health", 
            "/api/health", 
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/favicon.ico"
        ]
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and track analytics"""
        start_time = time.time()
        
        # Skip tracking for excluded paths
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Extract user information
        user_id = self._extract_user_id(request)
        session_id = self._get_or_create_session_id(request, user_id)
        
        # Track request start
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent", ""),
            "ip_address": self._get_client_ip(request),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Process request
        response = None
        error_occurred = False
        
        try:
            response = await call_next(request)
            
        except Exception as e:
            error_occurred = True
            logger.error(f"Request error: {e}")
            
            # Track API error
            analytics_service.track_event(
                "api_error",
                user_id=user_id,
                properties={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:200]  # Limit error message length
                },
                session_id=session_id
            )
            
            # Re-raise the exception
            raise
        
        finally:
            # Calculate response time
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Track successful API calls
            if not error_occurred and response:
                await self._track_api_call(
                    request, 
                    response, 
                    user_id, 
                    session_id, 
                    response_time_ms
                )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from tracking"""
        return any(excluded in path for excluded in self.exclude_paths)
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (JWT token, session, etc.)"""
        try:
            # Try to get from Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                # This would decode JWT token to get user ID
                # For now, return None for anonymous tracking
                return None
            
            # Try to get from session or cookies
            # This would integrate with your auth system
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract user ID: {e}")
            return None
    
    def _get_or_create_session_id(self, request: Request, user_id: Optional[str]) -> str:
        """Get or create session ID for tracking"""
        # Try to get existing session ID from headers or cookies
        session_id = request.headers.get("x-session-id")
        
        if not session_id:
            # Generate new session ID
            session_id = str(uuid.uuid4())
        
        # Update session info
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "request_count": 0
            }
        
        # Update last activity
        self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
        self.active_sessions[session_id]["request_count"] += 1
        
        return session_id
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address with privacy considerations"""
        if not analytics_config.anonymize_ip:
            # Get real IP if anonymization is disabled
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            return request.client.host if request.client else "unknown"
        else:
            # Return anonymized IP for privacy
            return "anonymized"
    
    async def _track_api_call(
        self, 
        request: Request, 
        response: Response, 
        user_id: Optional[str], 
        session_id: str, 
        response_time_ms: float
    ):
        """Track API call analytics"""
        try:
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            # Determine event name based on endpoint
            event_name = self._get_event_name_for_endpoint(endpoint, method)
            
            # Prepare analytics properties
            properties = {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "user_agent": request.headers.get("user-agent", "")[:100],  # Limit length
            }
            
            # Add specific tracking for document operations
            if "/api/documents" in endpoint:
                await self._track_document_operation(request, response, properties)
            
            # Add specific tracking for chat operations
            elif "/api/chat" in endpoint:
                await self._track_chat_operation(request, response, properties)
            
            # Track the event
            if event_name:
                analytics_service.track_event(
                    event_name,
                    user_id=user_id,
                    properties=properties,
                    session_id=session_id
                )
            
            # Track performance metrics
            analytics_service.track_event(
                "page_load_time",
                user_id=user_id,
                properties={
                    "endpoint": endpoint,
                    "response_time_ms": response_time_ms,
                    "status_code": status_code
                },
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
    
    def _get_event_name_for_endpoint(self, endpoint: str, method: str) -> Optional[str]:
        """Map API endpoints to analytics event names"""
        endpoint_mappings = {
            # Document operations
            ("/api/documents", "POST"): "document_created",
            ("/api/documents", "GET"): "documents_listed",
            ("/api/documents/", "PUT"): "document_saved",
            ("/api/documents/", "DELETE"): "document_deleted",
            
            # Chat operations
            ("/api/chat/message", "POST"): "ai_chat_message",
            ("/api/chat/basic", "GET"): "ai_chat_basic",
            
            # User operations
            ("/api/auth/login", "POST"): "user_login",
            ("/api/auth/logout", "POST"): "user_logout",
            ("/api/auth/register", "POST"): "user_signup",
        }
        
        # Check exact matches first
        key = (endpoint, method)
        if key in endpoint_mappings:
            return endpoint_mappings[key]
        
        # Check partial matches for dynamic routes
        for (pattern, pattern_method), event_name in endpoint_mappings.items():
            if pattern in endpoint and method == pattern_method:
                return event_name
        
        return None
    
    async def _track_document_operation(
        self, 
        request: Request, 
        response: Response, 
        properties: Dict[str, Any]
    ):
        """Add document-specific tracking properties"""
        try:
            # Extract document ID from URL if present
            path_parts = request.url.path.split("/")
            if len(path_parts) > 3 and path_parts[2] == "documents":
                document_id = path_parts[3] if len(path_parts) > 3 else None
                if document_id:
                    properties["document_id"] = document_id
            
            # For POST requests (document creation), try to get document info from response
            if request.method == "POST" and response.status_code == 201:
                # This would extract document info from response body if needed
                properties["operation"] = "create"
            elif request.method == "PUT":
                properties["operation"] = "update"
            elif request.method == "DELETE":
                properties["operation"] = "delete"
            elif request.method == "GET":
                properties["operation"] = "read"
                
        except Exception as e:
            logger.debug(f"Error tracking document operation: {e}")
    
    async def _track_chat_operation(
        self, 
        request: Request, 
        response: Response, 
        properties: Dict[str, Any]
    ):
        """Add chat-specific tracking properties"""
        try:
            # Add chat-specific properties
            properties["feature"] = "ai_chat"
            
            # Try to extract chat parameters from request body (if available)
            if request.method == "POST":
                # This would extract chat parameters like model, message length, etc.
                properties["operation"] = "send_message"
            
        except Exception as e:
            logger.debug(f"Error tracking chat operation: {e}")

class WritingSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware specifically for tracking writing sessions
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.writing_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Track writing session data"""
        
        # Only track document-related requests
        if "/api/documents" not in request.url.path:
            return await call_next(request)
        
        user_id = self._extract_user_id(request)
        session_id = request.headers.get("x-session-id", str(uuid.uuid4()))
        
        # Track writing session start/activity
        if request.method in ["POST", "PUT"]:
            await self._track_writing_activity(request, user_id, session_id)
        
        response = await call_next(request)
        return response
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        # This would integrate with your auth system
        return None
    
    async def _track_writing_activity(
        self, 
        request: Request, 
        user_id: Optional[str], 
        session_id: str
    ):
        """Track writing activity"""
        try:
            # This would extract writing data from request body
            # and track it using the writing analytics service
            
            analytics_service.track_event(
                "writing_session_start",
                user_id=user_id,
                properties={
                    "endpoint": request.url.path,
                    "method": request.method
                },
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error tracking writing activity: {e}")

# Middleware factory functions
def create_analytics_middleware(exclude_paths: Optional[list] = None):
    """Create analytics middleware with custom configuration"""
    def middleware_factory(app):
        return AnalyticsMiddleware(app, exclude_paths=exclude_paths)
    return middleware_factory

def create_writing_session_middleware():
    """Create writing session middleware"""
    def middleware_factory(app):
        return WritingSessionMiddleware(app)
    return middleware_factory 