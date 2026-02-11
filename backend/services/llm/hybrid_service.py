"""
Hybrid LLM Service - Smart Routing Between Local and Cloud Models

Optimizes cost, speed, and quality by intelligently routing requests between:
- Local OpenAI gpt-oss models (via Ollama) - Free, fast, private
- Cloud Gemini/OpenAI APIs - Fallback for complex tasks

This implements the cost optimization strategy for dialogue consistency detection.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .ollama_service import ollama_service
from .gemini_service import gemini_service
from .base_service import LLMError

logger = logging.getLogger(__name__)

# Try importing HuggingFace service
try:
    from .huggingface_service import huggingface_service
    HUGGINGFACE_AVAILABLE = True
    logger.info("🤗 HuggingFace service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ HuggingFace service not available: {e}")
    huggingface_service = None
    HUGGINGFACE_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Error importing HuggingFace service: {e}")
    huggingface_service = None
    HUGGINGFACE_AVAILABLE = False

class TaskComplexity(Enum):
    """Task complexity levels for routing decisions"""
    SIMPLE = "simple"      # Quick checks, simple analysis
    MEDIUM = "medium"      # Dialogue analysis, moderate reasoning
    COMPLEX = "complex"    # Deep reasoning, creative writing
    CRITICAL = "critical"  # Mission-critical tasks requiring highest quality

class ProviderType(Enum):
    """Available LLM provider types"""
    LOCAL_FAST = "local_20b"     # gpt-oss:20b via Ollama
    LOCAL_POWER = "local_120b"   # gpt-oss:120b via Ollama  
    CLOUD_GEMINI = "cloud_gemini" # Google Gemini API
    CLOUD_OPENAI = "cloud_openai" # OpenAI API (if available)
    HF_FAST = "hf_20b"          # gpt-oss:20b via HuggingFace
    HF_POWER = "hf_120b"        # gpt-oss:120b via HuggingFace

@dataclass
class RoutingRule:
    """Rules for routing tasks to appropriate providers"""
    task_type: str
    complexity: TaskComplexity
    preferred_provider: ProviderType
    fallback_providers: List[ProviderType] = field(default_factory=list)
    max_response_time: float = 30.0  # Maximum acceptable response time
    cost_sensitivity: float = 1.0    # 1.0 = prefer free, 0.0 = prefer quality

@dataclass
class RequestMetrics:
    """Metrics for tracking request performance and costs"""
    provider_used: str
    response_time: float
    cost_estimate: float
    success: bool
    error_message: Optional[str] = None
    model_used: Optional[str] = None

class HybridLLMService:
    """
    Intelligent routing service for optimal LLM usage
    
    Key Features:
    - Cost optimization: Prefer free local models when appropriate
    - Speed optimization: Route simple tasks to fast models
    - Quality assurance: Use cloud models for complex reasoning
    - Automatic fallback: Graceful degradation when local models fail
    """
    
    def __init__(self):
        """Initialize hybrid service with routing rules"""
        self.metrics_history: List[RequestMetrics] = []
        self.routing_rules = self._setup_routing_rules()
        self.local_available = False
        self.cloud_available = False
        self.huggingface_available = False
        
        # Initialize with capability check
        asyncio.create_task(self._check_capabilities())
    
    def _setup_routing_rules(self) -> Dict[str, RoutingRule]:
        """Define routing rules for different task types"""
        return {
            "quick_consistency_check": RoutingRule(
                task_type="quick_consistency_check",
                complexity=TaskComplexity.SIMPLE,
                preferred_provider=ProviderType.LOCAL_FAST,
                fallback_providers=[ProviderType.HF_FAST, ProviderType.CLOUD_GEMINI],
                max_response_time=10.0,
                cost_sensitivity=1.0
            ),
            "dialogue_analysis": RoutingRule(
                task_type="dialogue_analysis", 
                complexity=TaskComplexity.MEDIUM,
                preferred_provider=ProviderType.LOCAL_POWER,
                fallback_providers=[ProviderType.LOCAL_FAST, ProviderType.HF_POWER, ProviderType.HF_FAST, ProviderType.CLOUD_GEMINI],
                max_response_time=30.0,
                cost_sensitivity=0.8
            ),
            "deep_reasoning": RoutingRule(
                task_type="deep_reasoning",
                complexity=TaskComplexity.COMPLEX,
                preferred_provider=ProviderType.LOCAL_POWER,
                fallback_providers=[ProviderType.HF_POWER, ProviderType.CLOUD_GEMINI],
                max_response_time=60.0,
                cost_sensitivity=0.6
            ),
            "creative_writing": RoutingRule(
                task_type="creative_writing",
                complexity=TaskComplexity.COMPLEX,
                preferred_provider=ProviderType.CLOUD_GEMINI,  # Cloud better for creativity
                fallback_providers=[ProviderType.LOCAL_POWER, ProviderType.HF_POWER],
                max_response_time=45.0,
                cost_sensitivity=0.3
            ),
            "structured_output": RoutingRule(
                task_type="structured_output",
                complexity=TaskComplexity.MEDIUM,
                preferred_provider=ProviderType.LOCAL_POWER,
                fallback_providers=[ProviderType.HF_POWER, ProviderType.CLOUD_GEMINI, ProviderType.LOCAL_FAST, ProviderType.HF_FAST],
                max_response_time=25.0,
                cost_sensitivity=0.9
            )
        }
    
    async def _check_capabilities(self):
        """Check what providers are available"""
        try:
            # Check local Ollama availability
            ollama_status = await ollama_service.check_ollama_status()
            self.local_available = (
                ollama_status.get("status") == "healthy" and 
                len(ollama_status.get("gpt_oss_models", [])) > 0
            )
            
            # Check cloud Gemini availability
            self.cloud_available = gemini_service and gemini_service.is_available()
            
            # Check HuggingFace availability
            self.huggingface_available = (
                HUGGINGFACE_AVAILABLE and 
                huggingface_service and 
                huggingface_service.is_available()
            )
            
            logger.info(f"🏠 Local models available: {self.local_available}")
            logger.info(f"☁️ Cloud models available: {self.cloud_available}")
            logger.info(f"🤗 HuggingFace models available: {self.huggingface_available}")
            
            if self.local_available:
                models = ollama_status.get("gpt_oss_models", [])
                logger.info(f"✅ Available local models: {models}")
            
        except Exception as e:
            logger.error(f"Error checking capabilities: {e}")
            self.local_available = False
            self.huggingface_available = False
    
    async def route_request(self, 
                          task_type: str,
                          prompt: Union[str, List[Dict[str, Any]]],
                          **kwargs) -> Dict[str, Any]:
        """
        Smart routing of requests based on task type and available providers
        
        Returns:
            Dict containing response, metrics, and routing info
        """
        start_time = time.time()
        
        # Get routing rule for task type
        rule = self.routing_rules.get(task_type)
        if not rule:
            logger.warning(f"No routing rule for task_type: {task_type}, using default")
            rule = self.routing_rules["dialogue_analysis"]  # Default rule
        
        # Determine best available provider
        provider_chain = [rule.preferred_provider] + rule.fallback_providers
        
        for provider in provider_chain:
            try:
                result = await self._execute_with_provider(
                    provider, prompt, rule, **kwargs
                )
                
                # Track successful metrics
                metrics = RequestMetrics(
                    provider_used=provider.value,
                    response_time=time.time() - start_time,
                    cost_estimate=self._estimate_cost(provider, len(str(prompt))),
                    success=True,
                    model_used=result.get("model_used")
                )
                self.metrics_history.append(metrics)
                
                # Add routing info to result
                result.update({
                    "routing_info": {
                        "task_type": task_type,
                        "provider_used": provider.value,
                        "response_time": metrics.response_time,
                        "cost_estimate": metrics.cost_estimate,
                        "fallback_used": provider != rule.preferred_provider
                    }
                })
                
                return result
                
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {e}")
                
                # Track failed attempt
                metrics = RequestMetrics(
                    provider_used=provider.value,
                    response_time=time.time() - start_time,
                    cost_estimate=0.0,
                    success=False,
                    error_message=str(e)
                )
                self.metrics_history.append(metrics)
                
                # Continue to next provider in chain
                continue
        
        # All providers failed
        raise LLMError(f"All providers failed for task_type: {task_type}")
    
    async def _execute_with_provider(self, 
                                   provider: ProviderType,
                                   prompt: Union[str, List[Dict[str, Any]]],
                                   rule: RoutingRule,
                                   **kwargs) -> Dict[str, Any]:
        """Execute request with specific provider"""
        
        if provider == ProviderType.LOCAL_FAST:
            if not self.local_available:
                raise LLMError("Local models not available")
            
            if isinstance(prompt, str):
                response = await ollama_service.generate_text(
                    prompt, model_variant="20b", **kwargs
                )
            else:
                response = await ollama_service.generate_with_conversation_history(prompt)
            
            return {
                "content": response,
                "provider": "local_ollama",
                "model_used": "gpt-oss:20b",
                "cost": 0.0
            }
            
        elif provider == ProviderType.LOCAL_POWER:
            if not self.local_available:
                raise LLMError("Local models not available")
            
            if isinstance(prompt, str):
                response = await ollama_service.generate_text(
                    prompt, model_variant="120b", **kwargs
                )
            else:
                response = await ollama_service.generate_with_conversation_history(prompt)
            
            return {
                "content": response,
                "provider": "local_ollama",
                "model_used": "gpt-oss:120b", 
                "cost": 0.0
            }
            
        elif provider == ProviderType.CLOUD_GEMINI:
            if not self.cloud_available:
                raise LLMError("Cloud Gemini not available")
            
            if isinstance(prompt, str):
                response = await gemini_service.generate_text(prompt, **kwargs)
            else:
                response = await gemini_service.generate_with_conversation_history(prompt)
            
            return {
                "content": response,
                "provider": "cloud_gemini",
                "model_used": "gemini-2.5-flash",
                "cost": self._estimate_cost(provider, len(str(prompt)))
            }
            
        elif provider == ProviderType.HF_FAST:
            if not self.huggingface_available:
                raise LLMError("HuggingFace not available")
            
            if isinstance(prompt, str):
                response = await huggingface_service.generate_text(
                    prompt, model_name="gpt-oss-20b", **kwargs
                )
            else:
                response = await huggingface_service.generate_with_conversation_history(prompt)
            
            return {
                "content": response,
                "provider": "huggingface",
                "model_used": "gpt-oss-20b",
                "cost": self._estimate_cost(provider, len(str(prompt)))
            }
            
        elif provider == ProviderType.HF_POWER:
            if not self.huggingface_available:
                raise LLMError("HuggingFace not available")
            
            if isinstance(prompt, str):
                response = await huggingface_service.generate_text(
                    prompt, model_name="gpt-oss-120b", **kwargs
                )
            else:
                response = await huggingface_service.generate_with_conversation_history(prompt)
            
            return {
                "content": response,
                "provider": "huggingface",
                "model_used": "gpt-oss-120b", 
                "cost": self._estimate_cost(provider, len(str(prompt)))
            }
            
        else:
            raise LLMError(f"Provider {provider.value} not implemented")
    
    def _estimate_cost(self, provider: ProviderType, prompt_length: int) -> float:
        """Estimate cost based on provider and prompt length"""
        if provider in [ProviderType.LOCAL_FAST, ProviderType.LOCAL_POWER]:
            return 0.0  # Local models are free
        elif provider == ProviderType.CLOUD_GEMINI:
            # Rough estimate: $0.001 per 1000 characters
            return (prompt_length / 1000) * 0.001
        elif provider == ProviderType.HF_FAST:
            # HuggingFace gpt-oss-20b: $0.0002 per 1000 tokens (very competitive)
            estimated_tokens = prompt_length // 4  # Rough character to token conversion
            return (estimated_tokens / 1000) * 0.0002
        elif provider == ProviderType.HF_POWER:
            # HuggingFace gpt-oss-120b: $0.0008 per 1000 tokens
            estimated_tokens = prompt_length // 4
            return (estimated_tokens / 1000) * 0.0008
        else:
            return 0.01  # Default cloud cost estimate
    
    async def analyze_dialogue_consistency_optimized(self,
                                                   character_profile: Dict,
                                                   dialogue_segments: List[str],
                                                   speed_priority: bool = False) -> Dict[str, Any]:
        """
        Optimized dialogue consistency analysis with smart routing
        
        Args:
            character_profile: Character information
            dialogue_segments: List of dialogue strings to analyze
            speed_priority: If True, prefer speed over accuracy
        """
        
        task_type = "quick_consistency_check" if speed_priority else "dialogue_analysis"
        
        prompt = f"""DIALOGUE CONSISTENCY ANALYSIS

