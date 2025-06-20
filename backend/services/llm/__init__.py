"""
LLM Services package
"""
from typing import Dict, Type, Optional
import logging

from services.llm.base_service import BaseLLMService, LLMError
from services.llm.gemini_service import gemini_service
from services.llm.openai_service import openai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_services")

# Available LLM services registry
LLM_SERVICES = {
    "gemini": gemini_service,
    "openai": openai_service,
}

def get_llm_service(service_name: str) -> Optional[BaseLLMService]:
    """Get LLM service by name"""
    return LLM_SERVICES.get(service_name.lower()) 