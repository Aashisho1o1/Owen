"""
OpenAI Service

Handles OpenAI ChatGPT and DALL-E API interactions.
Now uses the most advanced OpenAI models available including GPT-4.1 and o3.
"""

import json
import asyncio
import logging
import openai
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

logger = logging.getLogger(__name__)

class OpenAIService(BaseLLMService):
    """OpenAI service for ChatGPT and DALL-E - now uses most advanced models"""
    
    def __init__(self):
        super().__init__("OPENAI_API_KEY")
        
        # Model preferences ordered by capability and recency
        # GPT-4.1 series: Most advanced flagship models (April 2025)
        # o-series: Advanced reasoning models
        # GPT-4o: Latest multimodal capabilities
        # GPT-4: Reliable fallback
        self.model_preferences = [
            'gpt-4.1',                    # Most advanced flagship model (1M context)
            'o3',                         # Advanced reasoning model
            'o1',                         # Enhanced reasoning capabilities  
            'gpt-4o-2024-11-20',          # Latest GPT-4o with enhanced creative writing
            'gpt-4o',                     # Latest multimodal model
            'gpt-4-turbo-2024-04-09',     # GPT-4 Turbo with vision
            'gpt-4-turbo',                # GPT-4 Turbo general
            'gpt-4',                      # Reliable fallback
        ]
        
        self.available_models = []
        
        if self.available:
            self.client = openai.OpenAI(api_key=self.api_key)
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and verify available models"""
        try:
            # Get available models from OpenAI
            models_response = self.client.models.list()
            available_model_ids = [model.id for model in models_response.data]
            
            # Filter our preferences by what's actually available
            for preferred_model in self.model_preferences:
                if preferred_model in available_model_ids:
                    self.available_models.append(preferred_model)
                    logger.info(f"✅ OpenAI model available: {preferred_model}")
            
            if not self.available_models:
                # If none of our preferred models are available, add the first available GPT model as fallback
                gpt_models = [model for model in available_model_ids if 'gpt' in model.lower()]
                if gpt_models:
                    self.available_models.append(gpt_models[0])
                    logger.warning(f"⚠️ Using fallback model: {gpt_models[0]}")
                else:
                    logger.error("❌ No GPT models available")
                    self.available = False
                    return
            
            logger.info(f"🎯 OpenAI service initialized with {len(self.available_models)} available models")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI models: {e}")
            self.available = False
    
    def _select_model(self, context: str = "general", max_tokens: int = 2000) -> str:
        """Select the best available model based on context and requirements"""
        if not self.available_models:
            raise LLMError("No OpenAI models available")
        
        # For reasoning tasks, prefer o-series models
        if any(keyword in context.lower() for keyword in ['reasoning', 'complex', 'analysis', 'logic', 'problem']):
            for model in self.available_models:
                if model.startswith(('o1', 'o3')):
                    logger.info(f"🧠 Selected reasoning model: {model} for {context}")
                    return model
        
        # For large context needs, prefer GPT-4.1 
        if max_tokens > 4000 or any(keyword in context.lower() for keyword in ['long', 'document', 'context']):
            for model in self.available_models:
                if model.startswith('gpt-4.1'):
                    logger.info(f"📚 Selected large context model: {model} for {context}")
                    return model
        
        # For creative writing, prefer latest GPT-4o
        if any(keyword in context.lower() for keyword in ['creative', 'writing', 'story', 'narrative']):
            for model in self.available_models:
                if 'gpt-4o' in model and '2024-11-20' in model:
                    logger.info(f"✍️ Selected creative model: {model} for {context}")
                    return model
        
        # Default: use the first (highest priority) available model
        selected = self.available_models[0]
        logger.info(f"🎯 Selected default model: {selected} for {context}")
        return selected

    async def _make_api_call(self, api_call_func: Callable, error_context: str, **kwargs):
        """Generic helper to make OpenAI API calls with enhanced error handling"""
        if not self.available:
            raise LLMError(f"OpenAI service not available - {error_context}")
        
        try:
            result = await asyncio.to_thread(api_call_func)
            return result
        except openai.RateLimitError as e:
            logger.warning(f"⚠️ OpenAI rate limit hit: {e}")
            raise LLMError(f"OpenAI rate limit exceeded. Please try again later.")
        except openai.AuthenticationError as e:
            logger.error(f"❌ OpenAI authentication error: {e}")
            raise LLMError(f"OpenAI authentication failed. Please check your API key.")
        except openai.InvalidRequestError as e:
            logger.error(f"❌ OpenAI invalid request: {e}")
            # Try fallback model if the request failed due to model unavailability
            if "model" in str(e).lower() and len(self.available_models) > 1:
                logger.info("🔄 Attempting with fallback model...")
                raise LLMError(f"Model request failed, try with fallback: {str(e)}")
            raise LLMError(f"OpenAI request invalid: {str(e)}")
        except Exception as e:
            log_api_error("OpenAI", e, error_context)
            raise LLMError(f"OpenAI {error_context} failed: {str(e)}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the most advanced available OpenAI model"""
        model = kwargs.get('model') or self._select_model("text generation", kwargs.get('max_tokens', 2000))
        
        def _generate():
            # Handle o-series models which might have different parameters
            if model.startswith(('o1', 'o3')):
                # o-series models work best with simpler parameters
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=kwargs.get('max_tokens', 2000)
                )
            else:
                # Standard models use regular parameters
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
            
            content = response.choices[0].message.content
            logger.info(f"✅ Generated {len(content) if content else 0} characters using {model}")
            return content
        
        result = await self._make_api_call(_generate, f"text generation with {model}")
        return result or ""
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using the most appropriate OpenAI model"""
        model = kwargs.get('model') or self._select_model("structured generation", kwargs.get('max_tokens', 2000))
        structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        
        def _generate():
            if model.startswith(('o1', 'o3')):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": structured_prompt}],
                    max_completion_tokens=kwargs.get('max_tokens', 2000)
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": structured_prompt}],
                    temperature=kwargs.get('temperature', 0.3),
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
            return response.choices[0].message.content

        result = await self._make_api_call(_generate, f"structured generation with {model}")
        cleaned_result = clean_json_response(result or "")
        
        try:
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from OpenAI: {str(e)}")
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history using advanced models"""
        model = kwargs.get('model') or self._select_model("conversation", kwargs.get('max_tokens', 2000))
        
        def _generate():
            if model.startswith(('o1', 'o3')):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=kwargs.get('max_tokens', 2000)
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
            return response.choices[0].message.content
        
        result = await self._make_api_call(_generate, f"conversation generation with {model}")
        return result or ""
    
    async def generate_image(self, description: str, size: str = "1024x1024", style: str = "natural") -> Optional[str]:
        """Generate image using DALL-E 3 (still the best image model)"""
        def _generate():
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=description,
                size=size,
                quality="standard",
                style=style,
                n=1
            )
            return response.data[0].url if response.data else None
            
        try:
            return await self._make_api_call(_generate, "image generation")
        except LLMError:
            # Don't raise exception for image generation failures - return None instead
            logger.warning("⚠️ Image generation failed, returning None")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI service and available models."""
        return {
            'available': self.is_available(),
            'model_name': self.available_models[0] if self.available_models else 'gpt-4',
            'available_models': self.available_models,
            'api_key_configured': bool(self.api_key),
            'service_type': 'OpenAI GPT',
            'client_type': 'openai.OpenAI'
        }

# Global instance
openai_service = OpenAIService() 