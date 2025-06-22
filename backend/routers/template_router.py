"""
Template Router
Handles all template-related endpoints.
Extracted from main.py as part of God File refactoring.
"""

import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/templates",
    tags=["templates"],
)

# Story Writing Templates - Essential templates only
# TODO: Move this to a proper service or database
templates_store = [
    {
        "id": "blank",
        "title": "Blank Document",
        "description": "Start with a clean slate",
        "content": "",
        "category": "General"
    },
    {
        "id": "story",
        "title": "Short Story",
        "description": "Template for creative writing and storytelling",
        "content": "",
        "category": "Fiction"
    },
    {
        "id": "essay",
        "title": "Essay",
        "description": "Template for essays and articles",
        "content": "",
        "category": "Non-Fiction"
    }
]

@router.get("")
async def get_templates():
    """Get all available templates"""
    return templates_store

@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = next((t for t in templates_store if t['id'] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template 
 