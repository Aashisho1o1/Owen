"""
Character Voice Service - Refactored with Demo Config

This version cleanly separates demo-specific logic from core functionality.
Demo-specific behavior is controlled via the DemoConfig module.
"""

import html
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import demo configuration
from config.demo_config import demo_config, is_demo_enabled, detect_demo_content

# ... (rest of imports remain the same)
from services.llm_service import llm_service
from services.dialogue_extractor import dialogue_extractor

logger = logging.getLogger(__name__)

@dataclass 
class DialogueSegment:
    """Represents a single piece of dialogue with context."""
    text: str
    speaker: str
    position: int
    context_before: str
    context_after: str

@dataclass
class CharacterVoiceProfile:
    """Character voice profile with dialogue samples and traits."""
    character_id: str
    character_name: str
    dialogue_samples: List[str]
    voice_traits: Dict[str, Any]
    last_updated: str
    sample_count: int

class CharacterVoiceServiceRefactored:
    """
    REFACTORED: Character Voice Service with Clean Demo Separation
    
    All demo-specific logic is now controlled via DemoConfig, making it easy to:
    1. Enable/disable demo mode
    2. Add new content types
    3. Maintain clean production code
    """
    
    def __init__(self):
        logger.info("🎭 CharacterVoiceService: Initializing refactored service...")
        try:
            # Core service initialization
            if hasattr(llm_service, 'generate_with_selected_llm'):
                logger.info("✅ LLM service coordinator available")
            else:
                logger.error("❌ LLM service coordinator missing")
            
            # Load demo profiles if demo mode is enabled
            self.demo_profiles = self._load_demo_profiles() if is_demo_enabled() else {}
            
            # Log demo status
            if is_demo_enabled():
                logger.info(f"🎭 Demo mode enabled: {len(self.demo_profiles)} profiles loaded")
                available_demos = demo_config.list_available_demos()
                logger.info(f"📋 Available demos: {list(available_demos.keys())}")
            else:
                logger.info("🏭 Production mode: No demo profiles loaded")
            
            logger.info("✅ CharacterVoiceService: Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ CharacterVoiceService: Initialization failed: {e}")
            raise
    
    def _load_demo_profiles(self) -> Dict[str, CharacterVoiceProfile]:
        """
        Load demo profiles based on current demo configuration.
        CLEAN: All demo logic centralized in DemoConfig.
        """
        if not is_demo_enabled():
            return {}
        
        try:
            # Get profile file from demo config
            profile_file = demo_config.get_profile_file()
            if not profile_file:
                logger.warning("⚠️ No profile file specified in demo config")
                return {}
            
            # Load profiles using existing logic
            return self._load_profiles_from_file(profile_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to load demo profiles: {e}")
            return {}
    
    def _load_profiles_from_file(self, filename: str) -> Dict[str, CharacterVoiceProfile]:
        """Load character profiles from JSON file."""
        import os
        import json
        
        try:
            service_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(service_dir)
            profiles_path = os.path.join(backend_dir, 'assets', filename)
            
            if not os.path.exists(profiles_path):
                logger.warning(f"⚠️ Profile file not found: {profiles_path}")
                return {}
            
            with open(profiles_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profiles = {}
            for char_name, profile_data in data.items():
                profiles[char_name] = CharacterVoiceProfile(
                    character_id=profile_data['character_id'],
                    character_name=profile_data['character_name'],
                    dialogue_samples=profile_data['dialogue_samples'],
                    voice_traits=profile_data['voice_traits'],
                    last_updated=profile_data['last_updated'],
                    sample_count=profile_data['sample_count']
                )
            
            logger.info(f"✅ Loaded {len(profiles)} profiles from {filename}")
            return profiles
            
        except Exception as e:
            logger.error(f"❌ Error loading profiles from {filename}: {e}")
            return {}
    
    def _detect_demo_content_type(self, text: str) -> Optional[str]:
        """
        CLEAN: Demo detection using centralized config.
        Returns content type string or None.
        """
        if not is_demo_enabled():
            return None
        
        detected_type = detect_demo_content(text)
        if detected_type:
            logger.info(f"🎭 Demo content detected: {detected_type}")
        
        return detected_type
    
    def _normalize_character_name(self, character_name: str, content_type: str = None) -> str:
        """
        CLEAN: Character name normalization using demo config.
        """
        if not is_demo_enabled() or not content_type:
            return character_name
        
        # Get aliases from demo config
        aliases = demo_config.get_character_aliases(content_type)
        
        # Try exact match first
        if character_name in aliases:
            normalized = aliases[character_name]
            logger.debug(f"🔄 Normalized: '{character_name}' -> '{normalized}'")
            return normalized
        
        # Try case-insensitive match
        for alias, canonical in aliases.items():
            if character_name.lower() == alias.lower():
                logger.debug(f"🔄 Normalized (case-insensitive): '{character_name}' -> '{canonical}'")
                return canonical
        
        return character_name
    
    def _get_text_length_limit(self, content_type: str = None) -> int:
        """
        CLEAN: Get text length limit from demo config or use default.
        """
        if is_demo_enabled() and content_type:
            return demo_config.get_max_text_length(content_type)
        
        return 10000  # Production default
    
    async def analyze(self, text: str, existing_profiles: Optional[Dict[str, CharacterVoiceProfile]] = None) -> Dict[str, Any]:
        """
        REFACTORED: Main analysis method with clean demo integration.
        """
        analysis_start_time = datetime.now()
        
        try:
            logger.info(f"🔍 === SERVICE ANALYSIS START ===")
            logger.info(f"📊 Input: {len(text)} chars")
            
            # CLEAN: Demo content detection
            detected_demo_type = self._detect_demo_content_type(text)
            
            # CLEAN: Demo profile injection
            if detected_demo_type and self.demo_profiles:
                logger.info(f"🎭 === DEMO MODE: {detected_demo_type.upper()} ===")
                logger.info(f"📜 Using {len(self.demo_profiles)} demo profiles")
                existing_profiles = self.demo_profiles.copy()
            
            # CLEAN: Text length handling
            max_length = self._get_text_length_limit(detected_demo_type)
            if len(text) > max_length:
                logger.info(f"🔧 Truncating text: {len(text)} -> {max_length}")
                text = text[:max_length] + "\n\n[Text truncated for analysis]"
            
            # Continue with existing analysis logic...
            # (HTML processing, dialogue extraction, etc.)
            
            # CLEAN: Character name normalization in dialogue segments
            dialogue_segments = self._extract_dialogue_segments(text)
            if detected_demo_type:
                # Apply demo-specific character name normalization
                for segment in dialogue_segments:
                    segment.speaker = self._normalize_character_name(segment.speaker, detected_demo_type)
            
            # Rest of analysis logic remains the same...
            
            return {
                'demo_mode': detected_demo_type is not None,
                'demo_type': detected_demo_type,
                'characters_analyzed': len(dialogue_segments),
                'processing_time_ms': (datetime.now() - analysis_start_time).total_seconds() * 1000
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            raise
    
    def _extract_dialogue_segments(self, text: str) -> List[DialogueSegment]:
        """Extract dialogue segments - core logic unchanged."""
        # Existing implementation remains the same
        return []

# Create instance that can be imported
character_voice_service_refactored = CharacterVoiceServiceRefactored()
