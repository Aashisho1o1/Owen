"""
# REFACTORING PLAN

This file should be reorganized by splitting routes into separate modules:

1. `main.py` - Core app initialization, CORS setup, main imports
2. `routers/chat_router.py` - Chat-related endpoints
3. `routers/manga_router.py` - Manga generation endpoints
4. `routers/checkpoint_router.py` - Checkpoint/save functionality

Implementation plan:
1. Create a 'routers' directory
2. Move each set of related routes to their own file
3. Use FastAPI's APIRouter for modular routing
4. Import and include routers in main.py

Example structure:
```python
# In routers/chat_router.py
from fastapi import APIRouter, Depends
router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Existing chat logic...

# In main.py
from routers import chat_router, manga_router
app = FastAPI()
app.include_router(chat_router.router)
app.include_router(manga_router.router)
```

This approach improves:
- Code organization
- Testability
- Maintainability
- Readability
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio # For running image generation concurrently

# Convert relative imports to absolute imports
from models.schemas import CheckpointRequest, MangaStoryRequest, MangaScriptResponse, MangaPage
from services.llm_service import LLMService
from services.persona_service import create_writer_persona
from routers import chat_router, voice_router # MODIFIED: Added voice_router

# Initialize LLM Service (this will handle API key loading via its own load_dotenv)
# This instance can be made available to routers via dependency injection if needed,
# or routers can instantiate their own if they are self-contained.
# For now, chat_router.py instantiates its own LLMService.
# llm_service = LLMService() # Commented out as chat_router instantiates its own for now

app = FastAPI()

# Configure CORS - Ensure all origins are allowed for development
origins = [
    "http://localhost:5173",  # Default Vite port
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:5176",
    "http://localhost:8001" # Added for the backend itself if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router
app.include_router(chat_router.router)
app.include_router(voice_router.router) # NEW: Include the voice router

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# The original /api/chat endpoint has been moved to routers/chat_router.py
# So, it is removed from here.

@app.post("/api/checkpoint")
async def create_checkpoint(request: CheckpointRequest):
    print("Checkpoint data received:")
    print(f"Editor text: {request.editor_text[:100]}...")
    print(f"Chat history length: {len(request.chat_history)} messages")
    return {"status": "success", "message": "Checkpoint saved successfully"}

@app.post("/api/manga/generate_script", response_model=MangaScriptResponse)
async def generate_manga_from_story(request: MangaStoryRequest):
    try:
        print(f"Received manga generation request for persona: {request.author_persona}")
        author_persona_data = create_writer_persona(request.author_persona)
        if not author_persona_data:
             author_persona_data = {"name": request.author_persona, "voice": "default"}

        # Instantiate LLMService here; consider dependency injection for better management
        current_llm_service = LLMService() 

        script_data_dict = await current_llm_service.generate_manga_script(request.story_text, author_persona_data)

        if not script_data_dict or "panels" not in script_data_dict or "character_designs" not in script_data_dict:
            print(f"Failed to generate valid manga script. Data: {script_data_dict}")
            error_message = "Failed to generate a valid manga script structure from the story."
            if isinstance(script_data_dict, dict) and script_data_dict.get("panels") and isinstance(script_data_dict["panels"], list) and script_data_dict["panels"][0].get("dialogue"):
                error_message = script_data_dict["panels"][0]["dialogue"][0].get("speech", error_message)
            return MangaScriptResponse(error=error_message)

        manga_page_data = MangaPage(**script_data_dict)

        panel_image_urls = []
        image_generation_errors = []
        for panel_data in manga_page_data.panels:
            print(f"Generating image for panel {panel_data.panel_number}...")
            image_url = await current_llm_service.generate_panel_image_with_dalle(
                panel_description=panel_data.description,
                character_descriptions=manga_page_data.character_designs
            )
            panel_image_urls.append(image_url)
            
            if image_url and "placehold.co" in image_url:
                error_msg = f"Panel {panel_data.panel_number} returned a placeholder image: {image_url}"
                print(error_msg)
                image_generation_errors.append(error_msg)

        if image_generation_errors:
            print(f"WARNING: {len(image_generation_errors)} panels had image generation issues")

        for i, panel_model in enumerate(manga_page_data.panels):
            panel_model.image_url = panel_image_urls[i]
            if not panel_image_urls[i]:
                print(f"Warning: Failed to generate image for panel {panel_model.panel_number}")
                panel_model.image_url = "https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed"

        if image_generation_errors:
            return MangaScriptResponse(
                manga_page=manga_page_data,
                warning=f"Some panels had image generation issues: {'; '.join(image_generation_errors)}"
            )
        return MangaScriptResponse(manga_page=manga_page_data)

    except Exception as e:
        print(f"General error in /api/manga/generate_script: {e}")
        import traceback
        traceback.print_exc()
        return MangaScriptResponse(error=f"An unexpected error occurred during manga generation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # When running main.py directly, this tells Uvicorn to load 'app' from the 'main' module (this file).
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 