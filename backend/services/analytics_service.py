"""
Analytics Service for DOG Writer
Privacy-compliant user behavior tracking and writing analytics
"""

import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from queue import Queue, Empty
import threading
import time

import posthog
from config.analytics_config import (
    analytics_config, 
    EventCategory, 
    PrivacyLevel, 
    TRACKED_EVENTS,
    PRIVACY_RULES
)

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    """Structured analytics event"""
    event_name: str
    user_id: Optional[str]
    properties: Dict[str, Any]
    timestamp: datetime
    category: EventCategory
    privacy_level: PrivacyLevel
    session_id: Optional[str] = None
    anonymized: bool = False

@dataclass
class WritingAnalytics:
    """Writing-specific analytics data"""
    user_id: str
    document_id: str
    session_id: str
    word_count: int
    character_count: int
    typing_speed_wpm: float
    session_duration_minutes: float
    sentiment_score: Optional[float] = None
    readability_score: Optional[float] = None
    writing_style_metrics: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class AnalyticsService:
    """
    Comprehensive analytics service with privacy compliance
    
    Features:
    - PostHog integration for user behavior tracking
    - Writing analytics with NLP analysis
    - GDPR-compliant data handling
    - Privacy-first approach with user consent management
    - Real-time and batch processing
    """
    
    def __init__(self):
        self.config = analytics_config
        self.event_queue = Queue(maxsize=self.config.max_queue_size)
        self.writing_analytics_queue = Queue(maxsize=self.config.max_queue_size)
        self.user_consents: Dict[str, Dict[str, bool]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize PostHog if configured
        if self.config.posthog_api_key:
            posthog.api_key = self.config.posthog_api_key
            posthog.host = self.config.posthog_host
            logger.info("PostHog analytics initialized")
        
        # Start background processing
        self._start_background_processors()
    
    def _start_background_processors(self):
        """Start background threads for processing analytics data"""
        # Temporarily disabled background processors for deployment stability
        # TODO: Re-enable after fixing queue processing issues
        logger.info("Analytics background processors temporarily disabled for deployment stability")
    
    def _process_event_queue(self):
        """Process events from the queue in batches"""
        batch = []
        last_flush = time.time()
        
        while True:
            try:
                # Get events from queue with timeout
                try:
                    event = self.event_queue.get(timeout=1.0)
                    batch.append(event)
                except (ValueError, TypeError, KeyError) as e:
                    # Fixed: Specific exception handling instead of bare except
                    # Log the specific error for better debugging and security
                    logger.warning(f"Failed to process analytics event: {e}")
                    continue
                except Exception as e:
                    # Catch any other unexpected exceptions
                    logger.error(f"Unexpected error processing analytics event: {e}")
                    continue
                
                # Flush batch if conditions are met
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.config.batch_size or
                    (batch and current_time - last_flush >= self.config.flush_interval_seconds)
                )
                
                if should_flush and batch:
                    self._flush_event_batch(batch)
                    batch = []
                    last_flush = current_time
                    
            except Exception as e:
                logger.error(f"Error processing event queue: {e}")
                time.sleep(1)
    
    def _process_writing_analytics_queue(self):
        """Process writing analytics from the queue"""
        while True:
            try:
                writing_data = self.writing_analytics_queue.get(timeout=1.0)
                self._process_writing_analytics(writing_data)
            except Empty:
                continue  # Queue is empty, wait for next item
            except Exception as e:
                logger.error(f"Error processing writing analytics: {e}")
                time.sleep(1)
    
    def _flush_event_batch(self, events: List[AnalyticsEvent]):
        """Flush a batch of events to analytics providers"""
        try:
            for event in events:
                # Check user consent before sending
                if not self._has_user_consent(event.user_id, event.privacy_level):
                    continue
                
                # Anonymize if required
                if self.config.anonymize_ip or event.privacy_level == PrivacyLevel.COMPREHENSIVE:
                    event = self._anonymize_event(event)
                
                # Send to PostHog
                if self.config.posthog_api_key:
                    self._send_to_posthog(event)
                
                # Store in local database for analysis
                self._store_event_locally(event)
                
        except Exception as e:
            logger.error(f"Error flushing event batch: {e}")
    
    def _send_to_posthog(self, event: AnalyticsEvent):
        """Send event to PostHog"""
        try:
            posthog.capture(
                distinct_id=event.user_id or "anonymous",
                event=event.event_name,
                properties={
                    **event.properties,
                    "category": event.category.value,
                    "privacy_level": event.privacy_level.value,
                    "session_id": event.session_id,
                    "timestamp": event.timestamp.isoformat(),
                    "anonymized": event.anonymized
                }
            )
        except Exception as e:
            logger.error(f"Error sending event to PostHog: {e}")
    
    def _store_event_locally(self, event: AnalyticsEvent):
        """Store event in local database for analysis"""
        # This would integrate with your existing database service
        # For now, we'll log it
        logger.info(f"Analytics Event: {event.event_name} - User: {event.user_id}")
    
    def _anonymize_event(self, event: AnalyticsEvent) -> AnalyticsEvent:
        """Anonymize event data for privacy compliance"""
        anonymized_event = AnalyticsEvent(
            event_name=event.event_name,
            user_id=self._hash_user_id(event.user_id) if event.user_id else None,
            properties=self._anonymize_properties(event.properties),
            timestamp=event.timestamp,
            category=event.category,
            privacy_level=event.privacy_level,
            session_id=self._hash_session_id(event.session_id) if event.session_id else None,
            anonymized=True
        )
        return anonymized_event
    
    def _hash_user_id(self, user_id: str) -> str:
        """Create anonymous hash of user ID"""
        return hashlib.sha256(f"{user_id}_{self.config.posthog_api_key}".encode()).hexdigest()[:16]
    
    def _hash_session_id(self, session_id: str) -> str:
        """Create anonymous hash of session ID"""
        return hashlib.sha256(session_id.encode()).hexdigest()[:12]
    
    def _anonymize_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or anonymize sensitive properties"""
        anonymized = {}
        
        for key, value in properties.items():
            if key in ['email', 'name', 'phone', 'address']:
                continue  # Skip PII
            elif key == 'content' and isinstance(value, str):
                # For text content, only store metadata
                anonymized[key] = {
                    'length': len(value),
                    'word_count': len(value.split()),
                    'has_content': len(value) > 0
                }
            elif isinstance(value, str):
                # Check for PII patterns
                anonymized[key] = self._redact_pii(value)
            else:
                anonymized[key] = value
        
        return anonymized
    
    def _redact_pii(self, text: str) -> str:
        """Redact personally identifiable information from text"""
        if not PRIVACY_RULES["pii_detection"]["enabled"]:
            return text
        
        redacted_text = text
        for pattern in PRIVACY_RULES["pii_detection"]["patterns"]:
            redacted_text = re.sub(pattern, "[REDACTED]", redacted_text)
        
        return redacted_text
    
    def _has_user_consent(self, user_id: Optional[str], privacy_level: PrivacyLevel) -> bool:
        """Check if user has given consent for this level of tracking"""
        if not user_id or not self.config.require_consent:
            return privacy_level == PrivacyLevel.MINIMAL
        
        user_consent = self.user_consents.get(user_id, {})
        
        if privacy_level == PrivacyLevel.MINIMAL:
            return user_consent.get("essential", True)
        elif privacy_level == PrivacyLevel.STANDARD:
            return user_consent.get("analytics", False)
        elif privacy_level == PrivacyLevel.COMPREHENSIVE:
            return user_consent.get("comprehensive", False)
        
        return False
    
    # Public API Methods
    
    def track_event(
        self, 
        event_name: str, 
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """
        Track a user event
        
        Args:
            event_name: Name of the event to track
            user_id: User identifier (optional for anonymous tracking)
            properties: Additional event properties
            session_id: Session identifier
        """
        if event_name not in TRACKED_EVENTS:
            logger.warning(f"Unknown event: {event_name}")
            return
        
        event_config = TRACKED_EVENTS[event_name]
        
        event = AnalyticsEvent(
            event_name=event_name,
            user_id=user_id,
            properties=properties or {},
            timestamp=datetime.utcnow(),
            category=event_config["category"],
            privacy_level=event_config["privacy_level"],
            session_id=session_id
        )
        
        try:
            self.event_queue.put_nowait(event)
        except:
            logger.warning("Analytics event queue is full, dropping event")
    
    def track_writing_session(
        self,
        user_id: str,
        document_id: str,
        session_id: str,
        content: str,
        session_duration_minutes: float,
        typing_speed_wpm: float
    ):
        """
        Track writing session analytics
        
        Args:
            user_id: User identifier
            document_id: Document being edited
            session_id: Writing session identifier
            content: Text content (will be analyzed for style/sentiment)
            session_duration_minutes: Duration of writing session
            typing_speed_wpm: Typing speed in words per minute
        """
        writing_data = WritingAnalytics(
            user_id=user_id,
            document_id=document_id,
            session_id=session_id,
            word_count=len(content.split()),
            character_count=len(content),
            typing_speed_wpm=typing_speed_wpm,
            session_duration_minutes=session_duration_minutes
        )
        
        try:
            self.writing_analytics_queue.put_nowait(writing_data)
        except:
            logger.warning("Writing analytics queue is full, dropping data")
    
    def _process_writing_analytics(self, writing_data: WritingAnalytics):
        """Process writing analytics with NLP analysis"""
        try:
            # This would integrate with NLP services for sentiment/style analysis
            # For now, we'll track the basic metrics
            self.track_event(
                "writing_session_analyzed",
                user_id=writing_data.user_id,
                properties={
                    "document_id": writing_data.document_id,
                    "word_count": writing_data.word_count,
                    "character_count": writing_data.character_count,
                    "typing_speed_wpm": writing_data.typing_speed_wpm,
                    "session_duration_minutes": writing_data.session_duration_minutes
                },
                session_id=writing_data.session_id
            )
        except Exception as e:
            logger.error(f"Error processing writing analytics: {e}")
    
    def set_user_consent(
        self, 
        user_id: str, 
        essential: bool = True,
        analytics: bool = False,
        comprehensive: bool = False
    ):
        """
        Set user consent preferences for analytics tracking
        
        Args:
            user_id: User identifier
            essential: Consent for essential analytics (minimal privacy level)
            analytics: Consent for standard analytics
            comprehensive: Consent for comprehensive analytics
        """
        self.user_consents[user_id] = {
            "essential": essential,
            "analytics": analytics,
            "comprehensive": comprehensive,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Track consent change
        self.track_event(
            "consent_updated",
            user_id=user_id,
            properties={
                "essential": essential,
                "analytics": analytics,
                "comprehensive": comprehensive
            }
        )
    
    def get_user_analytics_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get analytics summary for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing user analytics summary
        """
        # This would query the database for user analytics
        # For now, return a placeholder
        return {
            "user_id": user_id,
            "total_writing_sessions": 0,
            "total_words_written": 0,
            "average_typing_speed": 0,
            "most_active_hours": [],
            "writing_streak_days": 0,
            "consent_status": self.user_consents.get(user_id, {})
        }
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all analytics data for a user (GDPR compliance)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing all user analytics data
        """
        if not self.config.allow_data_export:
            raise ValueError("Data export is not enabled")
        
        # This would compile all user data from various sources
        return {
            "user_id": user_id,
            "consent_preferences": self.user_consents.get(user_id, {}),
            "analytics_summary": self.get_user_analytics_summary(user_id),
            "export_timestamp": datetime.utcnow().isoformat(),
            "data_retention_days": self.config.data_retention_days
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all analytics data for a user (GDPR compliance)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deletion was successful
        """
        if not self.config.allow_data_deletion:
            raise ValueError("Data deletion is not enabled")
        
        try:
            # Remove from local consent storage
            if user_id in self.user_consents:
                del self.user_consents[user_id]
            
            # This would also delete from database and external services
            logger.info(f"User data deleted for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False

# Global analytics service instance - temporarily disabled for deployment
# analytics_service = AnalyticsService() 