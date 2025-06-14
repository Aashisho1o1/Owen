"""
Writing Analytics Service for DOG Writer
Advanced NLP-based writing analysis and style detection
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import statistics

# NLP Libraries (2025 Latest - Python 3.13 compatible)
try:
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VaderAnalyzer
    import textstat
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("NLP libraries not available. Install textblob, vaderSentiment, textstat")

logger = logging.getLogger(__name__)

@dataclass
class WritingStyleMetrics:
    """Comprehensive writing style analysis"""
    readability_score: float
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_word_length: float
    vocabulary_diversity: float
    passive_voice_ratio: float
    sentiment_polarity: float
    sentiment_subjectivity: float
    complexity_score: float
    tone_analysis: Dict[str, float]
    writing_voice_indicators: Dict[str, Any]

@dataclass
class WritingSession:
    """Writing session data for analysis"""
    user_id: str
    document_id: str
    session_id: str
    start_time: datetime
    end_time: datetime
    content_before: str
    content_after: str
    words_added: int
    words_deleted: int
    typing_speed_wpm: float
    pause_patterns: List[float]
    revision_count: int

class WritingAnalyticsService:
    """
    Advanced writing analytics service using modern NLP
    
    Features:
    - Sentiment analysis using multiple models (VADER, TextBlob)
    - Writing style analysis (readability, complexity, voice)
    - Productivity pattern detection
    - Writing habit analysis
    - Personalized feedback generation
    """
    
    def __init__(self):
        self.initialized = False
        self.user_writing_profiles: Dict[str, Dict[str, Any]] = {}
        self.session_cache: Dict[str, WritingSession] = {}
        
        if NLP_AVAILABLE:
            self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """Initialize NLP models and download required data"""
        try:
            # Initialize sentiment analyzers
            self.vader_analyzer = VaderAnalyzer()
            
            self.initialized = True
            logger.info("Writing analytics NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            self.initialized = False
    
    def analyze_writing_style(self, text: str) -> WritingStyleMetrics:
        """
        Comprehensive writing style analysis
        
        Args:
            text: Text content to analyze
            
        Returns:
            WritingStyleMetrics with detailed analysis
        """
        if not self.initialized or not text.strip():
            return self._empty_metrics()
        
        try:
            # Basic readability metrics
            readability_score = textstat.flesch_reading_ease(text)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
            
            # Sentence and word analysis using simple string processing
            sentences = self._simple_sentence_tokenize(text)
            words = self._simple_word_tokenize(text)
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = statistics.mean([len(word) for word in words if word.isalpha()]) if words else 0
            
            # Vocabulary diversity (Type-Token Ratio)
            unique_words = set(word.lower() for word in words if word.isalpha())
            vocabulary_diversity = len(unique_words) / len(words) if words else 0
            
            # Sentiment analysis
            sentiment_scores = self._analyze_sentiment(text)
            
            # Passive voice detection
            passive_voice_ratio = self._detect_passive_voice(text)
            
            # Complexity analysis
            complexity_score = self._calculate_complexity(text)
            
            # Tone analysis
            tone_analysis = self._analyze_tone(text)
            
            # Writing voice indicators
            voice_indicators = self._analyze_writing_voice(text)
            
            return WritingStyleMetrics(
                readability_score=readability_score,
                flesch_kincaid_grade=flesch_kincaid_grade,
                avg_sentence_length=avg_sentence_length,
                avg_word_length=avg_word_length,
                vocabulary_diversity=vocabulary_diversity,
                passive_voice_ratio=passive_voice_ratio,
                sentiment_polarity=sentiment_scores['polarity'],
                sentiment_subjectivity=sentiment_scores['subjectivity'],
                complexity_score=complexity_score,
                tone_analysis=tone_analysis,
                writing_voice_indicators=voice_indicators
            )
            
        except Exception as e:
            logger.error(f"Error analyzing writing style: {e}")
            return self._empty_metrics()
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using multiple models"""
        try:
            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Combine scores for more robust analysis
            combined_polarity = (vader_scores['compound'] + textblob_polarity) / 2
            
            return {
                'polarity': combined_polarity,
                'subjectivity': textblob_subjectivity,
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu'],
                'vader_compound': vader_scores['compound']
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    def _detect_passive_voice(self, text: str) -> float:
        """Detect passive voice usage ratio"""
        try:
            sentences = self._simple_sentence_tokenize(text)
            passive_count = 0
            
            for sentence in sentences:
                # Simple passive voice detection using patterns
                if re.search(r'\b(was|were|been|being)\s+\w+ed\b', sentence.lower()):
                    passive_count += 1
                elif re.search(r'\b(is|are|am)\s+\w+ed\b', sentence.lower()):
                    passive_count += 1
            
            return passive_count / len(sentences) if sentences else 0.0
            
        except Exception as e:
            logger.error(f"Error detecting passive voice: {e}")
            return 0.0
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate writing complexity score"""
        try:
            # Combine multiple complexity indicators
            automated_readability = textstat.automated_readability_index(text)
            coleman_liau = textstat.coleman_liau_index(text)
            gunning_fog = textstat.gunning_fog(text)
            
            # Average complexity score
            complexity = (automated_readability + coleman_liau + gunning_fog) / 3
            return max(0.0, min(20.0, complexity))  # Normalize to 0-20 scale
            
        except Exception as e:
            logger.error(f"Error calculating complexity: {e}")
            return 0.0
    
    def _analyze_tone(self, text: str) -> Dict[str, float]:
        """Analyze writing tone using keyword patterns"""
        try:
            text_lower = text.lower()
            
            # Define tone indicators
            tone_patterns = {
                'formal': [r'\b(therefore|furthermore|consequently|moreover)\b', 
                          r'\b(shall|ought|must)\b'],
                'informal': [r'\b(gonna|wanna|kinda|sorta)\b', 
                            r'\b(yeah|yep|nope)\b'],
                'confident': [r'\b(certainly|definitely|absolutely|clearly)\b',
                             r'\b(will|shall|must)\b'],
                'uncertain': [r'\b(maybe|perhaps|possibly|might)\b',
                             r'\b(seems|appears|could be)\b'],
                'emotional': [r'\b(amazing|terrible|wonderful|awful)\b',
                             r'\b(love|hate|excited|devastated)\b'],
                'analytical': [r'\b(analyze|examine|consider|evaluate)\b',
                              r'\b(data|evidence|research|study)\b']
            }
            
            tone_scores = {}
            word_count = len(text.split())
            
            for tone, patterns in tone_patterns.items():
                matches = 0
                for pattern in patterns:
                    matches += len(re.findall(pattern, text_lower))
                
                # Normalize by word count
                tone_scores[tone] = matches / word_count if word_count > 0 else 0.0
            
            return tone_scores
            
        except Exception as e:
            logger.error(f"Error analyzing tone: {e}")
            return {}
    
    def _analyze_writing_voice(self, text: str) -> Dict[str, Any]:
        """Analyze writing voice characteristics"""
        try:
            sentences = self._simple_sentence_tokenize(text)
            words = self._simple_word_tokenize(text)
            
            # Voice indicators
            voice_indicators = {
                'sentence_variety': self._calculate_sentence_variety(sentences),
                'first_person_usage': self._count_first_person(text),
                'question_usage': len([s for s in sentences if s.strip().endswith('?')]) / len(sentences) if sentences else 0,
                'exclamation_usage': len([s for s in sentences if s.strip().endswith('!')]) / len(sentences) if sentences else 0,
                'average_paragraph_length': self._calculate_avg_paragraph_length(text),
                'dialogue_presence': self._detect_dialogue(text),
                'descriptive_language': self._analyze_descriptive_language(text)
            }
            
            return voice_indicators
            
        except Exception as e:
            logger.error(f"Error analyzing writing voice: {e}")
            return {}
    
    def _calculate_sentence_variety(self, sentences: List[str]) -> float:
        """Calculate sentence length variety"""
        if not sentences:
            return 0.0
        
        lengths = [len(sentence.split()) for sentence in sentences]
        if len(lengths) < 2:
            return 0.0
        
        # Calculate coefficient of variation
        mean_length = statistics.mean(lengths)
        std_dev = statistics.stdev(lengths)
        
        return std_dev / mean_length if mean_length > 0 else 0.0
    
    def _count_first_person(self, text: str) -> float:
        """Count first-person pronoun usage"""
        first_person_pronouns = ['i', 'me', 'my', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves']
        words = text.lower().split()
        
        first_person_count = sum(1 for word in words if word in first_person_pronouns)
        return first_person_count / len(words) if words else 0.0
    
    def _calculate_avg_paragraph_length(self, text: str) -> float:
        """Calculate average paragraph length"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            return 0.0
        
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        return statistics.mean(paragraph_lengths)
    
    def _detect_dialogue(self, text: str) -> float:
        """Detect presence of dialogue"""
        # Simple dialogue detection using quotation marks
        dialogue_patterns = [r'"[^"]*"', r"'[^']*'"]
        dialogue_count = 0
        
        for pattern in dialogue_patterns:
            dialogue_count += len(re.findall(pattern, text))
        
        return dialogue_count / len(text.split()) if text.split() else 0.0
    
    def _analyze_descriptive_language(self, text: str) -> float:
        """Analyze use of descriptive language (adjectives, adverbs)"""
        try:
            words = self._simple_word_tokenize(text)
            pos_tags = self._simple_pos_tag(words)
            
            descriptive_tags = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']  # Adjectives and adverbs
            descriptive_count = sum(1 for word, pos in pos_tags if pos in descriptive_tags)
            
            return descriptive_count / len(words) if words else 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing descriptive language: {e}")
            return 0.0
    
    def _empty_metrics(self) -> WritingStyleMetrics:
        """Return empty metrics when analysis fails"""
        return WritingStyleMetrics(
            readability_score=0.0,
            flesch_kincaid_grade=0.0,
            avg_sentence_length=0.0,
            avg_word_length=0.0,
            vocabulary_diversity=0.0,
            passive_voice_ratio=0.0,
            sentiment_polarity=0.0,
            sentiment_subjectivity=0.0,
            complexity_score=0.0,
            tone_analysis={},
            writing_voice_indicators={}
        )
    
    def track_writing_session(
        self,
        user_id: str,
        document_id: str,
        session_id: str,
        content_before: str,
        content_after: str,
        session_duration_minutes: float
    ) -> Dict[str, Any]:
        """
        Track and analyze a writing session
        
        Args:
            user_id: User identifier
            document_id: Document being edited
            session_id: Session identifier
            content_before: Content before the session
            content_after: Content after the session
            session_duration_minutes: Duration of the session
            
        Returns:
            Dictionary with session analysis results
        """
        try:
            # Calculate writing metrics
            words_before = len(content_before.split()) if content_before else 0
            words_after = len(content_after.split()) if content_after else 0
            words_added = max(0, words_after - words_before)
            
            # Calculate typing speed
            typing_speed_wpm = words_added / session_duration_minutes if session_duration_minutes > 0 else 0
            
            # Analyze the new content
            new_content = content_after[len(content_before):] if len(content_after) > len(content_before) else ""
            style_metrics = self.analyze_writing_style(new_content) if new_content else self._empty_metrics()
            
            # Update user writing profile
            self._update_user_profile(user_id, style_metrics, typing_speed_wpm)
            
            session_analysis = {
                'session_id': session_id,
                'user_id': user_id,
                'document_id': document_id,
                'words_added': words_added,
                'typing_speed_wpm': typing_speed_wpm,
                'session_duration_minutes': session_duration_minutes,
                'style_metrics': style_metrics,
                'productivity_score': self._calculate_productivity_score(words_added, session_duration_minutes),
                'writing_quality_score': self._calculate_quality_score(style_metrics),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return session_analysis
            
        except Exception as e:
            logger.error(f"Error tracking writing session: {e}")
            return {}
    
    def _update_user_profile(self, user_id: str, style_metrics: WritingStyleMetrics, typing_speed: float):
        """Update user's writing profile with new data"""
        if user_id not in self.user_writing_profiles:
            self.user_writing_profiles[user_id] = {
                'sessions_count': 0,
                'avg_typing_speed': 0.0,
                'avg_readability': 0.0,
                'avg_complexity': 0.0,
                'dominant_tone': {},
                'writing_patterns': {},
                'improvement_areas': [],
                'last_updated': datetime.utcnow().isoformat()
            }
        
        profile = self.user_writing_profiles[user_id]
        sessions_count = profile['sessions_count']
        
        # Update averages using incremental calculation
        profile['avg_typing_speed'] = (profile['avg_typing_speed'] * sessions_count + typing_speed) / (sessions_count + 1)
        profile['avg_readability'] = (profile['avg_readability'] * sessions_count + style_metrics.readability_score) / (sessions_count + 1)
        profile['avg_complexity'] = (profile['avg_complexity'] * sessions_count + style_metrics.complexity_score) / (sessions_count + 1)
        
        profile['sessions_count'] += 1
        profile['last_updated'] = datetime.utcnow().isoformat()
    
    def _calculate_productivity_score(self, words_added: int, duration_minutes: float) -> float:
        """Calculate productivity score based on words per minute and consistency"""
        if duration_minutes <= 0:
            return 0.0
        
        wpm = words_added / duration_minutes
        
        # Normalize WPM to 0-100 scale (assuming 50 WPM is excellent)
        productivity_score = min(100.0, (wpm / 50.0) * 100)
        return max(0.0, productivity_score)
    
    def _calculate_quality_score(self, style_metrics: WritingStyleMetrics) -> float:
        """Calculate writing quality score based on style metrics"""
        try:
            # Combine multiple quality indicators
            readability_score = max(0, min(100, style_metrics.readability_score))
            complexity_bonus = min(20, style_metrics.complexity_score * 2)  # Bonus for appropriate complexity
            vocabulary_bonus = min(20, style_metrics.vocabulary_diversity * 100)  # Bonus for vocabulary diversity
            
            # Penalty for excessive passive voice
            passive_penalty = style_metrics.passive_voice_ratio * 10
            
            quality_score = readability_score + complexity_bonus + vocabulary_bonus - passive_penalty
            return max(0.0, min(100.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def get_user_writing_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive writing insights for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with writing insights and recommendations
        """
        profile = self.user_writing_profiles.get(user_id, {})
        
        if not profile:
            return {
                'user_id': user_id,
                'insights': 'No writing data available yet. Start writing to see insights!',
                'recommendations': []
            }
        
        insights = {
            'user_id': user_id,
            'writing_summary': {
                'total_sessions': profile.get('sessions_count', 0),
                'average_typing_speed': round(profile.get('avg_typing_speed', 0), 1),
                'average_readability': round(profile.get('avg_readability', 0), 1),
                'average_complexity': round(profile.get('avg_complexity', 0), 1)
            },
            'strengths': self._identify_strengths(profile),
            'improvement_areas': self._identify_improvement_areas(profile),
            'recommendations': self._generate_recommendations(profile),
            'writing_style_summary': self._generate_style_summary(profile)
        }
        
        return insights
    
    def _identify_strengths(self, profile: Dict[str, Any]) -> List[str]:
        """Identify user's writing strengths"""
        strengths = []
        
        if profile.get('avg_typing_speed', 0) > 30:
            strengths.append("Fast typing speed - you're productive!")
        
        if profile.get('avg_readability', 0) > 60:
            strengths.append("Clear and readable writing style")
        
        if profile.get('avg_complexity', 0) > 8:
            strengths.append("Sophisticated writing complexity")
        
        return strengths or ["Keep writing to discover your strengths!"]
    
    def _identify_improvement_areas(self, profile: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        if profile.get('avg_readability', 0) < 40:
            improvements.append("Consider simplifying sentence structure for better readability")
        
        if profile.get('avg_complexity', 0) < 5:
            improvements.append("Try varying sentence length and structure")
        
        if profile.get('avg_typing_speed', 0) < 20:
            improvements.append("Practice typing to improve writing flow")
        
        return improvements
    
    def _generate_recommendations(self, profile: Dict[str, Any]) -> List[str]:
        """Generate personalized writing recommendations"""
        recommendations = []
        
        avg_readability = profile.get('avg_readability', 0)
        avg_complexity = profile.get('avg_complexity', 0)
        
        if avg_readability < 50:
            recommendations.append("Try shorter sentences and simpler words to improve readability")
        
        if avg_complexity < 6:
            recommendations.append("Experiment with varied sentence structures and advanced vocabulary")
        
        if profile.get('sessions_count', 0) < 5:
            recommendations.append("Keep writing regularly to develop your unique voice")
        
        return recommendations or ["Keep up the great writing!"]
    
    def _generate_style_summary(self, profile: Dict[str, Any]) -> str:
        """Generate a summary of the user's writing style"""
        sessions = profile.get('sessions_count', 0)
        readability = profile.get('avg_readability', 0)
        complexity = profile.get('avg_complexity', 0)
        
        if sessions < 3:
            return "Still learning your writing style. Keep writing!"
        
        style_descriptors = []
        
        if readability > 70:
            style_descriptors.append("clear and accessible")
        elif readability > 50:
            style_descriptors.append("moderately complex")
        else:
            style_descriptors.append("sophisticated")
        
        if complexity > 10:
            style_descriptors.append("highly detailed")
        elif complexity > 6:
            style_descriptors.append("well-structured")
        else:
            style_descriptors.append("concise")
        
        return f"Your writing style is {' and '.join(style_descriptors)}."

    def _simple_sentence_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization using punctuation"""
        import re
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty sentences and strip whitespace
        return [s.strip() for s in sentences if s.strip()]
    
    def _simple_word_tokenize(self, text: str) -> List[str]:
        """Simple word tokenization using whitespace and punctuation"""
        import re
        # Split on whitespace and punctuation, keep only alphabetic words
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return words
    
    def _simple_pos_tag(self, words: List[str]) -> List[Tuple[str, str]]:
        """Simple POS tagging using basic heuristics"""
        # This is a very basic implementation - for production, consider using spaCy or similar
        pos_tags = []
        for word in words:
            word_lower = word.lower()
            # Basic heuristics for common patterns
            if word_lower.endswith(('ly')):
                pos_tags.append((word, 'RB'))  # Adverb
            elif word_lower.endswith(('ed', 'ing')):
                pos_tags.append((word, 'VB'))  # Verb
            elif word_lower.endswith(('er', 'est', 'ful', 'ous', 'ive', 'able')):
                pos_tags.append((word, 'JJ'))  # Adjective
            else:
                pos_tags.append((word, 'NN'))  # Default to noun
        return pos_tags

# Global writing analytics service instance
writing_analytics_service = WritingAnalyticsService() 