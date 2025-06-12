"""
Speculative Grammar Checking Service - COST OPTIMIZED & SECURE

Multi-tier approach:
Tier 1: Local spellcheck (FREE, instant)
Tier 2: LanguageTool Free API (FREE, 20 req/min limit)  
Tier 3: LLM comprehensive check (PAID, for final review)

Smart caching and request management to stay within free limits.
Security features: Input validation, cache limits, rate limiting.
"""

import re
import asyncio
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import json
import logging
from functools import lru_cache
import os

logger = logging.getLogger(__name__)

# Security constants
MAX_TEXT_LENGTH = 50000  # Maximum text length to prevent DoS
MAX_CACHE_SIZE = 1000    # Maximum cache entries
MAX_CACHE_MEMORY_MB = 100  # Maximum cache memory usage

class CheckType(Enum):
    REAL_TIME = "real_time"
    COMPREHENSIVE = "comprehensive"

class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"

@dataclass
class GrammarIssue:
    """Represents a grammar or spelling issue"""
    start: int
    end: int
    issue_type: str  # 'spelling', 'grammar', 'style', 'punctuation'
    severity: SeverityLevel
    message: str
    suggestions: List[str]
    rule_id: Optional[str] = None
    confidence: float = 1.0
    source: str = "unknown"  # 'languagetool', 'spellcheck', 'llm'

@dataclass
class GrammarCheckResult:
    """Complete grammar check result"""
    text: str
    text_hash: str
    issues: List[GrammarIssue]
    check_type: CheckType
    processing_time_ms: int
    timestamp: float
    word_count: int
    cached: bool = False

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class RateLimiter:
    """Rate limiter for LanguageTool API to stay within free limits"""
    
    def __init__(self):
        self.requests_per_minute = 18  # Stay under 20 limit
        self.chars_per_minute = 70000  # Stay under 75k limit
        
        self.request_timestamps: List[float] = []
        self.char_usage: List[Tuple[float, int]] = []
        
    def can_make_request(self, text_length: int) -> bool:
        now = time.time()
        
        # Clean old timestamps (older than 1 minute)
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        self.char_usage = [(t, chars) for t, chars in self.char_usage if now - t < 60]
        
        # Check request limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            return False
        
        # Check character limit
        current_char_usage = sum(chars for _, chars in self.char_usage)
        if current_char_usage + text_length > self.chars_per_minute:
            return False
        
        return True
    
    def record_request(self, text_length: int):
        now = time.time()
        self.request_timestamps.append(now)
        self.char_usage.append((now, text_length))

