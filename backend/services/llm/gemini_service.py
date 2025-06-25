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
                'gemini-2.0-flash-exp',     # PRIMARY: Latest experimental 2.0 model (fast)
                'gemini-2.0-flash',         # BACKUP: Stable 2.0 model (fast)
                'gemini-1.5-flash',         # FALLBACK: Legacy fast model
                'gemini-1.5-pro',           # FALLBACK: Legacy high-quality model
                'gemini-pro'                # FINAL: Basic fallback
                # REMOVED: gemini-2.5-pro (too slow, causes timeouts)
                # REMOVED: gemini-2.5-flash (too slow, causes timeouts)  
                # REMOVED: gemini-2.5-flash-lite-preview-06-17 (too slow, causes timeouts)
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
        """Generate a response using Gemini with optimized fast models (2.0-flash-exp primary)."""
        if not self.is_available():
            raise LLMError("Gemini service not available")
        
        try:
            # Configure generation parameters optimized for fast Gemini 2.0 models
            # NOTE: Using simplified config for maximum speed and compatibility
            use_config = False  # Disabled for optimal performance
            
            if use_config:
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                    # Note: top_p and top_k removed for Gemini 2.5 Pro compatibility
                )
            
            # Enhanced safety settings for production use
            safety_settings = kwargs.get('safety_settings', [])
            if not safety_settings:
                # Default safety settings that work well with fast Gemini models
                # Use proper genai enums for safety settings
                try:
                    safety_settings = [
                        {
                            "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        },
                        {
                            "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        },
                        {
                            "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        },
                        {
                            "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                        },
                    ]
                except AttributeError:
                    # Fallback if enum types are not available - use minimal safety
                    safety_settings = []
            
            # Get current model name for adaptive behavior
            current_model = self.available_models[0] if self.available_models else 'unknown'
            
            # Log which model we're using for debugging
            logger.info(f"🎯 Using Gemini model: {current_model} for prompt length: {len(prompt)}")
            
            # Add timeout handling for Gemini 2.5 models - FIXED FOR TIMEOUT ISSUES
            import asyncio
            
            try:
                # Generate response with timeout protection
                # Use asyncio.wait_for to add timeout to the synchronous call
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.model.generate_content,
                        prompt,
                        safety_settings=safety_settings
                    ),
                    timeout=20.0  # 20 second timeout (less than frontend's 25s)
                )
                logger.info(f"✅ Gemini response generated successfully in <20s")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Gemini timeout after 20s with model {current_model}")
                # Try fallback to faster model if available
                if len(self.available_models) > 1:
                    fallback_model = self.available_models[1]  # Try second model
                    logger.info(f"🔄 Attempting fallback to {fallback_model}")
                    try:
                        fallback_genai_model = genai.GenerativeModel(fallback_model)
                        response = await asyncio.wait_for(
                            asyncio.to_thread(
                                fallback_genai_model.generate_content,
                                prompt,
                                safety_settings=safety_settings
                            ),
                            timeout=15.0  # Shorter timeout for fallback
                        )
                        logger.info(f"✅ Fallback model {fallback_model} succeeded")
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback model also failed: {fallback_error}")
                        raise LLMError(f"Gemini models timed out. Please try a shorter prompt or try again later.")
                else:
                    raise LLMError(f"Gemini model {current_model} timed out after 20 seconds. Please try a shorter prompt or try again later.")
            
            # Check if response was blocked before accessing text
            if not response.candidates:
                raise LLMError("No response candidates generated - possibly blocked by safety filters")
            
            candidate = response.candidates[0]
            
            # Check safety ratings if response is blocked
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                for rating in candidate.safety_ratings:
                    if hasattr(rating, 'blocked') and rating.blocked:
                        category = getattr(rating, 'category', 'Unknown')
                        probability = getattr(rating, 'probability', 'Unknown')
                        raise LLMError(f"Content blocked by safety filter - Category: {category}, Probability: {probability}")
            
            # Check finish reason
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                logger.info(f"🔍 Finish reason: {finish_reason}")
                
                # 1 = STOP (successful), 2 = MAX_TOKENS, 3 = SAFETY, 4 = RECITATION, 5 = OTHER
                if finish_reason == 3:  # SAFETY
                    raise LLMError("Content generation stopped due to safety concerns")
                elif finish_reason == 4:  # RECITATION
                    raise LLMError("Content generation stopped due to recitation concerns")
                elif finish_reason == 5:  # OTHER (problematic)
                    raise LLMError(f"Content generation stopped unexpectedly: {finish_reason}")
                elif finish_reason == 2:  # MAX_TOKENS
                    logger.info("ℹ️  Generation stopped due to max tokens limit")
            
            # Try to access text with better error handling
            response_text = None
            try:
                response_text = response.text
                if response_text:
                    response_text = response_text.strip()
            except Exception as text_error:
                logger.warning(f"⚠️  Failed to access response.text: {text_error}")
                
                # Try to access through candidate content parts
                try:
                    if hasattr(candidate, 'content') and candidate.content:
                        content = candidate.content
                        if hasattr(content, 'parts') and content.parts:
                            parts_text = []
                            for part in content.parts:
                                if hasattr(part, 'text') and part.text:
                                    parts_text.append(part.text)
                                    logger.info(f"✅ Found part with {len(part.text)} characters")
                            if parts_text:
                                response_text = ''.join(parts_text).strip()
                                logger.info(f"✅ Retrieved text via content parts: {len(response_text)} chars")
                            else:
                                logger.warning("⚠️  Content parts exist but no text found in any part")
                        else:
                            logger.warning("⚠️  Content exists but no parts found")
                    else:
                        logger.warning("⚠️  No content found in candidate")
                except Exception as parts_error:
                    logger.error(f"❌ Failed to access content parts: {parts_error}")
                    
                    # If all else fails, check for prompt feedback
                    if hasattr(response, 'prompt_feedback'):
                        feedback = response.prompt_feedback
                        if hasattr(feedback, 'block_reason'):
                            raise LLMError(f"Prompt blocked by safety filters: {feedback.block_reason}")
                    
                    raise LLMError(f"Could not access response text: {text_error}")
            
            if not response_text:
                raise LLMError("Empty response from Gemini - content may have been filtered")
            
            # Log successful generation with model info
            logger.info(f"✅ Generated {len(response_text)} characters using {current_model}")
            
            return response_text
            
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