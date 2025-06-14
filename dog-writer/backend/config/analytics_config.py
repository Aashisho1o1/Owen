"""
Analytics Configuration for DOG Writer
Privacy-compliant user behavior and writing analytics with GDPR compliance
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AnalyticsProvider(Enum):
    POSTHOG = "posthog"
    MIXPANEL = "mixpanel"
    CUSTOM = "custom"

class PrivacyLevel(Enum):
    MINIMAL = "minimal"  # Only essential analytics
    STANDARD = "standard"  # Standard analytics with user consent
    COMPREHENSIVE = "comprehensive"  # Full analytics with explicit consent

@dataclass
class AnalyticsConfig:
    """Analytics configuration with privacy controls"""
    
    # Provider Settings
    posthog_api_key: Optional[str] = os.getenv("POSTHOG_API_KEY")
    posthog_host: str = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    mixpanel_token: Optional[str] = os.getenv("MIXPANEL_TOKEN")
    
    # Privacy Settings
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    anonymize_ip: bool = True
    respect_do_not_track: bool = True
    data_retention_days: int = 365
    
    # GDPR Compliance
    gdpr_compliant: bool = True
    require_consent: bool = True
    allow_data_export: bool = True
    allow_data_deletion: bool = True
    
    # Feature Tracking
    track_button_clicks: bool = True
    track_feature_usage: bool = True
    track_writing_sessions: bool = True
    track_document_operations: bool = True
    
    # Writing Analytics
    analyze_writing_style: bool = True
    analyze_sentiment: bool = True
    analyze_readability: bool = True
    track_writing_patterns: bool = True
    
    # Performance Monitoring
    track_performance_metrics: bool = True
    track_error_rates: bool = True
    
    # Data Processing
    batch_size: int = 100
    flush_interval_seconds: int = 30
    max_queue_size: int = 1000

# Event Categories for Tracking
class EventCategory(Enum):
    USER_ACTION = "user_action"
    WRITING_ACTIVITY = "writing_activity"
    DOCUMENT_OPERATION = "document_operation"
    AI_INTERACTION = "ai_interaction"
    PERFORMANCE = "performance"
    ERROR = "error"

# Predefined Events for Consistent Tracking
TRACKED_EVENTS = {
    # User Actions
    "user_login": {"category": EventCategory.USER_ACTION, "privacy_level": PrivacyLevel.MINIMAL},
    "user_logout": {"category": EventCategory.USER_ACTION, "privacy_level": PrivacyLevel.MINIMAL},
    "user_signup": {"category": EventCategory.USER_ACTION, "privacy_level": PrivacyLevel.MINIMAL},
    
    # Writing Activities
    "writing_session_start": {"category": EventCategory.WRITING_ACTIVITY, "privacy_level": PrivacyLevel.STANDARD},
    "writing_session_end": {"category": EventCategory.WRITING_ACTIVITY, "privacy_level": PrivacyLevel.STANDARD},
    "text_typed": {"category": EventCategory.WRITING_ACTIVITY, "privacy_level": PrivacyLevel.COMPREHENSIVE},
    "auto_save_triggered": {"category": EventCategory.WRITING_ACTIVITY, "privacy_level": PrivacyLevel.STANDARD},
    
    # Document Operations
    "document_created": {"category": EventCategory.DOCUMENT_OPERATION, "privacy_level": PrivacyLevel.STANDARD},
    "document_saved": {"category": EventCategory.DOCUMENT_OPERATION, "privacy_level": PrivacyLevel.STANDARD},
    "document_deleted": {"category": EventCategory.DOCUMENT_OPERATION, "privacy_level": PrivacyLevel.STANDARD},
    "document_shared": {"category": EventCategory.DOCUMENT_OPERATION, "privacy_level": PrivacyLevel.STANDARD},
    
    # AI Interactions
    "ai_chat_message": {"category": EventCategory.AI_INTERACTION, "privacy_level": PrivacyLevel.COMPREHENSIVE},
    "ai_suggestion_accepted": {"category": EventCategory.AI_INTERACTION, "privacy_level": PrivacyLevel.STANDARD},
    "ai_suggestion_rejected": {"category": EventCategory.AI_INTERACTION, "privacy_level": PrivacyLevel.STANDARD},
    
    # Feature Usage
    "timer_started": {"category": EventCategory.USER_ACTION, "privacy_level": PrivacyLevel.MINIMAL},
    "timer_stopped": {"category": EventCategory.USER_ACTION, "privacy_level": PrivacyLevel.MINIMAL},
    "export_document": {"category": EventCategory.DOCUMENT_OPERATION, "privacy_level": PrivacyLevel.STANDARD},
    
    # Performance & Errors
    "page_load_time": {"category": EventCategory.PERFORMANCE, "privacy_level": PrivacyLevel.MINIMAL},
    "api_error": {"category": EventCategory.ERROR, "privacy_level": PrivacyLevel.MINIMAL},
}

# Writing Analysis Configuration
WRITING_ANALYSIS_CONFIG = {
    "sentiment_analysis": {
        "enabled": True,
        "models": ["vader", "textblob"],
        "batch_processing": True
    },
    "style_analysis": {
        "enabled": True,
        "features": [
            "readability_score",
            "sentence_complexity",
            "vocabulary_diversity",
            "tone_analysis",
            "writing_voice"
        ]
    },
    "pattern_detection": {
        "enabled": True,
        "track_writing_habits": True,
        "identify_peak_hours": True,
        "analyze_productivity_patterns": True
    }
}

# Privacy-Safe Data Collection Rules
PRIVACY_RULES = {
    "pii_detection": {
        "enabled": True,
        "auto_redact": True,
        "patterns": [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
        ]
    },
    "content_anonymization": {
        "enabled": True,
        "hash_sensitive_content": True,
        "store_only_metadata": True
    }
}

# Initialize default configuration
analytics_config = AnalyticsConfig() 