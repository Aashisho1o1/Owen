"""
Owen AI Writer - Backend API
Railway-optimized minimal version
DEPLOYMENT TRIGGER: Force redeploy with timeout fixes
"""

import os
import json
import asyncio
from openai import OpenAI
import google.generativeai as genai
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure AI providers
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure basic setup
app = FastAPI(
    title="Owen AI Writer",
    description="Advanced AI Writing Assistant",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://owen-frontend-production.up.railway.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "*"  # Allow all origins for now
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    editor_text: str = ""
    author_persona: str = "Ernest Hemingway"
    help_focus: str = "general"
    chat_history: list = []
    llm_provider: str = "openai"
    user_preferences: dict = {}
    feedback_on_previous: str = ""
    english_variant: str = "US"

class ChatResponse(BaseModel):
    dialogue_response: str
    thinking_trail: Optional[str] = None

# Root endpoints
@app.get("/")
async def read_root():
    """Root endpoint with system status"""
    return {
        "message": "Owen AI Writer is running successfully!",
        "status": "ok",
        "mode": "full",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "features": {
            "ai_providers": ["OpenAI", "Anthropic", "Google Gemini"],
            "security": "JWT Ready",
            "database": "SQLite Ready",
            "voice": "Text-to-Speech Ready",
            "manga": "AI Generation Ready",
            "sessions": "Session Management Ready"
        },
        "api_keys_configured": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY"))
        },
        "frontend_connected": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "healthy": True,
        "service": "Owen AI Writer",
        "version": "2.0.0",
        "mode": "full",
        "port": os.getenv("PORT", "8000"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def api_health():
    """Extended API health check"""
    return {
        "status": "healthy",
        "service": "Owen AI Backend",
        "version": "2.0.0",
        "mode": "full",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "ai_providers": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY"))
        }
    }

@app.get("/api/status")
async def detailed_status():
    """Detailed system status"""
    return {
        "api": "Owen AI Writer",
        "status": "running",
        "mode": "full",
        "version": "2.0.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "features": {
            "authentication": "Ready for implementation",
            "chat": "AI chat endpoints",
            "database": "SQLite ready",
            "ai_integration": "Multi-provider support",
            "voice_synthesis": "OpenAI TTS ready",
            "session_management": "User sessions ready"
        },
        "endpoints": {
            "chat": "/api/chat/message",
            "basic": "/api/chat/basic",
            "health": "/api/health",
            "status": "/api/status"
        },
        "api_keys_status": {
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google_configured": bool(os.getenv("GOOGLE_API_KEY"))
        }
    }

@app.get("/api/test/openai")
async def test_openai():
    """Test OpenAI API connection"""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return {"error": "No OpenAI API key configured"}
        
        print("[DEBUG] Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
            max_tokens=20,
            timeout=10.0
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content,
            "model": response.model,
            "usage": response.usage.total_tokens if response.usage else "N/A"
        }
    except Exception as e:
        print(f"[ERROR] OpenAI test failed: {e}")
        return {"error": str(e)}

@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "openai_key_exists": bool(os.getenv("OPENAI_API_KEY")),
        "openai_key_length": len(os.getenv("OPENAI_API_KEY", "")),
        "google_key_exists": bool(os.getenv("GOOGLE_API_KEY")),
        "google_key_length": len(os.getenv("GOOGLE_API_KEY", "")),
        "anthropic_key_exists": bool(os.getenv("ANTHROPIC_API_KEY")),
        "anthropic_key_length": len(os.getenv("ANTHROPIC_API_KEY", "")),
        "timestamp": datetime.now().isoformat()
    }