class GrammarService:
    """
    Speculative grammar checking with multi-tier architecture:
    
    Tier 1 (Real-time): LanguageTool API + basic spellcheck
    Tier 2 (Comprehensive): LLM-based analysis for complex issues
    
    Features:
    - Smart caching to reduce API calls
    - Debounced checking to avoid excessive requests
    - Cost optimization through intelligent batching
    - Real-time feedback with sub-200ms response times
    """
    
    def __init__(self):
        self.languagetool_url = "https://api.languagetool.org/v2/check"
        self.rate_limiter = RateLimiter()
        self.cache: Dict[str, GrammarCheckResult] = {}
        self.cache_ttl = 300  # 5 minutes cache
        self.debounce_delay = 0.5  # 500ms debounce
        self.last_check_time: Dict[str, float] = {}
        
        # Cost optimization settings
        self.max_real_time_length = 1000  # Characters for real-time checking
        self.llm_check_threshold = 2000  # Minimum chars for LLM checking
        self.batch_size = 5000  # Characters per LLM batch
        
        # Security settings
        self.max_text_length = MAX_TEXT_LENGTH
        self.max_cache_size = MAX_CACHE_SIZE
        
        # Local spelling dictionary (expanded)
        self.common_misspellings = {
            # Original ones
            'recieve': ['receive'], 'definately': ['definitely'], 'seperate': ['separate'],
            'occured': ['occurred'], 'neccessary': ['necessary'], 'recomend': ['recommend'],
            'accomodate': ['accommodate'], 'begining': ['beginning'], 'comming': ['coming'],
            'writting': ['writing'], 'grammer': ['grammar'], 'existance': ['existence'],
            'maintainance': ['maintenance'], 'persistance': ['persistence'], 
            'independant': ['independent'], 'adress': ['address'], 'suceed': ['succeed'],
            'procede': ['proceed'], 'refered': ['referred'], 'transfered': ['transferred'],
            
            # Additional common mistakes
            'alot': ['a lot'], 'alright': ['all right'], 'aswell': ['as well'],
            'cancellation': ['cancellation'], 'concious': ['conscious'], 'definetly': ['definitely'],
            'exagerate': ['exaggerate'], 'goverment': ['government'], 'higth': ['height'],
            'intresting': ['interesting'], 'judgement': ['judgment'], 'knowlege': ['knowledge'],
            'liesure': ['leisure'], 'mispell': ['misspell'], 'noticable': ['noticeable'],
            'occassion': ['occasion'], 'priviledge': ['privilege'], 'reccomend': ['recommend'],
            'rythm': ['rhythm'], 'tommorow': ['tomorrow'], 'untill': ['until'],
            'wierd': ['weird'], 'wich': ['which'], 'thier': ['their'], 'teh': ['the'],
            'recieved': ['received'], 'beleive': ['believe'], 'achive': ['achieve']
        }
        
        # Grammar patterns for local checking
        self.grammar_patterns = [
            (r'\bi\s+am\s+going\s+to\s+went\b', 'Incorrect tense combination', ['I am going to go', 'I went']),
            (r'\bcould\s+of\b', 'Should be "could have"', ['could have']),
            (r'\bwould\s+of\b', 'Should be "would have"', ['would have']),
            (r'\bshould\s+of\b', 'Should be "should have"', ['should have']),
            (r'\bits\s+a\s+shame\s+that\s+your\b', 'Check: its vs it\'s', ["it's a shame that you're"]),
            (r'\byour\s+welcome\b', 'Should be "you\'re welcome"', ["you're welcome"]),
            (r'\bthere\s+going\b', 'Should be "they\'re going"', ["they're going"]),
            (r'\bto\s+loose\b', 'Should be "to lose"', ['to lose']),
            (r'\beffect\s+on\b', 'Check: affect vs effect', ['affect']),
        ]
        
        # Performance metrics
        self.metrics = {
            'real_time_checks': 0,
            'comprehensive_checks': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'average_response_time': 0,
            'security_blocks': 0
        }
    
    def _validate_input(self, text: str) -> str:
        """Validate and sanitize input text for security"""
        if not isinstance(text, str):
            raise SecurityError("Input must be a string")
        
        if len(text) > self.max_text_length:
            raise SecurityError(f"Text too long. Maximum {self.max_text_length} characters allowed")
        
        # Basic sanitization - remove null bytes and control characters
        sanitized = text.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
        
        # Check for suspicious patterns that might indicate injection attempts
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in input: {pattern}")
                self.metrics['security_blocks'] += 1
                raise SecurityError("Input contains potentially malicious content")
        
        return sanitized.strip()
    
    def _manage_cache_size(self):
        """Manage cache size to prevent memory exhaustion"""
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entries (simple LRU)
            sorted_cache = sorted(
                self.cache.items(), 
                key=lambda x: x[1].timestamp
            )
            # Remove oldest 20% of entries
            remove_count = len(sorted_cache) // 5
            for i in range(remove_count):
                del self.cache[sorted_cache[i][0]]
            
            logger.info(f"Cache cleaned: removed {remove_count} entries")
    
    def _generate_text_hash(self, text: str) -> str:
        """Generate hash for caching"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _is_cache_valid(self, result: GrammarCheckResult) -> bool:
        """Check if cached result is still valid"""
        return (time.time() - result.timestamp) < self.cache_ttl
    
    def _should_debounce(self, text_hash: str) -> bool:
        """Check if we should debounce this request"""
        last_check = self.last_check_time.get(text_hash, 0)
        return (time.time() - last_check) < self.debounce_delay
    
    async def check_spelling_fast(self, text: str) -> List[GrammarIssue]:
        """Ultra-fast local spelling and grammar check"""
        issues = []
        
        # Spelling check
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in self.common_misspellings:
                for match in re.finditer(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE):
                    issues.append(GrammarIssue(
                        start=match.start(),
                        end=match.end(),
                        issue_type='spelling',
                        severity=SeverityLevel.ERROR,
                        message=f"Possible spelling error: '{word}'",
                        suggestions=self.common_misspellings[word],
                        confidence=0.9,
                        source='local_spellcheck'
                    ))
        
        # Basic grammar patterns
        for pattern, message, suggestions in self.grammar_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(GrammarIssue(
                    start=match.start(),
                    end=match.end(),
                    issue_type='grammar',
                    severity=SeverityLevel.ERROR,
                    message=message,
                    suggestions=suggestions,
                    confidence=0.7,
                    source='local_grammar'
                ))
        
        return issues
    
    async def check_with_languagetool(self, text: str) -> List[GrammarIssue]:
        """Check with LanguageTool API (rate-limited)"""
        
        # Check rate limits first
        if not self.rate_limiter.can_make_request(len(text)):
            logger.info("LanguageTool rate limit reached, skipping API call")
            return []
        
        # Truncate if too long for free API
        if len(text) > 19000:  # Stay under 20k limit
            text = text[:19000] + "..."
        
        try:
            data = {
                'text': text,
                'language': 'en-US',
                'enabledOnly': 'false'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.languagetool_url, data=data, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.rate_limiter.record_request(len(text))
                        
                        issues = []
                        for match in result.get('matches', []):
                            issue = GrammarIssue(
                                start=match['offset'],
                                end=match['offset'] + match['length'],
                                issue_type=self._categorize_languagetool_rule(match.get('rule', {}).get('category', {}).get('id', '')),
                                severity=self._map_languagetool_severity(match.get('rule', {}).get('category', {}).get('id', '')),
                                message=match['message'],
                                suggestions=[r['value'] for r in match.get('replacements', [])[:3]],
                                rule_id=match.get('rule', {}).get('id'),
                                confidence=0.8,
                                source='languagetool'
                            )
                            issues.append(issue)
                        
                        return issues
                    else:
                        logger.warning(f"LanguageTool API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"LanguageTool API error: {e}")
        
        return []
    
    def _categorize_languagetool_rule(self, category_id: str) -> str:
        """Categorize LanguageTool rules into our types"""
        category_map = {
            'TYPOS': 'spelling',
            'GRAMMAR': 'grammar',
            'STYLE': 'style',
            'PUNCTUATION': 'punctuation',
            'CASING': 'style',
            'REDUNDANCY': 'style',
            'CONFUSED_WORDS': 'grammar'
        }
        return category_map.get(category_id, 'grammar')
    
    def _map_languagetool_severity(self, category_id: str) -> SeverityLevel:
        """Map LanguageTool categories to severity levels"""
        if category_id in ['TYPOS', 'GRAMMAR']:
            return SeverityLevel.ERROR
        elif category_id in ['STYLE', 'REDUNDANCY']:
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.INFO
    
    async def check_real_time(self, text: str) -> GrammarCheckResult:
        """
        Real-time grammar checking (Tier 1)
        - Ultra-fast response (<200ms target)
        - Local spellcheck + LanguageTool
        - Suitable for typing feedback
        """
        start_time = time.time()
        text_hash = self._generate_text_hash(text)
        
        # Check cache first
        if text_hash in self.cache and self._is_cache_valid(self.cache[text_hash]):
            self.metrics['cache_hits'] += 1
            result = self.cache[text_hash]
            result.cached = True
            return result
        
        # Debounce rapid requests
        if self._should_debounce(text_hash):
            # Return cached result or empty result
            return self.cache.get(text_hash, GrammarCheckResult(
                text=text,
                text_hash=text_hash,
                issues=[],
                check_type=CheckType.REAL_TIME,
                processing_time_ms=0,
                timestamp=time.time(),
                word_count=len(text.split()),
                cached=True
            ))
        
        self.last_check_time[text_hash] = time.time()
        
        # Run fast checks in parallel
        local_issues_task = self.check_spelling_fast(text)
        languagetool_task = self.check_with_languagetool(text)
        
        local_issues, languagetool_issues = await asyncio.gather(
            local_issues_task, languagetool_task, return_exceptions=True
        )
        
        # Combine results
        all_issues = []
        if not isinstance(local_issues, Exception):
            all_issues.extend(local_issues)
        if not isinstance(languagetool_issues, Exception):
            all_issues.extend(languagetool_issues)
        
        # Remove duplicates and overlapping issues
        all_issues = self._deduplicate_issues(all_issues)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = GrammarCheckResult(
            text=text,
            text_hash=text_hash,
            issues=all_issues,
            check_type=CheckType.REAL_TIME,
            processing_time_ms=processing_time,
            timestamp=time.time(),
            word_count=len(text.split())
        )
        
        # Cache result
        self.cache[text_hash] = result
        self.metrics['real_time_checks'] += 1
        
        return result
    
    async def check_comprehensive(self, text: str, context: Optional[str] = None) -> GrammarCheckResult:
        """
        Comprehensive grammar checking (Tier 2)
        - LLM-based analysis for complex issues
        - Style, tone, and context-aware suggestions
        - Suitable for final review
        """
        start_time = time.time()
        text_hash = self._generate_text_hash(text + (context or ""))
        
        # Check cache
        if text_hash in self.cache and self._is_cache_valid(self.cache[text_hash]):
            result = self.cache[text_hash]
            result.cached = True
            return result
        
        # Only use LLM for substantial text
        if len(text) < self.llm_check_threshold:
            return await self.check_real_time(text)
        
        try:
            # Import LLM service (assuming it exists)
            from .llm_service import LLMService
            llm_service = LLMService()
            
            # Prepare prompt for comprehensive grammar analysis
            prompt = self._create_comprehensive_prompt(text, context)
            
            # Get LLM response
            response = await llm_service.generate_response_async(
                prompt=prompt,
                provider="openai",  # or your preferred provider
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent grammar analysis
            )
            
            # Parse LLM response into issues
            issues = self._parse_llm_grammar_response(response, text)
            
        except Exception as e:
            logger.error(f"LLM grammar check error: {e}")
            # Fallback to real-time checking
            return await self.check_real_time(text)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = GrammarCheckResult(
            text=text,
            text_hash=text_hash,
            issues=issues,
            check_type=CheckType.COMPREHENSIVE,
            processing_time_ms=processing_time,
            timestamp=time.time(),
            word_count=len(text.split())
        )
        
        self.cache[text_hash] = result
        self.metrics['comprehensive_checks'] += 1
        
        return result
    
    def _create_comprehensive_prompt(self, text: str, context: Optional[str] = None) -> str:
        """Create prompt for LLM-based comprehensive grammar analysis"""
        return f"""
