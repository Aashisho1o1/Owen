"""
Character Voice Consistency Detection Service - TinyStyler Edition

This service analyzes character dialogue for voice consistency in fiction writing.
It uses TinyStyler, a specialized model for text style transfer and authorship analysis,
providing superior character voice detection compared to general-purpose embeddings.

Key Features:
- TinyStyler-based character voice profiling
- Few-shot style learning from minimal dialogue samples
- Real-time style consistency detection
- Authorship embedding analysis
- Integration with existing chat system
"""

import re
import json
import logging
import asyncio
import importlib
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import torch
from huggingface_hub import hf_hub_download
from transformers import set_seed
import hashlib

from services.database import PostgreSQLService
from services.llm.gemini_service import GeminiService
from services.llm.openai_service import OpenAIService
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
    """Character voice profile with TinyStyler embeddings and metadata"""
    character_id: str
    character_name: str
    dialogue_samples: List[str]
    style_embedding: List[float]  # TinyStyler style embedding
    voice_characteristics: Dict[str, Any]
    sample_count: int
    last_updated: datetime
    user_id: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'character_id': self.character_id,
            'character_name': self.character_name,
            'dialogue_samples': self.dialogue_samples,
            'style_embedding': self.style_embedding,
            'voice_characteristics': self.voice_characteristics,
            'sample_count': self.sample_count,
            'last_updated': self.last_updated.isoformat(),
            'user_id': self.user_id
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
    analysis_method: str  # 'tinystyler_embedding' or 'tinystyler_llm_validated'

