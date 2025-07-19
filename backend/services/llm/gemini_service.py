"""
Google Gemini LLM Service

Handles all Google Gemini API interactions with error handling and response processing.
This version is standardized to use the modern Google Generative AI library with
gemini-1.5-pro-latest for all calls, ensuring consistency and leveraging the
most capable model.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

# Configure logging
logger = logging.getLogger(__name__)

# Import and validate the Google Generative AI library
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    logger.info("✅ Google Generative AI library imported successfully")
except ImportError:
    logger.error("❌ Failed to import google.generativeai. Gemini features will be disabled.")
    genai = None
    GENAI_AVAILABLE = False


class GeminiService(BaseLLMService):
    """
    Standardized Gemini service using the gemini-1.5-pro-latest model.
    This service ensures all API calls use the modern, correct methods.
    """

    def __init__(self):
        super().__init__("GEMINI_API_KEY")
        self.model = None
        
        if self.available and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
                logger.info("✅ Gemini service initialized successfully with gemini-1.5-pro-latest")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model: {e}")
                self.available = False
        else:
            logger.warning("⚠️ Gemini service is unavailable. Check API key and library installation.")

    def is_available(self) -> bool:
        return self.available and self.model is not None

    async def generate_response(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.5) -> str:
        if not self.is_available():
            raise LLMError("Gemini service is not available.")

        logger.info(f"🧠 Calling Gemini 1.5 Pro with prompt (length: {len(prompt)})...")
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            logger.info(f"✅ Gemini 1.5 Pro response received successfully.")
            return response.text
        except Exception as e:
            log_api_error("Gemini", e, f"Text generation failed for prompt: {prompt[:100]}...")
            raise LLMError(f"Gemini API error during text generation: {e}")

    async def generate_json_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.is_available():
            raise LLMError("Gemini service is not available.")
            
        logger.info(f"🧠 Calling Gemini 1.5 Pro in JSON mode (prompt length: {len(prompt)})...")
        json_prompt = f"Respond with ONLY valid JSON that adheres to the requested schema. Do not include any markdown formatting or explanatory text outside of the JSON structure.\n\n{prompt}"
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                json_prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    **kwargs
                )
            )
            logger.info(f"✅ Gemini 1.5 Pro JSON response received successfully.")
            return clean_json_response(response.text)
        except Exception as e:
            log_api_error("Gemini", e, f"JSON generation failed for prompt: {prompt[:100]}...")
            raise LLMError(f"Gemini API error during JSON generation: {e}")
            
    # Base class abstract method implementations
    async def generate_text(self, prompt: str, **kwargs) -> str:
        return await self.generate_response(prompt, **kwargs)

    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        # The schema can be implicitly defined in the prompt for Gemini
        return await self.generate_json_response(prompt, **kwargs)

    async def generate_with_conversation_history(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        if not self.is_available():
            raise LLMError("Gemini service is not available.")

        logger.info(f"🧠 Starting Gemini 1.5 Pro chat with {len(messages)} history messages...")
        try:
            chat = self.model.start_chat(history=messages)
            response = await asyncio.to_thread(chat.send_message, messages[-1]['parts'], **kwargs)
            logger.info("✅ Gemini 1.5 Pro chat response received.")
            return response.text
        except Exception as e:
            log_api_error("Gemini", e, "Chat generation failed.")
            raise LLMError(f"Gemini API error during chat: {e}")

# Global instance
gemini_service = GeminiService() 