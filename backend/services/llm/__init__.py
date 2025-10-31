"""
LLM Services package - Google AI Competition Edition
Simplified to use only Google Gemini
"""
from typing import Dict, Type, Optional
import logging

from services.llm.base_service import BaseLLMService, LLMError
from services.llm.gemini_service import gemini_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_services")

# Available LLM services registry - Gemini only for competition
LLM_SERVICES = {
    "gemini": gemini_service,
}

def get_llm_service(service_name: str) -> Optional[BaseLLMService]:
    """Get LLM service by name"""
    return LLM_SERVICES.get(service_name.lower()) 