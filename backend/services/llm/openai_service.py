"""
OpenAI Service

Handles OpenAI ChatGPT and DALL-E API interactions.
"""

import json
import asyncio
import openai
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

class OpenAIService(BaseLLMService):
    """OpenAI service for ChatGPT and DALL-E"""
    
    def __init__(self):
        super().__init__("OPENAI_API_KEY")
        if self.available:
            self.client = openai.OpenAI(api_key=self.api_key)
            self._test_connection()
    
    def _test_connection(self):
        """Test OpenAI API connection during initialization"""
        try:
            # Quick test to verify API connection
            self.client.models.list()
        except Exception as e:
            log_api_error("OpenAI", e, "connection test")
            self.available = False
    
    async def _make_api_call(self, api_call_func: Callable, error_context: str, **kwargs):
        """Generic helper to make OpenAI API calls"""
        if not self.available:
            raise LLMError(f"OpenAI service not available - {error_context}")
        
        try:
            result = await asyncio.to_thread(api_call_func)
            return result
        except Exception as e:
            log_api_error("OpenAI", e, error_context)
            raise LLMError(f"OpenAI {error_context} failed: {str(e)}")

    async def generate_text(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        """Generate text using ChatGPT"""
        def _generate():
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            return response.choices[0].message.content
        
        result = await self._make_api_call(_generate, "text generation")
        return result or ""
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using ChatGPT"""
        structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        
        def _generate():
            response = self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4'),
                messages=[{"role": "user", "content": structured_prompt}],
                temperature=kwargs.get('temperature', 0.3),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            return response.choices[0].message.content

        result = await self._make_api_call(_generate, "structured generation")
        cleaned_result = clean_json_response(result or "")
        
        try:
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from OpenAI: {str(e)}")
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history"""
        def _generate():
            response = self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4'),
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            return response.choices[0].message.content
        
        result = await self._make_api_call(_generate, "conversation generation")
        return result or ""
    
    async def generate_image(self, description: str, size: str = "1024x1024", style: str = "natural") -> Optional[str]:
        """Generate image using DALL-E"""
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
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI service."""
        return {
            'available': self.is_available(),
            'model_name': 'gpt-4',
            'api_key_configured': bool(self.api_key),
            'service_type': 'OpenAI GPT',
            'client_type': 'openai.OpenAI'
        }

# Global instance
openai_service = OpenAIService() 