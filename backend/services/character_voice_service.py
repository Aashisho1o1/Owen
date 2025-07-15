"""
Ultra-Simple Character Voice Consistency Service - Gemini Edition

This service provides character voice consistency analysis using only Gemini 1.5 Flash.
No complex ML dependencies, no TinyStyler, just pure Gemini-based analysis.

Key Features:
- Simple dialogue extraction using regex
- Gemini-based character voice similarity analysis
- Lightweight character profile storage
- Fast deployment with minimal dependencies
- Cost-effective using Gemini 1.5 Flash
"""

import re
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from services.database import PostgreSQLService
from services.llm.gemini_service import GeminiService
from services.validation_service import SimpleInputValidator
from services.security_logger import SecurityLogger, SecurityEventType, SecuritySeverity

logger = logging.getLogger(__name__)

@dataclass
class DialogueSegment:
    """Represents a single piece of dialogue with context"""
    text: str
    speaker: str
    context_before: str
    context_after: str
    position: int
    confidence: float

@dataclass
class CharacterVoiceProfile:
    """Simple character voice profile with dialogue samples"""
    character_id: str
    character_name: str
    dialogue_samples: List[str]
    sample_count: int
    last_updated: datetime
    user_id: int
    voice_characteristics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'character_id': self.character_id,
            'character_name': self.character_name,
            'dialogue_samples': self.dialogue_samples,
            'sample_count': self.sample_count,
            'last_updated': self.last_updated.isoformat(),
            'user_id': self.user_id,
            'voice_characteristics': self.voice_characteristics
        }

@dataclass
class VoiceConsistencyResult:
    """Result of voice consistency analysis"""
    is_consistent: bool
    confidence_score: float
    similarity_score: float
    character_name: str
    flagged_text: str
    explanation: str
    suggestions: List[str]
    analysis_method: str

