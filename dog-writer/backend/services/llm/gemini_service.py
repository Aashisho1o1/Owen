"""
Google Gemini LLM Service

Handles all Google Gemini API interactions with error handling and response processing.
"""

import json
import asyncio
import google.generativeai as genai
from typing import Dict, Any, List, Optional

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

class GeminiService(BaseLLMService):
    """Google Gemini LLM service implementation"""
    
    def __init__(self):
        super().__init__("GEMINI_API_KEY")
        if self.available:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini"""
        if not self.available:
            raise LLMError("Gemini service not available - missing API key")
        
        try:
            # Gemini API is synchronous, so we run it in a thread
            def _generate():
                response = self.model.generate_content(prompt)
                return response.text
            
            result = await asyncio.to_thread(_generate)
            return result
            
        except Exception as e:
            log_api_error("Gemini", e, "text generation")
            raise LLMError(f"Gemini text generation failed: {str(e)}")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using Gemini"""
        if not self.available:
            raise LLMError("Gemini service not available - missing API key")
        
        try:
            # Add JSON formatting instruction to prompt
            structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
            
            def _generate():
                response = self.model.generate_content(structured_prompt)
                return response.text
            
            result = await asyncio.to_thread(_generate)
            cleaned_result = clean_json_response(result)
            
            try:
                return json.loads(cleaned_result)
            except json.JSONDecodeError as e:
                raise LLMError(f"Invalid JSON response from Gemini: {str(e)}")
            
        except Exception as e:
            log_api_error("Gemini", e, "structured generation")
            raise LLMError(f"Gemini structured generation failed: {str(e)}")
    
    async def analyze_writing_style(self, writing_sample: str) -> Dict[str, Any]:
        """Analyze writing style using Gemini's advanced language understanding"""
        from .base_service import get_prompt_template
        
        prompt = get_prompt_template('style_analysis', writing_sample=writing_sample)
        return await self.generate_structured(prompt, {})
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history"""
        if not self.available:
            raise LLMError("Gemini service not available - missing API key")
        
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Add conversation history (except the last message)
            for message in messages[:-1]:
                if message['role'] == 'user':
                    chat.send_message(message['content'])
            
            # Generate response to the last message
            last_message = messages[-1]['content']
            
            def _generate():
                response = chat.send_message(last_message)
                return response.text
            
            result = await asyncio.to_thread(_generate)
            return result
            
        except Exception as e:
            log_api_error("Gemini", e, "conversation generation")
            raise LLMError(f"Gemini conversation generation failed: {str(e)}")

# Global instance
gemini_service = GeminiService() 