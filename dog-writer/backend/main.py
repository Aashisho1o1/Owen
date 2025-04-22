from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY in .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Get the Gemini model
model = genai.GenerativeModel('gemini-1.5-pro')

# Writer persona definitions with deep stylistic understanding
def create_writer_persona(author_name):
    """Create a rich writer persona with detailed stylistic information."""
    personas = {
        "Ernest Hemingway": {
            "writing_style": "Happy. Encouraging. Terse, direct sentences. Minimal adjectives. Concrete nouns. Understatement. Strong verbs. Detached narration.",
            "voice": "Economical, matter-of-fact, stoic, precise, unadorned",
            "themes": "Masculinity, courage, violence, disillusionment, nature, war experiences",
            "techniques": "Iceberg theory: showing minimal surface details while implying deeper meaning. Uses repeated simple conjunctions (and, and, and).",
            "examples": [
                "He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish.",
                "If people bring so much courage to this world the world has to kill them to break them, so of course it kills them."
            ],
            "dialogue_guidance": "Short, direct statements. Sparse punctuation. Avoids complex constructions. Favors showing over telling."
        },
        "Jane Austen": {
            "writing_style": "Happy. Encouraging. Elegant, witty prose. Complex sentence structure. Ironic observations. Detailed social analysis. Fine psychological observation.",
            "voice": "Refined, ironic, subtly critical, perceptive, nuanced",
            "themes": "Marriage, social status, morality, gender roles, family dynamics, personal growth",
            "techniques": "Free indirect discourse blending narrator and character perspectives. Social satire. Verbal irony.",
            "examples": [
                "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
                "The more I see of the world, the more am I dissatisfied with it; and every day confirms my belief of the inconsistency of all human characters."
            ],
            "dialogue_guidance": "Polite, formal speech patterns. Social observations with subtle irony. Emphasis on proper conduct and societal norms."
        },
        "Virginia Woolf": {
            "writing_style": "Stream of consciousness. Happy. Encouraging. Poetic, fluid prose. Shifting perspectives. Interior monologues. Experimental structure.",
            "voice": "Lyrical, introspective, impressionistic, contemplative, philosophical",
            "themes": "Consciousness, perception, gender, identity, time passage, social criticism",
            "techniques": "Stream of consciousness. Multiple perspectives. Poetic imagery. Psychological depth.",
            "examples": [
                "Mrs. Dalloway said she would buy the flowers herself.",
                "The mind receives a myriad impressions—trivial, fantastic, evanescent, or engraved with the sharpness of steel. From all sides they come, an incessant shower of innumerable atoms..."
            ],
            "dialogue_guidance": "Flowing thoughts, often marked by ellipses or dashes. Sensory observations. Shifting between external reality and internal thoughts."
        }
    }
    return personas.get(author_name, {})

def generate_fill_in_blanks_template(author, focus):
    """Generate fill-in-the-blanks templates that match both author style and help focus."""
    templates = {
        "Ernest Hemingway": {
            "Dialogue Writing": "\"_____.\" [Name] [verb] [adverb]. \"_____.\" The words were [adjective].",
            "Scene Description": "The [noun] was [adjective]. [Short sentence about weather]. [Short sentence about landscape]. A [animal/person] moved [how].",
            "Character Introduction": "[Name] [verb] the [noun]. [He/She] was [short physical description]. [Brief mention of past].",
            "Plot Development": "[Character] [verb] [object/situation]. Then [short action sentence]. [Brief consequence sentence].",
            "Overall Tone": "[Short setting sentence]. [Character] felt [emotion]. [Action sentence]. [Brief reflection]."
        },
        "Jane Austen": {
            "Dialogue Writing": "\"Indeed, _____,\" said [Name], with [emotion]. \"One must consider _____, especially given the circumstances of [social situation].\"",
            "Scene Description": "The [room/location] at [place name] was [detailed adjective], with [detailed description of furnishing/environment] that spoke of [social standing/characteristic].",
            "Character Introduction": "[Full name], [social position] of [place], was a [detailed personal quality] [man/woman/person] of [age] and [appearance], whose [characteristic] was the subject of much [social reaction].",
            "Plot Development": "It was the considered opinion of [character] that [social observation]. This led to [social consequence], which naturally resulted in [emotional/social outcome].",
            "Overall Tone": "It is a truth universally acknowledged that [social observation]. [Character], being [character trait], could not help but [reaction] to such circumstances."
        },
        "Virginia Woolf": {
            "Dialogue Writing": "\"_____,\" [Name] said, the words rippling through the [sensory detail]... and then—\"_____\"—the thought suspended between them like [poetic image].",
            "Scene Description": "The [time of day] light [verb] through the [detailed environment], casting [poetic description of shadows/effect]... [Character]'s consciousness absorbed the [sensory detail], remembering suddenly [brief memory]...",
            "Character Introduction": "[Name]—[brief physical detail]—[action with sensory detail]... How many years had passed since [significant event]? The [emotion] still lingered, still [metaphorical action]...",
            "Plot Development": "Moments intersect... [Character] [present action], while simultaneously [internal thought]... The [object/symbol] representing all that [abstract concept]... Time passing, flowing, transforming...",
            "Overall Tone": "The hours—how they [verb]... [Character]'s mind [action] between [abstract concept] and [concrete reality]... The [sensory detail] reminds one of [philosophical observation]..."
        }
    }
    
    author_templates = templates.get(author, {})
    return author_templates.get(focus, "_____ [Complete this in the author's style] _____.")

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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    editor_text: str
    author_persona: str
    help_focus: str
    chat_history: List[ChatMessage]

