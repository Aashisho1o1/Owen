"""
Demo Configuration Module

This module contains all demo-specific configurations that can be easily
enabled/disabled or modified without affecting the core application logic.

Created for GoT Season 8 dialogue analysis demo, but designed to be
extensible for other content types.
"""

from typing import Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class DemoConfig:
    """
    Centralized demo configuration management.
    
    This class encapsulates all demo-specific settings, making it easy to:
    1. Enable/disable demo mode
    2. Switch between different content types
    3. Maintain clean separation between demo and production code
    """
    
    def __init__(self):
        # Control demo mode via environment variable or direct setting
        self.enabled = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        self.current_demo = os.getenv('DEMO_TYPE', 'got')  # 'got', 'lotr', 'hp', etc.
        
        logger.info(f"🎭 Demo Config: Enabled={self.enabled}, Type={self.current_demo}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if demo mode is currently enabled."""
        return self.enabled
    
    def get_content_indicators(self, content_type: str = None) -> List[str]:
        """Get content detection indicators for specified type."""
        content_type = content_type or self.current_demo
        return self._demo_configs.get(content_type, {}).get('indicators', [])
    
    def get_detection_threshold(self, content_type: str = None) -> int:
        """Get detection threshold for specified type."""
        content_type = content_type or self.current_demo
        return self._demo_configs.get(content_type, {}).get('threshold', 3)  # Default production threshold
    
    def get_character_aliases(self, content_type: str = None) -> Dict[str, str]:
        """Get character name aliases for specified type."""
        content_type = content_type or self.current_demo
        return self._demo_configs.get(content_type, {}).get('character_aliases', {})
    
    def get_max_text_length(self, content_type: str = None) -> int:
        """Get maximum text length for specified type."""
        content_type = content_type or self.current_demo
        return self._demo_configs.get(content_type, {}).get('max_text_length', 10000)  # Default production limit
    
    def get_profile_file(self, content_type: str = None) -> str:
        """Get profile file path for specified type."""
        content_type = content_type or self.current_demo
        return self._demo_configs.get(content_type, {}).get('profile_file', None)
    
    def detect_content_type(self, text: str) -> str:
        """
        Auto-detect content type from text.
        Returns content type string or None if no demo content detected.
        """
        if not self.is_enabled:
            return None
            
        text_lower = text.lower()
        
        for content_type, config in self._demo_configs.items():
            indicators = config.get('indicators', [])
            threshold = config.get('threshold', 3)
            matches = 0
            
            for indicator in indicators:
                if indicator in text_lower:
                    matches += 1
                    if matches >= threshold:
                        logger.info(f"🎭 Auto-detected {content_type} content with {matches} indicators")
                        return content_type
        
        return None
    
    # DEMO CONFIGURATIONS
    # ===================
    # All demo-specific data is centralized here for easy management
    
    _demo_configs = {
        'got': {
            'name': 'Game of Thrones',
            'description': 'Season 8 dialogue analysis demo',
            'indicators': [
                # Character names (distinctive ones)
                'daenerys', 'tyrion', 'arya stark', 'jon snow', 'sansa stark', 'bran stark',
                'cersei', 'jaime', 'joffrey', 'tywin', 'robb stark', 'catelyn', 'ned stark',
                'theon', 'ramsay', 'margaery', 'olenna', 'oberyn', 'sandor', 'bronn',
                
                # Single name variants for script format
                'bran', 'tyrion', 'arya', 'sansa', 'jaime', 'joffrey', 'tywin', 'robb',
                'catelyn', 'theon', 'ramsay', 'margaery', 'oberyn', 'bronn', 'davos',
                'grey worm', 'missandei', 'varys', 'littlefinger', 'qyburn', 'mountain',
                'hound', 'tormund', 'gilly', 'samwell', 'gendry', 'yara', 'euron',
                
                # Unique GoT terms
                'winterfell', 'king\'s landing', 'westeros', 'essos', 'seven kingdoms',
                'iron throne', 'night\'s watch', 'wall', 'beyond the wall', 'wildlings',
                'dothraki', 'unsullied', 'faceless men', 'three-eyed raven',
                'night king', 'white walkers', 'dragons', 'dragonstone', 'valyrian',
                
                # Distinctive phrases
                'winter is coming', 'fire and blood', 'a girl has no name', 'dracarys',
                'you know nothing', 'the north remembers', 'valar morghulis', 'hodor',
                'what do we say to death', 'not today', 'chaos is a ladder',
                
                # Houses and titles
                'house stark', 'house lannister', 'house targaryen', 'house baratheon',
                'your grace', 'my lord', 'my lady', 'ser ', 'maester', 'lord commander',
                'hand of the king', 'mother of dragons', 'king in the north', 'lord tyrion'
            ],
            'threshold': 2,  # Easier activation for demo
            'character_aliases': {
                # Script format -> Profile name mappings
                'BRAN': 'Bran Stark', 'JON': 'Jon Snow', 'TYRION': 'Tyrion Lannister',
                'DAENERYS': 'Daenerys Targaryen', 'ARYA': 'Arya Stark', 'SANSA': 'Sansa Stark',
                'CERSEI': 'Cersei Lannister', 'JAIME': 'Jaime Lannister',
                
                # Alternative formats
                'bran': 'Bran Stark', 'jon': 'Jon Snow', 'tyrion': 'Tyrion Lannister',
                'daenerys': 'Daenerys Targaryen', 'arya': 'Arya Stark', 'sansa': 'Sansa Stark',
                'cersei': 'Cersei Lannister', 'jaime': 'Jaime Lannister',
                
                # Mixed case
                'Bran': 'Bran Stark', 'Jon': 'Jon Snow', 'Tyrion': 'Tyrion Lannister',
                'Daenerys': 'Daenerys Targaryen', 'Arya': 'Arya Stark', 'Sansa': 'Sansa Stark',
                'Cersei': 'Cersei Lannister', 'Jaime': 'Jaime Lannister',
            },
            'max_text_length': 50000,  # Higher limit for full scripts
            'profile_file': 'got_character_profiles.json'
        },
        
        # FUTURE: Add other content types
        # 'lotr': {
        #     'name': 'Lord of the Rings',
        #     'description': 'LOTR dialogue analysis demo',
        #     'indicators': ['frodo', 'gandalf', 'aragorn', 'legolas', 'gimli', 'middle-earth', 'mordor'],
        #     'threshold': 2,
        #     'character_aliases': {'FRODO': 'Frodo Baggins', 'GANDALF': 'Gandalf the Grey'},
        #     'max_text_length': 50000,
        #     'profile_file': 'lotr_character_profiles.json'
        # },
        
        # 'hp': {
        #     'name': 'Harry Potter',
        #     'description': 'Harry Potter dialogue analysis demo',
        #     'indicators': ['harry', 'hermione', 'ron', 'hogwarts', 'dumbledore', 'voldemort'],
        #     'threshold': 2,
        #     'character_aliases': {'HARRY': 'Harry Potter', 'HERMIONE': 'Hermione Granger'},
        #     'max_text_length': 50000,
        #     'profile_file': 'hp_character_profiles.json'
        # }
    }
    
    def list_available_demos(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all available demo configurations."""
        return {
            key: {
                'name': config.get('name', key),
                'description': config.get('description', ''),
                'enabled': self.is_enabled and key == self.current_demo
            }
            for key, config in self._demo_configs.items()
        }


# Global demo config instance
demo_config = DemoConfig()

# Convenience functions for easy access
def is_demo_enabled() -> bool:
    """Quick check if demo mode is enabled."""
    return demo_config.is_enabled

def get_demo_config() -> DemoConfig:
    """Get the global demo configuration instance."""
    return demo_config

def detect_demo_content(text: str) -> str:
    """Quick content type detection."""
    return demo_config.detect_content_type(text)
