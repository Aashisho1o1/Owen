"""
OpenAI DALL-E image generation service
"""
import asyncio
from typing import Dict, Optional, Union

import openai
from services.llm.base_service import BaseLLMService

class DalleService(BaseLLMService):
    """Service for generating images using OpenAI's DALL-E models"""
    
    def __init__(self):
        """Initialize the DALL-E service"""
        super().__init__()
        
        # Get API key
        self.api_key = self.get_env_var("OPENAI_API_KEY", required=True)
        
        # Configure client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Set model (allow override via env var)
        self.model = self.get_env_var("DALLE_MODEL") or "dall-e-3"
        
        # Test API connection
        try:
            # Just get the list of models to verify API connection
            self.client.models.list()
            self.initialized = True
            self.logger.info(f"✓ DALL-E service initialized with model: {self.model}")
        except Exception as e:
            self.log_api_error("OpenAI", e, "initialization")
            self.logger.error(f"⚠️ DALL-E service initialization failed")
    
    async def generate_text(self, prompt: Union[str, Dict], **kwargs) -> Union[str, Dict]:
        """
        Required by BaseLLMService but not applicable to DALL-E
        """
        self.logger.warning("generate_text called on DALL-E service, which is for image generation only")
        return "Error: DALL-E service is for image generation only, not text generation."
    
    async def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Optional[str]:
        """
        Generate an image using DALL-E
        
        Args:
            prompt: The image description
            size: Image size (1024x1024, 1792x1024, or 1024x1792)
            quality: Image quality (standard or hd)
            
        Returns:
            URL to the generated image or None on failure
        """
        if not self.initialized:
            self.logger.error("DALL-E service not properly initialized")
            return None
            
        try:
            # Execute the blocking call in a thread pool
            def generate_image_sync():
                """Synchronous image generation to run in thread pool"""
                try:
                    response = self.client.images.generate(
                        model=self.model,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=1,
                        response_format="url"
                    )
                    return response.data[0].url, None  # Return URL and no error
                except Exception as e:
                    return None, str(e)  # Return no URL and the error message
            
            # Execute the blocking call in a thread pool
            image_url, error = await asyncio.to_thread(generate_image_sync)
            
            if error:
                self.logger.error(f"Error generating DALL-E image: {error}")
                # Return a placeholder image with the error message
                return f"https://placehold.co/1024x1024/gray/white?text=API+Error:+{error.replace(' ', '+')[:80]}"
                
            if not image_url:
                self.logger.error("DALL-E returned no image URL")
                return "https://placehold.co/1024x1024/gray/white?text=No+Image+URL+Returned"
                
            return image_url
            
        except Exception as e:
            self.log_api_error("OpenAI DALL-E", e, "generate_image")
            return f"https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed:+{str(e).replace(' ', '+')[:80]}" 