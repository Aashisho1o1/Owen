"""
Character Voice Consistency Service - Complete Implementation

This service provides comprehensive character voice consistency analysis using the standardized GeminiService.
It includes dialogue extraction, speaker inference, character profiles, and voice analysis.
"""

import re
import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# CRITICAL FIX: Use the LLM service coordinator (same as successful contextual understanding)
from services.llm_service import llm_service

# Configure logging
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

@dataclass
class VoiceConsistencyResult:
    """Result of voice consistency analysis."""
    is_consistent: bool
    confidence_score: float
    character_name: str
    flagged_text: str
    explanation: str
    suggestions: List[str]

class CharacterVoiceService:
    """
    Analyzes character voice consistency using the same successful pattern as contextual understanding.
    Uses the LLM service coordinator for consistent Gemini 2.5 Flash integration.
    """
    
    def __init__(self):
        # CRITICAL FIX: Use the LLM service coordinator instead of direct GeminiService
        self.llm_service = llm_service
        logger.info("✅ CharacterVoiceService initialized with LLM service coordinator")
    
    def _extract_dialogue_segments(self, text: str) -> List[DialogueSegment]:
        """
        Extract dialogue segments from text with context.
        Handles various dialogue formats and quotation styles.
        """
        segments = []
        
        # Multiple dialogue patterns to handle different writing styles
        patterns = [
            # Standard quotes: "Hello," she said.
            r'"([^"]+)"[^a-zA-Z]*([^.!?]*[.!?])?',
            # Single quotes: 'Hello,' she said.
            r"'([^']+)'[^a-zA-Z]*([^.!?]*[.!?])?",
            # Em-dash dialogue: —Hello, she said.
            r'—([^—\n]+)',
            # Dialogue tags: She said, "Hello"
            r'([^.!?]*[.!?])[^a-zA-Z]*"([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                start_pos = match.start()
                end_pos = match.end()
                
                # Extract dialogue text (first capture group for most patterns)
                dialogue_text = match.group(1).strip()
                if not dialogue_text:
                    continue
                
                # Get context before and after
                context_start = max(0, start_pos - 100)
                context_end = min(len(text), end_pos + 100)
                
                context_before = text[context_start:start_pos].strip()
                context_after = text[end_pos:context_end].strip()
                
                # Infer speaker from context
                speaker = self._infer_speaker_from_context(
                    dialogue_text, context_before, context_after
                )
                
                segment = DialogueSegment(
                    text=dialogue_text,
                    speaker=speaker,
                    position=start_pos,
                    context_before=context_before,
                    context_after=context_after
                )
                segments.append(segment)
        
        # Remove duplicates and sort by position
        unique_segments = []
        seen_positions = set()
        
        for segment in sorted(segments, key=lambda x: x.position):
            if segment.position not in seen_positions:
                unique_segments.append(segment)
                seen_positions.add(segment.position)
        
        logger.info(f"📝 Extracted {len(unique_segments)} dialogue segments")
        return unique_segments
    
    def _infer_speaker_from_context(self, dialogue: str, context_before: str, context_after: str) -> str:
        """
        Infer the speaker of dialogue from surrounding context.
        Uses pattern matching and NLP techniques.
        """
        # Common dialogue tag patterns
        tag_patterns = [
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
        ]
        
        # Check context after dialogue first (more common)
        for pattern in tag_patterns:
            match = re.search(pattern, context_after, re.IGNORECASE)
            if match:
                speaker = match.group(1).title()
                logger.debug(f"🎭 Inferred speaker '{speaker}' from dialogue tag")
                return speaker
        
        # Check context before dialogue
        for pattern in tag_patterns:
            match = re.search(pattern, context_before, re.IGNORECASE)
            if match:
                speaker = match.group(1).title()
                logger.debug(f"🎭 Inferred speaker '{speaker}' from preceding context")
                return speaker
        
        # Look for character names in context (proper nouns)
        name_pattern = r'\b([A-Z][a-z]+)\b'
        names_before = re.findall(name_pattern, context_before)
        names_after = re.findall(name_pattern, context_after)
        
        # Prefer names from after context, then before
        all_names = names_after + names_before
        if all_names:
            # Filter out common words that aren't names
            common_words = {'The', 'She', 'He', 'They', 'It', 'This', 'That', 'But', 'And', 'Or'}
            potential_names = [name for name in all_names if name not in common_words]
            if potential_names:
                speaker = potential_names[0]
                logger.debug(f"🎭 Inferred speaker '{speaker}' from context names")
                return speaker
        
        # Default to "Unknown" if no speaker can be inferred
        logger.debug("🎭 Could not infer speaker, using 'Unknown'")
        return "Unknown"
    
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
        try:
            logger.info(f"🔍 Starting voice analysis for text ({len(text)} chars)")
            
            # Extract dialogue segments
            segments = self._extract_dialogue_segments(text)
            
            if not segments:
                logger.warning("⚠️ No dialogue found in text")
                return {
                    "results": [],
                    "characters_analyzed": 0,
                    "dialogue_segments_found": 0,
                    "processing_time_ms": 0
                }
            
            # Build character profiles from current text
            current_profiles = self._build_character_profiles(segments)
            
            # Merge with existing profiles if provided
            if existing_profiles:
                for char_name, existing_profile in existing_profiles.items():
                    if char_name in current_profiles:
                        # Merge dialogue samples (keep recent ones)
                        all_samples = existing_profile.dialogue_samples + current_profiles[char_name].dialogue_samples
                        current_profiles[char_name].dialogue_samples = all_samples[-20:]  # Keep last 20 samples
                        current_profiles[char_name].voice_traits = existing_profile.voice_traits
            
            # Perform AI analysis for each character
            results = []
            start_time = datetime.now()
            
            for character_name, profile in current_profiles.items():
                if len(profile.dialogue_samples) < 2:
                    # Need at least 2 samples for consistency analysis
                    continue
                
                # Analyze this character's voice consistency
                character_result = await self._analyze_character_voice(profile, segments)
                if character_result:
                    results.append(character_result)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"✅ Voice analysis complete: {len(results)} characters analyzed")
            
            return {
                "results": results,
                "characters_analyzed": len(results),
                "dialogue_segments_found": len(segments),
                "processing_time_ms": int(processing_time)
            }
            
        except Exception as e:
            logger.error(f"❌ Voice analysis failed: {str(e)}")
            # Return empty results instead of raising exception
            return {
                "results": [],
                "characters_analyzed": 0,
                "dialogue_segments_found": 0,
                "processing_time_ms": 0,
                "error": str(e)
            }
    
    async def _analyze_character_voice(self, profile: CharacterVoiceProfile, all_segments: List[DialogueSegment]) -> Optional[VoiceConsistencyResult]:
        """
        Analyze voice consistency for a specific character using the EXACT same pattern as successful contextual understanding.
        """
        try:
            # Get this character's dialogue from the segments
            character_dialogue = [seg.text for seg in all_segments if seg.speaker == profile.character_name]
            
            if len(character_dialogue) < 2:
                return None
            
            # Create analysis prompt with EXPLICIT JSON formatting requirements for Gemini 2.5 Flash
            prompt = f"""You are an expert character voice consistency analyzer. Analyze the voice consistency of the character "{profile.character_name}" based on their dialogue samples.

Character Dialogue Samples:
{chr(10).join(f'"{sample}"' for sample in character_dialogue)}

CRITICAL: You MUST respond with ONLY a valid JSON object. No other text before or after the JSON.

Analyze the character's voice consistency and respond with this EXACT JSON format:

{{
    "is_consistent": true,
    "confidence_score": 0.85,
    "explanation": "Detailed analysis of voice consistency patterns",
    "flagged_text": "Any specific inconsistent dialogue (empty string if all consistent)",
    "suggestions": ["Specific suggestion 1", "Specific suggestion 2"]
}}

Rules:
- is_consistent: true if voice is consistent, false if inconsistencies found
- confidence_score: number between 0.0 and 1.0 (higher = more confident)
- explanation: detailed analysis of speaking patterns, tone, vocabulary consistency
- flagged_text: exact dialogue text that seems inconsistent (empty string if none)
- suggestions: array of specific improvement suggestions

RESPOND WITH ONLY THE JSON OBJECT. NO OTHER TEXT."""
            
            # CRITICAL FIX: Use the EXACT same successful pattern as contextual understanding
            logger.info(f"🚀 Generating voice analysis with Google Gemini...")
            
            try:
                # Format prompt for Gemini (same as successful chat) - expects list of dicts
                prompts = [
                    {"role": "user", "parts": [prompt]}
                ]
                logger.info("🔧 Formatted prompt for Gemini (voice analysis)")
                
                # Use the same LLM service method as successful contextual understanding
                response_text = await self.llm_service.generate_with_selected_llm(prompts, "Google Gemini")
                logger.info(f"✅ Gemini voice analysis response received (length: {len(response_text) if response_text else 0} chars)")
                
            except Exception as llm_error:
                logger.error(f"❌ LLM Generation Error with Google Gemini (voice analysis): {llm_error}")
                logger.error(f"❌ LLM Error Type: {type(llm_error).__name__}")
                logger.error(f"❌ LLM Error Details: {str(llm_error)}")
                
                # Return fallback result with realistic confidence score
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.3,  # Lower confidence for fallback
                    character_name=profile.character_name,
                    flagged_text="",
                    explanation=f"Voice analysis temporarily unavailable for {profile.character_name}. AI service error: {str(llm_error)}",
                    suggestions=["Please try again later when the AI service is available."]
                )
            
            # Parse JSON response with improved error handling and multiple extraction methods
            try:
                analysis_data = None
                
                # Method 1: Try to parse the entire response as JSON first (best case)
                try:
                    analysis_data = json.loads(response_text.strip())
                    logger.info(f"✅ Successfully parsed complete response as JSON for {profile.character_name}")
                except json.JSONDecodeError:
                    # Method 2: Extract JSON object using regex (fallback)
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            analysis_data = json.loads(json_match.group())
                            logger.info(f"✅ Successfully extracted JSON from response for {profile.character_name}")
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Extracted text is not valid JSON for {profile.character_name}")
                
                # If we successfully parsed JSON, validate it has required fields
                if analysis_data and isinstance(analysis_data, dict):
                    # Ensure all required fields exist with defaults
                    analysis_data = {
                        "is_consistent": analysis_data.get("is_consistent", True),
                        "confidence_score": float(analysis_data.get("confidence_score", 0.5)),
                        "explanation": analysis_data.get("explanation", f"Voice analysis completed for {profile.character_name}"),
                        "flagged_text": analysis_data.get("flagged_text", ""),
                        "suggestions": analysis_data.get("suggestions", ["Analysis completed successfully"])
                    }
                else:
                    # Improved fallback if no valid JSON found
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
                    character_name=profile.character_name,
                    flagged_text=analysis_data.get("flagged_text", ""),
                    explanation=analysis_data.get("explanation", "Analysis completed"),
                    suggestions=analysis_data.get("suggestions", [])
                )
                
            except json.JSONDecodeError as json_error:
                logger.warning(f"⚠️ Could not parse JSON response for {profile.character_name}: {json_error}")
                # Return a realistic result with the actual response text
                return VoiceConsistencyResult(
                    is_consistent=True,
                    confidence_score=0.3,  # Lower confidence for parsing issues
                    character_name=profile.character_name,
                    flagged_text="",
                    explanation=f"Voice analysis completed for {profile.character_name}. Raw response: {response_text[:200]}..." if len(response_text) > 200 else response_text,
                    suggestions=["Analysis completed, but detailed suggestions are not available."]
                )
                
        except Exception as e:
            logger.error(f"❌ Character analysis failed for {profile.character_name}: {str(e)}")
            # Return a fallback result instead of None to prevent empty results
            return VoiceConsistencyResult(
                is_consistent=True,
                confidence_score=0.2,  # Very low confidence for errors
                character_name=profile.character_name,
                flagged_text="",
                explanation=f"Voice analysis failed for {profile.character_name}: {str(e)}",
                suggestions=["Please try again later."]
            )
