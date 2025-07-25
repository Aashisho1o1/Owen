#!/usr/bin/env python3
"""
Backend FolderScope Test
Tests the exact backend logic with the debugging we added
"""

import requests
import json
import time

# Configure the backend URL
BACKEND_URL = "https://doggyyyy-production.up.railway.app"  # Replace with your backend URL

def test_folderscope_request():
    """Test FolderScope request to see debugging logs in backend"""
    
    # First, we need to authenticate to get a valid user context
    # For this test, we'll use the debugging endpoint if available
    
    chat_payload = {
        "message": "Who is the main character in my story? Please analyze all documents in my folder.",
        "editor_text": "Chapter 1: Alice walked through the forest, thinking about her adventure...",
        "author_persona": "Ernest Hemingway",
        "help_focus": "Character Introduction",
        "chat_history": [],
        "llm_provider": "Google Gemini",
        "ai_mode": "talk",
        "user_preferences": {
            "user_corrections": [],
            "onboarding_completed": True
        },
        "feedback_on_previous": "",
        "highlighted_text": "",
        "highlight_id": "",
        "english_variant": "US",
        # CRITICAL: Enable FolderScope
        "folder_scope": True,
        "voice_guard": False
    }
    
    print("🧪 Testing FolderScope Backend Request")
    print("=" * 40)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Request payload preview:")
    print(f"  - message: {chat_payload['message'][:50]}...")
    print(f"  - folder_scope: {chat_payload['folder_scope']} ({type(chat_payload['folder_scope'])})")
    print(f"  - voice_guard: {chat_payload['voice_guard']} ({type(chat_payload['voice_guard'])})")
    print()
    
    try:
        print("📡 Sending request to backend...")
        response = requests.post(
            f"{BACKEND_URL}/api/chat/",
            json=chat_payload,
            headers={
                "Content-Type": "application/json",
                "X-Request-Type": "folder-scope"
            },
            timeout=30  # Short timeout for testing
        )
        
        print(f"✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response preview:")
            if 'dialogue_response' in data:
                print(f"   Response: {data['dialogue_response'][:100]}...")
            if 'thinking_trail' in data:
                print(f"   Thinking: {data['thinking_trail'][:100] if data['thinking_trail'] else 'None'}...")
        else:
            print(f"❌ Error Response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
    
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this suggests FolderScope is taking too long")
        print("   Check the backend logs for our debugging messages:")
        print("   - Should see: '📁 Folder Scope: ENABLED'")
        print("   - Should see: '📁 FolderScope enabled - retrieving folder context...'")
        print("   - Should see: '📁 ========== INTELLIGENT FOLDER SCOPE SEARCH =========='")
        
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - backend may be down or URL incorrect")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_authentication_status():
    """Test if we can check backend authentication status"""
    print("\n🔐 Testing Authentication Status")
    print("=" * 35)
    
    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        
        # Test basic API health
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        print(f"✅ API health: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")

if __name__ == "__main__":
    print("🚀 Backend FolderScope Testing")
    print("=" * 50)
    print("This test will:")
    print("1. Check backend accessibility")
    print("2. Send a FolderScope-enabled request")
    print("3. Analyze the response and any errors")
    print("4. Help identify why debugging logs aren't appearing")
    print()
    
    # Test backend accessibility first
    test_authentication_status()
    
    # Test FolderScope request
    test_folderscope_request()
    
    print("\n📋 Next Steps:")
    print("1. Check the Railway backend logs for our debugging messages")
    print("2. Look for these specific log entries:")
    print("   - '📁 Folder Scope: ENABLED'")
    print("   - '🔧 DEBUGGING - folder_scope type: <type>'")
    print("   - '🔧 DEBUGGING - folder_scope value: <value>'")
    print("   - '📁 FolderScope enabled - retrieving folder context...'")
    print("3. If these logs are missing, the request isn't reaching the backend correctly")
    print("4. If they appear but context retrieval fails, check the database/vector store logs") 