"""
HuggingFace Inference API Service

Provides access to OpenAI gpt-oss models via HuggingFace Inference API.
Offers cloud-based inference with automatic scaling and cost optimization.
"""

import json
import logging
import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

logger = logging.getLogger(__name__)

@dataclass
class HuggingFaceModelConfig:
    """Configuration for HuggingFace models"""
    name: str
    model_id: str
    context_length: int
    cost_per_1k_tokens: float
    recommended_use: str
    speed_tier: str

class HuggingFaceService(BaseLLMService):
    """
    HuggingFace Inference API service for OpenAI gpt-oss models
    Provides cloud-based inference with automatic scaling
    """
    
    # Available models on HuggingFace
    MODELS = {
        "gpt-oss-20b": HuggingFaceModelConfig(
            name="gpt-oss-20b",
            model_id="openai/gpt-oss-20b",
            context_length=128000,
            cost_per_1k_tokens=0.0002,  # Very competitive pricing
            recommended_use="Fast dialogue analysis, real-time feedback",
            speed_tier="fast"
        ),
        "gpt-oss-120b": HuggingFaceModelConfig(
            name="gpt-oss-120b", 
            model_id="openai/gpt-oss-120b",
            context_length=128000,
            cost_per_1k_tokens=0.0008,  # Higher quality, reasonable cost
            recommended_use="Deep reasoning, complex character analysis",
            speed_tier="powerful"
        )
    }
    
    def __init__(self, 
                 default_model: str = "gpt-oss-20b",
                 timeout_seconds: int = 120,
                 max_retries: int = 3):
        # Initialize with HuggingFace API key
        super().__init__("HUGGINGFACE_API_KEY")
        
        self.base_url = "https://api-inference.huggingface.co/models"
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        
        # Usage tracking for cost optimization
        self.usage_stats = {
            "requests_today": 0,
            "cost_today": 0.0,
            "fast_model_usage": 0,
            "powerful_model_usage": 0
        }
        
        # Circuit breaker for cost control
        self.daily_cost_limit = 10.0  # $10/day default limit
        
        logger.info(f"🤗 HuggingFace service initialized with default model: {default_model}")
    
    def is_available(self) -> bool:
        """Check if HuggingFace service is available"""
        return self.available and self.api_key is not None
    
    async def generate_text(self, 
                          prompt: str,
                          model_name: Optional[str] = None,
                          max_tokens: int = 2000,
                          temperature: float = 0.7,
                          **kwargs) -> str:
        """
        Generate text using HuggingFace Inference API
        
        Args:
            prompt: Input text prompt
            model_name: Model to use ("gpt-oss-20b" or "gpt-oss-120b")
            max_tokens: Maximum response length
            temperature: Creativity control (0.0-1.0)
        """
        # Cost control check
        if self.usage_stats["cost_today"] > self.daily_cost_limit:
            raise LLMError(f"Daily cost limit (${self.daily_cost_limit}) reached")
        
        model_name = model_name or self.default_model
        model_config = self.MODELS.get(model_name)
        
        if not model_config:
            raise LLMError(f"Unknown HuggingFace model: {model_name}")
        
        # Format for chat completion
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "inputs": messages,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": temperature > 0.0
            }
        }
        
        return await self._call_huggingface_api(model_config, payload)
    
    async def generate_structured(self, 
                                prompt: str, 
                                schema: Dict[str, Any],
                                model_name: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """Generate structured JSON response using HuggingFace API"""
        
        # Enhance prompt for JSON output
        json_prompt = f"""{prompt}

CRITICAL: You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Response format: Provide ONLY valid JSON, no additional text before or after.
"""
        
        response_text = await self.generate_text(
            json_prompt,
            model_name=model_name,
            temperature=0.3,  # Lower temperature for structured output
            **kwargs
        )
        
        try:
            # Clean and parse JSON response
            cleaned_response = clean_json_response(response_text)
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from HuggingFace: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise LLMError(f"Invalid JSON response from HuggingFace: {str(e)}")
    
    async def _call_huggingface_api(self, 
                                  model_config: HuggingFaceModelConfig,
                                  payload: Dict[str, Any]) -> str:
        """Core HuggingFace API call with retry logic and cost tracking"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{model_config.model_id}"
        start_time = time.time()
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
                ) as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        processing_time = time.time() - start_time
                        
                        if response.status == 200:
                            result = await response.json()
                            
                            # Extract content
                            if isinstance(result, list) and len(result) > 0:
                                content = result[0].get("generated_text", "")
                            else:
                                content = str(result)
                            
                            # Track usage and costs
                            estimated_tokens = len(payload["inputs"][0]["content"].split()) + len(content.split())
                            estimated_cost = (estimated_tokens / 1000) * model_config.cost_per_1k_tokens
                            
                            self.usage_stats["requests_today"] += 1
                            self.usage_stats["cost_today"] += estimated_cost
                            
                            if model_config.speed_tier == "fast":
                                self.usage_stats["fast_model_usage"] += 1
                            else:
                                self.usage_stats["powerful_model_usage"] += 1
                            
                            logger.info(f"🤗 HF inference completed in {processing_time:.2f}s using {model_config.name} (${estimated_cost:.4f})")
                            
                            return content
                            
                        elif response.status == 503:
                            # Model loading, wait and retry
                            error_data = await response.json()
                            estimated_time = error_data.get("estimated_time", 20)
                            
                            if attempt < self.max_retries - 1:
                                logger.info(f"🤗 Model loading, waiting {estimated_time}s before retry {attempt + 1}")
                                await asyncio.sleep(min(estimated_time, 30))  # Cap wait time
                                continue
                            else:
                                raise LLMError(f"Model {model_config.name} still loading after {self.max_retries} attempts")
                        
                        elif response.status == 429:
                            # Rate limited, exponential backoff
                            wait_time = min(2 ** attempt, 30)
                            if attempt < self.max_retries - 1:
                                logger.warning(f"🤗 Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise LLMError(f"Rate limit exceeded for {model_config.name}")
                        
                        else:
                            error_text = await response.text()
                            last_error = LLMError(f"HuggingFace API error {response.status}: {error_text}")
                            
                            # Don't retry for client errors (4xx)
                            if 400 <= response.status < 500:
                                raise last_error
                            
                            # Retry for server errors (5xx)
                            if attempt < self.max_retries - 1:
                                wait_time = 2 ** attempt
                                logger.warning(f"🤗 Server error, retrying in {wait_time}s (attempt {attempt + 1})")
                                await asyncio.sleep(wait_time)
                                continue
                            
            except asyncio.TimeoutError:
                last_error = LLMError(f"HuggingFace request timed out after {self.timeout_seconds}s")
                if attempt < self.max_retries - 1:
                    logger.warning(f"🤗 Timeout, retrying (attempt {attempt + 1})")
                    continue
            except Exception as e:
                last_error = LLMError(f"HuggingFace API call failed: {str(e)}")
                log_api_error("HuggingFace", e, f"model={model_config.name}")
                if attempt < self.max_retries - 1:
                    logger.warning(f"🤗 Error, retrying (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(2 ** attempt)
                    continue
        
        # All retries exhausted
        raise last_error or LLMError("All retry attempts failed")
    
    async def quick_consistency_check(self, 
                                    dialogue: str,
                                    character_context: str) -> Dict[str, Any]:
        """
        Ultra-fast dialogue consistency check using gpt-oss-20b
        Optimized for speed and cost efficiency
        """
        prompt = f"""Character Context: {character_context}
Dialogue: "{dialogue}"

Task: Quick consistency check - Is this dialogue consistent with the character?

Response format:
- Consistency: YES/NO
- Confidence: 1-10
- Issue (if any): [brief explanation]
- Suggestion (if needed): [quick fix]

Keep response under 100 words."""

        start_time = time.time()
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                model_name="gpt-oss-20b",  # Use fast model
                max_tokens=200,
                temperature=0.3
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            is_consistent = "consistency: yes" in response.lower()
            
            # Extract confidence score
            confidence = 7  # Default
            for line in response.split('\n'):
                if 'confidence:' in line.lower():
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                        break
                    except:
                        pass
            
            return {
                "is_consistent": is_consistent,
                "explanation": response,
                "processing_time": processing_time,
                "confidence": min(10, max(1, confidence)) / 10.0,
                "model_used": "gpt-oss-20b",
                "provider": "huggingface",
                "cost": (len(prompt.split()) + len(response.split())) / 1000 * 0.0002
            }
            
        except Exception as e:
            logger.error(f"HuggingFace quick consistency check failed: {e}")
            raise LLMError(f"Consistency check failed: {str(e)}")
    
    async def analyze_dialogue_comprehensive(self,
                                           character_profile: Dict,
                                           dialogue_segments: List[str],
                                           use_powerful_model: bool = False) -> Dict[str, Any]:
        """
        Comprehensive dialogue analysis using optimal model selection
        """
        model_name = "gpt-oss-120b" if use_powerful_model else "gpt-oss-20b"
        
        character_name = character_profile.get("name", "Unknown")
        personality = character_profile.get("personality", "")
        traits = character_profile.get("traits", [])
        
        dialogue_text = "\n".join([f"{i+1}. {seg}" for i, seg in enumerate(dialogue_segments[:10])])
        
        prompt = f"""COMPREHENSIVE CHARACTER DIALOGUE ANALYSIS

CHARACTER PROFILE:
Name: {character_name}
Personality: {personality}
Key Traits: {', '.join(traits)}

DIALOGUE SEGMENTS TO ANALYZE:
{dialogue_text}

ANALYSIS REQUIRED:
1. Overall consistency score (1-10)
2. Specific inconsistencies found (with examples)
3. Voice pattern analysis
4. Recommendations for improvement
5. Character development insights

Provide detailed analysis with specific examples and actionable feedback."""

        start_time = time.time()
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                model_name=model_name,
                max_tokens=2000,
                temperature=0.4
            )
            
            processing_time = time.time() - start_time
            
            # Estimate cost
            total_tokens = len(prompt.split()) + len(response.split())
            model_config = self.MODELS[model_name]
            cost = (total_tokens / 1000) * model_config.cost_per_1k_tokens
            
            return {
                "analysis": response,
                "character_name": character_name,
                "segments_analyzed": len(dialogue_segments),
                "processing_time": processing_time,
                "model_used": model_name,
                "provider": "huggingface",
                "cost": cost,
                "token_count": total_tokens
            }
            
        except Exception as e:
            logger.error(f"HuggingFace dialogue analysis failed: {e}")
            raise LLMError(f"Analysis failed: {str(e)}")
    
    async def generate_with_conversation_history(self, 
                                               conversation: List[Dict[str, str]]) -> str:
        """Generate response considering conversation history"""
        
        # Use conversation directly as messages
        messages = []
        for message in conversation[-10:]:  # Last 10 messages for context
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Ensure role is valid
            if role not in ["user", "assistant"]:
                role = "user"
            
            messages.append({"role": role, "content": content})
        
        # Create payload for chat completion
        payload = {
            "inputs": messages,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        model_config = self.MODELS[self.default_model]
        return await self._call_huggingface_api(model_config, payload)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics and cost analytics"""
        if self.usage_stats["requests_today"] == 0:
            return {
                "today": self.usage_stats,
                "message": "No requests processed yet"
            }
        
        fast_percentage = (self.usage_stats["fast_model_usage"] / 
                         self.usage_stats["requests_today"]) * 100
        
        avg_cost_per_request = (self.usage_stats["cost_today"] / 
                              self.usage_stats["requests_today"])
        
        return {
            "today": self.usage_stats,
            "efficiency_metrics": {
                "fast_model_percentage": f"{fast_percentage:.1f}%",
                "avg_cost_per_request": f"${avg_cost_per_request:.4f}",
                "projected_monthly_cost": f"${self.usage_stats['cost_today'] * 30:.2f}",
                "daily_limit_usage": f"{(self.usage_stats['cost_today'] / self.daily_cost_limit) * 100:.1f}%"
            },
            "recommendations": self._generate_cost_recommendations()
        }
    
    def _generate_cost_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        if self.usage_stats["requests_today"] == 0:
            return ["No usage data available yet"]
        
        fast_percentage = (self.usage_stats["fast_model_usage"] / 
                         self.usage_stats["requests_today"]) * 100
        
        if fast_percentage < 70:
            recommendations.append("💡 Consider using gpt-oss-20b for simple tasks to reduce costs")
        
        if self.usage_stats["cost_today"] > self.daily_cost_limit * 0.8:
            recommendations.append("⚠️ Approaching daily cost limit - consider local models")
        
        if self.usage_stats["requests_today"] > 100:
            recommendations.append("🔄 High usage detected - consider local Ollama models for zero cost")
        
        return recommendations or ["✅ Cost usage is well optimized!"]

# Global instance
huggingface_service = HuggingFaceService()

# Convenience functions
async def hf_quick_check(dialogue: str, character: str) -> Dict[str, Any]:
    """Quick consistency check via HuggingFace"""
    return await huggingface_service.quick_consistency_check(dialogue, character)

async def hf_deep_analysis(character_profile: Dict, dialogues: List[str]) -> Dict[str, Any]:
    """Deep dialogue analysis via HuggingFace"""
    return await huggingface_service.analyze_dialogue_comprehensive(
        character_profile, dialogues, use_powerful_model=True
    )