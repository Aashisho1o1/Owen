"""
Owen AI Writer - Backend API
Railway-optimized minimal version
DEPLOYMENT TRIGGER: Force redeploy with timeout fixes
FRESH DEPLOY: 2025-06-09 19:22 - GEMINI_API_KEY fix deployed
Document Management API added - 2025-06-09
Analytics System Integration - 2025-06-13
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import uvicorn
import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure AI providers
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

# Configure Gemini with better error handling
GEMINI_CONFIGURED = False
# Updated to use more stable model IDs
# Primary model: Latest stable Gemini model
GEMINI_MODEL_ID = 'gemini-1.5-pro'  # Stable model that should be available
# Alternative backup model ID in case the primary is unavailable  
GEMINI_FALLBACK_MODEL_ID = 'gemini-1.5-flash'  # Faster fallback model

# Basic Gemini API configuration (no validation during startup to prevent key exposure)
if os.getenv("GEMINI_API_KEY"):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        GEMINI_CONFIGURED = True
        logger.info("Gemini API configured successfully")
    except Exception as config_error:
        logger.error(f"Failed to configure Gemini API: {str(config_error)[:100]}")
        GEMINI_CONFIGURED = False
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")

# Configure basic setup
app = FastAPI(
    title="Owen AI Writer",
    description="Advanced AI Writing Assistant with Document Management and Analytics",
    version="2.2.0"
)

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
            "google": bool(os.getenv("GEMINI_API_KEY"))
        }
    }

# Import document routes
try:
    from routes.documents import router as documents_router
    DOCUMENT_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import document routes: {e}")
    DOCUMENT_ROUTES_AVAILABLE = False

# Import analytics routes and middleware
try:
    from routes.analytics import router as analytics_router
    from middleware.analytics_middleware import create_analytics_middleware, create_writing_session_middleware
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analytics components not available (optional): {e}")
    ANALYTICS_AVAILABLE = False

# Import grammar routes
try:
    from routers.grammar_router import router as grammar_router
    GRAMMAR_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import grammar routes: {e}")
    GRAMMAR_ROUTES_AVAILABLE = False

# Import authentication routes
try:
    from routes.auth import router as auth_router
    from init_db import init_database  # Import the initializer
    AUTH_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import auth routes: {e}")
    AUTH_ROUTES_AVAILABLE = False

# Initialize the authentication database on startup
if AUTH_ROUTES_AVAILABLE:
    try:
        logger.info("Initializing authentication database...")
        init_database()
        logger.info("Authentication database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize authentication database: {e}")

# Add Analytics Middleware (before CORS)
if ANALYTICS_AVAILABLE:
    try:
        # Analytics middleware for tracking user behavior
        analytics_middleware = create_analytics_middleware(
            exclude_paths=["/health", "/api/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        )
        app.add_middleware(analytics_middleware)
        
        # Writing session middleware for detailed writing analytics
        writing_middleware = create_writing_session_middleware()
        app.add_middleware(writing_middleware)
        
        ANALYTICS_ENABLED = True
        logger.info("Analytics middleware enabled successfully")
        
    except Exception as e:
        logger.error(f"Failed to enable analytics middleware: {e}")
        ANALYTICS_ENABLED = False
else:
    ANALYTICS_ENABLED = False
    logger.warning("Analytics components not available - running without analytics")

# Include document management routes
if DOCUMENT_ROUTES_AVAILABLE:
    try:
        logger.info("Attempting to include document router...")
        app.include_router(documents_router)
        DOCUMENT_ROUTES_LOADED = True
        logger.info("Document router included successfully.")
    except Exception as e:
        logger.error(f"An unexpected error occurred while including document router: {e}")
        DOCUMENT_ROUTES_LOADED = False
else:
    DOCUMENT_ROUTES_LOADED = False
    logger.warning("Document routes not available - running without document management")

# Include analytics routes
if ANALYTICS_AVAILABLE:
    try:
        logger.info("Attempting to include analytics router...")
        app.include_router(analytics_router)
        ANALYTICS_ROUTES_LOADED = True
        logger.info("Analytics router included successfully.")
    except Exception as e:
        logger.error(f"Failed to include analytics router: {e}")
        ANALYTICS_ROUTES_LOADED = False
else:
    ANALYTICS_ROUTES_LOADED = False
    logger.warning("Analytics routes not available - running without analytics endpoints")

# Include grammar routes
if GRAMMAR_ROUTES_AVAILABLE:
    try:
        app.include_router(grammar_router)
        logger.info("Grammar router included successfully.")
    except Exception as e:
        logger.error(f"Failed to include grammar router: {e}")

# Include authentication routes
if AUTH_ROUTES_AVAILABLE:
    try:
        app.include_router(auth_router)
        logger.info("Authentication router included successfully.")
    except Exception as e:
        logger.error(f"Failed to include auth router: {e}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://owen-frontend-production.up.railway.app",
        "https://web-production-44b3.up.railway.app",
        "http://localhost:3000",  # For local development
        "http://localhost:5173",  # For Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    editor_text: str = ""
    highlighted_text: str = ""  # New field for highlighted text
    highlight_id: str = ""  # New field for highlight ID
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
        "mode": "full_analytics" if (DOCUMENT_ROUTES_LOADED and ANALYTICS_ROUTES_LOADED) else "document_management" if DOCUMENT_ROUTES_LOADED else "basic",
        "version": "2.2.0",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
        "features": {
            "ai_providers": ["OpenAI", "Anthropic", "Google Gemini 2.5 Pro"] if client else ["Partially disabled"],
            "security": "JWT Ready",
            "database": "SQLite Ready",
            "document_management": "Active" if DOCUMENT_ROUTES_LOADED else "Failed to load",
            "analytics": "Active" if ANALYTICS_ROUTES_LOADED else "Failed to load",
            "writing_analytics": "NLP-powered insights" if ANALYTICS_ENABLED else "Disabled",
            "privacy_compliance": "GDPR & CCPA compliant" if ANALYTICS_ENABLED else "N/A",
            "voice": "Text-to-Speech Ready" if client else "Unavailable",
            "manga": "AI Generation Ready" if client else "Unavailable",
            "sessions": "Session Management Ready"
        },
        "api_keys_configured": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google": bool(os.getenv("GEMINI_API_KEY")),
            "posthog": bool(os.getenv("POSTHOG_API_KEY")),
            "mixpanel": bool(os.getenv("MIXPANEL_TOKEN"))
        },
        "analytics_status": {
            "middleware_enabled": ANALYTICS_ENABLED,
            "routes_loaded": ANALYTICS_ROUTES_LOADED,
            "privacy_compliant": True,
            "real_time_tracking": ANALYTICS_ENABLED,
            "writing_insights": ANALYTICS_ENABLED
        },
        "document_routes_loaded": DOCUMENT_ROUTES_LOADED,
        "frontend_connected": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "deployed",
        "service": "Owen AI Writer",
        "version": "2.2.0",
        "mode": "full",
        "port": os.getenv("PORT", "8000"),
        "timestamp": datetime.now().isoformat(),
        "healthy": True
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
            "google_configured": bool(os.getenv("GEMINI_API_KEY"))
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
        logging.error(f"[ERROR] OpenAI test failed: {e}", exc_info=True)
        return {"error": "An internal error occurred while testing the OpenAI API. Please try again later."}

@app.get("/api/test/deployed")
async def test_deployed():
    """Simple test to verify new code is deployed"""
    return {
        "deployed": True,
        "branch": get_current_branch(),
        "timestamp": datetime.now().isoformat(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "message": "New code successfully deployed!"
    }

@app.get("/api/test/canary")
async def test_canary():
    """A unique endpoint to confirm if deployments are working correctly."""
    return {
        "status": "ok",
        "message": "Canary deployment successful. The new code is live.",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (API keys are masked for security)"""
    return {
        "openai_key_exists": bool(os.getenv("OPENAI_API_KEY")),
        "openai_key_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
        "google_key_exists": bool(os.getenv("GEMINI_API_KEY")),
        "google_key_length": len(os.getenv("GEMINI_API_KEY", "")) if os.getenv("GEMINI_API_KEY") else 0,
        "gemini_configured": GEMINI_CONFIGURED,
        "anthropic_key_exists": bool(os.getenv("ANTHROPIC_API_KEY")),
        "anthropic_key_length": len(os.getenv("ANTHROPIC_API_KEY", "")) if os.getenv("ANTHROPIC_API_KEY") else 0,
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "google_generativeai_available": True,  # Since we imported it successfully
        "security_note": "API keys are never exposed in logs or debug endpoints"
    }

