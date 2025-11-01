"""
Character Voice Consistency Service - Refactored Implementation

This service provides comprehensive character voice consistency analysis using the standardized GeminiService.
It includes dialogue extraction, speaker inference, character profiles, and voice analysis.
"""

import re
import json
import logging
import hashlib
import html
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# CRITICAL FIX: Use the LLM service coordinator (same as successful contextual understanding)
from services.llm_service import llm_service
from services.dialogue_extractor import dialogue_extractor

# Import the proper schema models
from models.schemas import VoiceConsistencyResult, DialogueSegment, CharacterVoiceProfile
from config.demo_config import is_demo_enabled, detect_demo_content, demo_config

# Configure logging with more detailed formatting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PERFORMANCE OPTIMIZATION: Pre-compile frequently used regex patterns
# These patterns are used repeatedly in _infer_speaker_from_context and other methods
_NAME_PATTERN = re.compile(r'\b([A-Z][a-z]{1,15})\b')
_SENTENCE_NAME_PATTERN = re.compile(r'^([A-Z][a-z]{1,15})')
_HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
_DIALOGUE_PATTERN = re.compile(r'([.!?])\s*([A-Z][a-zA-Z\s]{1,25}):\s*"')
_JSON_ARRAY_PATTERN = re.compile(r'\[([^\]]*)\]')

# Optimized stopwords list - reduced from the original massive set for better performance
COMMON_NON_CHARACTER_WORDS = {
    # Core stopwords (most essential ones)
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 
    'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 
    'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 
    'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 
    'just', 'don', 'should', 'now',
    
    # Common titles and honorifics
    'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'professor', 'sir', 'madam', 'lord', 'lady',
    'king', 'queen', 'prince', 'princess', 'duke', 'duchess', 'count', 'countess', 'baron',
    'captain', 'major', 'colonel', 'general', 'admiral', 'sergeant', 'lieutenant',
    
    # Common places and locations
    'north', 'south', 'east', 'west', 'city', 'town', 'village', 'country', 'state', 
    'province', 'region', 'area', 'place', 'street', 'road', 'avenue', 'lane', 'drive',
    'house', 'home', 'building', 'hall', 'castle', 'palace', 'church', 'cathedral',
    'school', 'university', 'college', 'hospital', 'hotel', 'restaurant', 'shop', 'store',
    'market', 'square', 'park', 'garden', 'forest', 'mountain', 'hill', 'river', 'lake',
    'sea', 'ocean', 'island', 'bridge', 'tower', 'gate', 'wall', 'door', 'window', 'room',
    
    # Common objects and time-related words
    'thing', 'something', 'anything', 'nothing', 'everything', 'someone', 'anyone', 'everyone',
    'time', 'day', 'night', 'morning', 'afternoon', 'evening', 'week', 'month', 'year',
    'moment', 'hour', 'minute', 'second', 'today', 'tomorrow', 'yesterday', 'now', 'then',
    'way', 'manner', 'method', 'means', 'reason', 'cause', 'effect', 'result', 'end',
    'beginning', 'start', 'finish', 'part', 'whole', 'piece', 'bit', 'lot', 'much', 'many',
    'little', 'few', 'several', 'some', 'all', 'none', 'both', 'either', 'neither',
    
    # Numbers (written out)
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 
    'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
    'eighty', 'ninety', 'hundred', 'thousand', 'million', 'billion', 'first', 'second',
    'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
    
    # Common adjectives
    'good', 'bad', 'great', 'small', 'large', 'big', 'little', 'old', 'new', 'young',
    'long', 'short', 'high', 'low', 'right', 'left', 'next', 'last', 'first', 'final',
    'early', 'late', 'quick', 'slow', 'fast', 'easy', 'hard', 'difficult', 'simple',
    'complex', 'clear', 'dark', 'light', 'heavy', 'empty', 'full', 'open', 'closed',
    
    # Common dialogue verbs
    'said', 'told', 'asked', 'answered', 'replied', 'spoke', 'talked', 'whispered',
    'shouted', 'cried', 'laughed', 'smiled', 'looked', 'saw', 'watched', 'heard',
    'listened', 'felt', 'touched', 'held', 'took', 'gave', 'put', 'placed', 'moved',
    'walked', 'ran', 'came', 'went', 'left', 'arrived', 'stayed', 'lived', 'died',
    'worked', 'played', 'thought', 'knew', 'understood', 'remembered', 'forgot',
    
    # Common interjections
    'oh', 'ah', 'eh', 'um', 'hmm', 'yes', 'no', 'okay', 'ok', 'well', 'so', 'but',
    'however', 'therefore', 'thus', 'hence', 'indeed', 'certainly', 'surely', 'perhaps',
    'maybe', 'probably', 'definitely', 'absolutely', 'exactly', 'quite', 'rather',
    'really', 'truly', 'actually', 'basically', 'generally', 'usually', 'often',
    'sometimes', 'never', 'always', 'almost', 'nearly', 'hardly', 'barely',
    
    # Days and months
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
    'september', 'october', 'november', 'december'
}

