"""
Ollama Local LLM Service

Handles local OpenAI gpt-oss model interactions through Ollama.
Provides cost-free, privacy-focused AI inference with fallback capabilities.
"""

import json
import asyncio
import logging
import aiohttp
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for different gpt-oss model variants"""
    name: str
    size_gb: int
    context_length: int
    recommended_use: str
    memory_requirement: str

class OllamaService(BaseLLMService):
    """
    Local OpenAI gpt-oss model service via Ollama
    Supports both 20B (fast) and 120B (powerful) variants
    """
    
    # Model configurations
    MODELS = {
        "20b": ModelConfig(
            name="gpt-oss:20b",
            size_gb=14,
            context_length=128000,
            recommended_use="Fast dialogue analysis, real-time feedback",
            memory_requirement="16GB+ RAM"
        ),
        "120b": ModelConfig(
            name="gpt-oss:120b", 
            size_gb=65,
            context_length=128000,
            recommended_use="Deep reasoning, complex analysis",
            memory_requirement="64GB+ RAM"
        )
    }
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 default_model: str = "20b",
                 timeout_seconds: int = 60):
        # Ollama doesn't need API key, so we pass a dummy env var
        super().__init__("OLLAMA_DUMMY_KEY")
        
        self.base_url = base_url
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.available_models = []
        
        # Override availability check - Ollama doesn't need API key
        self.available = True
        
        logger.info(f"🏠 Ollama service initialized with base URL: {base_url}")
        logger.info(f"🎯 Default model: gpt-oss:{default_model}")
    
    async def check_ollama_status(self) -> Dict[str, Any]:
        """Check if Ollama is running and what models are available"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Check if Ollama is running
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        # Check for gpt-oss models
                        gpt_oss_models = [
                            model for model in models 
                            if "gpt-oss" in model.get("name", "")
                        ]
                        
                        self.available_models = [model["name"] for model in gpt_oss_models]
                        
                        return {
                            "status": "healthy",
                            "ollama_running": True,
                            "total_models": len(models),
                            "gpt_oss_models": self.available_models,
                            "recommended_setup": self._get_setup_recommendations()
                        }
                    else:
                        return {
                            "status": "error",
                            "ollama_running": False,
                            "message": f"Ollama responded with status {response.status}"
                        }
                        
        except aiohttp.ClientConnectorError:
            return {
                "status": "error",
                "ollama_running": False,
                "message": "Ollama is not running. Please start Ollama first.",
                "setup_instructions": [
                    "1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh",
                    "2. Start Ollama: ollama serve",
                    "3. Download gpt-oss model: ollama pull gpt-oss:20b"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "ollama_running": False,
                "message": f"Error checking Ollama status: {str(e)}"
            }
    
    def _get_setup_recommendations(self) -> List[str]:
        """Get setup recommendations based on available models"""
        recommendations = []
        
        if not self.available_models:
            recommendations.extend([
                "🚀 Quick Start: ollama pull gpt-oss:20b (14GB download)",
                "💪 For better quality: ollama pull gpt-oss:120b (65GB download)",
                "⚡ Test installation: ollama run gpt-oss:20b"
            ])
        elif len(self.available_models) == 1:
            if "20b" in self.available_models[0]:
                recommendations.append("💡 Consider adding gpt-oss:120b for complex reasoning tasks")
            else:
                recommendations.append("⚡ Consider adding gpt-oss:20b for faster responses")
        else:
            recommendations.append("✅ Optimal setup detected - both models available!")
            
        return recommendations
    
    def is_available(self) -> bool:
        """Check if Ollama service is available (sync version for compatibility)"""
        # For sync compatibility, we return True if Ollama base_url is set
        # Actual model checking happens in async check_ollama_status()
        return self.available and self.base_url is not None
    
    async def generate_text(self, 
                          prompt: str,
                          model_variant: Optional[str] = None,
                          reasoning_effort: str = "medium",
                          max_tokens: int = 2000,
                          temperature: float = 0.7,
                          stream: bool = False,
                          **kwargs) -> str:
        """
        Generate text using local gpt-oss model
        
        Args:
            prompt: Input text prompt
            model_variant: "20b" or "120b", defaults to configured default
            reasoning_effort: "low", "medium", or "high" for different complexity
            max_tokens: Maximum response length
            temperature: Creativity control (0.0-1.0)
            stream: Enable streaming response (not implemented yet)
        """
        model_variant = model_variant or self.default_model
        model_name = self.MODELS[model_variant].name
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "reasoning_effort": reasoning_effort
            },
            "stream": False  # Start with non-streaming
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
            ) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMError(f"Ollama API error {response.status}: {error_text}")
                    
                    result = await response.json()
                    processing_time = time.time() - start_time
                    
                    logger.info(f"🏠 Local inference completed in {processing_time:.2f}s using {model_name}")
                    
                    return result.get("response", "")
                    
        except asyncio.TimeoutError:
            raise LLMError(f"Ollama request timed out after {self.timeout_seconds}s")
        except Exception as e:
            log_api_error("Ollama", e, f"model={model_name}")
            raise LLMError(f"Local model inference failed: {str(e)}")
    
    async def generate_structured(self, 
                                prompt: str, 
                                schema: Dict[str, Any],
                                model_variant: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """Generate structured JSON response using local model"""
        
        # Enhance prompt for JSON output
        json_prompt = f"""{prompt}

CRITICAL: You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Response format: Provide ONLY valid JSON, no additional text before or after.
"""
        
        response_text = await self.generate_text(
            json_prompt,
            model_variant=model_variant,
            temperature=0.3,  # Lower temperature for structured output
            **kwargs
        )
        
        try:
            # Clean and parse JSON response
            cleaned_response = clean_json_response(response_text)
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama: {e}")
            logger.error(f"Raw response: {response_text[:500]}...")
            raise LLMError(f"Invalid JSON response from local model: {str(e)}")
    
    async def analyze_dialogue_consistency(self, 
                                         character_profile: Dict,
                                         dialogue_segments: List[str],
                                         use_powerful_model: bool = False) -> Dict[str, Any]:
        """
        Optimized dialogue consistency analysis using local models
        """
        model_variant = "120b" if use_powerful_model else "20b"
        reasoning_effort = "high" if use_powerful_model else "medium"
        
        prompt = f"""DIALOGUE CONSISTENCY ANALYSIS - Chain of Thought Reasoning

Character Profile: {json.dumps(character_profile, indent=2)}

Dialogue Segments to Analyze:
{chr(10).join([f"{i+1}. {seg}" for i, seg in enumerate(dialogue_segments)])}

INSTRUCTIONS:
1. Think step-by-step about each character's voice patterns
2. Identify inconsistencies in tone, vocabulary, speech patterns  
3. Provide specific examples and recommendations
4. Rate consistency on a scale of 1-10

Please show your complete reasoning process, then provide final analysis.
"""
        
        start_time = time.time()
        result_text = await self.generate_text(
            prompt=prompt,
            model_variant=model_variant,
            reasoning_effort=reasoning_effort,
            max_tokens=3000
        )
        
        processing_time = time.time() - start_time
        
        return {
            "analysis": result_text,
            "model_used": f"gpt-oss:{model_variant}",
            "processing_time": processing_time,
            "cost": 0.0,  # Local inference is free
            "reasoning_effort": reasoning_effort,
            "character_count": len(character_profile.get("name", "")),
            "segments_analyzed": len(dialogue_segments)
        }
    
    async def quick_consistency_check(self, 
                                    new_dialogue: str,
                                    character_context: str) -> Dict[str, Any]:
        """
        Ultra-fast consistency check using 20B model for real-time feedback
        Target: Sub-5 second response time
        """
        prompt = f"""QUICK CONSISTENCY CHECK (30 seconds max)

Character Context: {character_context}
New Dialogue: "{new_dialogue}"

Quick assessment: Is this dialogue consistent with the character? (Yes/No + brief reason)
"""
        
        start_time = time.time()
        result_text = await self.generate_text(
            prompt=prompt,
            model_variant="20b",  # Always use fast model
            reasoning_effort="low",
            max_tokens=500,
            temperature=0.3  # Lower temperature for consistency
        )
        
        processing_time = time.time() - start_time
        
        # Parse simple yes/no response
        is_consistent = "yes" in result_text.lower()
        
        return {
            "is_consistent": is_consistent,
            "explanation": result_text,
            "processing_time": processing_time,
            "model_used": "gpt-oss:20b",
            "cost": 0.0,
            "confidence": 0.8 if processing_time < 10 else 0.6  # Lower confidence if slow
        }
    
    async def generate_with_conversation_history(self, 
                                               conversation: List[Dict[str, str]]) -> str:
        """Generate response considering conversation history"""
        
        # Convert conversation to prompt format
        prompt_parts = []
        for message in conversation[-10:]:  # Last 10 messages for context
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        full_prompt += "\n\nAssistant: "
        
        return await self.generate_text(
            prompt=full_prompt,
            model_variant=self.default_model,
            reasoning_effort="medium"
        )

# Global instance for the service
ollama_service = OllamaService()

async def check_ollama_setup() -> Dict[str, Any]:
    """Convenience function to check Ollama setup"""
    return await ollama_service.check_ollama_status()

async def download_model_recommendations() -> List[str]:
    """Get recommendations for which models to download"""
    status = await ollama_service.check_ollama_status()
    
    if not status.get("ollama_running", False):
        return [
            "⚠️ Ollama is not running. Please start it first:",
            "   ollama serve",
            "",
            "Then download models:",
            "   ollama pull gpt-oss:20b  # Fast model (14GB)",
            "   ollama pull gpt-oss:120b # Powerful model (65GB)"
        ]
    
    available_models = status.get("gpt_oss_models", [])
    
    if not available_models:
        return [
            "🚀 Ollama is running! Now download gpt-oss models:",
            "   ollama pull gpt-oss:20b  # Recommended first download",
            "   ollama pull gpt-oss:120b # Optional for complex tasks"
        ]
    
    return [
        f"✅ Found {len(available_models)} gpt-oss model(s): {', '.join(available_models)}",
        "🎉 Ready for local AI inference!"
    ]
