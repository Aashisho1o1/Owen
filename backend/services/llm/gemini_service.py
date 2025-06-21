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
            model_preferences = [
                'gemini-2.0-flash-exp',  # Latest experimental model
                'gemini-2.0-flash',      # Stable 2.0 model
                'gemini-1.5-pro',        # High-quality model
                'gemini-1.5-flash',      # Fast model
                'gemini-pro'             # Fallback model
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
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate a response using Gemini."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', 0.8),
                top_k=kwargs.get('top_k', 40)
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=kwargs.get('safety_settings', [])
            )
            
            if not response.text:
                raise LLMError("Empty response from Gemini")
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Gemini generation failed: {str(e)}"
            log_api_error("gemini", error_msg, {"prompt_length": len(prompt)})
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
            log_api_error("gemini", error_msg, {"prompt_length": len(prompt)})
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
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', 0.8),
                top_k=kwargs.get('top_k', 40)
            )
            
            # Generate streaming response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
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
            log_api_error("gemini", error_msg, {"prompt_length": len(prompt)})
            raise LLMError(error_msg)
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Generate response with conversation history using Gemini."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Convert messages to Gemini format
            # Gemini expects a list of parts, not the OpenAI format
            conversation_parts = []
            
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                # Handle different message formats
                if 'parts' in message:
                    # Already in Gemini format
                    conversation_parts.extend(message['parts'])
                else:
                    # Convert from OpenAI format
                    conversation_parts.append(content)
            
            # Join all conversation parts into a single prompt
            # For Gemini, we'll treat the conversation as a single context
            conversation_prompt = '\n\n'.join(str(part) for part in conversation_parts)
            
            # Generate response using the conversation prompt
            return await self.generate_response(conversation_prompt, **kwargs)
            
        except Exception as e:
            error_msg = f"Gemini conversation generation failed: {str(e)}"
            log_api_error("gemini", error_msg, {"messages_count": len(messages)})
            raise LLMError(error_msg)
    
    # Required abstract methods from BaseLLMService
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini - maps to generate_response."""
        return await self.generate_response(prompt, **kwargs)
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured data using Gemini - maps to generate_json_response."""
        return await self.generate_json_response(prompt, **kwargs)


# Global instance
gemini_service = GeminiService() 