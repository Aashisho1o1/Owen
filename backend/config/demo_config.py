"""
Demo Configuration Module

This module centralizes all configurations for different demo modes,
making it easy to switch between or add new demos.
"""
import os
import json
import logging
from typing import Dict, List, Any

# Assuming CharacterVoiceProfile is defined in models.schemas
# We will adjust this import once the refactoring is complete
try:
    from models.schemas import CharacterVoiceProfile
except ImportError:
    # This is a fallback for the refactoring process
    from dataclasses import dataclass
    
    @dataclass
    class CharacterVoiceProfile:
        character_id: str
        character_name: str
        dialogue_samples: List[str]
        voice_traits: Dict[str, Any]
        last_updated: str
        sample_count: int

logger = logging.getLogger(__name__)

class DemoConfig:
    """
    Manages and provides configurations for different demo modes.
    """
    def __init__(self, demo_name: str = 'game_of_thrones'):
        self.demo_name = demo_name
        self.profiles: Dict[str, CharacterVoiceProfile] = {}
        self.aliases: Dict[str, str] = {}
        self.indicators: List[str] = []
        self.indicator_threshold: int = 2
        self.max_text_length: int = 50000

        if self.demo_name == 'game_of_thrones':
            self._load_game_of_thrones_config()

    def _load_game_of_thrones_config(self):
        """Loads all Game of Thrones specific configurations."""
        self.profiles = self._load_got_profiles()
        self.aliases = self._get_got_aliases()
        self.indicators = self._get_got_indicators()

    def _load_got_profiles(self) -> Dict[str, CharacterVoiceProfile]:
        """Loads Game of Thrones character profiles from a JSON file."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            profiles_path = os.path.join(base_dir, '..', 'assets', 'got_character_profiles.json')
            
            if not os.path.exists(profiles_path):
                logger.warning(f"GoT profiles file not found at {profiles_path}")
                return {}
            
            with open(profiles_path, 'r', encoding='utf-8') as f:
                profiles_data = json.load(f)

            got_profiles = {}
            for character_name, profile_data in profiles_data.items():
                got_profiles[character_name] = CharacterVoiceProfile(**profile_data)

            logger.info(f"Loaded {len(got_profiles)} GoT character profiles.")
            return got_profiles
        except Exception as e:
            logger.error(f"Failed to load GoT profiles: {e}")
            return {}

    def _get_got_aliases(self) -> Dict[str, str]:
        """Returns the character name alias mapping for Game of Thrones."""
        return {
            'BRAN': 'Bran Stark', 'JON': 'Jon Snow', 'TYRION': 'Tyrion Lannister',
            'DAENERYS': 'Daenerys Targaryen', 'ARYA': 'Arya Stark', 'SANSA': 'Sansa Stark',
            'CERSEI': 'Cersei Lannister', 'JAIME': 'Jaime Lannister',
        }

    def _get_got_indicators(self) -> List[str]:
        """Returns the list of text indicators for Game of Thrones content."""
        return [
            'daenerys', 'tyrion', 'arya stark', 'jon snow', 'sansa stark', 'bran stark',
            'cersei', 'jaime', 'winterfell', 'king\'s landing', 'westeros', 'iron throne',
            'house stark', 'house lannister', 'house targaryen', 'your grace', 'my lord',
        ]

# --- Global Functions for Easy Access ---

def get_demo_config() -> DemoConfig:
    """
    Factory function to get the current demo configuration.
    In the future, this could read from an environment variable to select the demo.
    """
    # For now, we hardcode to Game of Thrones.
    # To switch demos, you would change this line:
    # demo_name = os.getenv('CURRENT_DEMO', 'game_of_thrones')
    return DemoConfig(demo_name='game_of_thrones')

def is_demo_enabled() -> bool:
    """Check if any demo mode is currently active."""
    return os.getenv('DEMO_MODE', 'true').lower() == 'true'

def detect_demo_content(text: str) -> bool:
    """Detects if the text matches the active demo's indicators."""
    if not is_demo_enabled():
        return False
        
    config = get_demo_config()
    text_lower = text.lower()
    matches = sum(1 for indicator in config.indicators if indicator in text_lower)
    
    if matches >= config.indicator_threshold:
        logger.info(f"'{config.demo_name}' demo content detected with {matches} indicators.")
        return True
    return False

demo_config = get_demo_config()