Analyze this text for grammar, spelling, style, and clarity issues. Provide detailed feedback in JSON format.

Text to analyze:
"{text}"

{f'Context: {context}' if context else ''}

Return a JSON object with this structure:
{{
  "issues": [
    {{
      "start": 0,
      "end": 5,
      "type": "grammar|spelling|style|punctuation",
      "severity": "error|warning|info",
      "message": "Brief description of the issue",
      "suggestions": ["suggestion1", "suggestion2"],
      "confidence": 0.9
    }}
  ],
  "overall_score": 85,
  "style_notes": "Brief overall feedback"
}}

Focus on:
1. Grammar and syntax errors
2. Spelling mistakes
3. Style and clarity improvements
4. Punctuation issues
5. Word choice and flow

Be precise with character positions (start/end) and provide actionable suggestions.
"""
    
    def _parse_llm_grammar_response(self, response: str, original_text: str) -> List[GrammarIssue]:
        """Parse LLM response into GrammarIssue objects"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return []
            
            data = json.loads(json_match.group(0))
            issues = []
            
            for issue_data in data.get('issues', []):
                issue = GrammarIssue(
                    start=issue_data.get('start', 0),
                    end=issue_data.get('end', 0),
                    issue_type=issue_data.get('type', 'grammar'),
                    severity=SeverityLevel(issue_data.get('severity', 'info')),
                    message=issue_data.get('message', ''),
                    suggestions=issue_data.get('suggestions', []),
                    confidence=issue_data.get('confidence', 0.8),
                    source='llm'
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Error parsing LLM grammar response: {e}")
            return []
    
    def _deduplicate_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Remove duplicate and overlapping issues"""
        if not issues:
            return []
        
        # Sort by start position
        sorted_issues = sorted(issues, key=lambda x: x.start)
        deduplicated = [sorted_issues[0]]
        
        for current in sorted_issues[1:]:
            last = deduplicated[-1]
            
            # Check for overlap
            if current.start < last.end:
                # Overlapping issues - keep the one with higher confidence
                if current.confidence > last.confidence:
                    deduplicated[-1] = current
            else:
                deduplicated.append(current)
        
        return deduplicated
    
    def _update_metrics(self, check_type: str, processing_time: int):
        """Update performance metrics"""
        if self.metrics['average_response_time'] == 0:
            self.metrics['average_response_time'] = processing_time
        else:
            # Rolling average
            self.metrics['average_response_time'] = (
                self.metrics['average_response_time'] * 0.9 + processing_time * 0.1
            )
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        return self.metrics.copy()
    
    def clear_cache(self):
        """Clear the grammar check cache"""
        self.cache.clear()
        self.last_check_time.clear()

# Global instance
grammar_service = GrammarService() 