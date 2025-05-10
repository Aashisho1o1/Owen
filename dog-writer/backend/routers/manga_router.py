from fastapi import APIRouter, HTTPException, Depends
import traceback

from models.schemas import MangaStoryRequest, MangaScriptResponse
from services.manga_service import MangaService
from services.persona_service import create_writer_persona

router = APIRouter(prefix="/api/manga", tags=["manga"])

# Dependency for MangaService
def get_manga_service():
    return MangaService()

@router.post("/generate_script", response_model=MangaScriptResponse)
async def generate_manga_from_story(
    request: MangaStoryRequest,
    manga_service: MangaService = Depends(get_manga_service)
):
    """
    Generate a manga script and images from a story text
    """
    try:
        print(f"Received manga generation request for persona: {request.author_persona}")
        
        # Get author persona data
        author_persona_data = create_writer_persona(request.author_persona)
        if not author_persona_data:
            author_persona_data = {"name": request.author_persona, "voice": "default"}

        # Generate complete manga page with script and images
        manga_page_data, errors = await manga_service.generate_complete_manga_page(
            request.story_text, author_persona_data
        )
        
        if not manga_page_data:
            error_message = "Failed to generate manga page."
            if errors:
                error_message += f" Errors: {'; '.join(errors)}"
            return MangaScriptResponse(error=error_message)
            
        # Return the generated manga page and any warnings
        if errors:
            return MangaScriptResponse(
                manga_page=manga_page_data,
                warning=f"Some issues occurred during generation: {'; '.join(errors)}"
            )
            
        return MangaScriptResponse(manga_page=manga_page_data)

    except Exception as e:
        print(f"General error in manga generation: {e}")
        traceback.print_exc()
        return MangaScriptResponse(error=f"An unexpected error occurred during manga generation: {str(e)}")