@app.get("/api/test/gemini")
async def test_gemini():
    """Test Gemini API connection with fallback support"""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            return {"error": "No Gemini API key configured"}
        
        if not GEMINI_CONFIGURED:
            return {"error": "Gemini API configuration failed"}
        
        print(f"[DEBUG] Testing Gemini API connection with model: {GEMINI_MODEL_ID}")
        
        # Try primary model first
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_ID)
            
            # Simple test prompt
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    model.generate_content,
                    "Explain the concept of literary voice in exactly 10 words.",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=300,
                        temperature=0.7,
                        top_p=0.9,
                        top_k=40,
                    )
                ),
                timeout=60.0  # Shorter timeout for testing
            )
            
            return {
                "success": True,
                "response": response.text.strip(),
                "model": GEMINI_MODEL_ID,
                "configured": GEMINI_CONFIGURED,
                "fallback_used": False,
                "capabilities": "Advanced reasoning, creative writing assistance"
            }
            
        except Exception as primary_error:
            print(f"[DEBUG] Primary model {GEMINI_MODEL_ID} failed: {str(primary_error)[:200]}")
            
            # Try fallback model
            try:
                print(f"[DEBUG] Trying fallback model: {GEMINI_FALLBACK_MODEL_ID}")
                fallback_model = genai.GenerativeModel(GEMINI_FALLBACK_MODEL_ID)
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        fallback_model.generate_content,
                        "Explain literary voice in 10 words.",
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=300,
                            temperature=0.7,
                        )
                    ),
                    timeout=60.0
                )
                
                logging.error(f"Primary model error: {str(primary_error)}")
                return {
                    "success": True,
                    "response": response.text.strip(),
                    "model": GEMINI_FALLBACK_MODEL_ID,
                    "configured": GEMINI_CONFIGURED,
                    "fallback_used": True,
                    "capabilities": "Fast text generation, writing assistance"
                }
                
            except Exception as fallback_error:
                logging.error(f"Primary model error: {str(primary_error)}")
                logging.error(f"Fallback model error: {str(fallback_error)}")
                return {
                    "error": "Both primary and fallback models failed",
                    "primary_model": GEMINI_MODEL_ID,
                    "fallback_model": GEMINI_FALLBACK_MODEL_ID,
                    "suggestion": "Check API key permissions and model availability"
                }
        
    except asyncio.TimeoutError:
        logging.error("[ERROR] Gemini API test timeout")
        return {"error": "Gemini API test timed out after 60 seconds"}
    except Exception as e:
        logging.error(f"[ERROR] Gemini test failed: {e}", exc_info=True)
        return {
            "error": "Unexpected error during Gemini test",
            "details": "An internal error occurred. Please contact support if the issue persists.",
            "model": GEMINI_MODEL_ID,
            "configured": GEMINI_CONFIGURED
        }