class SimpleCharacterVoiceService:
    """
    Ultra-Simple Character Voice Consistency Service
    
    Uses only Gemini 1.5 Flash for character voice analysis.
    No complex ML dependencies, fast deployment, cost-effective.
    """
    
    def __init__(self):
        self.db = PostgreSQLService()
        self.gemini_service = GeminiService()
        self.validator = SimpleInputValidator()
        self.security_logger = SecurityLogger()
        
        # Simple dialogue extraction patterns
        self.dialogue_patterns = [
            # Pattern 1: "Dialogue text," Speaker said
            r'"([^"]{10,})",?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)',
            
            # Pattern 2: Speaker said, "Dialogue text"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized),?\s*"([^"]{10,})"',
            
            # Pattern 3: "Dialogue text," Speaker said with additional description
            r'"([^"]{10,})"\s*[,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)\s+[a-z]+'
        ]
        
        # Simple configuration
        self.config = {
            'min_samples_for_profile': 3,
            'max_profile_samples': 10,
            'dialogue_min_length': 10,
            'context_window': 150,
            'consistency_threshold': 0.7
        }
        
        logger.info("Simple Character Voice Service initialized with Gemini")
    
    async def analyze_text_for_voice_consistency(
        self, 
        text: str, 
        user_id: int,
        document_id: Optional[str] = None
    ) -> List[VoiceConsistencyResult]:
        """
        Analyze text for character voice consistency using Gemini
        """
        try:
            # Validate input
            text = self.validator.validate_text_input(text, max_length=10000)
            
            # Extract dialogue segments
            dialogue_segments = self._extract_dialogue_segments(text)
            
            if not dialogue_segments:
                return []
            
            # Load user's character profiles
            character_profiles = await self._load_character_profiles(user_id)
            
            # Analyze each dialogue segment using Gemini
            results = []
            for segment in dialogue_segments:
                if segment.speaker and len(segment.text) >= self.config['dialogue_min_length']:
                    result = await self._analyze_dialogue_with_gemini(
                        segment, character_profiles, user_id
                    )
                    if result:
                        results.append(result)
            
            # Update character profiles with new dialogue
            await self._update_character_profiles(dialogue_segments, user_id)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing text for voice consistency: {str(e)}")
            self.security_logger.log_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY,
                SecuritySeverity.MEDIUM,
                user_id=user_id,
                details={"error": str(e), "text_length": len(text)}
            )
            return []
    
    def _extract_dialogue_segments(self, text: str) -> List[DialogueSegment]:
        """Extract dialogue segments from text using simple regex patterns"""
        segments = []
        
        for pattern_idx, pattern in enumerate(self.dialogue_patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Extract dialogue text and speaker based on pattern
                if len(match.groups()) >= 2:
                    if pattern_idx == 0:  # Pattern 1: "Dialogue," Speaker said
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip()
                    elif pattern_idx == 1:  # Pattern 2: Speaker said, "Dialogue"
                        speaker = match.group(1).strip()
                        dialogue_text = match.group(2).strip()
                    else:  # Pattern 3: "Dialogue," Speaker said with description
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip()
                    
                    # Skip if dialogue is too short
                    if len(dialogue_text) < self.config['dialogue_min_length']:
                        continue
                    
                    # Skip if speaker is None or empty
                    if not speaker:
                        continue
                    
                    # Extract context
                    start_pos = max(0, match.start() - self.config['context_window'])
                    end_pos = min(len(text), match.end() + self.config['context_window'])
                    
                    context_before = text[start_pos:match.start()].strip()
                    context_after = text[match.end():end_pos].strip()
                    
                    # Create dialogue segment
                    segment = DialogueSegment(
                        text=dialogue_text,
                        speaker=speaker,
                        context_before=context_before,
                        context_after=context_after,
                        position=match.start(),
                        confidence=0.9
                    )
                    
                    segments.append(segment)
        
        # Remove duplicates and sort by position
        unique_segments = []
        seen_positions = set()
        
        for segment in sorted(segments, key=lambda x: x.position):
            if segment.position not in seen_positions:
                unique_segments.append(segment)
                seen_positions.add(segment.position)
        
        logger.info(f"Extracted {len(unique_segments)} dialogue segments")
        return unique_segments
    
    async def _load_character_profiles(self, user_id: int) -> Dict[str, CharacterVoiceProfile]:
        """Load character voice profiles for a user"""
        try:
            # Load from database
            query = """
            SELECT character_id, character_name, dialogue_samples, 
                   voice_characteristics, sample_count, last_updated
            FROM character_voice_profiles 
            WHERE user_id = %s AND sample_count >= %s
            """
            
            result = self.db.execute_query(
                query, 
                (user_id, self.config['min_samples_for_profile']),
                fetch='all'
            )
            
            profiles = {}
            if result:
                for row in result:
                    profile = CharacterVoiceProfile(
                        character_id=row['character_id'],
                        character_name=row['character_name'],
                        dialogue_samples=json.loads(row['dialogue_samples']),
                        sample_count=row['sample_count'],
                        last_updated=row['last_updated'],
                        user_id=user_id,
                        voice_characteristics=json.loads(row['voice_characteristics'])
                    )
                    profiles[row['character_name'].lower()] = profile
            
            logger.info(f"Loaded {len(profiles)} character profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Error loading character profiles: {str(e)}")
            return {}
    
    async def _analyze_dialogue_with_gemini(
        self, 
        segment: DialogueSegment, 
        character_profiles: Dict[str, CharacterVoiceProfile],
        user_id: int
    ) -> Optional[VoiceConsistencyResult]:
        """Analyze dialogue segment using Gemini for voice consistency"""
        try:
            speaker_key = segment.speaker.lower()
            
            # Check if we have a profile for this character
            if speaker_key not in character_profiles:
                return None
            
            profile = character_profiles[speaker_key]
            
            # Create Gemini prompt for voice consistency analysis
            previous_dialogue = "\n".join([f'"{sample}"' for sample in profile.dialogue_samples[-5:]])
            
            prompt = f"""
            Analyze if this new dialogue is consistent with the character's established voice pattern.
            
            Character: {profile.character_name}
            
            Previous dialogue examples from this character:
            {previous_dialogue}
            
            New dialogue to analyze:
            "{segment.text}"
            
            Context: {segment.context_before} [...] {segment.context_after}
            
            Please analyze:
            1. Is this dialogue consistent with the character's voice? (yes/no)
            2. What is your confidence level? (0.0 to 1.0)
            3. What makes it consistent or inconsistent?
            4. If inconsistent, provide 2-3 specific suggestions to improve voice consistency.
            
            Focus on: vocabulary choice, sentence structure, tone, personality traits, and speech patterns.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "confidence_score": float,
                "similarity_score": float,
                "explanation": "detailed explanation",
                "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
            }}
            """
            
            # Use Gemini 1.5 Flash for analysis (cheaper and faster)
            response = await self.gemini_service.generate_json_response(
                prompt, 
                max_tokens=400, 
                temperature=0.3
            )
            
            if response and isinstance(response, dict):
                # Create result
                result = VoiceConsistencyResult(
                    is_consistent=response.get('is_consistent', True),
                    confidence_score=min(response.get('confidence_score', 0.8), 1.0),
                    similarity_score=min(response.get('similarity_score', 0.8), 1.0),
                    character_name=profile.character_name,
                    flagged_text=segment.text,
                    explanation=response.get('explanation', 'Voice analysis completed'),
                    suggestions=response.get('suggestions', []),
                    analysis_method='gemini_voice_analysis'
                )
                
                logger.debug(f"Gemini analysis - Character: {profile.character_name}, "
                           f"Consistent: {result.is_consistent}, "
                           f"Confidence: {result.confidence_score:.3f}")
                
                return result
            
        except Exception as e:
            logger.error(f"Error in Gemini dialogue analysis: {str(e)}")
        
        return None
    
    async def _update_character_profiles(self, segments: List[DialogueSegment], user_id: int):
        """Update character profiles with new dialogue samples"""
        try:
            character_updates = {}
            
            # Group segments by character
            for segment in segments:
                if segment.speaker and len(segment.text) >= self.config['dialogue_min_length']:
                    speaker_key = segment.speaker.lower()
                    if speaker_key not in character_updates:
                        character_updates[speaker_key] = []
                    character_updates[speaker_key].append(segment)
            
            # Update each character's profile
            for speaker_key, speaker_segments in character_updates.items():
                await self._update_single_character_profile(
                    speaker_key, speaker_segments, user_id
                )
            
        except Exception as e:
            logger.error(f"Error updating character profiles: {str(e)}")
    
    async def _update_single_character_profile(
        self, 
        speaker_key: str, 
        segments: List[DialogueSegment], 
        user_id: int
    ):
        """Update a single character's voice profile"""
        try:
            character_name = segments[0].speaker
            character_id = hashlib.md5(f"{user_id}_{character_name}".encode()).hexdigest()
            
            # Get existing profile
            query = """
            SELECT dialogue_samples, voice_characteristics, sample_count
            FROM character_voice_profiles 
            WHERE character_id = %s AND user_id = %s
            """
            
            result = self.db.execute_query(query, (character_id, user_id), fetch='one')
            
            # Collect new dialogue samples
            new_samples = [segment.text for segment in segments]
            
            if result:
                # Update existing profile
                existing_samples = json.loads(result['dialogue_samples'])
                all_samples = existing_samples + new_samples
                
                # Keep only the most recent samples
                if len(all_samples) > self.config['max_profile_samples']:
                    all_samples = all_samples[-self.config['max_profile_samples']:]
                
                # Update database
                update_query = """
                UPDATE character_voice_profiles 
                SET dialogue_samples = %s, sample_count = %s, 
                    last_updated = CURRENT_TIMESTAMP
                WHERE character_id = %s AND user_id = %s
                """
                
                self.db.execute_query(
                    update_query, 
                    (json.dumps(all_samples), len(all_samples), character_id, user_id)
                )
                
            else:
                # Create new profile
                if len(new_samples) >= self.config['min_samples_for_profile']:
                    insert_query = """
                    INSERT INTO character_voice_profiles 
                    (character_id, character_name, user_id, dialogue_samples, 
                     voice_embedding, voice_characteristics, sample_count, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """
                    
                    # Use empty JSON for voice_embedding since we're not using embeddings
                    self.db.execute_query(
                        insert_query,
                        (character_id, character_name, user_id, json.dumps(new_samples),
                         json.dumps([]), json.dumps({}), len(new_samples))
                    )
            
        except Exception as e:
            logger.error(f"Error updating character profile for {speaker_key}: {str(e)}")
    
    async def get_character_profiles(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all character profiles for a user"""
        try:
            query = """
            SELECT character_id, character_name, sample_count, 
                   last_updated, voice_characteristics
            FROM character_voice_profiles 
            WHERE user_id = %s
            ORDER BY last_updated DESC
            """
            
            result = self.db.execute_query(query, (user_id,), fetch='all')
            
            profiles = []
            if result:
                for row in result:
                    profiles.append({
                        'character_id': row['character_id'],
                        'character_name': row['character_name'],
                        'sample_count': row['sample_count'],
                        'last_updated': row['last_updated'].isoformat(),
                        'voice_characteristics': json.loads(row['voice_characteristics'])
                    })
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error getting character profiles: {str(e)}")
            return []
    
    async def delete_character_profile(self, user_id: int, character_name: str) -> bool:
        """Delete a character profile"""
        try:
            character_id = hashlib.md5(f"{user_id}_{character_name}".encode()).hexdigest()
            
            query = """
            DELETE FROM character_voice_profiles 
            WHERE character_id = %s AND user_id = %s
            """
            
            rows_affected = self.db.execute_query(query, (character_id, user_id))
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Error deleting character profile: {str(e)}")
            return False
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Test database connection
            db_healthy = self.db.health_check()['status'] == 'healthy'
            
            # Test Gemini service
            gemini_healthy = self.gemini_service.is_available()
            
            # Service is healthy if both database and Gemini work
            service_healthy = db_healthy and gemini_healthy
            
            return {
                'status': 'healthy' if service_healthy else 'unhealthy',
                'database': db_healthy,
                'gemini_service': gemini_healthy,
                'analysis_mode': 'gemini_only',
                'config': self.config
            }
            
        except Exception as e:
            logger.error(f"Error checking service health: {str(e)}")
            return {'status': 'error', 'error': str(e)}

# Create alias for backward compatibility
CharacterVoiceService = SimpleCharacterVoiceService 