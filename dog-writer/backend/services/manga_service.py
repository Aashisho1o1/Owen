"""
Manga script and image generation service
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from models.schemas import MangaPage
from services.llm import get_llm_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manga_service")

class MangaService:
    """
    Service for generating manga scripts and images
    """
    def __init__(self):
        """Initialize the manga service"""
        # Get LLM service (Gemini for script generation)
        self.gemini_service = get_llm_service("gemini")
        
        # Get DALL-E service for image generation
        self.dalle_service = get_llm_service("dalle")
        
        # Track if services are available
        self.is_script_service_available = self.gemini_service is not None
        self.is_image_service_available = self.dalle_service is not None
        
        if not self.is_script_service_available:
            logger.error("Manga service initialization failed: Script generation service unavailable")
        if not self.is_image_service_available:
            logger.warning("Manga service initialized without image generation capability")
    
    async def generate_manga_script(self, story_text: str, author_persona_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a structured manga script from story text
        
        Args:
            story_text: The story text to adapt
            author_persona_data: Author persona information to influence generation
            
        Returns:
            Structured manga script data or None on failure
        """
        if not self.is_script_service_available:
            logger.error("Cannot generate manga script: Script service unavailable")
            return None
            
        persona_name = author_persona_data.get('name', "the author")
        
        manga_script_prompt = f"""
        You are a master manga scriptwriter. Your task is to convert the following story text into a structured manga script. 
        The script should be for a single page with 2 to 3 panels. 
        For each panel, describe the scene, character actions/expressions, and any dialogue.
        Also, provide a brief description for any distinct characters mentioned, which will be used for image generation. 
        Characters should be named. If names aren't in the story, invent plausible ones.

        Output the script in JSON format with the following structure:
        {{ 
            "title": "[A concise title for the manga page]",
            "page_number": 1,
            "character_designs": {{ 
                "CharacterName1": "[Brief visual description, e.g., 'Young man, tall, spiky blonde hair, wearing a red jacket']",
                "CharacterName2": "[Brief visual description]".
                // ... more characters if present
            }},
            "panels": [
                {{
                    "panel_number": 1,
                    "description": "[Detailed visual description of the scene, setting, character actions, and expressions. E.g., 'Close up on CharacterName1's face, looking shocked. Background is a dimly lit alleyway.']",
                    "dialogue": [
                        {{"character": "CharacterName1", "speech": "What was that?!"}},
                        {{"character": "Narrator", "speech": "A sudden noise startled him."}} // Use "Narrator" for captions
                    ]
                }},
                {{
                    "panel_number": 2,
                    "description": "[Scene description for panel 2]",
                    "dialogue": [
                        {{"character": "CharacterName2", "speech": "I've been waiting for you."}}
                    ]
                }}
                // Add a third panel if it makes sense for the story flow.
            ]
        }}

        Story Text to Convert:
        ------------------------
        {story_text}
        ------------------------

        Remember to stick to the JSON format exactly. Ensure character names used in panels and dialogue match those in character_designs.
        """
        
        try:
            # Using Gemini to generate structured script
            response_json_str = await self.gemini_service.generate_text(manga_script_prompt)
            
            if not response_json_str or not isinstance(response_json_str, str):
                logger.error(f"Manga script generation failed: Invalid response type: {type(response_json_str)}")
                return None
                
            # Clean the response
            cleaned_json_str = self.gemini_service.clean_json_response(response_json_str)
            
            # Parse JSON
            script_data = json.loads(cleaned_json_str)
            
            # Basic validation
            if "panels" not in script_data or "character_designs" not in script_data:
                logger.error(f"Manga script validation failed: Missing key fields. Got: {script_data}")
                # Fallback for error cases
                return {
                    "title": "Script Error", 
                    "page_number": 1, 
                    "character_designs": {}, 
                    "panels": [{
                        "panel_number": 1, 
                        "description": "Error: Could not generate script structure.", 
                        "dialogue": [{
                            "character": "Error", 
                            "speech": cleaned_json_str[:500]
                        }]
                    }]
                }
                
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding manga script JSON: {e}")
            logger.error(f"Raw response (first 500 chars): {response_json_str[:500] if isinstance(response_json_str, str) else 'Invalid type'}")
            return {
                "title": "JSON Decode Error", 
                "page_number": 1, 
                "character_designs": {}, 
                "panels": [{
                    "panel_number": 1, 
                    "description": f"Error: Malformed JSON. {str(e)}", 
                    "dialogue": [{
                        "character": "Error", 
                        "speech": response_json_str[:500] if isinstance(response_json_str, str) else 'Raw response was not a string.'
                    }]
                }]
            }
        except Exception as e:
            logger.error(f"Error generating manga script: {e}")
            return None
            
    async def generate_panel_image(self, panel_description: str, character_descriptions: Dict[str, str], 
                                   panel_style: str = "monochrome manga, clean lines, dynamic action, high contrast") -> str:
        """
        Generate an image for a manga panel
        
        Args:
            panel_description: Description of the panel scene
            character_descriptions: Dictionary of character descriptions
            panel_style: Style guidelines for the image
            
        Returns:
            URL to the generated image or a placeholder on failure
        """
        if not self.is_image_service_available:
            logger.warning("Cannot generate panel image: Image service unavailable")
            return "https://placehold.co/1024x1024/gray/white?text=Image+Generation+Unavailable"
            
        # Combine character descriptions for the prompt
        char_details = "; ".join([f"{name}: {desc}" for name, desc in character_descriptions.items()])
        full_prompt = f"{panel_description}. Characters involved: {char_details}. Style: {panel_style}."
        
        logger.info(f"Generating panel image with prompt: {full_prompt[:100]}...")
        
        try:
            # Use DALL-E service to generate the image
            image_url = await self.dalle_service.generate_image(full_prompt)
            
            if not image_url:
                logger.error("Failed to generate panel image: No URL returned")
                return "https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed"
                
            return image_url
            
        except Exception as e:
            logger.error(f"Error generating panel image: {e}")
            return f"https://placehold.co/1024x1024/gray/white?text=Image+Generation+Error:+{str(e).replace(' ', '+')[:80]}"
            
    async def generate_complete_manga_page(self, story_text: str, author_persona_data: Dict[str, Any]) -> Tuple[Optional[MangaPage], List[str]]:
        """
        Generate a complete manga page with script and images
        
        Args:
            story_text: The story text to adapt
            author_persona_data: Author persona information
            
        Returns:
            Tuple of (manga page data or None, list of error messages)
        """
        errors = []
        
        # Generate script
        script_data = await self.generate_manga_script(story_text, author_persona_data)
        if not script_data:
            errors.append("Failed to generate manga script")
            return None, errors
            
        # Create manga page from script data
        try:
            manga_page_data = MangaPage(**script_data)
        except Exception as e:
            errors.append(f"Error creating manga page from script data: {str(e)}")
            return None, errors
            
        # Generate images for each panel
        panel_image_errors = []
        for panel_data in manga_page_data.panels:
            try:
                image_url = await self.generate_panel_image(
                    panel_description=panel_data.description,
                    character_descriptions=manga_page_data.character_designs
                )
                
                panel_data.image_url = image_url
                
                if "placehold.co" in image_url:
                    error_msg = f"Panel {panel_data.panel_number} returned a placeholder image"
                    panel_image_errors.append(error_msg)
            except Exception as e:
                error_msg = f"Panel {panel_data.panel_number} image generation failed: {str(e)}"
                panel_image_errors.append(error_msg)
                panel_data.image_url = "https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed"
                
        if panel_image_errors:
            errors.extend(panel_image_errors)
            
        return manga_page_data, errors 