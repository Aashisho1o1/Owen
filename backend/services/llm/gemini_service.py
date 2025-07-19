"""
Google Gemini LLM Service

Handles all Google Gemini API interactions with error handling and response processing.
Updated for Railway deployment compatibility with stable google-generativeai library.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

# Configure logging
logger = logging.getLogger(__name__)

# CRITICAL FIX: Robust import handling for Railway deployment
GENAI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
    logger.info("✅ Google Generative AI library imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Google Generative AI library: {e}")
    logger.error("This will disable Gemini functionality but app will continue to work")
    GENAI_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Unexpected error importing Google Generative AI: {e}")
    GENAI_AVAILABLE = False


class GeminiService(BaseLLMService):
    """Gemini service for generative AI - now uses 1.5 Pro"""
    
    def __init__(self):
        super().__init__("GEMINI_API_KEY")
        
        if self.available:
            try:
                # Configure the generative AI client with the API key
                genai.configure(api_key=self.api_key)
                
                # Use Gemini 1.5 Pro model for enhanced contextual understanding
                self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                logger.info("✅ Gemini service initialized successfully with gemini-1.5-pro-latest")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini service: {e}")
                self.available = False
        else:
            logger.warning("⚠️ Gemini API key not found. Service will be unavailable.")
    
    def is_available(self) -> bool:
        """Check if Gemini service is available."""
        return GENAI_AVAILABLE and self.available and self.client is not None and self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.is_available():
            return {
                'available': False,
                'model_name': None,
                'api_key_configured': bool(self.api_key),
                'service_type': 'Google Gemini',
                'library_available': GENAI_AVAILABLE,
                'error': 'Service not available'
            }
        
        return {
            'available': True,
            'model_name': self.available_models[0] if self.available_models else 'unknown',
            'api_key_configured': bool(self.api_key),
            'service_type': 'Google Gemini',
            'library_available': GENAI_AVAILABLE,
            'available_models': self.available_models,
            'client_type': 'google.generativeai'
        }
    
    async def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response using Gemini with optimized settings"""
        if not self.available:
            raise Exception("Gemini service not available")
        
        if not self.model:
            raise Exception("Gemini model not initialized")
        
        # Truncate input to prevent timeouts
        if len(prompt) > 1000:
            logger.info(f"🔧 Truncating prompt from {len(prompt)} to 1000 characters")
            prompt = prompt[:1000] + ' [TRUNCATED FOR PROCESSING SPEED]'
        
        logger.info(f"🧠 Gemini processing request (length: {len(prompt)} chars)")
        logger.info("⏳ Expected processing time: 15-45 seconds")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Increased timeout for voice analysis
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self.model.generate_content(prompt)),
                timeout=45.0  # Increased from 8 to 45 seconds
            )
            
            if not response.text:
                logger.warning("⚠️ Gemini returned empty response")
                raise Exception("Gemini returned empty response")
            
            logger.info(f"✅ Gemini response generated (length: {len(response.text)} chars)")
            return response.text
            
        except asyncio.TimeoutError:
            logger.error("⏰ Gemini request timed out after 45 seconds")
            raise Exception("Gemini API timeout - please try with shorter text")
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
            
        except Exception as e:
            current_model = self.available_models[0] if self.available_models else 'unknown'
            error_msg = f"Gemini generation failed with {current_model}: {str(e)}"
            
            # Convert context dict to string for logging
            context_info = {
                "prompt_length": len(prompt), 
                "model": current_model,
                "max_tokens": max_tokens,
                "temperature": 0.7 # Default temperature for generation
            }
            context_str = str(context_info)
            
            log_api_error("gemini", e, context_str)
            raise LLMError(error_msg)
    
    async def generate_json_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a JSON response using Gemini."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Add JSON formatting instruction to prompt
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
            
            response_text = await self.generate_response(
                json_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return clean_json_response(response_text)
            
        except Exception as e:
            error_msg = f"Gemini JSON generation failed: {str(e)}"
            log_api_error("gemini", e, f"JSON generation - prompt_length: {len(prompt)}")
            raise LLMError(error_msg)
    
    async def generate_streaming_response(
        self,
        prompt: str,
        callback: Callable[[str], None],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> None:
        """Generate a streaming response using Gemini."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Generate streaming response with default settings for Gemini 2.5 Pro compatibility
            # NOTE: GenerationConfig disabled for Gemini 2.5 Pro compatibility
            response = self.model.generate_content(
                prompt,
                safety_settings=kwargs.get('safety_settings', []),
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    callback(chunk.text)
                    # Small delay to prevent overwhelming the callback
                    await asyncio.sleep(0.01)
            
        except Exception as e:
            error_msg = f"Gemini streaming failed: {str(e)}"
            log_api_error("gemini", e, f"streaming - prompt_length: {len(prompt)}")
            raise LLMError(error_msg)
    
    # Required abstract methods from BaseLLMService
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini - maps to generate_response."""
        return await self.generate_response(prompt, **kwargs)
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured data using Gemini - maps to generate_json_response."""
        return await self.generate_json_response(prompt, **kwargs)
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Generate response with conversation history using Gemini."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Convert messages to Gemini format and process conversation history
            conversation_parts = []
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                # Handle different message formats
                if 'parts' in message:
                    # Already in Gemini format
                    conversation_parts.append(message)
                else:
                    # Convert from standard format to Gemini format
                    if role == 'user':
                        conversation_parts.append({
                            "role": "user", 
                            "parts": [content]
                        })
                    elif role == 'assistant':
                        conversation_parts.append({
                            "role": "model", 
                            "parts": [content]
                        })
            
            # If only one message and it's already formatted for Gemini, use it directly
            if len(conversation_parts) == 1 and isinstance(conversation_parts[0].get('parts'), list):
                prompt_content = conversation_parts[0]['parts'][0]
                return await self.generate_response(prompt_content, **kwargs)
            
            # For multi-turn conversation, use chat format
            # Convert to simple prompt for now (Gemini chat requires more complex setup)
            combined_prompt = ""
            for part in conversation_parts:
                role = part.get('role', 'user')
                parts = part.get('parts', [])
                content = parts[0] if parts else ""
                
                if role == 'user':
                    combined_prompt += f"User: {content}\n"
                elif role == 'model':
                    combined_prompt += f"Assistant: {content}\n"
            
            # Add instruction for assistant to respond
            combined_prompt += "Assistant:"
            
            return await self.generate_response(combined_prompt, **kwargs)
            
        except Exception as e:
            error_msg = f"Gemini conversation generation failed: {str(e)}"
            log_api_error("gemini", e, f"conversation - messages_count: {len(messages)}")
            raise LLMError(error_msg)


# Global instance
gemini_service = GeminiService() 