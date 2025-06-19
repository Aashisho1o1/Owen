"""
Google Gemini LLM Service

Handles all Google Gemini API interactions with error handling and response processing.
"""

import json
import asyncio
import google.generativeai as genai
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

class GeminiService(BaseLLMService):
    """Google Gemini LLM service implementation"""
    
    def __init__(self):
        super().__init__("GEMINI_API_KEY")
        if self.available:
            genai.configure(api_key=self.api_key)
            # Updated to use Gemini 2.5 Pro (stable, generally available as of June 17, 2025)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            
            # Configure generation settings to disable thinking for better performance
            self.generation_config = genai.types.GenerationConfig(
                temperature=1.0,
                top_p=0.95,
                top_k=64,
                max_output_tokens=8192,
                # Set thinking budget to 0 for fastest response
                thinking_budget=0
            )

    async def _make_api_call(self, api_call_func: Callable, error_context: str, **kwargs):
        """Generic helper to make Gemini API calls"""
        if not self.available:
            raise LLMError(f"Gemini service not available - {error_context}")
        
        try:
            result = await asyncio.to_thread(api_call_func)
            return result
        except Exception as e:
            log_api_error("Gemini", e, error_context)
            raise LLMError(f"Gemini {error_context} failed: {str(e)}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini with optimized settings"""
        def _generate():
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            return response.text
        
        return await self._make_api_call(_generate, "text generation")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using Gemini with optimized settings"""
        structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        
        def _generate():
            response = self.model.generate_content(
                structured_prompt,
                generation_config=self.generation_config
            )
            return response.text
        
        result = await self._make_api_call(_generate, "structured generation")
        cleaned_result = clean_json_response(result)
        
        try:
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON response from Gemini: {str(e)}")
    
    async def analyze_writing_style(self, writing_sample: str) -> Dict[str, Any]:
        """Analyze writing style using Gemini's advanced language understanding"""
        from .base_service import get_prompt_template
        
        prompt = get_prompt_template('style_analysis', writing_sample=writing_sample)
        return await self.generate_structured(prompt, {})
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history using optimized settings"""
        def _generate():
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            for message in messages[:-1]:
                if message['role'] == 'user':
                    chat.send_message(message['content'])
            
            # Generate response to the last message with optimized config
            last_message = messages[-1]['content']
            response = chat.send_message(
                last_message,
                generation_config=self.generation_config
            )
            return response.text
        
        return await self._make_api_call(_generate, "conversation generation")

# Global instance
gemini_service = GeminiService() 