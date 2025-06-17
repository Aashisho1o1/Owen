"""
LLM Services package
"""
from typing import Dict, Type, Optional
import logging

from services.llm.base_service import BaseLLMService
from services.llm.gemini_service import GeminiService
from services.llm.dalle_service import DalleService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_services")

# Service registry
SERVICE_REGISTRY: Dict[str, Type[BaseLLMService]] = {
    "gemini": GeminiService,
    "dalle": DalleService,
    # Add other services as they are implemented
}

# Service instances cache
_service_instances: Dict[str, BaseLLMService] = {}

def get_llm_service(service_name: str) -> Optional[BaseLLMService]:
    """
    Get a specific LLM service instance
    
    Args:
        service_name: Name of the service to get
        
    Returns:
        The service instance or None if not found
    """
    # Check if we already have an instance
    if service_name in _service_instances:
        return _service_instances[service_name]
        
    # Check if we know how to create this service
    if service_name not in SERVICE_REGISTRY:
        logger.error(f"Unknown LLM service: {service_name}")
        return None
        
    # Create a new instance
    try:
        service_class = SERVICE_REGISTRY[service_name]
        service_instance = service_class()
        _service_instances[service_name] = service_instance
        return service_instance
    except Exception as e:
        logger.error(f"Error creating LLM service {service_name}: {str(e)}")
        return None 