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
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# CRITICAL FIX: Use the LLM service coordinator (same as successful contextual understanding)
from services.llm_service import llm_service

# Import the proper schema models
from models.schemas import VoiceConsistencyResult

# Configure logging with more detailed formatting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

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
            
            logger.info("✅ CharacterVoiceService: Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ CharacterVoiceService: Initialization failed: {e}")
            raise
    
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
        Extract dialogue segments from text with context.
        Handles various dialogue formats and quotation styles.
        """
        logger.info(f"🔍 Starting dialogue extraction from {len(text)} chars of text")
        logger.debug(f"   Text sample: {text[:500]}{'...' if len(text) > 500 else ''}")
        
        segments = []
        
        # IMPROVED: More robust dialogue patterns that handle modern writing styles
        patterns = [
            # FIXED: Bold markdown dialogue format: **Speaker:** "dialogue"
            r'\*\*([A-Z][a-zA-Z]*)\*\*:\s*"([^"]{2,})"',
            
            # Basic quoted dialogue: "Hello" (most common)
            r'"([^"]{2,})"',
            # Single quoted dialogue: 'Hello'
            r"'([^']{2,})'",
            # Em-dash dialogue: —Hello
            r'—([^—\n]{2,})',
            # Dialogue with attribution: "Hello," she said.
            r'"([^"]{2,}),"?\s*[a-zA-Z][^.!?]*[.!?]',
            # Dialogue with speaker tags: She said, "Hello"
            r'[A-Z][^.!?]*[.!?]?\s*"([^"]{2,})"',
        ]
        
        logger.info(f"🔍 Testing {len(patterns)} improved dialogue patterns...")
        
        # Track found segments to avoid duplicates
        found_segments = set()
        
        for i, pattern in enumerate(patterns):
            pattern_name = [
                'Bold markdown dialogue',  # **Speaker:** "dialogue"
                'Basic quoted dialogue',
                'Single quoted dialogue', 
                'Em-dash dialogue',
                'Dialogue with attribution',
                'Speaker tag dialogue'
            ][i]
            
            logger.debug(f"   Testing pattern {i+1}: {pattern_name}")
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            pattern_matches = 0
            
            for match in matches:
                pattern_matches += 1
                start_pos = match.start()
                end_pos = match.end()
                
                # FIXED: Handle both single-group and two-group patterns
                if len(match.groups()) == 2:
                    # Two groups: speaker and dialogue (e.g., **Speaker:** "dialogue")
                    speaker = match.group(1).strip()
                    dialogue_text = match.group(2).strip()
                elif len(match.groups()) == 1:
                    # One group: just dialogue (infer speaker from context)
                    dialogue_text = match.group(1).strip()
                    speaker = None  # Will be inferred later
                else:
                    # Skip patterns with unexpected group count
                    logger.debug(f"     Match {pattern_matches}: Unexpected group count {len(match.groups())}, skipping")
                    continue
                
                # Skip very short or empty dialogue
                if not dialogue_text or len(dialogue_text) < 3:
                    logger.debug(f"     Match {pattern_matches}: Too short dialogue text, skipping")
                    continue
                
                # Skip if we've already found this exact dialogue at this position
                segment_key = (dialogue_text, start_pos)
                if segment_key in found_segments:
                    logger.debug(f"     Match {pattern_matches}: Duplicate dialogue, skipping")
                    continue
                
                found_segments.add(segment_key)
                
                logger.debug(f"     Match {pattern_matches}: Found dialogue: '{dialogue_text[:50]}{'...' if len(dialogue_text) > 50 else ''}'")
                
                # Get context before and after
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), end_pos + 100)
                
                context_before = text[context_start:start_pos].strip()
                context_after = text[end_pos:context_end].strip()
                
                # Use extracted speaker or infer from context
                if not speaker:
                    speaker = self._infer_speaker_from_context(
                        dialogue_text, context_before, context_after
                    )
                
                logger.debug(f"     Match {pattern_matches}: Speaker: '{speaker}'")
                
                segment = DialogueSegment(
                    text=dialogue_text,
                    speaker=speaker,
                    position=start_pos,
                    context_before=context_before,
                    context_after=context_after
                )
                
                segments.append(segment)
                
            logger.debug(f"   Pattern {i+1} ({pattern_name}): Found {pattern_matches} matches")
        
        # Remove duplicate segments (same dialogue text with different speakers)
        unique_segments = []
        seen_dialogue = set()
        
        for segment in segments:
            # Create a normalized version for comparison
            normalized_dialogue = segment.text.lower().strip('.,!?;:"\'')
            
            if normalized_dialogue not in seen_dialogue:
                seen_dialogue.add(normalized_dialogue)
                unique_segments.append(segment)
            else:
                logger.debug(f"   Removing duplicate dialogue: '{segment.text[:30]}...'")
        
        logger.info(f"✅ Dialogue extraction complete: Found {len(unique_segments)} unique dialogue segments")
        
        if unique_segments:
            logger.info(f"📝 Sample extracted dialogue:")
            for i, segment in enumerate(unique_segments[:3]):
                logger.info(f"   {i+1}. Speaker: '{segment.speaker}' → '{segment.text[:80]}{'...' if len(segment.text) > 80 else ''}'")
        else:
            logger.warning(f"⚠️ No dialogue segments found. Text sample for debugging:")
            logger.warning(f"   {text[:300]}{'...' if len(text) > 300 else ''}")
        
        return unique_segments
    
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
        name_pattern = r'\b([A-Z][a-z]{1,15})\b'  # Limit length to avoid false positives
        
        # Search in context after first, then before
        names_after = re.findall(name_pattern, context_after)
        names_before = re.findall(name_pattern, context_before)
        
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
                name_match = re.match(r'^([A-Z][a-z]{1,15})', sentence)
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
                json_match = re.search(r'\[([^\]]*)\]', response_text)
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
            logger.info(f"🔍 === SERVICE ANALYSIS START ===")
            logger.info(f"📊 Input Analysis:")
            logger.info(f"   - Text length: {len(text)} chars")
            logger.info(f"   - Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")
            logger.info(f"   - Has HTML tags: {bool(re.search(r'<[^>]+>', text))}")
            logger.info(f"   - Existing profiles: {len(existing_profiles) if existing_profiles else 0}")
            
            logger.info(f"🚀 SERVICE STEP 1: Text preprocessing...")
            # Limit text length to prevent API timeouts
            MAX_TEXT_LENGTH = 10000
            if len(text) > MAX_TEXT_LENGTH:
                logger.info(f"🔧 Truncating text from {len(text)} to {MAX_TEXT_LENGTH} characters for analysis")
                text = text[:MAX_TEXT_LENGTH] + "\n\n[Text truncated for analysis efficiency]"
            
            logger.info(f"🧹 Removing HTML tags and entities...")
            # Remove HTML tags since TipTap editor sends HTML-formatted content
            original_length = len(text)
            text = html.unescape(text)
            logger.debug(f"   HTML entities unescaped: {original_length} -> {len(text)} chars")
            
            # Convert HTML structure to preserve dialogue formatting
            text = re.sub(r'<(?:p|div|br)[^>]*>', '\n', text, flags=re.IGNORECASE)
            text = re.sub(r'</(?:p|div)>', '\n', text, flags=re.IGNORECASE)
            
            # Remove all remaining HTML tags
            html_tag_pattern = re.compile(r'<[^>]+>')
            plain_text = html_tag_pattern.sub('', text)
            logger.debug(f"   HTML tags removed: {len(text)} -> {len(plain_text)} chars")
            
            # Clean whitespace while preserving dialogue structure
            plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
            plain_text = re.sub(r'[ \t]+', ' ', plain_text)
            plain_text = '\n'.join(line.strip() for line in plain_text.split('\n'))
            plain_text = re.sub(r'\n{3,}', '\n\n', plain_text)
            plain_text = plain_text.strip()
            
            logger.debug(f"   Whitespace cleaned: {len(plain_text)} chars final")
            logger.info(f"📝 Text processing result:")
            logger.info(f"   - Original: {original_length} chars")
            logger.info(f"   - Final: {len(plain_text)} chars")
            logger.info(f"   - Sample: {plain_text[:300]}{'...' if len(plain_text) > 300 else ''}")
            
            logger.info(f"✅ SERVICE STEP 1 COMPLETE: Text cleaned from {original_length} to {len(plain_text)} chars")
            
            text = plain_text
            
            logger.info(f"🚀 SERVICE STEP 2: Extracting dialogue segments...")
            try:
                segments = self._extract_dialogue_segments(text)
                logger.info(f"✅ SERVICE STEP 2 COMPLETE: Found {len(segments)} dialogue segments")
                
                if segments:
                    logger.info(f"📝 Dialogue segments preview:")
                    for i, segment in enumerate(segments[:3]):
                        logger.info(f"   Segment {i+1}: Speaker='{segment.speaker}', Text='{segment.text[:50]}{'...' if len(segment.text) > 50 else ''}'")
                        
            except Exception as segment_error:
                logger.error(f"❌ SERVICE STEP 2 FAILED: Dialogue extraction error: {segment_error}")
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
            
            logger.info(f"🚀 SERVICE STEP 3: Building character profiles...")
            try:
                current_profiles = self._build_character_profiles(segments)
                logger.info(f"📊 Initial profile building found {len(current_profiles)} potential characters")
                
                # Use LLM to validate character names
                potential_character_names = list(current_profiles.keys())
                if potential_character_names:
                    logger.info(f"🤖 SERVICE STEP 3a: LLM validation of character names...")
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
                        
                        logger.info(f"✅ SERVICE STEP 3 COMPLETE: LLM validated {len(validated_profiles)} real characters from {len(current_profiles)} potential names")
                        logger.info(f"   Validated characters: {list(validated_profiles.keys())}")
                        logger.info(f"   Filtered out: {[name for name in current_profiles.keys() if name not in validated_character_names]}")
                        
                        current_profiles = validated_profiles
                    else:
                        logger.warning(f"⚠️ LLM validation failed or returned zero characters")
                        logger.info(f"➡️ FALLBACK: Using all {len(current_profiles)} heuristically detected characters")
                        logger.info(f"   Fallback characters: {list(current_profiles.keys())}")
                
                for char_name, profile in current_profiles.items():
                    logger.debug(f"   Final profile: {char_name} - {len(profile.dialogue_samples)} samples")
                    
            except Exception as profile_error:
                logger.error(f"❌ SERVICE STEP 3 FAILED: Profile building error: {profile_error}")
                logger.exception("Profile building traceback:")
                raise
            
            logger.info(f"🚀 SERVICE STEP 4: Merging with existing profiles...")
            merged_count = 0
            if existing_profiles:
                for char_name, existing_profile in existing_profiles.items():
                    if char_name in current_profiles:
                        logger.debug(f"   Merging profile for: {char_name}")
                        # Merge dialogue samples (keep recent ones)
                        all_samples = existing_profile.dialogue_samples + current_profiles[char_name].dialogue_samples
                        current_profiles[char_name].dialogue_samples = all_samples[-20:]  # Keep last 20 samples
                        current_profiles[char_name].voice_traits = existing_profile.voice_traits
                        merged_count += 1
                        
            logger.info(f"✅ SERVICE STEP 4 COMPLETE: Merged {merged_count} existing profiles")
            
            logger.info(f"🚀 SERVICE STEP 5: Performing AI analysis for each character...")
            results = []
            start_time = datetime.now()
            
            character_count = 0
            for character_name, profile in current_profiles.items():
                character_count += 1
                logger.info(f"🧠 Analyzing character {character_count}/{len(current_profiles)}: {character_name}")
                
                try:
                    logger.debug(f"   Calling _analyze_character_voice for {character_name}...")
                    result = await self._analyze_character_voice(profile, segments)
                    
                    if result:
                        results.append(result)
                        logger.info(f"   ✅ Analysis complete for {character_name}: Consistent={result.is_consistent}, Confidence={result.confidence_score}")
                    else:
                        logger.warning(f"   ⚠️ No result returned for {character_name}")
                        
                except Exception as char_error:
                    logger.error(f"   ❌ Analysis failed for {character_name}: {char_error}")
                    logger.exception(f"Character analysis traceback for {character_name}:")
                    continue
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            total_processing_time = (datetime.now() - analysis_start_time).total_seconds() * 1000
            
            logger.info(f"✅ SERVICE STEP 5 COMPLETE: {len(results)} characters analyzed")
            logger.info(f"📊 Analysis Results Summary:")
            logger.info(f"   - Characters analyzed: {len(results)}")
            logger.info(f"   - Dialogue segments found: {len(segments)}")
            logger.info(f"   - AI processing time: {int(processing_time)}ms")
            logger.info(f"   - Total processing time: {int(total_processing_time)}ms")
            
            for i, result in enumerate(results):
                logger.debug(f"   Result {i+1}: {result.character_name} - Consistent: {result.is_consistent}, Confidence: {result.confidence_score}")
            
            logger.info(f"✅ === SERVICE ANALYSIS COMPLETE ===")
            
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
            
            # Return empty results instead of raising exception to prevent 500 errors
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
            # Create analysis prompt with explicit JSON formatting requirements
            prompt = f"""You are an expert character voice consistency analyzer. Analyze the voice consistency of the character "{profile.character_name}" based on their dialogue samples.

Character Dialogue Samples:
{chr(10).join(f'"{sample}"' for sample in character_dialogue)}

CRITICAL: You MUST respond with ONLY a valid JSON object. No other text before or after the JSON.

Analyze the character's voice consistency and respond with this EXACT JSON format:

{{
    "is_consistent": true,
    "confidence_score": 0.85,
    "explanation": "The character maintains consistent voice patterns across all samples.",
    "flagged_text": "Any specific inconsistent dialogue here",
    "suggestions": ["Suggestion 1", "Suggestion 2"]
}}

Focus on:
1. Speech patterns and vocabulary consistency
2. Tone and formality level consistency  
3. Character-specific phrases or expressions
4. Overall voice authenticity

Respond with ONLY the JSON object."""
            
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