class TinyStylerVoiceAnalyzer:
    """
    TinyStyler-based voice analyzer for character consistency detection
    
    This class handles the TinyStyler model loading, style embedding generation,
    and voice consistency analysis specifically for literary dialogue.
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.initialized = False
        
        # TinyStyler configuration
        self.config = {
            'max_length': 128,
            'temperature': 0.8,
            'top_p': 0.9,
            'do_sample': True,
            'seed': 42
        }
        
        logger.info(f"TinyStyler analyzer initialized on device: {self.device}")
    
    def _load_tinystyler_model(self):
        """Load TinyStyler model from Hugging Face Hub"""
        try:
            # Check for required dependencies first
            try:
                import sentencepiece
            except ImportError:
                logger.warning("sentencepiece not available - TinyStyler model loading will use fallback")
                # Don't raise error, just log warning
                return
            
            # Download TinyStyler module
            tinystyler_path = hf_hub_download(
                repo_id="tinystyler/tinystyler", 
                filename="tinystyler.py"
            )
            
            # Import TinyStyler module
            spec = importlib.util.spec_from_file_location("tinystyler", tinystyler_path)
            tinystyler_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tinystyler_module)
            
            # Get model loading functions
            get_tinystyler_model = tinystyler_module.get_tinystyler_model
            self.get_target_style_embeddings = tinystyler_module.get_target_style_embeddings
            
            # Load the model
            self.tokenizer, self.model = get_tinystyler_model(self.device)
            
            # Set seed for reproducibility
            set_seed(self.config['seed'])
            
            self.initialized = True
            logger.info("TinyStyler model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load TinyStyler model: {str(e)}")
            logger.info("TinyStyler will use fallback embeddings - this is expected in local development")
            # Don't raise error, just log it
            self.initialized = False
    
    def ensure_model_loaded(self):
        """Ensure TinyStyler model is loaded"""
        if not self.initialized:
            self._load_tinystyler_model()
            # If still not initialized after loading attempt, that's okay for local development
    
    def get_style_embedding(self, dialogue_samples: List[str]) -> List[float]:
        """
        Generate style embedding for character dialogue samples using TinyStyler
        
        Args:
            dialogue_samples: List of dialogue samples from the character
            
        Returns:
            Style embedding vector as list of floats
        """
        self.ensure_model_loaded()
        
        try:
            # Use TinyStyler to generate style embeddings
            style_embeddings = self.get_target_style_embeddings(
                [dialogue_samples], 
                self.device
            )
            
            # Convert to list for JSON serialization
            embedding_vector = style_embeddings[0].cpu().numpy().tolist()
            
            logger.debug(f"Generated style embedding of dimension {len(embedding_vector)}")
            return embedding_vector
            
        except Exception as e:
            logger.error(f"Failed to generate style embedding: {str(e)}")
            # Fallback to zero vector if embedding generation fails
            return [0.0] * 512  # Default embedding dimension
    
    def calculate_style_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate style similarity between two TinyStyler embeddings
        
        Args:
            embedding1: First style embedding
            embedding2: Second style embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to torch tensors
            tensor1 = torch.tensor(embedding1, device=self.device)
            tensor2 = torch.tensor(embedding2, device=self.device)
            
            # Calculate cosine similarity
            similarity = torch.nn.functional.cosine_similarity(
                tensor1.unsqueeze(0), 
                tensor2.unsqueeze(0)
            ).item()
            
            # Normalize to 0-1 range
            normalized_similarity = (similarity + 1) / 2
            
            return float(normalized_similarity)
            
        except Exception as e:
            logger.error(f"Error calculating style similarity: {str(e)}")
            return 0.0
    
    def analyze_style_transfer(self, source_text: str, target_samples: List[str]) -> Dict[str, Any]:
        """
        Analyze how well source text matches target style using TinyStyler
        
        Args:
            source_text: Text to analyze
            target_samples: Examples of target style
            
        Returns:
            Analysis results including consistency score and suggestions
        """
        self.ensure_model_loaded()
        
        try:
            # Generate style-transferred version
            inputs = self.tokenizer(
                [source_text], 
                padding="longest", 
                truncation=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # Get target style embeddings
            style_embeddings = self.get_target_style_embeddings(
                [target_samples], 
                self.device
            )
            
            # Generate style-transferred text
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    style=style_embeddings.to(self.device),
                    do_sample=self.config['do_sample'],
                    temperature=self.config['temperature'],
                    top_p=self.config['top_p'],
                    max_new_tokens=self.config['max_length']
                )
            
            # Decode generated text
            generated_text = self.tokenizer.batch_decode(output, skip_special_tokens=True)[0]
            
            # Calculate similarity between original and style-transferred text
            # If they're very similar, the original already matches the style
            original_embedding = self.get_style_embedding([source_text])
            target_embedding = self.get_style_embedding(target_samples)
            
            consistency_score = self.calculate_style_similarity(original_embedding, target_embedding)
            
            return {
                'consistency_score': consistency_score,
                'is_consistent': consistency_score > 0.75,
                'style_transferred_text': generated_text,
                'original_text': source_text,
                'analysis_method': 'tinystyler_style_transfer'
            }
            
        except Exception as e:
            logger.error(f"Error in style transfer analysis: {str(e)}")
            return {
                'consistency_score': 0.0,
                'is_consistent': False,
                'style_transferred_text': source_text,
                'original_text': source_text,
                'analysis_method': 'tinystyler_error'
            }

class CharacterVoiceService:
    """
    Character Voice Consistency Detection Service - TinyStyler Edition
    
    This service provides real-time character voice consistency analysis
    for fiction writing using TinyStyler's specialized style analysis.
    """
    
    def __init__(self):
        self.db = PostgreSQLService()
        self.gemini_service = GeminiService()
        self.openai_service = OpenAIService()
        self.validator = SimpleInputValidator()
        self.security_logger = SecurityLogger()
        
        # Initialize TinyStyler analyzer
        self.style_analyzer = TinyStylerVoiceAnalyzer()
        
        # Cache for character profiles
        self.character_cache: Dict[str, CharacterVoiceProfile] = {}
        
        # Enhanced configuration for TinyStyler
        self.config = {
            'similarity_threshold': 0.75,  # Threshold for voice consistency
            'min_samples_for_profile': 3,   # Minimum dialogue samples needed
            'max_profile_samples': 15,      # Reduced for better style focus
            'llm_validation_threshold': 0.65,  # When to use LLM validation
            'dialogue_min_length': 15,      # Increased for better style analysis
            'context_window': 200,          # Context characters before/after dialogue
            'style_learning_rate': 0.1,    # How quickly to adapt to new samples
        }
        
        # Enhanced dialogue patterns for better extraction
        self.dialogue_patterns = [
            # Pattern 1: "Dialogue text," Speaker said/asked/etc.
            r'"([^"]{15,})"\s*[,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)',
            # Pattern 2: Speaker said/asked/etc., "Dialogue text"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)[,:]?\s*"([^"]{15,})"',
            # Pattern 3: "Dialogue text," Speaker said with additional description
            r'"([^"]{15,})"\s*[,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)\s+[a-z]+',
        ]
        
        logger.info("CharacterVoiceService initialized with TinyStyler")
    
    async def analyze_text_for_voice_consistency(
        self, 
        text: str, 
        user_id: int,
        document_id: Optional[str] = None
    ) -> List[VoiceConsistencyResult]:
        """
        Analyze text for character voice consistency issues using TinyStyler
        
        Args:
            text: The text to analyze
            user_id: User ID for personalization
            document_id: Optional document ID for context
            
        Returns:
            List of voice consistency results
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
            
            # Analyze each dialogue segment using TinyStyler
            results = []
            for segment in dialogue_segments:
                if segment.speaker and len(segment.text) >= self.config['dialogue_min_length']:
                    result = await self._analyze_dialogue_consistency_tinystyler(
                        segment, character_profiles, user_id
                    )
                    if result:
                        results.append(result)
            
            # Update character profiles with new dialogue
            await self._update_character_profiles_tinystyler(dialogue_segments, user_id)
            
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
        """Extract dialogue segments from text with enhanced speaker attribution"""
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
                    
                    # Skip if dialogue is too short for style analysis
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
                        confidence=0.9  # Higher confidence for TinyStyler
                    )
                    
                    segments.append(segment)
        
        # Remove duplicates and sort by position
        unique_segments = []
        seen_positions = set()
        
        for segment in sorted(segments, key=lambda x: x.position):
            if segment.position not in seen_positions:
                unique_segments.append(segment)
                seen_positions.add(segment.position)
        
        logger.info(f"Extracted {len(unique_segments)} dialogue segments for TinyStyler analysis")
        return unique_segments
    
    async def _load_character_profiles(self, user_id: int) -> Dict[str, CharacterVoiceProfile]:
        """Load character voice profiles for a user"""
        try:
            # Check cache first
            cache_key = f"user_{user_id}_profiles"
            if cache_key in self.character_cache:
                return self.character_cache[cache_key]
            
            # Load from database
            query = """
            SELECT character_id, character_name, dialogue_samples, voice_embedding, 
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
                        style_embedding=json.loads(row['voice_embedding']),  # Now contains TinyStyler embedding
                        voice_characteristics=json.loads(row['voice_characteristics']),
                        sample_count=row['sample_count'],
                        last_updated=row['last_updated'],
                        user_id=user_id
                    )
                    profiles[row['character_name'].lower()] = profile
            
            # Cache the profiles
            self.character_cache[cache_key] = profiles
            
            logger.info(f"Loaded {len(profiles)} character profiles for TinyStyler analysis")
            return profiles
            
        except Exception as e:
            logger.error(f"Error loading character profiles: {str(e)}")
            return {}
    
    async def _analyze_dialogue_consistency_tinystyler(
        self, 
        segment: DialogueSegment, 
        character_profiles: Dict[str, CharacterVoiceProfile],
        user_id: int
    ) -> Optional[VoiceConsistencyResult]:
        """Analyze dialogue segment using TinyStyler for voice consistency"""
        try:
            speaker_key = segment.speaker.lower()
            
            # Check if we have a profile for this character
            if speaker_key not in character_profiles:
                return None
            
            profile = character_profiles[speaker_key]
            
            # Use TinyStyler for style analysis
            style_analysis = self.style_analyzer.analyze_style_transfer(
                source_text=segment.text,
                target_samples=profile.dialogue_samples
            )
            
            # Extract results
            is_consistent = style_analysis['is_consistent']
            similarity_score = style_analysis['consistency_score']
            
            # Generate explanation based on TinyStyler analysis
            if is_consistent:
                explanation = f"The dialogue matches {profile.character_name}'s established speaking style well."
            else:
                explanation = f"The dialogue shows stylistic deviation from {profile.character_name}'s typical voice patterns."
            
            # Generate suggestions
            suggestions = self._generate_tinystyler_suggestions(
                segment.text, 
                profile.character_name, 
                style_analysis
            )
            
            # Use LLM validation for borderline cases
            analysis_method = 'tinystyler_embedding'
            if (similarity_score < self.config['similarity_threshold'] and 
                similarity_score > self.config['llm_validation_threshold']):
                
                llm_result = await self._get_llm_voice_validation(
                    segment, profile, similarity_score
                )
                
                if llm_result:
                    is_consistent = llm_result.get('is_consistent', False)
                    explanation = llm_result.get('explanation', explanation)
                    suggestions = llm_result.get('suggestions', suggestions)
                    analysis_method = 'tinystyler_llm_validated'
            
            # Create result
            result = VoiceConsistencyResult(
                is_consistent=is_consistent,
                confidence_score=min(similarity_score * 1.1, 1.0),  # Slight boost for TinyStyler
                similarity_score=similarity_score,
                character_name=profile.character_name,
                flagged_text=segment.text,
                explanation=explanation,
                suggestions=suggestions,
                analysis_method=analysis_method
            )
            
            # Log analysis for debugging
            logger.debug(f"TinyStyler analysis - Character: {profile.character_name}, "
                        f"Similarity: {similarity_score:.3f}, "
                        f"Consistent: {is_consistent}, "
                        f"Method: {analysis_method}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in TinyStyler dialogue consistency analysis: {str(e)}")
            return None
    
    def _generate_tinystyler_suggestions(
        self, 
        dialogue_text: str, 
        character_name: str, 
        style_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions based on TinyStyler analysis"""
        suggestions = []
        
        # Add style-specific suggestions
        if style_analysis.get('style_transferred_text'):
            suggestions.append(
                f"Consider this style-adjusted version: '{style_analysis['style_transferred_text']}'"
            )
        
        # Add character-specific suggestions
        suggestions.extend([
            f"Review {character_name}'s previous dialogue for consistent vocabulary and tone",
            f"Consider {character_name}'s personality traits and how they influence speech patterns",
            f"Check if the sentence structure and rhythm match {character_name}'s established voice"
        ])
        
        return suggestions
    
    async def _update_character_profiles_tinystyler(self, segments: List[DialogueSegment], user_id: int):
        """Update character profiles with new dialogue samples using TinyStyler"""
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
                await self._update_single_character_profile_tinystyler(
                    speaker_key, speaker_segments, user_id
                )
            
        except Exception as e:
            logger.error(f"Error updating character profiles with TinyStyler: {str(e)}")
    
    async def _update_single_character_profile_tinystyler(
        self, 
        speaker_key: str, 
        segments: List[DialogueSegment], 
        user_id: int
    ):
        """Update a single character's voice profile using TinyStyler"""
        try:
            character_name = segments[0].speaker
            character_id = hashlib.md5(f"{user_id}_{character_name}".encode()).hexdigest()
            
            # Get existing profile
            query = """
            SELECT dialogue_samples, voice_embedding, voice_characteristics, sample_count
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
                
                # Keep only the most recent samples (reduced for better style focus)
                if len(all_samples) > self.config['max_profile_samples']:
                    all_samples = all_samples[-self.config['max_profile_samples']:]
                
                # Generate new TinyStyler embedding
                new_embedding = self.style_analyzer.get_style_embedding(all_samples)
                
                # Update database
                update_query = """
                UPDATE character_voice_profiles 
                SET dialogue_samples = %s, voice_embedding = %s, sample_count = %s, 
                    last_updated = CURRENT_TIMESTAMP
                WHERE character_id = %s AND user_id = %s
                """
                
                self.db.execute_query(
                    update_query, 
                    (json.dumps(all_samples), json.dumps(new_embedding), 
                     len(all_samples), character_id, user_id)
                )
                
            else:
                # Create new profile
                if len(new_samples) >= self.config['min_samples_for_profile']:
                    embedding = self.style_analyzer.get_style_embedding(new_samples)
                    
                    insert_query = """
                    INSERT INTO character_voice_profiles 
                    (character_id, character_name, user_id, dialogue_samples, 
                     voice_embedding, voice_characteristics, sample_count, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """
                    
                    self.db.execute_query(
                        insert_query,
                        (character_id, character_name, user_id, json.dumps(new_samples),
                         json.dumps(embedding), json.dumps({}), len(new_samples))
                    )
            
            # Clear cache to force reload
            cache_key = f"user_{user_id}_profiles"
            if cache_key in self.character_cache:
                del self.character_cache[cache_key]
            
        except Exception as e:
            logger.error(f"Error updating TinyStyler character profile for {speaker_key}: {str(e)}")
    
    async def _get_llm_voice_validation(
        self, 
        segment: DialogueSegment, 
        profile: CharacterVoiceProfile, 
        similarity_score: float
    ) -> Optional[Dict[str, Any]]:
        """Get LLM validation for borderline voice consistency cases"""
        try:
            # Prepare context for LLM
            sample_dialogue = "\n".join(profile.dialogue_samples[-5:])  # Last 5 samples
            
            prompt = f"""
            Analyze if the following dialogue is consistent with the character's established voice using advanced style analysis.
            
            Character: {profile.character_name}
            
            Previous dialogue examples from this character:
            {sample_dialogue}
            
            New dialogue to analyze:
            "{segment.text}"
            
            Context: {segment.context_before} [...] {segment.context_after}
            
            TinyStyler similarity score: {similarity_score:.3f}
            
            Please analyze:
            1. Is this dialogue consistent with the character's voice? (yes/no)
            2. What specific stylistic aspects make it consistent or inconsistent?
            3. If inconsistent, provide 2-3 specific suggestions to improve voice consistency.
            
            Focus on: vocabulary choice, sentence structure, rhythm, tone, and character-specific speech patterns.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "explanation": "detailed explanation",
                "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
            }}
            """
            
            # Use Gemini for analysis (faster and cheaper than OpenAI for this task)
            response = await self.gemini_service.generate_json_response(
                prompt, max_tokens=500, temperature=0.3
            )
            
            if response and isinstance(response, dict):
                return response
            
        except Exception as e:
            logger.error(f"Error getting LLM voice validation: {str(e)}")
        
        return None
    
    async def get_character_profiles(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all character profiles for a user"""
        try:
            profiles = await self._load_character_profiles(user_id)
            return [profile.to_dict() for profile in profiles.values()]
        except Exception as e:
            logger.error(f"Error getting character profiles: {str(e)}")
            return []
    
    async def delete_character_profile(self, user_id: int, character_name: str) -> bool:
        """Delete a character profile"""
        try:
            character_id = hashlib.sha256(f"{user_id}_{character_name}".encode()).hexdigest()
            
            query = "DELETE FROM character_voice_profiles WHERE character_id = %s AND user_id = %s"
            self.db.execute_query(query, (character_id, user_id))
            
            # Clear cache
            cache_key = f"user_{user_id}_profiles"
            if cache_key in self.character_cache:
                del self.character_cache[cache_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting character profile: {str(e)}")
            return False
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Test database connection
            db_healthy = self.db.health_check()['status'] == 'healthy'
            
            # Test TinyStyler model
            tinystyler_healthy = True
            try:
                self.style_analyzer.ensure_model_loaded()
                tinystyler_healthy = self.style_analyzer.initialized
            except:
                tinystyler_healthy = False
            
            # Test LLM services
            gemini_healthy = self.gemini_service.is_available()
            
            return {
                'status': 'healthy' if all([db_healthy, tinystyler_healthy, gemini_healthy]) else 'unhealthy',
                'database': db_healthy,
                'tinystyler_model': tinystyler_healthy,
                'gemini_service': gemini_healthy,
                'cache_size': len(self.character_cache),
                'config': self.config,
                'device': self.style_analyzer.device
            }
            
        except Exception as e:
            logger.error(f"Error checking service health: {str(e)}")
            return {'status': 'error', 'error': str(e)} 