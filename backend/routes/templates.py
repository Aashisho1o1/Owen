"""
Simple Templates API for DOG Writer
Ultra minimal template system.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_templates():
    """Get document templates - no auth required, ultra simple"""
    return [
        {
            "id": "blank",
            "name": "Blank Document",
            "content": "",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Start with a blank document"
        },
        {
            "id": "novel",
            "name": "Novel",
            "content": "Chapter 1\n\n",
            "document_type": "novel", 
            "is_system": True,
            "preview_text": "Basic novel template with chapter structure"
        },
        {
            "id": "short-story",
            "name": "Short Story",
            "content": "# Title\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Short story template"
        },
        {
            "id": "romance",
            "name": "Romance Novel",
            "content": "# Romance Novel\n\nChapter 1\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Romance novel template with romantic elements"
        },
        {
            "id": "fantasy", 
            "name": "Fantasy Epic",
            "content": "# Fantasy Epic\n\nChapter 1: The Beginning\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Fantasy template for epic adventures"
        },
        {
            "id": "thriller",
            "name": "Thriller",
            "content": "# Thriller\n\nChapter 1: The Hook\n\n",
            "document_type": "novel",
            "is_system": True,
            "preview_text": "Thriller template for suspenseful stories"
        }
    ] 