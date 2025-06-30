"""
Backend services package

This package contains:
- LLM services for different providers
- Voice processing services
- Manga generation services
- User persona services
"""

# This file can be empty, but its presence makes this directory a Python package. 

# Import fiction template service
from .fiction_templates import FictionTemplateService

# Create global instances
fiction_template_service = FictionTemplateService() 