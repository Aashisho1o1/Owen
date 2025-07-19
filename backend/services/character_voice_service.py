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
        
        # Simple configuration
        self.config = {
            'min_samples_for_profile': 1,  # Reduced from 3 to 1 for immediate analysis
            'max_profile_samples': 10,
            'dialogue_min_length': 10,  # Increased from 3 to 10 for better quality
            'context_window': 150,
            'consistency_threshold': 0.7,
            'max_segments_to_analyze': 20  # Limit to prevent overwhelming results
        }
        
        # Enhanced dialogue extraction patterns - Support both straight and curly quotes
        self.dialogue_patterns = [
            # Pattern 0: Basic quoted dialogue (FIXED - properly includes all quote types)
            r'[""\'"]([^""\'"\n]{10,})[""\'"]',
            
            # Pattern 1: "Dialogue text," Speaker said (FIXED - better speaker capture)
            r'[""\'"]([^""\'"\n]{10,})[""\'"][,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed)',
            
            # Pattern 2: Speaker said, "Dialogue text" (FIXED - better speaker capture)
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed)[,.]?\s*[""\'"]([^""\'"\n]{10,})[""\'"]',
            
            # Pattern 3: "Dialogue," he/she said (FIXED - simpler pronouns only)
            r'[""\'"]([^""\'"\n]{10,})[""\'"][,.]?\s*(he|she|it|they)\s+(?:said|asked|replied|whispered|shouted|murmured)',
            
            # Pattern 4: Simple "dialogue" with basic punctuation (FIXED)
            r'[""\'"]([^""\'"\n]{10,})[.!?]?[""\'"]'
        ]
        
        logger.info("Simple Character Voice Service initialized with Gemini")
    
    def _is_narrative_text(self, text: str) -> bool:
        """Check if text is likely narrative rather than dialogue"""
        if not text:
            return True
        
        text_lower = text.lower().strip()
        
        # Common narrative indicators
        narrative_patterns = [
            # Action descriptions
            r'\b(walked|ran|looked|turned|smiled|laughed|nodded|shook|moved|stepped|entered|left|sat|stood|opened|closed)\b',
            # Descriptive text
            r'\b(the|a|an)\s+\w+\s+(was|were|is|are)',
            # Time/place indicators
            r'\b(then|meanwhile|later|earlier|yesterday|tomorrow|here|there)\b',
            # Very short fragments (likely parsing errors)
            r'^\w{1,3}$',
            # Common narrative phrases
            r'\b(he said|she said|it was|there was|they were)\b'
        ]
        
        # Check if text matches narrative patterns
        import re
        for pattern in narrative_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check if text is very short and doesn't look like dialogue
        if len(text.strip()) < 5:
            return True
        
        # Check if text doesn't have dialogue punctuation
        if not any(punct in text for punct in ['"', "'", "!", "?", ".", ","]):
            return True
        
        return False
    
    def _clean_character_name(self, name: str) -> str:
        """Clean and validate character names"""
        if not name:
            return ""
        
        # Remove common parsing artifacts
        name = name.strip()
        
        # Remove narrative text that got captured
        narrative_indicators = [
            'rolled their eyes but', 'looked at', 'turned to', 'walked to',
            'sat down', 'stood up', 'moved toward', 'stepped back',
            'nodded', 'shook', 'smiled', 'frowned', 'laughed', 'sighed'
        ]
        
        for indicator in narrative_indicators:
            if indicator in name.lower():
                return ""
        
        # Only allow proper names (capitalized words)
        words = name.split()
        valid_words = []
        
        for word in words:
            # Keep only capitalized words that look like names
            if word and word[0].isupper() and word.isalpha() and len(word) > 1:
                valid_words.append(word)
            # Allow common pronouns
            elif word.lower() in ['he', 'she', 'it', 'they']:
                valid_words.append(word.title())
        
        # Join valid words
        cleaned_name = ' '.join(valid_words)
        
        # Validate final name
        if len(cleaned_name) < 2 or len(cleaned_name) > 50:
            return ""
        
        # Don't allow names that are clearly not character names
        invalid_names = ['The', 'A', 'An', 'This', 'That', 'These', 'Those']
        if cleaned_name in invalid_names:
            return ""
        
        return cleaned_name
    
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
            logger.info(f"🎭 Starting voice consistency analysis for user {user_id}")
            logger.info(f"📝 Text length: {len(text)} characters")
            logger.info(f"📝 Text preview: {text[:200]}...")
            
            # Validate input - use validate_suggestion_text to avoid HTML escaping
            try:
                # CRITICAL: Strip HTML before processing to prevent corruption
                import re
                # Remove HTML tags properly
                text_clean = re.sub(r'<[^>]+>', ' ', text)
                # Decode HTML entities
                text_clean = text_clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                # Normalize whitespace
                text_clean = re.sub(r'\s+', ' ', text_clean).strip()
                
                text = self.validator.validate_suggestion_text(text_clean, max_length=10000)
                logger.info(f"✅ Text validation passed - cleaned from {len(text)} to {len(text_clean)} characters")
            except Exception as e:
                logger.error(f"❌ Text validation failed: {e}")
                raise
            
            # Extract dialogue segments
            try:
                dialogue_segments = self._extract_dialogue_segments(text)
                logger.info(f"📊 Found {len(dialogue_segments)} dialogue segments")
            except Exception as e:
                logger.error(f"❌ Dialogue extraction failed: {e}")
                raise
            
            if not dialogue_segments:
                logger.warning("❌ No dialogue segments found - returning empty results")
                return []
            
            # Load user's character profiles
            try:
                character_profiles = await self._load_character_profiles(user_id)
                logger.info(f"👥 Loaded {len(character_profiles)} character profiles for user {user_id}")
            except Exception as e:
                logger.error(f"❌ Character profile loading failed: {e}")
                raise
            
            # Analyze each dialogue segment using Gemini
            results = []
            analyzed_count = 0
            
            # Sort segments by confidence and text length to prioritize better dialogue
            dialogue_segments.sort(key=lambda s: (s.confidence, len(s.text)), reverse=True)
            
            for i, segment in enumerate(dialogue_segments):
                # Skip if we've analyzed enough segments
                if analyzed_count >= self.config['max_segments_to_analyze']:
                    logger.info(f"⏭️ Reached maximum segments limit ({self.config['max_segments_to_analyze']}), stopping analysis")
                    break
                
                logger.info(f"🔍 Analyzing segment {i+1}/{len(dialogue_segments)}: '{segment.text[:50]}...' by {segment.speaker}")
                
                # Enhanced filtering for better quality analysis
                should_analyze = (
                    segment.speaker and 
                    len(segment.text) >= self.config['dialogue_min_length'] and
                    not self._is_narrative_text(segment.text) and
                    segment.confidence >= 0.5  # Only analyze confident dialogue detection
                )
                
                if should_analyze:
                    try:
                        result = await self._analyze_dialogue_with_gemini(
                            segment, character_profiles, user_id
                        )
                        if result:
                            results.append(result)
                            analyzed_count += 1
                            logger.info(f"✅ Analysis complete for segment {i+1}: {result.character_name} - {'Consistent' if result.is_consistent else 'Inconsistent'}")
                        else:
                            logger.warning(f"❌ Analysis failed for segment {i+1}")
                    except Exception as e:
                        logger.error(f"❌ Gemini analysis failed for segment {i+1}: {e}")
                        # Continue with other segments instead of failing completely
                        continue
                else:
                    logger.info(f"⚠️ Skipping segment {i+1}: speaker='{segment.speaker}', length={len(segment.text)}, min_length={self.config['dialogue_min_length']}, confidence={segment.confidence:.2f}")
            
            logger.info(f"📊 Analyzed {analyzed_count} out of {len(dialogue_segments)} total segments")
            
            # Update character profiles with new dialogue
            try:
                await self._update_character_profiles(dialogue_segments, user_id)
                logger.info(f"📝 Updated character profiles with {len(dialogue_segments)} segments")
            except Exception as e:
                logger.error(f"❌ Character profile update failed: {e}")
                # Don't fail the whole process if profile update fails
                pass
            
            logger.info(f"🎉 Voice consistency analysis complete: {len(results)} results generated")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error analyzing text for voice consistency: {str(e)}")
            logger.error(f"🔍 Error details: {type(e).__name__}: {str(e)}")
            logger.error(f"🔍 Error traceback: {e.__traceback__}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
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
        
        logger.info(f"Starting dialogue extraction from text with {len(text)} characters")
        logger.info(f"Text preview: {text[:200]}...")
        logger.info(f"Dialogue patterns count: {len(self.dialogue_patterns)}")
        logger.info(f"Minimum dialogue length: {self.config['dialogue_min_length']}")
        
        # DEBUG: Test each pattern individually
        for i, pattern in enumerate(self.dialogue_patterns):
            try:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
                logger.info(f"🔍 Pattern {i} found {len(matches)} matches")
                for j, match in enumerate(matches[:3]):  # Show first 3 matches
                    logger.info(f"  Match {j+1}: {match.group()}")
            except Exception as e:
                logger.error(f"❌ Pattern {i} failed: {e}")
        
        # First, try to extract dialogue with speaker attribution
        attributed_segments = 0
        for pattern_idx in range(1, len(self.dialogue_patterns)):  # Skip pattern 0 (basic quotes)
            pattern = self.dialogue_patterns[pattern_idx]
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            logger.info(f"Pattern {pattern_idx} found {len(matches)} matches")
            
            for match in matches:
                # Extract dialogue text and speaker based on pattern
                dialogue_text = None
                speaker = None
                
                if len(match.groups()) >= 2:
                    if pattern_idx == 1:  # Pattern 1: "Dialogue," Speaker said
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip()
                    elif pattern_idx == 2:  # Pattern 2: Speaker said, "Dialogue"
                        speaker = match.group(1).strip()
                        dialogue_text = match.group(2).strip()
                    elif pattern_idx == 3:  # Pattern 3: "Dialogue," he/she said
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip().title()  # Convert "he" to "He"
                elif len(match.groups()) >= 1:
                    # Pattern 4: Simple "dialogue" with basic punctuation
                    dialogue_text = match.group(1).strip()
                    speaker = "Unknown Speaker"
                
                # Skip if dialogue is too short
                if not dialogue_text or len(dialogue_text) < self.config['dialogue_min_length']:
                    logger.debug(f"Skipping short dialogue: '{dialogue_text}' (length: {len(dialogue_text) if dialogue_text else 0})")
                    continue
                
                # Skip if speaker is None or empty
                if not speaker:
                    logger.debug(f"Skipping dialogue with no speaker: '{dialogue_text}'")
                    continue
                
                # Clean and validate speaker name
                speaker = self._clean_character_name(speaker)
                if not speaker:
                    logger.debug(f"Skipping dialogue with invalid speaker after cleaning: '{dialogue_text}'")
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
                    confidence=0.9 if speaker != "Unknown Speaker" else 0.6
                )
                
                segments.append(segment)
                attributed_segments += 1
                logger.debug(f"Added attributed dialogue: '{dialogue_text}' by {speaker}")
        
        logger.info(f"Found {attributed_segments} attributed dialogue segments")
        
        # ALWAYS try to extract basic quoted dialogue and attempt to infer speakers
        # This ensures we don't miss dialogue just because it lacks clear attribution
        logger.info("Extracting basic quoted dialogue for speaker inference")
        basic_quotes = list(re.finditer(self.dialogue_patterns[0], text, re.IGNORECASE | re.MULTILINE))
        logger.info(f"Found {len(basic_quotes)} basic quoted dialogue segments")
        
        # CRITICAL: Log the actual pattern and some sample matches for debugging
        logger.info(f"Basic dialogue pattern: {self.dialogue_patterns[0]}")
        if basic_quotes:
            for i, match in enumerate(basic_quotes[:3]):  # Log first 3 matches
                logger.info(f"Basic match {i+1}: '{match.group(1)}' at position {match.start()}")
        else:
            logger.warning("❌ No basic quoted dialogue found - this might indicate a pattern issue")
        
        inferred_segments = 0
        for match in basic_quotes:
            dialogue_text = match.group(1).strip()
            
            # Skip if dialogue is too short
            if len(dialogue_text) < self.config['dialogue_min_length']:
                logger.debug(f"Skipping short basic dialogue: '{dialogue_text}' (length: {len(dialogue_text)})")
                continue
            
            # Skip if this dialogue is already captured by attributed patterns
            already_captured = False
            for existing_segment in segments:
                if abs(existing_segment.position - match.start()) < 50:  # Within 50 characters
                    already_captured = True
                    break
            
            if already_captured:
                logger.debug(f"Skipping already captured dialogue: '{dialogue_text}'")
                continue
            
            # Try to infer speaker from surrounding context
            start_pos = max(0, match.start() - self.config['context_window'])
            end_pos = min(len(text), match.end() + self.config['context_window'])
            
            context_before = text[start_pos:match.start()].strip()
            context_after = text[match.end():end_pos].strip()
            
            # Simple speaker inference - look for capitalized names near the dialogue
            speaker = self._infer_speaker_from_context(context_before, context_after, dialogue_text)
            
            if speaker:
                # Create dialogue segment
                segment = DialogueSegment(
                    text=dialogue_text,
                    speaker=speaker,
                    context_before=context_before,
                    context_after=context_after,
                    position=match.start(),
                    confidence=0.6  # Lower confidence for inferred speakers
                )
                
                segments.append(segment)
                inferred_segments += 1
                logger.debug(f"Added inferred dialogue: '{dialogue_text}' by {speaker} (inferred)")
            else:
                # Create segment with generic speaker for analysis
                segment = DialogueSegment(
                    text=dialogue_text,
                    speaker="Unknown Speaker",
                    context_before=context_before,
                    context_after=context_after,
                    position=match.start(),
                    confidence=0.4  # Lower confidence for unknown speakers
                )
                
                segments.append(segment)
                inferred_segments += 1
                logger.debug(f"Added unknown speaker dialogue: '{dialogue_text}' by Unknown Speaker")
        
        logger.info(f"Found {inferred_segments} basic dialogue segments (inferred/unknown speakers)")
        
        # Remove duplicates and sort by position
        unique_segments = []
        seen_positions = set()
        
        for segment in sorted(segments, key=lambda x: x.position):
            if segment.position not in seen_positions:
                unique_segments.append(segment)
                seen_positions.add(segment.position)
        
        logger.info(f"Final result: {len(unique_segments)} unique dialogue segments from {len(text)} characters")
        
        # Debug logging - show first few segments
        for i, segment in enumerate(unique_segments[:3]):  # Log first 3 segments
            logger.info(f"Segment {i+1}: Speaker='{segment.speaker}', Text='{segment.text[:50]}...', Confidence={segment.confidence}")
        
        return unique_segments
    
    def _infer_speaker_from_context(self, context_before: str, context_after: str, dialogue_text: str) -> Optional[str]:
        """Try to infer speaker from surrounding context"""
        # Combine contexts for analysis
        full_context = f"{context_before} {context_after}"
        
        # Look for patterns like "John said" or "Mary asked" near the dialogue
        speaker_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)',
            r'(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in speaker_patterns:
            matches = re.finditer(pattern, full_context, re.IGNORECASE)
            for match in matches:
                speaker = match.group(1).strip()
                # Basic validation - speaker should be a reasonable name
                if len(speaker) >= 2 and len(speaker) <= 50:
                    return speaker
        
        # If no speaker found, try to find any capitalized name in context
        name_pattern = r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b'
        names = re.findall(name_pattern, full_context)
        
        if names:
            # Return the first reasonable name found
            for name in names:
                if len(name) >= 3 and len(name) <= 50:
                    return name
        
        return None
    
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
            
            # Handle "Unknown Speaker" segments with general quality analysis
            if segment.speaker == "Unknown Speaker":
                return await self._analyze_dialogue_quality_only(segment, user_id)
            
            # Check if we have a profile for this character
            if speaker_key not in character_profiles:
                # For first-time analysis, provide general dialogue quality feedback
                return await self._analyze_dialogue_first_time(segment, user_id)
            
            profile = character_profiles[speaker_key]
            
            # Create Gemini prompt for voice consistency analysis
            previous_dialogue = "\n".join([f'"{sample}"' for sample in profile.dialogue_samples[-5:]])
            
            prompt = f"""
            You are analyzing character voice consistency. Be CRITICAL and look for actual inconsistencies.
            
            Character: {profile.character_name}
            
            Previous dialogue examples from this character:
            {previous_dialogue}
            
            New dialogue to analyze:
            "{segment.text}"
            
            CRITICAL ANALYSIS - Look for these inconsistencies:
            - Different vocabulary level (formal vs casual)
            - Different sentence structure patterns  
            - Different personality traits showing through speech
            - Different regional/cultural speech patterns
            - Different emotional expression styles
            - Contradictory character voice elements
            
            BE CRITICAL: Only mark as consistent if the voice truly matches the established pattern.
            If there are ANY noticeable differences in how this character speaks, mark as inconsistent.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "confidence_score": float (0.7-1.0),
                "similarity_score": float (0.7-1.0),
                "explanation": "specific explanation with examples from the text",
                "suggestions": ["specific actionable suggestions"]
            }}
            """
            
            # Use Gemini 1.5 Flash for analysis (cheaper and faster)
            logger.info(f"🤖 Calling Gemini for voice analysis: {profile.character_name}")
            
            # Add timeout protection at service level to prevent hanging
            import asyncio
            try:
                response = await asyncio.wait_for(
                    self.gemini_service.generate_json_response(
                        prompt, 
                        max_tokens=400, 
                        temperature=0.3
                    ),
                    timeout=15.0  # 15 second timeout to prevent frontend timeout
                )
                logger.info(f"🤖 Gemini response received for {profile.character_name}: {type(response)}")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Gemini analysis timed out after 15s for {profile.character_name}")
                # Return a default "consistent" result instead of failing
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name=profile.character_name,
                    flagged_text=segment.text,
                    explanation="Voice analysis timed out. Please try again with shorter text.",
                    suggestions=["Try analyzing smaller text segments"],
                    analysis_method='gemini_timeout_fallback'
                )
            except Exception as e:
                logger.error(f"❌ Gemini analysis failed for {profile.character_name}: {str(e)}")
                # Return a default "consistent" result instead of failing
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name=profile.character_name,
                    flagged_text=segment.text,
                    explanation=f"Voice analysis failed: {str(e)[:100]}...",
                    suggestions=["Try again later or check your internet connection"],
                    analysis_method='gemini_error_fallback'
                )
            
            if response and isinstance(response, dict):
                # Create result
                result = VoiceConsistencyResult(
                    is_consistent=response.get('is_consistent', False),
                    confidence_score=max(response.get('confidence_score', 0.8), 0.7),  # Minimum 0.7
                    similarity_score=max(response.get('similarity_score', 0.8), 0.7),  # Minimum 0.7
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
    
    async def _analyze_dialogue_quality_only(
        self, 
        segment: DialogueSegment, 
        user_id: int
    ) -> Optional[VoiceConsistencyResult]:
        """Analyze dialogue quality when speaker is unknown"""
        try:
            # Create a general dialogue quality analysis prompt
            prompt = f"""
            You are analyzing dialogue quality. Be CRITICAL and identify real issues.
            
            Character: {segment.speaker}
            Dialogue: "{segment.text}"
            
            CRITICAL ANALYSIS - Look for these problems:
            - Unnatural or awkward phrasing
            - Inconsistent character voice within this dialogue
            - Poor word choices or unclear meaning
            - Dialogue that doesn't sound like real speech
            - Generic or bland character voice
            
            BE CRITICAL: Mark as inconsistent (poor quality) if there are real issues.
            Don't just mark everything as good - look for actual problems.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "confidence_score": float (0.7-1.0),
                "similarity_score": float (0.7-1.0),
                "explanation": "specific assessment of what works or doesn't work",
                "suggestions": ["specific ways to improve this dialogue"]
            }}
            """
            
            # Use Gemini 1.5 Flash for analysis with timeout protection
            logger.info(f"🤖 Calling Gemini for quality analysis: Unknown Speaker")
            import asyncio
            try:
                response = await asyncio.wait_for(
                    self.gemini_service.generate_json_response(
                        prompt, 
                        max_tokens=400, 
                        temperature=0.3
                    ),
                    timeout=15.0  # 15 second timeout
                )
                logger.info(f"🤖 Gemini response received for quality analysis: {type(response)}")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Gemini quality analysis timed out after 15s")
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name="Unknown Speaker",
                    flagged_text=segment.text,
                    explanation="Dialogue quality analysis timed out. Please try again with shorter text.",
                    suggestions=["Try analyzing smaller text segments"],
                    analysis_method='gemini_timeout_fallback'
                )
            except Exception as e:
                logger.error(f"❌ Gemini quality analysis failed: {str(e)}")
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name="Unknown Speaker",
                    flagged_text=segment.text,
                    explanation=f"Dialogue quality analysis failed: {str(e)[:100]}...",
                    suggestions=["Try again later or check your internet connection"],
                    analysis_method='gemini_error_fallback'
                )
            
            if response and isinstance(response, dict):
                # Create result - mark as inconsistent if dialogue quality is poor
                is_consistent = response.get('is_consistent', False)
                
                result = VoiceConsistencyResult(
                    is_consistent=is_consistent,
                    confidence_score=min(response.get('confidence_score', 0.6), 1.0),
                    similarity_score=min(response.get('similarity_score', 0.6), 1.0),
                    character_name="Unknown Speaker",
                    flagged_text=segment.text,
                    explanation=response.get('explanation', 'General dialogue quality analysis completed'),
                    suggestions=response.get('suggestions', []),
                    analysis_method='gemini_quality_analysis'
                )
                
                logger.debug(f"Quality analysis - Unknown Speaker, "
                           f"Quality: {result.is_consistent}, "
                           f"Confidence: {result.confidence_score:.3f}")
                
                return result
            
        except Exception as e:
            logger.error(f"Error in dialogue quality analysis: {str(e)}")
        
        return None
    
    async def _analyze_dialogue_first_time(
        self, 
        segment: DialogueSegment, 
        user_id: int
    ) -> Optional[VoiceConsistencyResult]:
        """Analyze dialogue for first-time character appearance"""
        try:
            # Create a general dialogue quality analysis prompt
            prompt = f"""
            You are analyzing dialogue quality. Be CRITICAL and identify real issues.
            
            Character: {segment.speaker}
            Dialogue: "{segment.text}"
            
            CRITICAL ANALYSIS - Look for these problems:
            - Unnatural or awkward phrasing
            - Inconsistent character voice within this dialogue
            - Poor word choices or unclear meaning
            - Dialogue that doesn't sound like real speech
            - Generic or bland character voice
            
            BE CRITICAL: Mark as inconsistent (poor quality) if there are real issues.
            Don't just mark everything as good - look for actual problems.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "confidence_score": float (0.7-1.0),
                "similarity_score": float (0.7-1.0),
                "explanation": "specific assessment of what works or doesn't work",
                "suggestions": ["specific ways to improve this dialogue"]
            }}
            """
            
            # Use Gemini 1.5 Flash for analysis with timeout protection
            logger.info(f"�� Calling Gemini for first-time analysis: {segment.speaker}")
            import asyncio
            try:
                response = await asyncio.wait_for(
                    self.gemini_service.generate_json_response(
                        prompt, 
                        max_tokens=400, 
                        temperature=0.3
                    ),
                    timeout=15.0  # 15 second timeout
                )
                logger.info(f"🤖 Gemini response received for first-time analysis: {type(response)}")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Gemini first-time analysis timed out after 15s for {segment.speaker}")
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name=segment.speaker,
                    flagged_text=segment.text,
                    explanation="First-time dialogue analysis timed out. Please try again with shorter text.",
                    suggestions=["Try analyzing smaller text segments"],
                    analysis_method='gemini_timeout_fallback'
                )
            except Exception as e:
                logger.error(f"❌ Gemini first-time analysis failed for {segment.speaker}: {str(e)}")
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.5,
                    similarity_score=0.5,
                    character_name=segment.speaker,
                    flagged_text=segment.text,
                    explanation=f"First-time dialogue analysis failed: {str(e)[:100]}...",
                    suggestions=["Try again later or check your internet connection"],
                    analysis_method='gemini_error_fallback'
                )
            
            if response and isinstance(response, dict):
                # Create result - mark as inconsistent if dialogue quality is poor
                is_consistent = response.get('is_consistent', False)
                
                result = VoiceConsistencyResult(
                    is_consistent=is_consistent,
                    confidence_score=min(response.get('confidence_score', 0.7), 1.0),
                    similarity_score=min(response.get('similarity_score', 0.7), 1.0),
                    character_name=segment.speaker,
                    flagged_text=segment.text,
                    explanation=response.get('explanation', 'First-time character analysis completed'),
                    suggestions=response.get('suggestions', []),
                    analysis_method='gemini_first_time_analysis'
                )
                
                logger.debug(f"First-time analysis - Character: {segment.speaker}, "
                           f"Quality: {result.is_consistent}, "
                           f"Confidence: {result.confidence_score:.3f}")
                
                return result
            
        except Exception as e:
            logger.error(f"Error in first-time dialogue analysis: {str(e)}")
        
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
                    
                    logger.info(f"Created new character profile for '{character_name}' with {len(new_samples)} samples")
            
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
            character_id = hashlib.sha256(f"{user_id}_{character_name}".encode()).hexdigest()
            
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
            return {'status': 'error'}

# Create alias for backward compatibility
CharacterVoiceService = SimpleCharacterVoiceService 