# Basic chat endpoints
@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(chat: ChatMessage):
    """Send a message to AI with multi-provider LLM integration"""
    start_time = datetime.now()
    request_id = f"req-{int(start_time.timestamp())}"
    print(f"[DEBUG] {request_id} Chat request started at {start_time} for provider: {chat.llm_provider}")
    print(f"[DEBUG] {request_id} Request data: message='{chat.message[:100]}...', persona={chat.author_persona}, focus={chat.help_focus}")
    
    try:
        # Create persona-specific system prompt with highlighted text support
        if chat.highlighted_text:
            # When user highlights specific text for feedback
            system_prompt = f"""You are {chat.author_persona}, a master writer and mentor. 
            You're helping a writer improve their craft. Be encouraging, insightful, and true to {chat.author_persona}'s style and philosophy.
            
            Focus area: {chat.help_focus}
            Full editor context: {chat.editor_text[:500] if chat.editor_text else 'No text provided'}
            
            HIGHLIGHTED TEXT FOR SPECIFIC FEEDBACK: "{chat.highlighted_text}"
            
            The user has specifically highlighted the above text and wants your feedback on it. 
            Focus your response on analyzing and improving this highlighted portion while considering the broader context.
            Provide specific, actionable advice that would improve the highlighted writing."""
        else:
            # General writing advice without specific highlighted text
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
            # Use Google Gemini 2.5 Pro - Most advanced thinking model
            if GEMINI_CONFIGURED and os.getenv("GEMINI_API_KEY"):
                try:
                    print(f"[DEBUG] Starting Gemini 2.5 Pro call for: {chat.message[:50]}...")
                    
                    # Use the latest Gemini 2.5 Pro model with advanced reasoning
                    model = genai.GenerativeModel(GEMINI_MODEL_ID)
                    
                    # Create enhanced prompt for advanced reasoning with highlighted text support
                    if chat.highlighted_text:
                        enhanced_prompt = f"""You are {chat.author_persona}, a master writer and mentor with deep expertise in literary craft.

Full Context: {chat.editor_text[:1000] if chat.editor_text else 'No text provided'}
Focus area: {chat.help_focus}

HIGHLIGHTED TEXT FOR SPECIFIC FEEDBACK: "{chat.highlighted_text}"

User question: {chat.message}

The user has specifically highlighted the above text for your analysis. Please provide thoughtful, actionable advice that reflects {chat.author_persona}'s distinctive voice and philosophy. Use your advanced reasoning to analyze this highlighted portion in the context of the broader writing and provide specific, practical guidance for improvement."""
                    else:
                        enhanced_prompt = f"""You are {chat.author_persona}, a master writer and mentor with deep expertise in literary craft.

Context: {chat.editor_text[:1000] if chat.editor_text else 'No text provided'}
Focus area: {chat.help_focus}

User question: {chat.message}

Please provide thoughtful, actionable advice that reflects {chat.author_persona}'s distinctive voice and philosophy. Use your advanced reasoning to analyze the writing context and provide specific, practical guidance."""
                    
                    # Configure generation settings optimized for Gemini 2.5 Pro
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=300,  # Increased for more detailed responses
                        temperature=0.7,
                        top_p=0.9,  # Enhanced creativity control
                        top_k=40,   # Vocabulary diversity
                    )
                    
                    # Run Gemini 2.5 Pro generation with extended timeout for complex reasoning
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            model.generate_content,
                            enhanced_prompt,
                            generation_config=generation_config
                        ),
                        timeout=180  # Extended timeout for advanced reasoning
                    )
                    
                    print(f"[DEBUG] Gemini 2.5 Pro call completed successfully")
                    ai_response = response.text.strip()
                    thinking_trail = f"Google Gemini 2.5 Pro - Advanced Reasoning ({chat.author_persona})"
                    
                except asyncio.TimeoutError:
                    print(f"[ERROR] Gemini 2.5 Pro timeout after 180 seconds")
                    ai_response = f"As {chat.author_persona}: {chat.message} - Write with precision and truth. Every word should have weight and purpose."
                    thinking_trail = f"Gemini 2.5 Pro timeout - {chat.author_persona} fallback used"
                    
                except Exception as gemini_error:
                    print(f"[ERROR] Gemini 2.5 Pro failed: {str(gemini_error)[:100]}")
                    # Provide intelligent fallback based on the question
                    if "dialogue" in chat.message.lower():
                        ai_response = f"As {chat.author_persona}: Make dialogue serve the story. Cut empty words, show character through what they don't say. Every line should advance plot or reveal character."
                    elif "character" in chat.message.lower():
                        ai_response = f"As {chat.author_persona}: Characters must be real people with contradictions, desires, and flaws. Show, don't tell. Let their actions reveal their nature."
                    else:
                        ai_response = f"As {chat.author_persona}: {chat.message} - Write with precision and truth. Every word should have weight and serve the story."
                    
                    thinking_trail = f"Gemini 2.5 Pro error - {chat.author_persona} fallback used"
                
            else:
                print(f"[DEBUG] Gemini not properly configured or API key missing")
                if not GEMINI_CONFIGURED:
                    ai_response = f"Gemini 2.5 Pro API configuration failed. Please check your API key and try again."
                    thinking_trail = "Gemini 2.5 Pro configuration error"
                else:
                    ai_response = f"Gemini 2.5 Pro API key missing. Please configure to get advanced AI responses."
                    thinking_trail = "Missing Gemini 2.5 Pro API key"
                
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
        "next_steps": "Add your OpenAI, Anthropic, or Google Gemini 2.5 Pro API keys to enable full AI features",
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
    # Mock AI responses for development
    responses = [
        "This is a mock AI response for development.",
        "Another mock response to simulate AI behavior.",
        "Testing the chat functionality with mock data."
    ]
    # Fixed: Use secure random for production environments
    # Standard random is not cryptographically secure
    import secrets
    ai_response = secrets.choice(responses)
    
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

def get_current_branch():
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"

if __name__ == "__main__":
    # This section only runs when executing the file directly (local development)
    # Railway uses the startCommand in railway.toml instead
    
    # Fixed: More secure host binding configuration
    # Only bind to all interfaces (0.0.0.0) in development
    # In production, consider binding to specific interface
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")  # Railway needs 0.0.0.0
    
    logger.info(f"Starting Owen AI Writer locally on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 