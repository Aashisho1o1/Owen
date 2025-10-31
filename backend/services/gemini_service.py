"""
Gemini Service - Core AI functionality for competition
Replaces llm_service with focused Gemini API integration
"""

import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
from functools import lru_cache
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Simplified Gemini service for voice consistency analysis.
    Handles dialogue extraction and character voice analysis using Gemini API.
    Includes response caching for improved performance.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment")
        else:
            genai.configure(api_key=self.api_key)
            logger.info("✅ Gemini service initialized")

        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self._response_cache: Dict[str, Any] = {}
        self._cache_max_size = 100

    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()

    def _get_cached_response(self, prompt: str) -> Optional[Any]:
        """Get cached response if available."""
        cache_key = self._get_cache_key(prompt)
        return self._response_cache.get(cache_key)

    def _cache_response(self, prompt: str, response: Any) -> None:
        """Cache a response with size limit."""
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self._response_cache))
            del self._response_cache[first_key]
        
        cache_key = self._get_cache_key(prompt)
        self._response_cache[cache_key] = response

    async def extract_dialogue(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract dialogue segments using Gemini (replaces regex patterns).

        Returns:
            List of { speaker: str, text: str, confidence: float }
        """
        prompt = f"""Extract all dialogue from this text and identify the speakers.

TEXT:
\"\"\"
{text}
\"\"\"

Return ONLY valid JSON in this exact format:
{{
  "dialogues": [
    {{"speaker": "Character Name", "text": "Their dialogue here", "confidence": 0.95}}
  ]
}}

Rules:
- Extract ALL dialogue, even without explicit speaker tags
- Infer speaker from context when not explicitly stated
- Use "Unknown" if speaker cannot be determined
- Confidence: 1.0 = explicit speaker, 0.8 = inferred, 0.5 = uncertain
"""

        # Check cache first
        cached = self._get_cached_response(prompt)
        if cached is not None:
            logger.info("✅ Using cached dialogue extraction")
            return cached

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Optimized JSON extraction - try direct parse first
            data = None
            try:
                # Try parsing the entire response as JSON
                data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fall back to finding JSON boundaries
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    data = json.loads(json_str)

            if data:
                dialogues = data.get('dialogues', [])
                self._cache_response(prompt, dialogues)
                return dialogues

            logger.error("❌ No valid JSON in Gemini response")
            return []

        except Exception as e:
            logger.error(f"❌ Dialogue extraction failed: {e}")
            return []

    async def analyze_voice_consistency(
        self,
        character_name: str,
        dialogue_samples: List[str],
        existing_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze voice consistency for a character.

        Args:
            character_name: Name of the character
            dialogue_samples: List of dialogue strings
            existing_profile: Previous voice traits (if any)

        Returns:
            {
                "is_consistent": bool,
                "confidence_score": float,
                "voice_traits": {...},
                "suggestions": [...]
            }
        """
        profile_context = ""
        if existing_profile and existing_profile.get('voice_traits'):
            traits = existing_profile['voice_traits']
            profile_context = f"""
KNOWN VOICE PROFILE for {character_name}:
- Formality: {traits.get('formality', 'Unknown')}
- Vocabulary: {traits.get('vocabulary', 'Unknown')}
- Tone: {traits.get('tone', 'Unknown')}
- Complexity: {traits.get('complexity', 'Unknown')}
"""

        prompt = f"""Analyze voice consistency for the character "{character_name}".

{profile_context}

NEW DIALOGUE SAMPLES:
{chr(10).join(f'{i+1}. "{sample}"' for i, sample in enumerate(dialogue_samples))}

Analyze:
1. Is the voice consistent across all samples?
2. What are the voice traits (formality, vocabulary, tone, complexity)?
3. If inconsistent, what specific issues exist?

Return ONLY valid JSON in this format:
{{
  "is_consistent": true/false,
  "confidence_score": 0.0-1.0,
  "voice_traits": {{
    "formality": "formal/neutral/casual",
    "vocabulary": "simple/moderate/sophisticated",
    "tone": "serious/friendly/humorous/etc",
    "complexity": "simple/moderate/complex"
  }},
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["suggestion 1", "suggestion 2"]
}}
"""

        # Check cache first
        cached = self._get_cached_response(prompt)
        if cached is not None:
            logger.info(f"✅ Using cached voice analysis for {character_name}")
            return cached

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Optimized JSON extraction
            analysis = None
            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError:
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = result_text[json_start:json_end]
                    analysis = json.loads(json_str)

            if analysis:
                self._cache_response(prompt, analysis)
                return analysis

            logger.error("❌ No valid JSON in voice analysis response")
            return self._default_analysis()

        except Exception as e:
            logger.error(f"❌ Voice analysis failed: {e}")
            return self._default_analysis()

    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when Gemini fails."""
        return {
            "is_consistent": True,
            "confidence_score": 0.5,
            "voice_traits": {
                "formality": "neutral",
                "vocabulary": "moderate",
                "tone": "neutral",
                "complexity": "moderate"
            },
            "issues": [],
            "suggestions": ["Unable to analyze - please try again"]
        }

# Global instance
gemini_service = GeminiService()
