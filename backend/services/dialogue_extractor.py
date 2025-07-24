"""
Dialogue Extraction Module - Comprehensive Pattern Recognition

This module provides robust dialogue extraction capabilities for character voice analysis.
Separated for maintainability and easy pattern extension.

Design Principles:
- Single Responsibility: Only dialogue extraction logic
- Extensible: Easy to add new patterns
- Testable: Isolated logic for unit testing
- Performance: Optimized regex compilation
"""

import re
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DialogueMatch:
    """Represents a matched dialogue segment with metadata."""
    text: str
    speaker: Optional[str]
    start_pos: int
    end_pos: int
    pattern_name: str
    confidence: float  # 0.0-1.0, how confident we are this is dialogue

class DialogueExtractor:
    """
    Comprehensive dialogue extraction with pattern-based recognition.
    
    Handles various formats:
    - Standard format: Character: "dialogue"
    - Markdown format: **Character:** "dialogue" 
    - Attribution format: "dialogue," Character said
    - Tag format: Character said, "dialogue"
    - Plain quotes: "dialogue" (speaker inferred)
    - And many more...
    """
    
    def __init__(self):
        # Compile patterns once for performance
        self.patterns = self._compile_patterns()
        logger.debug(f"🎭 DialogueExtractor initialized with {len(self.patterns)} patterns")
    
    def _compile_patterns(self) -> List[Tuple[re.Pattern, str, float, bool]]:
        """
        Compile all dialogue patterns with metadata.
        
        Returns:
            List of (compiled_pattern, name, confidence, has_explicit_speaker)
        """
        
        # Pattern definitions: (regex, name, confidence, has_explicit_speaker)
        pattern_defs = [
            # HIGH CONFIDENCE - Explicit speaker patterns
            
            # Standard dialogue format: "Character: dialogue"
            (r'^([A-Z][a-zA-Z\s]{1,25}):\s*"([^"]{3,})"', 
             'Standard Character Colon', 0.95, True),
            
            # Markdown bold: "**Character:** dialogue"
            (r'\*\*([A-Z][a-zA-Z\s]{1,25})\*\*:\s*"([^"]{3,})"', 
             'Markdown Bold Character', 0.9, True),
            
            # Paragraph start with character name
            (r'\n([A-Z][a-zA-Z\s]{1,25}):\s*"([^"]{3,})"', 
             'Paragraph Character Colon', 0.9, True),
            
            # Character name at line start
            (r'(?:^|\n)\s*([A-Z][a-zA-Z\s]{1,25}):\s*"([^"]{3,})"', 
             'Line Start Character', 0.85, True),
            
            # MEDIUM CONFIDENCE - Attribution patterns
            
            # Post-dialogue attribution: "dialogue," Character said
            (r'"([^"]{3,}),"?\s+([A-Z][a-zA-Z\s]{1,25})\s+(?:said|asked|replied|whispered|shouted|muttered|exclaimed|continued|added|interrupted)', 
             'Post Attribution', 0.8, True),
            
            # Pre-dialogue tag: Character said, "dialogue"
            (r'([A-Z][a-zA-Z\s]{1,25})\s+(?:said|asked|replied|whispered|shouted|muttered|exclaimed|continued|added|interrupted)[^"]*"([^"]{3,})"', 
             'Pre Attribution', 0.8, True),
            
            # LOWER CONFIDENCE - Speaker inference required
            
            # Basic quoted dialogue (speaker inferred)
            (r'"([^"]{5,})"', 
             'Basic Quotes', 0.6, False),
            
            # Single quoted dialogue  
            (r"'([^']{5,})'", 
             'Single Quotes', 0.5, False),
            
            # Em-dash dialogue
            (r'—([^—\n]{5,})', 
             'Em Dash', 0.4, False),
            
            # Angle bracket dialogue (sometimes used)
            (r'<([^<>]{5,})>', 
             'Angle Brackets', 0.3, False),
        ]
        
        compiled = []
        for regex, name, confidence, has_speaker in pattern_defs:
            try:
                pattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
                compiled.append((pattern, name, confidence, has_speaker))
                logger.debug(f"✅ Compiled pattern: {name}")
            except re.error as e:
                logger.error(f"❌ Failed to compile pattern {name}: {e}")
        
        return compiled
    
    def extract_dialogue(self, text: str, min_confidence: float = 0.3) -> List[DialogueMatch]:
        """
        Extract dialogue segments from text.
        
        Args:
            text: Input text to analyze
            min_confidence: Minimum confidence threshold (0.0-1.0)
            
        Returns:
            List of DialogueMatch objects sorted by position
        """
        if not text or not text.strip():
            return []
        
        logger.info(f"🎭 Extracting dialogue from {len(text)} chars (min_confidence={min_confidence})")
        
        matches = []
        found_positions = set()  # Avoid overlapping matches
        
        for pattern, name, confidence, has_explicit_speaker in self.patterns:
            if confidence < min_confidence:
                continue
                
            pattern_matches = 0
            
            for match in pattern.finditer(text):
                start_pos = match.start()
                end_pos = match.end()
                
                # Skip if this position overlaps with a higher-confidence match
                if any(start_pos < existing_end and end_pos > existing_start 
                       for existing_start, existing_end in found_positions):
                    continue
                
                # Extract speaker and dialogue based on pattern type
                if has_explicit_speaker and len(match.groups()) >= 2:
                    speaker = match.group(1).strip()
                    dialogue_text = match.group(2).strip()
                elif len(match.groups()) >= 1:
                    dialogue_text = match.group(1).strip()
                    speaker = None  # Will be inferred later
                else:
                    continue
                
                # Validate dialogue quality
                if not self._is_valid_dialogue(dialogue_text):
                    continue
                
                # Clean speaker name
                if speaker:
                    speaker = self._clean_speaker_name(speaker)
                    if not self._is_valid_speaker_name(speaker):
                        speaker = None
                
                dialogue_match = DialogueMatch(
                    text=dialogue_text,
                    speaker=speaker,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    pattern_name=name,
                    confidence=confidence
                )
                
                matches.append(dialogue_match)
                found_positions.add((start_pos, end_pos))
                pattern_matches += 1
                
                logger.debug(f"   📝 {name}: '{dialogue_text[:30]}...' → {speaker or 'Unknown'}")
            
            if pattern_matches > 0:
                logger.debug(f"✅ Pattern '{name}': {pattern_matches} matches")
        
        # Sort by position and apply speaker inference
        matches.sort(key=lambda x: x.start_pos)
        matches = self._infer_missing_speakers(matches, text)
        
        logger.info(f"✅ Extracted {len(matches)} dialogue segments")
        return matches
    
    def _is_valid_dialogue(self, text: str) -> bool:
        """Validate if text looks like actual dialogue."""
        if not text or len(text.strip()) < 3:
            return False
        
        # Filter out common non-dialogue patterns
        text_lower = text.lower().strip()
        
        # Too short or just punctuation
        if len(text_lower) < 3 or re.match(r'^[^a-z]*$', text_lower):
            return False
        
        # Common false positives
        false_positives = [
            r'^(yes|no|ok|okay|oh|ah|um|uh|hm|hmm)\.?$',
            r'^\.{3,}$',  # Just ellipsis
            r'^\s*[\-—]\s*$',  # Just dashes
            r'^chapter \d+',  # Chapter headings
            r'^\d+[\.\)]\s',  # Numbered lists
        ]
        
        for pattern in false_positives:
            if re.match(pattern, text_lower):
                return False
        
        return True
    
    def _clean_speaker_name(self, speaker: str) -> str:
        """Clean and normalize speaker name."""
        if not speaker:
            return ""
        
        # Remove common artifacts
        speaker = re.sub(r'[^\w\s]', '', speaker)  # Remove punctuation
        speaker = re.sub(r'\s+', ' ', speaker)     # Normalize whitespace
        speaker = speaker.strip().title()          # Title case
        
        return speaker
    
    def _is_valid_speaker_name(self, speaker: str) -> bool:
        """Validate if a string looks like a valid character name."""
        if not speaker or len(speaker) < 2:
            return False
        
        # Must be alphabetic with possible spaces
        if not re.match(r'^[A-Za-z\s]{2,25}$', speaker):
            return False
        
        # Filter out common non-character words
        speaker_lower = speaker.lower()
        non_character_words = {
            'chapter', 'part', 'section', 'prologue', 'epilogue',
            'narrator', 'author', 'voice', 'person', 'someone',
            'anyone', 'everyone', 'nobody', 'somebody',
            'the', 'and', 'but', 'for', 'with', 'said', 'asked'
        }
        
        if speaker_lower in non_character_words:
            return False
        
        return True
    
    def _infer_missing_speakers(self, matches: List[DialogueMatch], text: str) -> List[DialogueMatch]:
        """
        Infer speakers for dialogue segments that don't have explicit speakers.
        Uses context analysis and speaker tracking.
        """
        if not matches:
            return matches
        
        # Track known speakers and their recent positions
        known_speakers = {}
        last_speaker = None
        
        for i, match in enumerate(matches):
            if match.speaker:
                # We have an explicit speaker
                known_speakers[match.speaker] = match.start_pos
                last_speaker = match.speaker
            else:
                # Try to infer speaker from context
                inferred_speaker = self._infer_speaker_from_context(
                    match, text, known_speakers, last_speaker
                )
                
                if inferred_speaker:
                    # Create new match with inferred speaker
                    matches[i] = DialogueMatch(
                        text=match.text,
                        speaker=inferred_speaker,
                        start_pos=match.start_pos,
                        end_pos=match.end_pos,
                        pattern_name=match.pattern_name + " (Inferred)",
                        confidence=match.confidence * 0.8  # Reduce confidence for inference
                    )
                    last_speaker = inferred_speaker
        
        return matches
    
    def _infer_speaker_from_context(
        self, 
        dialogue_match: DialogueMatch, 
        full_text: str,
        known_speakers: dict,
        last_speaker: Optional[str]
    ) -> Optional[str]:
        """Infer speaker from surrounding context."""
        
        # Get context around the dialogue
        context_start = max(0, dialogue_match.start_pos - 200)
        context_end = min(len(full_text), dialogue_match.end_pos + 200)
        context = full_text[context_start:context_end]
        
        # Look for speaker attribution patterns in context
        attribution_patterns = [
            r'([A-Z][a-zA-Z\s]{2,15})\s+(?:said|asked|replied|whispered|shouted|muttered|exclaimed|continued|added|interrupted)',
            r'([A-Z][a-zA-Z\s]{2,15})(?:\'s|s)\s+voice',
            r'([A-Z][a-zA-Z\s]{2,15})\s+(?:looked|turned|smiled|frowned|nodded|shook|gestured)',
        ]
        
        for pattern in attribution_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            for potential_speaker in matches:
                cleaned = self._clean_speaker_name(potential_speaker)
                if self._is_valid_speaker_name(cleaned):
                    return cleaned
        
        # If no attribution found, check if we can use the last known speaker
        # (useful for continued dialogue from same character)
        if last_speaker and len(dialogue_match.text) < 50:  # Short responses often from same speaker
            return last_speaker
        
        # Look for any proper nouns in context that might be character names
        proper_nouns = re.findall(r'\b([A-Z][a-z]{2,15})\b', context)
        for noun in proper_nouns:
            if self._is_valid_speaker_name(noun) and noun not in {'The', 'And', 'But', 'For', 'With'}:
                return noun
        
        return None

# Global instance for easy import
dialogue_extractor = DialogueExtractor() 