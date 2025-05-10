"""
Base service for LLM interactions with common functionality
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List, Optional
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_service")

class BaseLLMService(ABC):
    """
    Abstract base class for LLM service providers
    
    This defines the common interface that all LLM services should implement.
    """
    def __init__(self):
        """Initialize with environment variables"""
        # Ensure environment variables are loaded
        load_dotenv()
        self.logger = logger
        
        # Track initialization status
        self.initialized = False
        
    @abstractmethod
    async def generate_text(self, prompt: Union[str, List[Dict[str, Any]]], **kwargs) -> Union[str, Dict[str, Any]]:
        """
        Generate text based on the provided prompt
        
        Args:
            prompt: Either a string prompt or a structured prompt (list of dictionaries)
            kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text or a dictionary containing generated text and metadata
        """
        pass
    
    @staticmethod
    def clean_json_response(response_text: str) -> str:
        """
        Clean a response that might contain JSON in markdown format
        
        Args:
            response_text: The raw response text
            
        Returns:
            Cleaned JSON string
        """
        if not response_text:
            return ""
            
        cleaned_text = response_text.strip()
        
        # Handle markdown code blocks
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]  # Remove ```
            
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]  # Remove closing ```
            
        return cleaned_text.strip()
        
    def log_api_error(self, provider: str, error: Exception, context: str = "") -> None:
        """
        Log API errors consistently
        
        Args:
            provider: The LLM provider name
            error: The exception
            context: Additional context about the operation
        """
        self.logger.error(f"{provider} API Error{' in ' + context if context else ''}: {str(error)}")
        
    def get_env_var(self, name: str, required: bool = False) -> Optional[str]:
        """
        Get environment variable with proper error handling
        
        Args:
            name: Environment variable name
            required: Whether the variable is required
            
        Returns:
            The environment variable value or None if not found
            
        Raises:
            ValueError: If required is True and the variable is not found
        """
        value = os.getenv(name)
        if required and not value:
            error_msg = f"Required environment variable {name} not found"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not value:
            self.logger.warning(f"Environment variable {name} not found")
            
        return value 