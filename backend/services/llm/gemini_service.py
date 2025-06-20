"""
Google Gemini LLM Service

Handles all Google Gemini API interactions with error handling and response processing.
Updated for June 2025 with stable model configuration.
"""

import json
import asyncio
import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional, Callable

from .base_service import BaseLLMService, LLMError, log_api_error, clean_json_response

# Configure logging
logger = logging.getLogger(__name__)

class GeminiService(BaseLLMService):
    """Google Gemini LLM service implementation with enhanced error handling"""
    
    def __init__(self):
        super().__init__("GEMINI_API_KEY")
        self.model_name = None
        self.model = None
        
        if self.available:
            try:
                genai.configure(api_key=self.api_key)
                logger.info("✅ Gemini API configured successfully")
                
                # PRIORITIZE STABLE 1.5 MODELS FOR MVP - MUCH SIMPLER AND RELIABLE
                # 2.5 models have thinking mode complexity that can cause issues
                model_preferences = [
                    'gemini-1.5-pro',          # Most stable and reliable for MVP
                    'gemini-1.5-flash',        # Fast and stable alternative
                    'gemini-pro',              # Legacy fallback
                    'gemini-2.5-flash',        # Only try 2.5 if 1.5 unavailable
                    'gemini-2.5-pro',          # Last resort
                ]
                
                for model_name in model_preferences:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        self.model_name = model_name
                        logger.info(f"✅ Successfully initialized Gemini model: {model_name}")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to initialize {model_name}: {e}")
                        continue
                
                if not self.model:
                    logger.error("❌ No Gemini models available")
                    self.available = False
                    return
                
                # Configure generation settings optimized for writing feedback
                # Simpler config for 1.5 models - no thinking mode complexity
                base_config = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "candidate_count": 1
                }
                
                # Log which model type we're using
                if self.model_name and '1.5' in self.model_name:
                    logger.info(f"🚀 Using stable Gemini 1.5 model: {self.model_name} - Optimized for MVP reliability")
                elif self.model_name and '2.5' in self.model_name:
                    logger.info(f"⚠️ Using Gemini 2.5 model: {self.model_name} - May have thinking mode complexity")
                
                self.generation_config = genai.types.GenerationConfig(**base_config)
                
                # Configure safety settings
                self.safety_settings = {
                    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
                
                logger.info(f"🚀 Gemini service initialized with model: {self.model_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini service: {e}")
                self.available = False

    async def _make_api_call(self, api_call_func: Callable, error_context: str, **kwargs):
        """Generic helper to make Gemini API calls with comprehensive error handling"""
        if not self.available:
            raise LLMError(f"Gemini service not available - {error_context}")
        
        try:
            result = await asyncio.to_thread(api_call_func)
            return result
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific Gemini API errors with user-friendly messages
            if "api_key" in error_msg or "authentication" in error_msg:
                raise LLMError("Invalid Gemini API key. Please check your GEMINI_API_KEY environment variable.")
            elif "quota" in error_msg or "rate limit" in error_msg:
                raise LLMError("Gemini API quota exceeded. Please check your usage limits or try again later.")
            elif "model not found" in error_msg or "model" in error_msg:
                raise LLMError(f"Gemini model '{self.model_name}' not found. The model may not be available in your region.")
            elif "safety" in error_msg:
                raise LLMError("Response blocked by safety filters. Please try rephrasing your request.")
            elif "network" in error_msg or "connection" in error_msg:
                raise LLMError("Network error connecting to Gemini API. Please check your internet connection.")
            elif "timeout" in error_msg:
                raise LLMError("Request timed out. Please try again with a shorter prompt.")
            else:
                log_api_error("Gemini", e, error_context)
                raise LLMError(f"Gemini {error_context} failed: {str(e)}")

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini with comprehensive error handling"""
        def _generate():
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
                
                # Handle blocked responses
                if not response.text:
                    if response.prompt_feedback:
                        feedback = response.prompt_feedback
                        if feedback.block_reason:
                            return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                    
                    # Check if response was blocked
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'finish_reason'):
                            if candidate.finish_reason == genai.types.FinishReason.SAFETY:
                                return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                            elif candidate.finish_reason == genai.types.FinishReason.MAX_TOKENS:
                                return "Response was too long. Please try a shorter prompt or request."
                    
                    return "I'm unable to generate a response right now. Please try rephrasing your request."
                
                return response.text
                
            except Exception as e:
                if 'safety' in str(e).lower():
                    return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                raise e
        
        return await self._make_api_call(_generate, "text generation")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate structured JSON data using Gemini"""
        structured_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
        
        def _generate():
            response = self.model.generate_content(
                structured_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        
        result = await self._make_api_call(_generate, "structured generation")
        
        if not result:
            raise LLMError("Empty response from Gemini for structured generation")
        
        cleaned_result = clean_json_response(result)
        
        try:
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Gemini: {cleaned_result}")
            raise LLMError(f"Invalid JSON response from Gemini: {str(e)}")
    
    async def analyze_writing_style(self, writing_sample: str) -> Dict[str, Any]:
        """Analyze writing style using Gemini's advanced language understanding"""
        from .base_service import get_prompt_template
        
        prompt = get_prompt_template('style_analysis', writing_sample=writing_sample)
        return await self.generate_structured(prompt, {})
    
    async def generate_with_conversation_history(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response with conversation history - handles multiple input formats"""
        def _generate():
            try:
                # Handle different message formats from chat router vs direct calls
                if len(messages) == 1 and "parts" in messages[0]:
                    # Format from chat router: [{"role": "user", "parts": [prompt]}]
                    prompt = messages[0]["parts"][0]
                    logger.info("Using single prompt format from chat router")
                    
                    response = self.model.generate_content(
                        prompt,
                        generation_config=self.generation_config,
                        safety_settings=self.safety_settings
                    )
                else:
                    # Standard conversation format: [{"role": "user", "content": "message"}]
                    logger.info("Using conversation history format")
                    chat = self.model.start_chat(history=[])
                    
                    # Add conversation history (all but last message)
                    for message in messages[:-1]:
                        if message.get('role') == 'user':
                            content = message.get('content', message.get('parts', [''])[0])
                            chat.send_message(content)
                    
                    # Generate response to the last message
                    last_message = messages[-1]
                    last_content = last_message.get('content', last_message.get('parts', [''])[0])
                    
                    response = chat.send_message(
                        last_content,
                        generation_config=self.generation_config,
                        safety_settings=self.safety_settings
                    )
                
                # ROBUST RESPONSE EXTRACTION - Handle all possible response structures
                response_text = None
                
                # Method 1: Direct text attribute (most common)
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
                    logger.info("✅ Extracted text using direct .text attribute")
                
                # Method 2: Extract from candidates (backup method)
                elif hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    
                    # Try candidate.content.parts[0].text
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts = candidate.content.parts
                        if parts and hasattr(parts[0], 'text') and parts[0].text:
                            response_text = parts[0].text
                            logger.info("✅ Extracted text from candidate.content.parts")
                    
                    # Try candidate.text directly
                    elif hasattr(candidate, 'text') and candidate.text:
                        response_text = candidate.text
                        logger.info("✅ Extracted text from candidate.text")
                
                # Method 3: Check for blocked response
                if not response_text:
                    # Check if response was blocked by safety filters
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        feedback = response.prompt_feedback
                        if hasattr(feedback, 'block_reason') and feedback.block_reason:
                            logger.warning(f"Response blocked by safety filters: {feedback.block_reason}")
                            return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                    
                    # Check candidate finish reason
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'finish_reason'):
                            reason = candidate.finish_reason
                            if reason == genai.types.FinishReason.SAFETY:
                                return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                            elif reason == genai.types.FinishReason.MAX_TOKENS:
                                return "Response was too long. Please try a shorter prompt or request."
                            elif reason == genai.types.FinishReason.RECITATION:
                                return "Response blocked due to recitation concerns. Please try rephrasing your request."
                            else:
                                logger.warning(f"Response finished with reason: {reason}")
                    
                    # If still no text, return fallback message
                    logger.error("Could not extract text from Gemini response using any method")
                    logger.error(f"Response structure: {type(response)}, has text: {hasattr(response, 'text')}, has candidates: {hasattr(response, 'candidates')}")
                    return "I'm unable to generate a response right now. Please try rephrasing your request."
                
                return response_text
                
            except Exception as e:
                logger.error(f"Error in conversation generation: {e}")
                if 'safety' in str(e).lower():
                    return "I apologize, but I cannot generate a response to that request due to safety guidelines. Please try rephrasing your question."
                # Re-raise the exception so it gets caught by _make_api_call for proper error handling
                raise e
        
        return await self._make_api_call(_generate, "conversation generation")
    
    # Thinking mode removed for MVP - using stable 1.5 models for simplicity
    
    def is_available(self) -> bool:
        """Check if the service is available and properly configured"""
        return self.available and self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "available": self.available,
            "model_name": self.model_name,
            "api_key_configured": bool(self.api_key),
            "service_type": "Google Gemini"
        }

# Global instance
gemini_service = GeminiService()

# Deployment marker: 2025-06-19 - Enhanced error handling and model fallback 