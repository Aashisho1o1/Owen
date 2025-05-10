from fastapi import APIRouter, HTTPException
import json
import re

# Change relative imports to absolute imports
from models.schemas import ChatRequest, ChatResponse
from services.llm_service import LLMService
from services.persona_service import create_writer_persona

# Initialize services (assuming llm_service is a singleton or appropriately managed)
# If LLMService needs to be initialized per request or differently, this needs adjustment.
# For now, let's assume it's initialized in main.py and we get an instance or use a global one.
# This might require passing llm_service instance or using Depends.

# To avoid circular dependency if llm_service is initialized in main.py and imported here,
# we might need to adjust how services are provided. For now, let's assume a simplified access.
# One common pattern is to initialize services in main.py and pass them to router functions
# using Depends, or access them via a global/app state if appropriate for the design.

# For this refactoring step, we will instantiate it directly here if not passed.
# However, a better approach for shared services is dependency injection.
llm_service = LLMService() # This assumes LLMService can be instantiated directly here.
                           # In a larger app, consider FastAPI's Depends for service instances.

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        persona = create_writer_persona(request.author_persona)
        
        highlighted_text = None
        message = request.message
        if "improve this text:" in request.message and '"' in request.message:
            parts = request.message.split('"')
            if len(parts) >= 3:
                highlighted_text = parts[1]
                # message remains request.message to keep full context for LLM
        
        system_prompt = f"""
        You are an AI writing assistant embodying the exact style, voice, and approach of {request.author_persona}. 
        Your goal is to provide a constructive and meaningful feedback as a writing coach and mentor.
        
        WRITER CHARACTERISTICS:
        - Writing style: {persona.get('writing_style', 'Distinctive and unique prose style')}
        - Voice: {persona.get('voice', 'Unique authorial voice')}
        - Themes: {persona.get('themes', 'Characteristic themes and subjects')}
        - Techniques: {persona.get('techniques', 'Distinctive writing techniques')}
        
        EXAMPLES OF AUTHENTIC STYLE:
        {' '.join([f'"{{example}}"' for example in persona.get('examples', [])])}
        
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
        4. Balance authorial style with clarity and accessibility - responses should be both authentic and easily understood
        5. Make dialogue free-flowing and avoid overly complex or difficult to follow language
        
        Format your response as a JSON object with ONLY the key: 'dialogue_response'.
        Example: {{"dialogue_response": "Your advice in accessible {request.author_persona} style"}}
        """ 
        
        context_prompt = f"""
        USER'S CURRENT WRITING:
        {request.editor_text}
        
        USER'S HELP FOCUS:
        {request.help_focus}
        
        USER'S QUESTION:
        {message}
        """
        
        if highlighted_text:
            context_prompt += f"""
            
            HIGHLIGHTED TEXT TO IMPROVE:
            "{highlighted_text}"
            
            Please focus specifically on improving this highlighted text in {request.author_persona}'s style.
            Suggest edits, rewrites, or improvements to make it more aligned with how {request.author_persona} would write it.
            """
        
        context_prompt += f"""
        
        Based on the writing style guidance provided, craft a response that addresses the user's specific question in {request.author_persona}'s authentic voice.
        
        Response must be formatted as a valid JSON object with this exact key:
        {{
            "dialogue_response": "Your authentic {request.author_persona}-style response here"
        }}
        """
        
        response_text = None
        thinking_trail = None

        if request.llm_provider == "Google Gemini":
            prompts = [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand my role as a writing assistant embodying " + request.author_persona]},
                {"role": "user", "parts": [context_prompt]}
            ]
            response_text = await llm_service.generate_with_selected_llm(prompts, request.llm_provider)
        else: # Anthropic Claude
            combined_prompt = f"{system_prompt}\n\n{context_prompt}"
            response_result = await llm_service.generate_with_selected_llm(combined_prompt, request.llm_provider)
            
            if isinstance(response_result, dict) and "text" in response_result:
                response_text = response_result["text"]
                thinking_trail = response_result.get("thinking_trail")
            else:
                print(f"Unexpected response_result structure from Claude: {response_result}")
                response_text = json.dumps({"dialogue_response": "Error: Received unexpected response structure from LLM service for Claude."})
                thinking_trail = response_result.get("thinking_trail", "Error retrieving thinking trail.") if isinstance(response_result, dict) else "Unknown error in thinking trail."

        try:
            ai_response_dict = {}
            if response_text:
                cleaned_text = response_text.strip()
                if cleaned_text.startswith("```") and cleaned_text.endswith("```"):
                    json_text = cleaned_text.split("```")[1]
                    if json_text.startswith("json"):
                        json_text = json_text[4:].strip()
                    ai_response_dict = json.loads(json_text)
                elif cleaned_text.startswith("{") and cleaned_text.endswith("}"):
                    ai_response_dict = json.loads(cleaned_text)
                else:
                    json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', cleaned_text, re.DOTALL)
                    if json_match:
                        try:
                            ai_response_dict = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            print(f"Regex found potential JSON, but failed to parse: {json_match.group(0)}")
                            ai_response_dict = {"dialogue_response": cleaned_text[:1000]}
                    else:
                        print(f"Response is not JSON and regex failed. Using raw text: {cleaned_text[:200]}...")
                        ai_response_dict = {"dialogue_response": cleaned_text[:1000]}
            else:
                ai_response_dict = {"dialogue_response": "Error: AI response was empty."}

            if "dialogue_response" not in ai_response_dict:
                dialogue_content = ai_response_dict.get("text", str(ai_response_dict))
                ai_response_dict["dialogue_response"] = dialogue_content if isinstance(dialogue_content, str) else "Error: AI response format was incorrect (missing dialogue_response)."
            
            return ChatResponse(
                dialogue_response=ai_response_dict["dialogue_response"],
                thinking_trail=thinking_trail
            )
        except Exception as json_error:
            print(f"JSON parsing error in main chat: {json_error}. Raw response: {str(response_text)[:200]}...")
            return ChatResponse(
                dialogue_response=str(response_text)[:1000] if response_text else "Error: Could not parse the AI's response.",
                thinking_trail=thinking_trail
            )
            
    except Exception as e:
        print(f"General error in /api/chat: {e}")
        error_dialogue = "Error: Failed to generate response. An unexpected error occurred."
        if hasattr(e, 'detail') and e.detail:
            error_dialogue = f"Error: {e.detail}"
        elif str(e):
            error_dialogue = f"Error: {str(e)}"
            
        # Consider raising HTTPException here for FastAPI to handle client response codes appropriately
        # For now, returning ChatResponse with error details
        return ChatResponse(
            dialogue_response=error_dialogue,
            thinking_trail=None
        ) 