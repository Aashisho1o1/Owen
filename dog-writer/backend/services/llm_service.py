"""
# REFACTORING PLAN

This file is too large and should be split into these specialized modules:

1. `base_llm_service.py` - Base class with common functionality and API key loading
2. `openai_service.py` - OpenAI-specific functionality, including DALL-E image generation
3. `gemini_service.py` - Google Gemini-specific functionality 
4. `anthropic_service.py` - Anthropic/Claude-specific functionality
5. `manga_service.py` - Manga-specific generation functionality

The relationship would be:
- BaseLLMService (abstract base class)
  |- OpenAIService
  |- GeminiService  
  |- AnthropicService
- MangaService (uses the LLM services)

Benefits:
- Single responsibility principle: Each service handles one LLM provider
- Easier testing: Test each service independently
- Better error isolation: Issues in one service don't affect others
- Improved readability: Smaller files are easier to understand
- Easier maintenance: Changes to one provider don't risk breaking others
"""

import os
import json
import google.generativeai as genai
import anthropic
import openai
import asyncio  # Added for to_thread
from dotenv import load_dotenv
from typing import Union, Dict, Any, List, Tuple  # Added Tuple for error return

# Load environment variables
load_dotenv() # Ensures .env is loaded when this module is imported

class LLMService:
    def __init__(self):
        # Set up Gemini API
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            # Consider logging this instead of raising an error immediately if one LLM failing is acceptable
            raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY in .env file.")
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')

        # Set up Anthropic API
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = None
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            print("Warning: No Anthropic API key found. Claude model will not be available.")

        # Set up OpenAI API
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("Warning: No OpenAI API key found. DALL-E image generation will not be available.")
            self.openai_client = None
        else:
            # Print first few characters of the key to verify it's loaded (don't print the full key!)
            print(f"OpenAI API key loaded: {self.openai_api_key[:5]}...")
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            # Test API connection (optional - can be removed later)
            try:
                # Just get the list of models to verify API connection
                self.openai_client.models.list()
                print("✓ OpenAI API connection successful")
            except Exception as e:
                print(f"⚠️ OpenAI API connection test failed: {e}")

    async def generate_panel_image_with_dalle(self, panel_description: str, character_descriptions: Dict[str, str], panel_style: str = "monochrome manga, clean lines, dynamic action, high contrast") -> Union[str, None]:
        """Generates an image for a manga panel using DALL-E 3."""
        if not self.openai_client:
            print("Error: OpenAI client not initialized. Cannot generate DALL-E image.")
            # Return a placeholder/error image URL instead of None
            return "https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed:+No+API+Key" 
        
        # Combine character descriptions into the prompt for better consistency
        # E.g., "Aiko: a young woman with short black hair and a determined expression."
        char_details_for_prompt = "; ".join([f"{name}: {desc}" for name, desc in character_descriptions.items()])
        
        full_prompt = f"{panel_description}. Characters involved: {char_details_for_prompt}. Style: {panel_style}."
        
        print(f"DALL-E Prompt: {full_prompt}") # For debugging

        try:
            # Run the synchronous OpenAI client in a separate thread to avoid blocking
            # the event loop in this async function
            def generate_image():
                try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024", # Standard DALL-E 3 size
                quality="standard", # Can be "hd" for higher quality but more cost
                n=1,
                response_format="url" # Get a URL to the image
            )
                    return response.data[0].url, None  # Return URL and no error
                except Exception as e:
                    return None, str(e)  # Return no URL and the error message
            
            # Execute the blocking call in a thread pool
            image_url, error = await asyncio.to_thread(generate_image)
            
            if error:
                # If there was an error, log it
                print(f"Error generating DALL-E image: {error}")
                # Return a placeholder image with the error message
                return f"https://placehold.co/1024x1024/gray/white?text=API+Error:+{error.replace(' ', '+')[:80]}"
                
            if not image_url:
                print("Error: DALL-E returned no image URL")
                return "https://placehold.co/1024x1024/gray/white?text=No+Image+URL+Returned"
                
            return image_url
        except Exception as e:
            print(f"Error generating DALL-E image: {e}")
            return f"https://placehold.co/1024x1024/gray/white?text=Image+Generation+Failed:+{str(e).replace(' ', '+')[:80]}"

    async def generate_manga_script(self, story_text: str, author_persona_data: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """Generates a structured manga script from story text using an LLM (Gemini)."""
        
        # We can refine this prompt to be more specific about desired output structure.
        # For a PoC, we'll aim for a simple structure: one page, 2-3 panels.
        # The persona_data can be used to influence character naming or style if desired.
        
        persona_name = "the author" # Fallback
        if isinstance(author_persona_data, dict) and author_persona_data.get('voice'): # Crude check for valid persona
            # This assumes author_persona_data has a 'name' or similar key we can extract for the prompt.
            # For now, let's just use a generic reference or allow the LLM to infer from style.
            # Or, if persona_service.create_writer_persona returns the name in a predictable way:
            # persona_name = author_persona_data.get('name', "the author") # Assuming a 'name' key in persona dict
            pass # Persona style is implicitly in the story_text or could be added to system prompt

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
        
        # Using Gemini for structured JSON output, as it's already configured.
        # The prompt to `generate_with_selected_llm` for Gemini needs to be in List[Dict] format.
        gemini_structured_prompt = [
            # System prompt could be added here if desired, but the main instructions are in the user prompt for JSON.
            {"role": "user", "parts": [manga_script_prompt]}
        ]

        try:
            # Assuming generate_with_selected_llm with Gemini returns a JSON string directly
            response_json_str = await self.generate_with_selected_llm(gemini_structured_prompt, "Google Gemini")
            
            if not response_json_str or not isinstance(response_json_str, str):
                print(f"Manga script generation failed: LLM returned invalid data type: {type(response_json_str)}")
                return None
            
            # Clean the response if it's wrapped in markdown code blocks
            cleaned_json_str = response_json_str.strip()
            if cleaned_json_str.startswith("```json"):
                cleaned_json_str = cleaned_json_str[7:]
            if cleaned_json_str.startswith("```"):
                cleaned_json_str = cleaned_json_str[3:]
            if cleaned_json_str.endswith("```"):
                cleaned_json_str = cleaned_json_str[:-3]
            cleaned_json_str = cleaned_json_str.strip()

            script_data = json.loads(cleaned_json_str)
            # Basic validation (can be expanded)
            if "panels" not in script_data or "character_designs" not in script_data:
                print(f"Manga script validation failed: Missing key fields. Got: {script_data}")
                # Fallback: try to extract at least dialogue if possible
                return { "title": "Script Error", "page_number": 1, "character_designs": {}, "panels": [{"panel_number":1, "description": "Error: Could not generate script structure.", "dialogue":[{"character":"Error", "speech": cleaned_json_str[:500]}]}]}
            return script_data
        except json.JSONDecodeError as e:
            print(f"Error decoding manga script JSON from LLM: {e}")
            print(f"LLM Raw Response for script (first 500 chars): {response_json_str[:500] if isinstance(response_json_str, str) else 'Invalid response type'}")
            return { "title": "JSON Decode Error", "page_number": 1, "character_designs": {}, "panels": [{"panel_number":1, "description": f"Error: Malformed JSON from LLM. {str(e)}", "dialogue":[{"character":"Error", "speech": response_json_str[:500] if isinstance(response_json_str, str) else 'Raw response was not a string.'}]}]}
        except Exception as e:
            print(f"Error generating manga script: {e}")
            return None

    async def generate_with_selected_llm(self, prompt: Union[str, List[Dict[str, Any]]], llm_provider: str) -> Union[str, Dict[str, Any]]:
        """Generate content using the selected LLM provider."""
        if llm_provider == "Google Gemini" or not llm_provider: # Default to Gemini
            try:
                # Ensure prompt is in the correct format for Gemini (List[Dict])
                if not isinstance(prompt, list):
                    # This case should ideally be handled by the caller preparing the prompt correctly.
                    # For now, if it's a string, we might need to adapt it or log an error.
                    print(f"Warning: Gemini prompt received as string, expected List[Dict]. Prompt: {str(prompt)[:100]}...")
                    # Fallback or specific error handling if prompt is just a string for Gemini
                    # For now, let's assume the caller (main.py) will format it correctly.
                    # If it must handle a string, it might need to be wrapped: e.g., [{"role": "user", "parts": [prompt]}]
                    # However, the main chat function prepares it as a list of dicts.
                    pass # Assuming prompt is already correctly formatted by the caller as List[Dict]

                response = self.gemini_model.generate_content(prompt)
                
                if response.candidates and len(response.candidates) > 0 and \
                   response.candidates[0].content and response.candidates[0].content.parts and \
                   len(response.candidates[0].content.parts) > 0:
                    
                    full_text_response = ""
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and isinstance(part.text, str):
                            full_text_response += part.text
                    
                    if not full_text_response.strip():
                        feedback_info = ""
                        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and \
                           hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                            feedback_info = f" Reason: {response.prompt_feedback.block_reason} Message: {getattr(response.prompt_feedback, 'block_reason_message', '')}"
                        elif hasattr(response, 'candidates') and response.candidates and \
                             hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != 'STOP':
                             feedback_info = f" Finish Reason: {response.candidates[0].finish_reason}"
                        print(f"Gemini API Error: Response received, but no text content found.{feedback_info}")
                        return json.dumps({
                            "dialogue_response": f"Error: Gemini returned an empty or non-text response.{feedback_info}",
                            # "reasoning": "The response from Gemini did not contain usable text." # Reasoning removed
                        })
                    return full_text_response # This is the JSON string
                else:
                    feedback_info = ""
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback and \
                       hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                        feedback_info = f" Reason: {response.prompt_feedback.block_reason}. Message: {getattr(response.prompt_feedback, 'block_reason_message', '')}."
                    elif hasattr(response, 'candidates') and response.candidates and \
                         hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason != 'STOP':
                         feedback_info = f" Finish Reason: {response.candidates[0].finish_reason}."
                    else:
                        feedback_info = " Unknown reason for empty/invalid response."
                    print(f"Gemini API Error: No valid candidates or content parts in response.{feedback_info}")
                    return json.dumps({
                        "dialogue_response": f"Error: Gemini returned no valid response content.{feedback_info}",
                        # "reasoning": "The response from Gemini was empty, filtered, or malformed." # Reasoning removed
                    })
            except Exception as e:
                print(f"Error calling Gemini API or processing its response: {e}")
                return json.dumps({
                    "dialogue_response": f"Error: {str(e)}",
                    # "reasoning": "There was an error processing your request with Gemini." # Reasoning removed
                })
        
        elif llm_provider == "Anthropic Claude":
            if not self.anthropic_client:
                print("Error: Anthropic client not available for Claude, API key might be missing or invalid.")
                error_text_content = json.dumps({
                    "dialogue_response": "Error: Claude (Anthropic) API client is not configured. Please check server logs and API key.",
                    # "reasoning": "Configuration error." # Reasoning removed
                })
                return {
                    "text": error_text_content,
                    "thinking_trail": "Anthropic client not initialized. API key may be missing or invalid."
                }
            
            try:
                message_content = prompt # Claude expects a string or a list/dict (already handled by caller)
                                
                response = self.anthropic_client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=16000,
                    temperature=1,
                    thinking={"type": "enabled", "budget_tokens": 8000},
                    system="You are an AI writing assistant embodying the style and voice of famous authors. Format your response as JSON with 'dialogue_response' field.", # Removed reasoning from system prompt
                    messages=[
                        {"role": "user", "content": message_content}
                    ]
                )
                
                extracted_dialogue_json_text = ""
                thinking_trail_parts = []

                if response.content and isinstance(response.content, list):
                    for block in response.content:
                        if hasattr(block, 'type'):
                            if block.type == "text":
                                if hasattr(block, 'text'):
                                    extracted_dialogue_json_text += block.text
                            elif block.type == "thinking":
                                if hasattr(block, 'thinking') and isinstance(block.thinking, str):
                                    thinking_trail_parts.append(block.thinking)
                            elif block.type == "redacted_thinking":
                                thinking_trail_parts.append("[Claude's reasoning was redacted for safety.]")
                
                thinking_trail = "\\n".join(thinking_trail_parts)
                
                return {
                    "text": extracted_dialogue_json_text,
                    "thinking_trail": thinking_trail
                }
            except Exception as e:
                print(f"Error calling Claude API: {e}")
                error_text_content = json.dumps({
                    "dialogue_response": f"Error: {str(e)}",
                    # "reasoning": "There was an error processing your request with Claude." # Reasoning removed
                })
                return {
                    "text": error_text_content,
                    "thinking_trail": f"Claude API Error: {str(e)}"
                }
        else:
            print(f"Error: Unknown LLM provider selected: {llm_provider}")
            error_text_content = json.dumps({
                "dialogue_response": f"Error: Unknown LLM provider selected: '{llm_provider}'.",
                # "reasoning": "Invalid configuration." # Reasoning removed
            })
            return {
                "text": error_text_content,
                "thinking_trail": f"Unknown LLM provider: '{llm_provider}'."
            } 

    async def organize_dictated_text(self, transcribed_text: str) -> dict:
        """
        Organizes transcribed text using an LLM for simple categorization or summarization.
        This method uses the OpenAI client as an example. Adapt if using another client for this.
        """
        if not self.openai_client: # Check if the client for this task is available
            print("OpenAI client (for organization) not initialized. Cannot organize text.")
            return {"error": "LLM client for organization not available"}

        try:
            prompt_instructions = """Organize the following dictated text from a writer.
Provide a very brief one-sentence summary and suggest a category (e.g., 'Plot Idea', 'Character Note', 'Dialogue Snippet', 'World-Building', 'General Thought').
Output in JSON format with keys "summary" and "category".
Example: {"summary": "The protagonist discovers a hidden compartment in the old desk.", "category": "Plot Idea"}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo", # Or your preferred model
                messages=[
                    {"role": "system", "content": prompt_instructions},
                    {"role": "user", "content": f"Dictated Text: \"{transcribed_text}\""}
                ],
                response_format={ "type": "json_object" }
            )
            
            organized_content_str = response.choices[0].message.content
            import json # Make sure to import json
            return json.loads(organized_content_str)

        except Exception as e:
            print(f"Error organizing text with OpenAI LLM: {e}")
            # In a real app, you might return the original text or a more specific error
            return {"original_text": transcribed_text, "error": str(e), "summary": "Error in organization", "category": "Error"} 