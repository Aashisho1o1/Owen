"""
Fiction Template Router
Handles all fiction template-related endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

# Import services
from services.fiction_templates import fiction_template_service
from models.schemas import FictionTemplate, DocumentType

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/fiction-templates",
    tags=["fiction-templates"],
)

# Create a secondary router for backward compatibility with old /api/templates endpoint
legacy_router = APIRouter(
    prefix="/api/templates",
    tags=["templates"],
)

@router.get("", response_model=List[FictionTemplate])
async def get_fiction_templates(
    category: Optional[str] = Query(None, description="Filter by template category"),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    search: Optional[str] = Query(None, description="Search templates by name, description, or tags")
):
    """Get all fiction writing templates with optional filtering"""
    try:
        templates = fiction_template_service.get_all_templates()
        
        # Apply filters
        if category:
            templates = [t for t in templates if t.category == category]
        
        if document_type:
            templates = [t for t in templates if t.document_type == document_type]
        
        if search:
            templates = fiction_template_service.search_templates(search)
        
        return templates
        
    except Exception as e:
        logger.error(f"Error fetching fiction templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")

@router.get("/categories")
async def get_template_categories():
    """Get all available template categories"""
    try:
        categories = fiction_template_service.get_categories()
        return {"categories": sorted(categories)}
    except Exception as e:
        logger.error(f"Error fetching template categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/{template_id}", response_model=FictionTemplate)
async def get_fiction_template(template_id: str):
    """Get a specific fiction template by ID"""
    try:
        template = fiction_template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch template")

@router.get("/category/{category}", response_model=List[FictionTemplate])
async def get_templates_by_category(category: str):
    """Get all templates in a specific category"""
    try:
        templates = fiction_template_service.get_templates_by_category(category)
        return templates
    except Exception as e:
        logger.error(f"Error fetching templates for category {category}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")

@router.get("/type/{document_type}", response_model=List[FictionTemplate])
async def get_templates_by_document_type(document_type: DocumentType):
    """Get all templates for a specific document type"""
    try:
        templates = fiction_template_service.get_templates_by_document_type(document_type)
        return templates
    except Exception as e:
        logger.error(f"Error fetching templates for document type {document_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")

# =============================================================================
# LEGACY ENDPOINTS - Backward compatibility with old /api/templates
# =============================================================================

@legacy_router.get("")
async def get_legacy_templates():
    """Get basic templates for backward compatibility"""
    try:
        # Return a subset of fiction templates formatted as basic templates
        all_templates = fiction_template_service.get_all_templates()
        
        # Convert to legacy format
        legacy_templates = [
            {
                "id": "blank",
                "title": "Blank Document",
                "description": "Start with a clean slate",
                "content": "",
                "category": "General"
            },
            {
                "id": "novel",
                "title": "Novel",
                "description": "Template for novel writing",
                "content": next((t.content for t in all_templates if t.id == "novel-template"), ""),
                "category": "Fiction"
            },
            {
                "id": "character",
                "title": "Character Profile",
                "description": "Template for character development",
                "content": next((t.content for t in all_templates if t.id == "character-profile-basic"), ""),
                "category": "Fiction"
            }
        ]
        
        return legacy_templates
        
    except Exception as e:
        logger.error(f"Error fetching legacy templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch templates")

@legacy_router.get("/{template_id}")
async def get_legacy_template(template_id: str):
    """Get a specific legacy template by ID"""
    try:
        # Handle legacy template IDs
        if template_id == "blank":
            return {
                "id": "blank",
                "title": "Blank Document",
                "description": "Start with a clean slate",
                "content": "",
                "category": "General"
            }
        elif template_id == "novel":
            template = fiction_template_service.get_template_by_id("novel-template")
            if template:
                return {
                    "id": "novel",
                    "title": "Novel",
                    "description": "Template for novel writing",
                    "content": template.content,
                    "category": "Fiction"
                }
        elif template_id == "character":
            template = fiction_template_service.get_template_by_id("character-profile-basic")
            if template:
                return {
                    "id": "character",
                    "title": "Character Profile",
                    "description": "Template for character development",
                    "content": template.content,
                    "category": "Fiction"
                }
        
        # If not found, try to find in fiction templates
        fiction_template = fiction_template_service.get_template_by_id(template_id)
        if fiction_template:
            return {
                "id": fiction_template.id,
                "title": fiction_template.name,
                "description": fiction_template.description,
                "content": fiction_template.content,
                "category": fiction_template.category
            }
        
        raise HTTPException(status_code=404, detail="Template not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching legacy template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch template") 