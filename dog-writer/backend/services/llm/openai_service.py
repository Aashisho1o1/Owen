"""
OpenAI Service

Handles OpenAI ChatGPT and DALL-E API interactions.
"""

import json
import asyncio
import openai
from typing import Dict, Any, List, Optional

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
    
    async def generate_text(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        """Generate text using ChatGPT"""
        if not self.available:
            raise LLMError("OpenAI service not available - missing API key or connection failed")
        
        try:
            def _generate():
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
                return response.choices[0].message.content
            
            result = await asyncio.to_thread(_generate)
            return result or ""
            
        except Exception as e:
            log_api_error("OpenAI", e, "text generation")
            raise LLMError(f"OpenAI text generation failed: {str(e)}")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using ChatGPT"""
        if not self.available:
            raise LLMError("OpenAI service not available - missing API key")
        
        try:
            # Add JSON formatting instruction
            structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
            
            def _generate():
                response = self.client.chat.completions.create(
                    model=kwargs.get('model', 'gpt-4'),
                    messages=[{"role": "user", "content": structured_prompt}],
                    temperature=kwargs.get('temperature', 0.3),  # Lower temperature for structured output
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
                return response.choices[0].message.content
            
            result = await asyncio.to_thread(_generate)
            cleaned_result = clean_json_response(result or "")
            
            try:
                return json.loads(cleaned_result)
            except json.JSONDecodeError as e:
                raise LLMError(f"Invalid JSON response from OpenAI: {str(e)}")
            
        except Exception as e:
            log_api_error("OpenAI", e, "structured generation")
            raise LLMError(f"OpenAI structured generation failed: {str(e)}")
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history"""
        if not self.available:
            raise LLMError("OpenAI service not available - missing API key")
        
        try:
            def _generate():
                response = self.client.chat.completions.create(
                    model=kwargs.get('model', 'gpt-4'),
                    messages=messages,
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 2000)
                )
                return response.choices[0].message.content
            
            result = await asyncio.to_thread(_generate)
            return result or ""
            
        except Exception as e:
            log_api_error("OpenAI", e, "conversation generation")
            raise LLMError(f"OpenAI conversation generation failed: {str(e)}")
    
    async def generate_image(self, description: str, size: str = "1024x1024", style: str = "natural") -> Optional[str]:
        """Generate image using DALL-E"""
        if not self.available:
            raise LLMError("OpenAI service not available - missing API key")
        
        try:
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
            
            result = await asyncio.to_thread(_generate)
            return result
            
        except Exception as e:
            log_api_error("OpenAI", e, "image generation")
            # Don't raise exception for image generation failures - return None instead
            return None

# Global instance
openai_service = OpenAIService() 