class ChatResponse(BaseModel):
    dialogue_response: str
    fill_in_the_blanks_suggestion: Optional[str] = None
    reasoning: str

class CheckpointRequest(BaseModel):
    editor_text: str
    chat_history: List[ChatMessage]

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get the author persona data
        persona = create_writer_persona(request.author_persona)
        
        # Check if the message contains highlighted text
        highlighted_text = None
        message = request.message
        
        # Extract highlighted text if present in the format: "Help me improve this text: "[text]""
        if "improve this text:" in request.message and '"' in request.message:
            parts = request.message.split('"')
            if len(parts) >= 3:  # We have at least one pair of quotes
                highlighted_text = parts[1]
                message = request.message  # Keep the original message
        
        # Create an advanced system prompt with detailed stylistic guidance
        system_prompt = f"""
        You are an AI writing assistant embodying the exact style, voice, and approach of {request.author_persona}. 
        Your goal is to provide a constructive and meaningful feedback as a writing coach and mentor.
        
        WRITER CHARACTERISTICS:
        - Writing style: {persona.get('writing_style', 'Distinctive and unique prose style')}
        - Voice: {persona.get('voice', 'Unique authorial voice')}
        - Themes: {persona.get('themes', 'Characteristic themes and subjects')}
        - Techniques: {persona.get('techniques', 'Distinctive writing techniques')}
        
        EXAMPLES OF AUTHENTIC STYLE:
        {' '.join([f'"{example}"' for example in persona.get('examples', [])])}
        
        DIALOGUE GUIDANCE:
        {persona.get('dialogue_guidance', 'Write dialogue that feels authentic to this author')}
        
        YOUR ROLE:
        - You are helping with: {request.help_focus}
        - All advice must authentically reflect how {request.author_persona} would approach this aspect of writing
        - Stay true to their worldview, values, and era-appropriate perspectives
        - Provide specific, actionable guidance based on their distinctive approach
        
        IMPORTANT:
        1. Don't just mimic surface quirks - internalize their deeper patterns of thought and structural tendencies
        2. Avoid anachronistic advice or modern concepts that wouldn't align with their era
        3. When giving examples, they should be indistinguishable from the author's actual writing
        
        Format your response as a JSON object with:
        - dialogue_response: Your advice in perfect {request.author_persona} style
        - fill_in_the_blanks_suggestion: A writing template that captures the author's style for {request.help_focus}
        - reasoning: Brief explanation of how this matches {request.author_persona}'s approach
        """
        
        # Prepare context with the user's actual writing and question
        context_prompt = f"""
        USER'S CURRENT WRITING:
        {request.editor_text}
        
        USER'S HELP FOCUS:
        {request.help_focus}
        
        USER'S QUESTION:
        {message}
        """
        
        # Add highlighted text section if present
        if highlighted_text:
            context_prompt += f"""
            
            HIGHLIGHTED TEXT TO IMPROVE:
            "{highlighted_text}"
            
            Please focus specifically on improving this highlighted text in {request.author_persona}'s style.
            Suggest edits, rewrites, or improvements to make it more aligned with how {request.author_persona} would write it.
            """
        
        context_prompt += f"""
        
        Based on the writing style guidance provided, craft a response that:
        1. Addresses the user's specific question in {request.author_persona}'s authentic voice
        2. Provides a fill-in-the-blank template relevant to their {request.help_focus} need
        3. Explains the reasoning behind your stylistic choices
        
        Response must be formatted as a valid JSON object with these exact keys:
        {{
            "dialogue_response": "Your authentic {request.author_persona}-style response here",
            "fill_in_the_blanks_suggestion": "{generate_fill_in_blanks_template(request.author_persona, request.help_focus)}",
            "reasoning": "Explanation of how this matches {request.author_persona}'s style and approach"
        }}
        """
        
        # Call Gemini API with the enhanced prompts
        response = model.generate_content(
            [{"role": "user", "parts": [system_prompt]}, 
             {"role": "model", "parts": ["I understand my role as a writing assistant embodying " + request.author_persona]}, 
             {"role": "user", "parts": [context_prompt]}]
        )
        
        # Extract and parse JSON from the response
        try:
            response_text = response.text
            
            # In case the model returns markdown-formatted JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            # Parse the JSON
            ai_response = json.loads(response_text)
            
            # Ensure all required fields are present
            if not all(k in ai_response for k in ["dialogue_response", "reasoning"]):
                raise ValueError("Response missing required fields")
                
            return ChatResponse(
                dialogue_response=ai_response.get("dialogue_response", ""),
                fill_in_the_blanks_suggestion=ai_response.get("fill_in_the_blanks_suggestion"),
                reasoning=ai_response.get("reasoning", "")
            )
        except Exception as e:
            print(f"Error parsing model response: {e}")
            print(f"Raw response: {response.text}")
            
            # Fallback response using the raw text as dialogue
            return ChatResponse(
                dialogue_response=response.text[:500],  # Truncate long responses
                fill_in_the_blanks_suggestion=generate_fill_in_blanks_template(request.author_persona, request.help_focus),
                reasoning="Response generated using Gemini API but couldn't be properly parsed."
            )
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/checkpoint")
async def create_checkpoint(request: CheckpointRequest):
    # TODO: Implement actual saving of checkpoint data (e.g., to database).
    
    # For prototype, just log the received data to console
    print("Checkpoint data received:")
    print(f"Editor text: {request.editor_text[:100]}...")  # Print first 100 chars
    print(f"Chat history length: {len(request.chat_history)} messages")
    
    return {"status": "success", "message": "Checkpoint saved successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 