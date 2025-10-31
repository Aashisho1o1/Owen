"""
Gemini Service - Core AI functionality for competition
Replaces llm_service with focused Gemini API integration
"""

import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Simplified Gemini service for voice consistency analysis.
    Handles dialogue extraction and character voice analysis using Gemini API.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY not found in environment")
        else:
            genai.configure(api_key=self.api_key)
            logger.info("✅ Gemini service initialized")

        self.model = genai.GenerativeModel('gemini-1.5-flash')

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

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                data = json.loads(json_str)
                return data.get('dialogues', [])

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

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Extract JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                return json.loads(json_str)

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
