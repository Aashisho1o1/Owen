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
    """Google Gemini API service implementation."""
    
    def __init__(self):
        """Initialize Gemini service with error handling."""
        # Initialize base class with API key environment variable
        super().__init__('GEMINI_API_KEY')
        self.client = None
        self.model = None
        self.available_models = []
        
        # Only initialize if library is available
        if GENAI_AVAILABLE:
            self._initialize_client()
        else:
            logger.warning("⚠️ Gemini service not available - Google Generative AI library not imported")
            self.available = False
    
    def _initialize_client(self):
        """Initialize the Gemini client with robust error handling."""
        try:
            if not self.api_key:
                logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")
                self.available = False
                return
                
            # Configure the client
            genai.configure(api_key=self.api_key)
            
            # Test available models in order of preference
            # OPTIMIZED MODEL PREFERENCES - Fast, reliable models only
            # Removed slow thinking models that cause timeouts
            model_preferences = [
                'gemini-1.5-flash-8b',  # Ultra-fast experimental model
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash'
            ]
            
            for model_name in model_preferences:
                try:
                    # Test model initialization
                    test_model = genai.GenerativeModel(model_name)
                    self.model = test_model
                    self.available_models.append(model_name)
                    logger.info(f"✅ Successfully initialized Gemini model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize {model_name}: {e}")
                    continue
            
            if not self.model:
                logger.error("❌ No Gemini models available")
                return
                
            self.client = genai
            logger.info(f"✅ Gemini service initialized with {len(self.available_models)} available models")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            self.client = None
            self.model = None
    
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
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate a response using Gemini with optimized fast models (2.0-flash-exp primary)."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # NEW: Truncate input to prevent timeouts with large text
            if len(prompt) > 1000:
                prompt = prompt[:1000] + " [TRUNCATED]"
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self.model.generate_content(prompt)),
                timeout=8.0  # REDUCED: Stricter timeout for faster failure
            )
            return response.text
        except asyncio.TimeoutError:
            logger.warning("Gemini primary call timed out")
            return "[TIMEOUT] Voice analysis took too long - please try shorter text"
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
            
        except Exception as e:
            current_model = self.available_models[0] if self.available_models else 'unknown'
            error_msg = f"Gemini generation failed with {current_model}: {str(e)}"
            
            # Convert context dict to string for logging
            context_info = {
                "prompt_length": len(prompt), 
                "model": current_model,
                "max_tokens": max_tokens,
                "temperature": temperature
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