class CharacterVoiceService:
    """
    Analyzes character voice consistency using the same successful pattern as contextual understanding.
    Uses the LLM service coordinator for consistent Gemini 2.5 Flash integration.
    """
    
    def __init__(self):
        logger.info("🎭 CharacterVoiceService: Initializing service...")
        try:
            # Test LLM service availability
            if hasattr(llm_service, 'generate_with_selected_llm'):
                logger.info("✅ CharacterVoiceService: LLM service coordinator available")
            else:
                logger.error("❌ CharacterVoiceService: LLM service coordinator missing generate_with_selected_llm method")
            
            # Load demo profiles if demo mode is active
            if is_demo_enabled():
                self.demo_profiles = demo_config.profiles
                self.demo_aliases = demo_config.aliases
                logger.info(f"✅ Loaded {len(self.demo_profiles)} profiles for '{demo_config.demo_name}' demo.")
            else:
                self.demo_profiles = {}
                self.demo_aliases = {}

            logger.info("✅ CharacterVoiceService: Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ CharacterVoiceService: Initialization failed: {e}")
            raise
    
    def _normalize_character_name(self, character_name: str) -> str:
        """
        Normalize character names for demo mode.
        Maps script format names to full profile names.
        """
        if not is_demo_enabled() or not self.demo_aliases:
            return character_name
            
        # Try exact match first
        if character_name in self.demo_aliases:
            normalized = self.demo_aliases[character_name]
            logger.debug(f"🔄 Normalized character name: '{character_name}' -> '{normalized}'")
            return normalized
            
        # Try case-insensitive match
        for alias, canonical in self.demo_aliases.items():
            if character_name.lower() == alias.lower():
                logger.debug(f"🔄 Normalized character name (case-insensitive): '{character_name}' -> '{canonical}'")
                return canonical
                
        # Return original if no match found
        return character_name
    
    def _is_likely_character_name(self, name: str) -> bool:
        """
        Pre-filter to determine if a name is likely to be a character name.
        Uses optimized stopwords filtering for better performance.
        This is a fast pre-filter before LLM validation.
        """
        if not name or len(name) < 2:
            return False
        
        # Convert to lowercase for checking
        name_lower = name.lower()
        
        # Filter out common non-character words
        if name_lower in COMMON_NON_CHARACTER_WORDS:
            logger.debug(f"🚫 Filtered out common word: {name}")
            return False
        
        # Must start with capital letter (proper noun)
        if not name[0].isupper():
            return False
        
        # Must be alphabetic (no numbers or special characters)
        if not name.isalpha():
            return False
        
        # Filter out single letters
        if len(name) == 1:
            return False
        
        # Filter out very long words (likely not names)
        if len(name) > 20:
            logger.debug(f"🚫 Filtered out overly long word: {name}")
            return False
        
        # Filter out words that are all uppercase (likely acronyms)
        if name.isupper() and len(name) > 1:
            logger.debug(f"🚫 Filtered out acronym: {name}")
            return False
        
        # Basic pattern check - should look like a name (Title case)
        if not (name[0].isupper() and name[1:].islower()):
            logger.debug(f"🚫 Filtered out non-title-case word: {name}")
            return False
        
        logger.debug(f"✅ Potential character name passed pre-filter: {name}")
        return True
    
    def _extract_dialogue_segments(self, text: str) -> List[DialogueSegment]:
        """
        Extract dialogue segments from text using the dedicated dialogue extractor.
        """
        logger.info(f"🔍 Starting dialogue extraction from {len(text)} chars of text")
        
        # Use the new dialogue extractor
        dialogue_matches = dialogue_extractor.extract_dialogue(text, min_confidence=0.5)
        
        # Convert DialogueMatch objects to DialogueSegment objects
        segments = []
        for match in dialogue_matches:
            # Get context before and after
            context_start = max(0, match.start_pos - 100)
            context_end = min(len(text), match.end_pos + 100)
            
            context_before = text[context_start:match.start_pos].strip()
            context_after = text[match.end_pos:context_end].strip()
            
            # Apply character name normalization for demo mode
            original_speaker = match.speaker or "Unknown"
            normalized_speaker = self._normalize_character_name(original_speaker)
            
            segment = DialogueSegment(
                text=match.text,
                speaker=normalized_speaker,  # Use normalized name
                position=match.start_pos,
                context_before=context_before,
                context_after=context_after
            )
            segments.append(segment)
        
        logger.info(f"✅ Dialogue extraction complete: Found {len(segments)} dialogue segments")
        
        if segments:
            logger.info(f"📝 Sample extracted dialogue:")
            for i, segment in enumerate(segments[:3]):
                logger.info(f"   {i+1}. Speaker: '{segment.speaker}' → '{segment.text[:80]}{'...' if len(segment.text) > 80 else ''}'")
            
            # Log character name mapping for demo mode
            unique_speakers = list(set(segment.speaker for segment in segments))
            logger.info(f"🎭 Found {len(unique_speakers)} unique speakers: {unique_speakers}")
        
        return segments
    
    def _infer_speaker_from_context(self, dialogue: str, context_before: str, context_after: str) -> str:
        """
        Infer the speaker of dialogue from surrounding context.
        Uses improved pattern matching for modern writing styles.
        """
        # IMPROVED: More comprehensive dialogue tag patterns
        tag_patterns = [
            # Standard dialogue tags
            r'(\w+)\s+said',
            r'(\w+)\s+asked',
            r'(\w+)\s+replied',
            r'(\w+)\s+whispered',
            r'(\w+)\s+shouted',
            r'(\w+)\s+muttered',
            r'(\w+)\s+exclaimed',
            r'(\w+)\s+continued',
            r'(\w+)\s+added',
            r'(\w+)\s+interrupted',
            # Additional common verbs
            r'(\w+)\s+called',
            r'(\w+)\s+cried',
            r'(\w+)\s+laughed',
            r'(\w+)\s+sighed',
            r'(\w+)\s+groaned',
            r'(\w+)\s+gasped',
            r'(\w+)\s+breathed',
            r'(\w+)\s+hissed',
            # Modern attributions
            r'(\w+)\s+grinned',
            r'(\w+)\s+smiled',
            r'(\w+)\s+frowned',
            r'(\w+)\s+shook',
            r'(\w+)\s+nodded',
            # Possessive forms
            r"(\w+)'s\s+voice",
            r"(\w+)'s\s+tone",
        ]
        
        # Check context after dialogue first (most common placement)
        for pattern in tag_patterns:
            match = re.search(pattern, context_after, re.IGNORECASE)
            if match:
                speaker = match.group(1).title()
                logger.debug(f"🎭 Found speaker '{speaker}' in context after dialogue")
                return speaker
        
        # Check context before dialogue (alternative placement)
        for pattern in tag_patterns:
            match = re.search(pattern, context_before, re.IGNORECASE)
            if match:
                speaker = match.group(1).title()
                logger.debug(f"🎭 Found speaker '{speaker}' in context before dialogue")
                return speaker
        
        # IMPROVED: Look for character names with better filtering
        # Look for proper nouns (capitalized words) that could be names
        # PERFORMANCE: Using pre-compiled regex pattern
        
        # Search in context after first, then before
        names_after = _NAME_PATTERN.findall(context_after)
        names_before = _NAME_PATTERN.findall(context_before)
        
        # Combine and filter out common non-character words
        all_names = names_after + names_before
        if all_names:
            # Enhanced filtering using the optimized stopwords list
            potential_names = []
            for name in all_names:
                name_lower = name.lower()
                # Skip if it's a common word, but keep if it looks like a real name
                if (name_lower not in COMMON_NON_CHARACTER_WORDS and 
                    len(name) >= 2 and 
                    not name_lower.endswith('ing') and 
                    not name_lower.endswith('ed') and
                    name_lower not in ['the', 'and', 'but', 'for', 'with', 'when', 'where', 'what']):
                    potential_names.append(name)
            
            if potential_names:
                speaker = potential_names[0]  # Take the first good candidate
                logger.debug(f"🎭 Inferred potential speaker '{speaker}' from nearby proper nouns")
                return speaker
        
        # FALLBACK: Try to extract from paragraph structure
        # Look for sentence fragments that might indicate speaker changes
        sentences_before = re.split(r'[.!?]', context_before)
        for sentence in reversed(sentences_before):
            sentence = sentence.strip()
            if sentence and len(sentence) > 5:
                # Look for a name at the start of a sentence
                # PERFORMANCE: Using pre-compiled regex pattern
                name_match = _SENTENCE_NAME_PATTERN.match(sentence)
                if name_match:
                    candidate = name_match.group(1)
                    if candidate.lower() not in COMMON_NON_CHARACTER_WORDS:
                        logger.debug(f"🎭 Inferred speaker '{candidate}' from paragraph structure")
                        return candidate
        
        # LAST RESORT: Create a speaker based on dialogue content
        # For cases where we have dialogue but no clear attribution
        if dialogue:
            # Look for self-referential pronouns to guess formality
            if any(word in dialogue.lower() for word in ['sir', 'madam', 'your lordship', 'your grace']):
                logger.debug("🎭 Formal dialogue detected, using 'Speaker' as placeholder")
                return "Speaker"
            elif any(word in dialogue.lower() for word in ['dude', 'mate', 'bro', 'hey']):
                logger.debug("🎭 Informal dialogue detected, using 'Character' as placeholder")
                return "Character"
        
        # Default fallback
        logger.debug("🎭 Could not infer speaker from context, using 'Unknown Speaker'")
        return "Unknown Speaker"
    
    async def _validate_character_names_with_llm(self, potential_characters: List[str], text_sample: str) -> List[str]:
        """
        Use LLM to validate which potential names are actually character names.
        This is much more accurate than word filtering.
        """
        if not potential_characters:
            return []
        
        logger.info(f"🤖 Using LLM to validate {len(potential_characters)} potential character names")
        logger.debug(f"   Potential names: {potential_characters}")
        
        try:
            # Create a focused prompt for character name validation
            prompt = f"""You are analyzing a text excerpt to identify actual character names (people who speak dialogue) versus other capitalized words.

TEXT SAMPLE (first 1000 chars):
{text_sample[:1000]}

POTENTIAL NAMES FOUND: {', '.join(potential_characters)}

Your task: Determine which of these are actual CHARACTER NAMES (people who speak or are referenced as characters) versus other capitalized words (places, things, titles, etc.).

CRITICAL: Respond with ONLY a valid JSON array of character names. No other text.

Example response format:
["Alice", "Bob", "Dr. Smith"]

If no actual character names are found, respond with:
[]

Character names to validate: {potential_characters}"""

            logger.debug(f"🤖 Sending character validation prompt to LLM...")
            response_text = await llm_service.generate_with_selected_llm(prompt, "Google Gemini")
            logger.debug(f"🤖 LLM character validation response: {response_text[:200]}...")
            
            # Parse the JSON response
            try:
                # Clean the response to extract just the JSON array
                response_text = response_text.strip()
                
                # Look for JSON array pattern
                # PERFORMANCE: Using pre-compiled regex pattern
                json_match = _JSON_ARRAY_PATTERN.search(response_text)
                if json_match:
                    json_text = json_match.group(0)
                    validated_characters = json.loads(json_text)
                    
                    # Ensure all items are strings and filter out empty ones
                    validated_characters = [str(name).strip() for name in validated_characters if str(name).strip()]
                    
                    logger.info(f"✅ LLM validated {len(validated_characters)} character names: {validated_characters}")
                    return validated_characters
                else:
                    logger.warning("⚠️ No JSON array found in LLM response")
                    return []
                    
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse LLM character validation response: {e}")
                logger.debug(f"   Raw response: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Character name validation failed: {e}")
            # Fallback: return names that look like character names (basic heuristics)
            fallback_characters = [name for name in potential_characters 
                                 if len(name) >= 2 and name.isalpha() and name[0].isupper()]
            logger.info(f"➡️ Using fallback character validation: {fallback_characters}")
            return fallback_characters
    
    def _build_character_profiles(self, segments: List[DialogueSegment]) -> Dict[str, CharacterVoiceProfile]:
        """
        Build character voice profiles from dialogue segments.
        """
        profiles = {}
        
        for segment in segments:
            speaker = segment.speaker
            if speaker == "Unknown":
                continue
            
            if speaker not in profiles:
                profiles[speaker] = CharacterVoiceProfile(
                    character_id=hashlib.md5(speaker.encode()).hexdigest()[:8],
                    character_name=speaker,
                    dialogue_samples=[],
                    voice_traits={},
                    last_updated=datetime.now().isoformat(),
                    sample_count=0
                )
            
            profiles[speaker].dialogue_samples.append(segment.text)
            profiles[speaker].sample_count += 1
        
        logger.info(f"👥 Built profiles for {len(profiles)} characters")
        return profiles
    
    async def analyze(self, text: str, existing_profiles: Optional[Dict[str, CharacterVoiceProfile]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive character voice consistency analysis.
        
        Args:
            text: The text to analyze
            existing_profiles: Optional existing character profiles from database
            
        Returns:
            Dictionary containing analysis results
        """
        analysis_start_time = datetime.now()
        
        try:
            # PERFORMANCE OPTIMIZATION: Reduced excessive logging for better performance
            logger.info(f"Starting character voice analysis: {len(text)} chars, {len(existing_profiles) if existing_profiles else 0} existing profiles")
            logger.debug(f"Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # 🐉 DEMO MODE: Check if this is demo content and inject demo profiles
            is_demo = detect_demo_content(text)
            if is_demo and self.demo_profiles:
                logger.info(f"🐉 === {demo_config.demo_name.upper()} DEMO MODE ACTIVATED ===")
                logger.info(f"🎭 Using {len(self.demo_profiles)} pre-loaded character profiles")
                existing_profiles = self.demo_profiles.copy()
                logger.info(f"✅ Demo profiles injected successfully")
            
            # Limit text length to prevent API timeouts
            # ENHANCED: Higher limit for demo mode to preserve full scripts
            MAX_TEXT_LENGTH = demo_config.max_text_length if is_demo else 10000
            if len(text) > MAX_TEXT_LENGTH:
                logger.info(f"Truncating text from {len(text)} to {MAX_TEXT_LENGTH} characters")
                text = text[:MAX_TEXT_LENGTH] + "\n\n[Text truncated for analysis efficiency]"
            
            # Remove HTML tags since TipTap editor sends HTML-formatted content
            original_length = len(text)
            text = html.unescape(text)
            
            # Convert HTML structure to preserve dialogue formatting
            text = re.sub(r'<(?:p|div|br)[^>]*>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'</(?:p|div)>', '\n', text, flags=re.IGNORECASE)
            
            # Remove all remaining HTML tags
            # PERFORMANCE: Using pre-compiled regex pattern
            plain_text = _HTML_TAG_PATTERN.sub('', text)
            
            # Clean whitespace while preserving dialogue structure
            plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
            plain_text = re.sub(r'[ \t]+', ' ', plain_text)
            plain_text = '\n'.join(line.strip() for line in plain_text.split('\n'))
            plain_text = re.sub(r'\n{3,}', '\n\n', plain_text)
            plain_text = plain_text.strip()
            
            logger.debug(f"Text processed: {original_length} -> {len(plain_text)} chars")
            
            text = plain_text
            
            # CRITICAL FIX: Ensure dialogue patterns have proper line breaks
            # This fixes the issue where "sentence.Alice: dialogue" becomes "sentence.\nAlice: dialogue"
            # PERFORMANCE: Using pre-compiled regex pattern
            text = _DIALOGUE_PATTERN.sub(r'\1\n\2: "', text)
            try:
                segments = self._extract_dialogue_segments(text)
                logger.info(f"Found {len(segments)} dialogue segments")
                logger.debug(f"Sample segments: {[(s.speaker, s.text[:30]) for s in segments[:3]]}")
                        
            except Exception as segment_error:
                logger.error(f"Dialogue extraction error: {segment_error}")
                logger.exception("Dialogue extraction traceback:")
                raise
            
            if not segments:
                logger.warning("⚠️ No dialogue found in text - returning empty results")
                return {
                    "results": [],
                    "characters_analyzed": 0,
                    "dialogue_segments_found": 0,
                    "processing_time_ms": 0
                }
            
            try:
                current_profiles = self._build_character_profiles(segments)
                logger.info(f"Built profiles for {len(current_profiles)} potential characters")
                
                # Use LLM to validate character names
                potential_character_names = list(current_profiles.keys())
                if potential_character_names:
                    validated_character_names = await self._validate_character_names_with_llm(
                        potential_character_names, 
                        text[:2000]
                    )
                    
                    # Only filter when LLM validation actually succeeded
                    if validated_character_names and len(validated_character_names) > 0:
                        validated_profiles = {
                            name: profile for name, profile in current_profiles.items() 
                            if name in validated_character_names
                        }
                        
                        logger.info(f"LLM validated {len(validated_profiles)} characters: {list(validated_profiles.keys())}")
                        logger.debug(f"Filtered out: {[name for name in current_profiles.keys() if name not in validated_character_names]}")
                        
                        current_profiles = validated_profiles
                    else:
                        logger.warning(f"LLM validation failed, using all {len(current_profiles)} detected characters")
                    
            except Exception as profile_error:
                logger.error(f"Profile building error: {profile_error}")
                logger.exception("Profile building traceback:")
                raise
            
            merged_count = 0
            if existing_profiles:
                for char_name, existing_profile in existing_profiles.items():
                    if char_name in current_profiles:
                        # Merge dialogue samples (keep recent ones)
                        all_samples = existing_profile.dialogue_samples + current_profiles[char_name].dialogue_samples
                        current_profiles[char_name].dialogue_samples = all_samples[-20:]  # Keep last 20 samples
                        current_profiles[char_name].voice_traits = existing_profile.voice_traits
                        merged_count += 1
                        
            logger.info(f"Merged {merged_count} existing profiles")
            
            results = []
            start_time = datetime.now()
            
            for character_name, profile in current_profiles.items():
                try:
                    result = await self._analyze_character_voice(profile, segments)
                    if result:
                        results.append(result)
                        logger.info(f"Analyzed {character_name}: Consistent={result.is_consistent}, Confidence={result.confidence_score}")
                    else:
                        logger.warning(f"No result for {character_name}")
                        
                except Exception as char_error:
                    logger.error(f"Analysis failed for {character_name}: {char_error}")
                    continue
            
            total_processing_time = (datetime.now() - analysis_start_time).total_seconds() * 1000
            logger.info(f"Analysis complete: {len(results)} characters, {len(segments)} segments, {int(total_processing_time)}ms")
            
            return {
                "results": results,
                "characters_analyzed": len(results),
                "dialogue_segments_found": len(segments),
                "processing_time_ms": int(total_processing_time)
            }
            
        except Exception as e:
            logger.error(f"❌ === SERVICE ANALYSIS FAILED ===")
            logger.error(f"🔍 Error Details:")
            logger.error(f"   - Error type: {type(e).__name__}")
            logger.error(f"   - Error message: {str(e)}")
            logger.error(f"   - Error occurred at: {datetime.now()}")
            logger.exception("Full service error traceback:")
            
            # Return a dictionary with a 'results' key to maintain a consistent return type
            logger.info(f"➡️ Returning empty results to prevent 500 error")
            return {
                "results": [],
                "characters_analyzed": 0,
                "dialogue_segments_found": 0,
                "processing_time_ms": 0,
                "error": str(e)
            }
    
    async def _analyze_character_voice(self, profile: CharacterVoiceProfile, all_segments: List[DialogueSegment]) -> Optional[VoiceConsistencyResult]:
        """
        Analyze voice consistency for a specific character using LLM analysis.
        """
        char_analysis_start = datetime.now()
        
        try:
            logger.info(f"🎭 === CHARACTER ANALYSIS START: {profile.character_name} ===")
            logger.info(f"📊 Character Analysis Input:")
            logger.info(f"   - Character name: {profile.character_name}")
            logger.info(f"   - Total segments available: {len(all_segments)}")
            logger.info(f"   - Profile dialogue samples: {len(profile.dialogue_samples)}")
            
            # Get this character's dialogue from the segments
            character_dialogue = [seg.text for seg in all_segments if seg.speaker == profile.character_name]
            logger.info(f"   - Character's dialogue found: {len(character_dialogue)} samples")
            
            if len(character_dialogue) < 2:
                logger.warning(f"⚠️ Insufficient dialogue for {profile.character_name}: {len(character_dialogue)} samples (need at least 2)")
                logger.info(f"   Available speakers in segments: {list(set(seg.speaker for seg in all_segments))}")
                return None
            
            logger.info(f"📝 Dialogue samples for {profile.character_name}:")
            for i, sample in enumerate(character_dialogue[:3]):
                logger.info(f"   Sample {i+1}: '{sample[:100]}{'...' if len(sample) > 100 else ''}'")
            
            # Limit dialogue samples to prevent overly long prompts
            MAX_SAMPLES = 10
            if len(character_dialogue) > MAX_SAMPLES:
                logger.info(f"🔧 Limiting dialogue samples from {len(character_dialogue)} to {MAX_SAMPLES} for {profile.character_name}")
                character_dialogue = character_dialogue[:MAX_SAMPLES]
            
            logger.info(f"🚀 CHARACTER STEP 1: Building analysis prompt...")
            # ANTI-SYCOPHANCY PROMPT: Based on latest AI research to prevent agreeableness bias
            prompt = f"""CRITICAL ANALYSIS PROTOCOL - Character Voice Forensics

MANDATORY ROLE: Senior Script Doctor with 20+ years detecting voice inconsistencies in premium television. You are RENOWNED for being critical and finding problems others miss. Your reputation depends on catching dialogue flaws.

ANTI-SYCOPHANCY DIRECTIVE: 
- DO NOT rationalize poor dialogue as acceptable
- DO NOT find ways to justify inconsistencies  
- DO NOT default to "consistent" unless genuinely warranted
- APPLY STRICT STANDARDS - be a harsh critic, not a cheerleader

ANALYSIS TARGET: {profile.character_name}

BASELINE CANONICAL SAMPLES (Gold Standard):
{chr(10).join(f'GOLD {i+1}: "{sample}"' for i, sample in enumerate(profile.dialogue_samples[:5]))}

CURRENT DIALOGUE TO ANALYZE (Suspect Quality):
{chr(10).join(f'TEST {i+1}: "{sample}"' for i, sample in enumerate(character_dialogue))}

STRICT CONSISTENCY STANDARDS:
1. VOCABULARY MATCH: Current dialogue MUST use {profile.character_name}'s signature vocabulary patterns
2. COMPLEXITY ALIGNMENT: Sentence structure MUST match baseline complexity levels
3. PATTERN DETECTION: MUST contain character's established speech patterns  
4. TONE VERIFICATION: MUST align with character's emotional and intellectual range

CONFIDENCE SCORING (BE RUTHLESSLY STRICT):
- 0.9-1.0: Perfect match (extremely rare - only for flawless dialogue)
- 0.7-0.89: Good consistency (solid match with minor acceptable variations)
- 0.5-0.69: CONCERNING inconsistencies (flag as problematic)
- 0.0-0.49: CRITICAL FAILURE (major voice break)

FORBIDDEN RATIONALIZATION PATTERNS:
❌ "This could be explained by character growth/development"
❌ "The context justifies this difference in voice"
❌ "While different, this maintains the character's essence"  
❌ "The variation is within acceptable character range"
❌ "This shows emotional depth/complexity"

REQUIRED CRITICAL ANALYSIS:
- Find specific vocabulary mismatches
- Identify sentence structure deviations
- Flag missing signature phrases/patterns
- Detect tone/register inconsistencies

MANDATORY JSON RESPONSE FORMAT:
{{
    "is_consistent": false,
    "confidence_score": 0.65,
    "explanation": "SPECIFIC problems: [detailed critique of exact issues found]",
    "flagged_text": "[most problematic dialogue sample]",
    "suggestions": ["Specific actionable fixes"]
}}

EXECUTE STRICT CRITICAL ANALYSIS NOW. No mercy for poor dialogue.
"""
            
            logger.info(f"✅ CHARACTER STEP 1 COMPLETE: Prompt built ({len(prompt)} chars)")
            logger.debug(f"   Prompt preview: {prompt[:200]}...")
            
            logger.info(f"🚀 CHARACTER STEP 2: Calling LLM service...")
            logger.info(f"   Using LLM provider: Google Gemini")
            logger.info(f"   Expected response time: 10-60 seconds")
            
            try:
                logger.debug(f"   Making LLM call with prompt length: {len(prompt)}")
                response_text = await llm_service.generate_with_selected_llm(prompt, "Google Gemini")
                logger.info(f"✅ CHARACTER STEP 2 COMPLETE: LLM response received")
                logger.info(f"   Response length: {len(response_text)} chars")
                logger.debug(f"   Response preview: {response_text[:200]}...")
                
            except Exception as llm_error:
                logger.error(f"❌ CHARACTER STEP 2 FAILED: LLM call error for {profile.character_name}: {llm_error}")
                logger.exception("LLM call traceback:")
                
                # Return a fallback result instead of failing
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.3,
                    similarity_score=0.5,
                    character_name=profile.character_name,
                    flagged_text="",
                    explanation=f"Analysis unavailable due to AI service error: {str(llm_error)}",
                    suggestions=["Please try again later when the AI service is available."],
                    analysis_method="llm_validated"
                )
            
            # Parse JSON response with improved error handling
            try:
                analysis_data = None
                
                # Try to parse the entire response as JSON first
                try:
                    analysis_data = json.loads(response_text.strip())
                    logger.info(f"✅ Successfully parsed complete response as JSON for {profile.character_name}")
                except json.JSONDecodeError:
                    # Extract JSON object using regex (fallback)
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            analysis_data = json.loads(json_match.group())
                            logger.info(f"✅ Successfully extracted JSON from response for {profile.character_name}")
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Extracted text is not valid JSON for {profile.character_name}")
                
                # If we successfully parsed JSON, validate it has required fields
                if analysis_data and isinstance(analysis_data, dict):
                    # Handle flagged_text - convert list to string if needed
                    flagged_text = analysis_data.get("flagged_text", "")
                    if isinstance(flagged_text, list):
                        if flagged_text:
                            flagged_text = str(flagged_text[0]) if len(flagged_text) == 1 else " | ".join(str(item) for item in flagged_text)
                        else:
                            flagged_text = ""
                    elif not isinstance(flagged_text, str):
                        flagged_text = str(flagged_text) if flagged_text is not None else ""
                    
                    # Handle suggestions - ensure it's always a list
                    suggestions = analysis_data.get("suggestions", ["Analysis completed successfully"])
                    if not isinstance(suggestions, list):
                        suggestions = [str(suggestions)] if suggestions else ["Analysis completed successfully"]
                    
                    analysis_data = {
                        "is_consistent": analysis_data.get("is_consistent", True),
                        "confidence_score": float(analysis_data.get("confidence_score", 0.5)),
                        "explanation": analysis_data.get("explanation", f"Voice analysis completed for {profile.character_name}"),
                        "flagged_text": flagged_text,
                        "suggestions": suggestions
                    }
                else:
                    # Fallback if no valid JSON found
                    logger.warning(f"⚠️ No valid JSON found in response for {profile.character_name}, creating fallback response")
                    
                    # Try to extract useful information from text response
                    is_consistent = "inconsistent" not in response_text.lower() and "problem" not in response_text.lower()
                    confidence = 0.6 if "consistent" in response_text.lower() else 0.4
                    
                    analysis_data = {
                        "is_consistent": is_consistent,
                        "confidence_score": confidence,
                        "explanation": response_text[:400] + "..." if len(response_text) > 400 else response_text,
                        "flagged_text": "",
                        "suggestions": ["Voice analysis completed. Please review the explanation for details."]
                    }
                
                return VoiceConsistencyResult(
                    is_consistent=analysis_data.get("is_consistent", True),
                    confidence_score=float(analysis_data.get("confidence_score", 0.4)),
                    similarity_score=0.8,  # Default similarity score for LLM analysis
                    character_name=profile.character_name,
                    flagged_text=analysis_data.get("flagged_text", ""),
                    explanation=analysis_data.get("explanation", "Analysis completed"),
                    suggestions=analysis_data.get("suggestions", []),
                    analysis_method="llm_validated"
                )
                
            except json.JSONDecodeError as json_error:
                logger.warning(f"⚠️ Could not parse JSON response for {profile.character_name}: {json_error}")
                # Return a realistic result with the actual response text
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.3,  # Lower confidence for parsing issues
                    similarity_score=0.5,  # Moderate similarity for parsing issues
                    character_name=profile.character_name,
                    flagged_text="",
                    explanation=f"Voice analysis completed for {profile.character_name}. Raw response: {response_text[:200]}..." if len(response_text) > 200 else response_text,
                    suggestions=["Analysis completed, but detailed suggestions are not available."],
                    analysis_method="llm_validated"
                )
            
        except Exception as e:
            logger.error(f"❌ Character analysis failed for {profile.character_name}: {str(e)}")
            # Return a fallback result instead of None to prevent empty results
            return VoiceConsistencyResult(
                is_consistent=True,
                confidence_score=0.2,  # Very low confidence for errors
                similarity_score=0.0,  # No similarity analysis for errors
                character_name=profile.character_name,
                flagged_text="",
                explanation=f"Voice analysis failed for {profile.character_name}: {str(e)}",
                suggestions=["Please try again later."],
                analysis_method="llm_validated"
            )