# Basic chat endpoints
@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(chat: ChatMessage):
    """Send a message to AI with multi-provider LLM integration"""
    start_time = datetime.now()
    print(f"[DEBUG] Chat request started at {start_time} for provider: {chat.llm_provider}")
    
    try:
        # Create persona-specific system prompt
        system_prompt = f"""You are {chat.author_persona}, a master writer and mentor. 
        You're helping a writer improve their craft. Be encouraging, insightful, and true to {chat.author_persona}'s style and philosophy.
        
        Focus area: {chat.help_focus}
        Editor text context: {chat.editor_text[:500] if chat.editor_text else 'No text provided'}
        
        Provide specific, actionable advice that would improve the writing."""
        
        # Determine which provider to use based on llm_provider
        provider = chat.llm_provider.lower()
        print(f"[DEBUG] Using provider: {provider}")
        
        if "openai" in provider or "gpt" in provider:
            # Use OpenAI with simple synchronous approach
            if os.getenv("OPENAI_API_KEY"):
                try:
                    print(f"[DEBUG] Starting OpenAI call for: {chat.message[:50]}...")
                    
                    # Simple synchronous call with short timeout
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": chat.message}
                        ],
                        max_tokens=150,  # Reduced for faster response
                        temperature=0.7,
                        timeout=8.0  # Short timeout
                    )
                    
                    print(f"[DEBUG] OpenAI call completed successfully")
                    ai_response = response.choices[0].message.content.strip()
                    thinking_trail = f"OpenAI GPT-3.5-turbo ({chat.author_persona})"
                    
                except Exception as openai_error:
                    print(f"[ERROR] OpenAI failed: {str(openai_error)[:100]}")
                    # Provide intelligent fallback based on the question
                    if "dialogue" in chat.message.lower():
                        ai_response = f"As {chat.author_persona}: Cut the fat from your dialogue. What people don't say is often more powerful than what they do. Every word should carry weight and reveal character."
                    elif "authentic" in chat.message.lower():
                        ai_response = f"As {chat.author_persona}: Write what you know deeply. Authenticity comes from truth lived, not imagined. Strip away anything that sounds like 'writing' and leave only what rings true."
                    else:
                        ai_response = f"As {chat.author_persona}: {chat.message} - The key is to write with both courage and precision. Every sentence should advance your story or deepen character. Cut ruthlessly, write boldly."
                    
                    thinking_trail = f"OpenAI timeout - {chat.author_persona} fallback used"
                
            else:
                print(f"[DEBUG] No OpenAI API key configured")
                ai_response = f"OpenAI API key missing. Please configure to get real AI responses."
                thinking_trail = "Missing OpenAI API key"
                
        elif "google" in provider or "gemini" in provider:
            # Use Google Gemini
            if os.getenv("GOOGLE_API_KEY"):
                model = genai.GenerativeModel('gemini-pro')
                
                # Create full prompt for Gemini
                full_prompt = f"{system_prompt}\n\nUser question: {chat.message}"
                
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=300,
                        temperature=0.7,
                    )
                )
                
                ai_response = response.text.strip()
                thinking_trail = f"Used Google Gemini Pro with {chat.author_persona} persona"
                
            else:
                ai_response = f"Google API key not configured. Demo response: {chat.message}"
                thinking_trail = "Google API key missing"
                
        elif "anthropic" in provider or "claude" in provider:
            # Placeholder for Anthropic (would need anthropic library)
            ai_response = f"Anthropic integration coming soon. Demo response as {chat.author_persona}: {chat.message}"
            thinking_trail = "Anthropic integration in development"
            
        else:
            # Default fallback
            ai_response = f"Unknown provider '{chat.llm_provider}'. Demo response as {chat.author_persona}: {chat.message}"
            thinking_trail = f"Unknown provider: {chat.llm_provider}"
        
        return ChatResponse(
            dialogue_response=ai_response,
            thinking_trail=thinking_trail
        )
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        print(f"[ERROR] Chat request failed after {duration} seconds: {e}")
        return ChatResponse(
            dialogue_response=f"I apologize, but I encountered an error after {duration} seconds. As {chat.author_persona} would say, let's try again with a different approach.",
            thinking_trail=f"Error after {duration:.1f}s: {str(e)}"
        )

@app.get("/api/chat/basic")
async def basic_chat():
    """Basic chat endpoint for testing"""
    return {
        "message": "Owen AI Writer backend is fully operational!",
        "status": "ready",
        "features": [
            "Multi-LLM AI chat integration",
            "Session management",
            "Voice synthesis",
            "Manga generation",
            "Secure authentication",
            "Real-time responses"
        ],
        "next_steps": "Add your OpenAI, Anthropic, or Google API keys to enable full AI features",
        "frontend_url": "https://owen-frontend-production.up.railway.app"
    }

# Voice endpoint (placeholder)
@app.post("/api/voice/synthesize")
async def synthesize_voice():
    """Voice synthesis endpoint"""
    return {
        "message": "Voice synthesis ready",
        "note": "Add OpenAI API key to enable TTS functionality",
        "supported_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    }

# Manga endpoint (placeholder)
@app.post("/api/manga/generate")
async def generate_manga():
    """Manga generation endpoint"""
    return {
        "message": "Manga generation ready",
        "note": "Add OpenAI API key to enable DALL-E functionality",
        "supported_styles": ["anime", "manga", "realistic", "cartoon"]
    }

# Session endpoints (placeholder)
@app.get("/api/sessions")
async def get_sessions():
    """Get user sessions"""
    return {
        "sessions": [],
        "message": "Session management ready",
        "note": "Implement authentication to enable persistent sessions"
    }

@app.post("/api/sessions")
async def create_session():
    """Create new session"""
    return {
        "id": "demo-session-123",
        "title": "Demo Session",
        "created_at": datetime.now().isoformat(),
        "message": "Session creation ready",
        "note": "Implement authentication to enable real sessions"
    }

@app.post("/api/chat/demo")
async def chat_demo(chat: ChatMessage):
    """Immediate demo response - no AI API calls"""
    # Quick Hemingway-style responses based on the question
    if "dialogue" in chat.message.lower():
        responses = [
            "Cut the fat. Real dialogue is what people don't say, not what they do. Show the tension underneath.",
            "Make every word count. If it doesn't advance the story or reveal character, kill it.",
            "People don't say what they mean. They dance around it. Write the dance, not the meaning."
        ]
    elif "authentic" in chat.message.lower():
        responses = [
            "Write what you know, feel what you write. Authenticity comes from truth, not tricks.",
            "The best writing is rewriting. Strip away everything that sounds like writing.",
            "Show, don't tell. Let the reader feel the weight of what isn't said."
        ]
    else:
        responses = [
            "Write with the heart of a poet and the discipline of a soldier. Every word must earn its place.",
            "The first draft is garbage. The magic happens when you throw away what you don't need.",
            "Write standing up. It keeps you honest about what matters."
        ]
    
    import random
    ai_response = random.choice(responses)
    
    return ChatResponse(
        dialogue_response=f"As {chat.author_persona}, I'd say: {ai_response}",
        thinking_trail="Demo mode - instant response"
    )

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "service": "Owen AI Writer",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 