Character Profile: {character_profile.get('name', 'Unknown')}
- Traits: {character_profile.get('traits', [])}
- Speech Patterns: {character_profile.get('speech_patterns', [])}

Dialogue Segments ({len(dialogue_segments)} total):
{chr(10).join([f"{i+1}. {seg}" for i, seg in enumerate(dialogue_segments[:10])])}

Task: Analyze consistency and provide specific feedback on voice patterns.
"""
        
        result = await self.route_request(task_type, prompt)
        
        # Enhanced result with dialogue-specific metadata
        result.update({
            "character_analyzed": character_profile.get("name"),
            "segments_count": len(dialogue_segments),
            "analysis_type": "speed_optimized" if speed_priority else "thorough"
        })
        
        return result
    
    async def get_cost_analytics(self) -> Dict[str, Any]:
        """Get cost and performance analytics"""
        if not self.metrics_history:
            return {"message": "No requests processed yet"}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 requests
        
        total_requests = len(recent_metrics)
        successful_requests = len([m for m in recent_metrics if m.success])
        
        local_requests = len([m for m in recent_metrics if "local" in m.provider_used])
        cloud_requests = len([m for m in recent_metrics if "cloud" in m.provider_used])
        hf_requests = len([m for m in recent_metrics if "huggingface" in m.provider_used])
        
        total_cost = sum(m.cost_estimate for m in recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / total_requests
        
        # Calculate potential savings (if all requests were cloud)
        potential_cloud_cost = len(recent_metrics) * 0.005  # Estimate $0.005 per request
        savings = potential_cloud_cost - total_cost
        
        return {
            "summary": {
                "total_requests": total_requests,
                "success_rate": f"{(successful_requests/total_requests*100):.1f}%",
                "avg_response_time": f"{avg_response_time:.2f}s"
            },
            "cost_optimization": {
                "total_cost": f"${total_cost:.4f}",
                "estimated_savings": f"${savings:.4f}",
                "local_requests": local_requests,
                "hf_requests": hf_requests,
                "cloud_requests": cloud_requests,
                "cost_efficiency": f"{((local_requests)/total_requests*100):.1f}% free requests",
                "low_cost_efficiency": f"{((local_requests + hf_requests)/total_requests*100):.1f}% free or low-cost requests"
            },
            "recommendations": self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on usage patterns"""
        if not self.metrics_history:
            return ["Start using the service to get personalized recommendations"]
        
        recommendations = []
        
        if not self.local_available and not self.huggingface_available:
            recommendations.extend([
                "🚀 Setup Options for Cost Savings:",
                "   1. Local: Install Ollama (ollama pull gpt-oss:20b) - 100% free",
                "   2. Cloud: Setup HuggingFace API - 90% cost reduction vs Gemini",
                "   Expected savings: $50-200/month"
            ])
        elif not self.local_available and self.huggingface_available:
            recommendations.extend([
                "🏠 Consider local models for even greater savings:",
                "   Run: ollama pull gpt-oss:20b",
                "   Upgrade from low-cost to zero-cost inference"
            ])
        elif self.local_available and not self.huggingface_available:
            recommendations.extend([
                "🤗 Consider HuggingFace as cloud fallback:",
                "   Setup HUGGINGFACE_API_KEY for better reliability",
                "   Much cheaper than Gemini API for cloud requests"
            ])
        
        recent_failures = [m for m in self.metrics_history[-50:] if not m.success]
        if len(recent_failures) > 5:
            recommendations.append("⚠️ Consider upgrading hardware for local model reliability or enable HuggingFace fallback")
        
        cloud_usage = len([m for m in self.metrics_history[-50:] if "cloud_gemini" in m.provider_used])
        if cloud_usage > 25:
            recommendations.append("💰 High Gemini usage detected - HuggingFace models are 80% cheaper for same quality")
        
        hf_usage = len([m for m in self.metrics_history[-50:] if "huggingface" in m.provider_used])
        local_usage = len([m for m in self.metrics_history[-50:] if "local" in m.provider_used])
        
        if hf_usage > local_usage and self.local_available:
            recommendations.append("🏠 You're using more cloud HF than local - consider routing more tasks locally")
        
        return recommendations or ["✅ Your setup is optimally configured!"]

# Global instance
hybrid_llm_service = HybridLLMService()

# Convenience functions for easy integration
async def quick_consistency_check(dialogue: str, character_context: str) -> Dict[str, Any]:
    """Ultra-fast consistency check using optimal routing"""
    prompt = f"Character: {character_context}\nDialogue: {dialogue}\nConsistent? (Yes/No + reason)"
    return await hybrid_llm_service.route_request("quick_consistency_check", prompt)

async def analyze_dialogue_deep(character_profile: Dict, dialogues: List[str]) -> Dict[str, Any]:
    """Deep dialogue analysis using optimal routing"""
    return await hybrid_llm_service.analyze_dialogue_consistency_optimized(
        character_profile, dialogues, speed_priority=False
    )
