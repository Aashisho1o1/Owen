"""
Google Gemini LLM service implementation
"""
import google.generativeai as genai
from typing import Dict, Any, Union, List, Optional

from services.llm.base_service import BaseLLMService

class GeminiService(BaseLLMService):
    """
    Service for interacting with Google's Gemini models
    """
    def __init__(self):
        """Initialize the Gemini service"""
        super().__init__()
        
        # Get API key
        self.api_key = self.get_env_var("GEMINI_API_KEY", required=True)
        
        # Configure the client
        genai.configure(api_key=self.api_key)
        
        # Set up model (default to gemini-1.5-pro, but can be overridden)
        self.model_name = self.get_env_var("GEMINI_MODEL_NAME") or "gemini-1.5-pro"
        self.model = genai.GenerativeModel(self.model_name)
        
        self.initialized = True
        self.logger.info(f"Gemini service initialized with model: {self.model_name}")
        
    async def generate_text(self, prompt: Union[str, List[Dict[str, Any]]], **kwargs) -> Union[str, Dict[str, Any]]:
        """
        Generate text using Gemini
        
        Args:
            prompt: Either a string prompt or a list of dictionaries with 'role' and 'parts' keys
            kwargs: Additional parameters for Gemini
            
        Returns:
            Generated text or dictionary with text and metadata
        """
        if not self.initialized:
            self.logger.error("Gemini service not properly initialized")
            return "Error: Gemini service not initialized"
            
        try:
            # Ensure prompt is properly formatted for Gemini
            if isinstance(prompt, str):
                # Convert string prompt to the format expected by Gemini
                formatted_prompt = [{"role": "user", "parts": [prompt]}]
            else:
                formatted_prompt = prompt
                
            # Generate content
            response = self.model.generate_content(formatted_prompt)
            
            # Process response
            if response.candidates and len(response.candidates) > 0 and \
               response.candidates[0].content and response.candidates[0].content.parts and \
               len(response.candidates[0].content.parts) > 0:
                
                full_text_response = ""
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and isinstance(part.text, str):
                        full_text_response += part.text
                
                if not full_text_response.strip():
                    self.logger.warning("Gemini returned empty response")
                    return "Error: Empty response from Gemini"
                    
                return full_text_response
            else:
                self.logger.warning("Invalid response structure from Gemini")
                return "Error: Invalid response structure from Gemini"
                
        except Exception as e:
            self.log_api_error("Gemini", e, "generate_text")
            return f"Error generating text with Gemini: {str(e)}" 