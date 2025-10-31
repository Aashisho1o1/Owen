"""
Character Voice Service - Simplified for competition
Uses Gemini for all analysis (no regex extraction)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from services.gemini_service import gemini_service
from services.database import db_service

logger = logging.getLogger(__name__)

class CharacterVoiceService:
    """
    Analyzes character voice consistency using Gemini API.
    Stores character profiles in database for ongoing tracking.
    """

    async def analyze(
        self,
        text: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Main analysis method.

        1. Extract dialogue using Gemini
        2. Load existing character profiles from database
        3. Analyze voice consistency for each character
        4. Update profiles in database
        5. Return results

        Args:
            text: Text to analyze
            user_id: User ID for profile storage

        Returns:
            {
                "results": [VoiceAnalysisResult],
                "characters_analyzed": int,
                "dialogue_segments_found": int
            }
        """
        logger.info(f"🎭 Starting voice analysis for user {user_id}")
        logger.info(f"📝 Text length: {len(text)} chars")

        # Step 1: Extract dialogue using Gemini
        logger.info("🔍 Extracting dialogue...")
        dialogues = await gemini_service.extract_dialogue(text)
        logger.info(f"✅ Found {len(dialogues)} dialogue segments")

        if not dialogues:
            logger.warning("⚠️ No dialogue found in text")
            return {
                "results": [],
                "characters_analyzed": 0,
                "dialogue_segments_found": 0
            }

        # Step 2: Load existing character profiles
        logger.info("📚 Loading character profiles...")
        profiles = {}
        if db_service.is_available():
            profile_rows = await db_service.get_character_profiles(user_id)
            profiles = {p['character_name']: p for p in profile_rows}
            logger.info(f"✅ Loaded {len(profiles)} existing profiles")

        # Step 3: Group dialogues by character
        character_dialogues: Dict[str, List[str]] = {}
        for dialogue in dialogues:
            speaker = dialogue.get('speaker', 'Unknown')
            if speaker and speaker != 'Unknown':
                if speaker not in character_dialogues:
                    character_dialogues[speaker] = []
                character_dialogues[speaker].append(dialogue['text'])

        logger.info(f"👥 Found {len(character_dialogues)} unique characters")

        # Step 4: Analyze all characters in parallel for better performance
        async def analyze_character(character_name: str, dialogue_samples: List[str]) -> Dict[str, Any]:
            """Analyze a single character's voice consistency."""
            logger.info(f"🎯 Analyzing {character_name} ({len(dialogue_samples)} samples)...")
            
            existing_profile = profiles.get(character_name)
            
            # Analyze with Gemini
            analysis = await gemini_service.analyze_voice_consistency(
                character_name,
                dialogue_samples,
                existing_profile
            )
            
            result = {
                "character_name": character_name,
                "is_consistent": analysis.get("is_consistent", True),
                "confidence_score": analysis.get("confidence_score", 0.8),
                "voice_traits": analysis.get("voice_traits", {}),
                "issues": analysis.get("issues", []),
                "suggestions": analysis.get("suggestions", []),
                "flagged_text": dialogue_samples[0] if not analysis.get("is_consistent") else None
            }
            
            # Update database
            if db_service.is_available():
                success = await db_service.upsert_character_profile(
                    user_id=user_id,
                    character_name=character_name,
                    dialogue_samples=dialogue_samples,
                    voice_traits=analysis.get("voice_traits", {})
                )
                if success:
                    logger.info(f"✅ Updated profile for {character_name}")
            
            return result
        
        # Execute all character analyses in parallel
        analysis_tasks = [
            analyze_character(char_name, samples)
            for char_name, samples in character_dialogues.items()
        ]
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Filter out any exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                char_name = list(character_dialogues.keys())[i]
                logger.error(f"❌ Failed to analyze {char_name}: {result}")
            else:
                valid_results.append(result)

        logger.info(f"✅ Analysis complete: {len(valid_results)} characters analyzed")

        return {
            "results": valid_results,
            "characters_analyzed": len(character_dialogues),
            "dialogue_segments_found": len(dialogues)
        }

# Global instance
character_voice_service = CharacterVoiceService()
