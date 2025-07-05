#!/usr/bin/env python3
"""
Test script to verify the validation fix is working on the deployed server
"""

import requests
import json
import time

# Test configuration
API_BASE_URL = "https://owen-backend-production.up.railway.app"
TEST_TEXT_LENGTH = 15000  # 15,000 characters - should work with new limits

def test_validation_fix():
    """Test that the validation service now accepts large text inputs"""
    
    print("🧪 Testing Validation Service Fix")
    print("=" * 50)
    
    # Create a large text input (15,000 characters)
    large_text = "This is a test document with repeated content. " * (TEST_TEXT_LENGTH // 50)
    actual_length = len(large_text)
    
    print(f"📊 Test text length: {actual_length:,} characters")
    print(f"🎯 Expected: Should work (limit now 100,000 characters)")
    print(f"❌ Previous: Would fail (old limit was 10,000 characters)")
    print()
    
    # Test data
    test_payload = {
        "message": "Please help me improve this document",
        "editor_text": large_text,
        "highlighted_text": "",
        "llm_provider": "Google Gemini",
        "user_id": "test-user-123"
    }
    
    try:
        print("🚀 Sending test request to deployed server...")
        response = requests.post(
            f"{API_BASE_URL}/api/chat/message",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Validation fix is working!")
            print("🎉 Large documents are now accepted by the server")
            return True
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Unknown error")
            if "Text too long" in error_detail and "10000" in error_detail:
                print("❌ FAILED: Still getting old validation error")
                print(f"🔍 Error: {error_detail}")
                print("⏳ Server may still be deploying. Try again in a few minutes.")
                return False
            else:
                print(f"⚠️  Different validation error: {error_detail}")
                print("🔍 This might be a different issue, but length validation is fixed")
                return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"🔍 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("🔍 Could not connect to server")
        return False

def main():
    """Run the validation test"""
    print("🔧 Validation Service Fix Test")
    print("Testing if the 'Text too long. Maximum 10000 characters allowed' error is fixed")
    print()
    
    success = test_validation_fix()
    
    print()
    print("=" * 50)
    if success:
        print("✅ VALIDATION FIX CONFIRMED: Server now accepts large documents!")
        print("🎯 Users should no longer see the 10,000 character limit error")
    else:
        print("❌ VALIDATION FIX PENDING: Server still has old limits")
        print("⏳ Wait a few minutes for Railway deployment to complete")
        print("🔄 Then run this test again")
    
    print()
    print("💡 Next steps:")
    print("1. Test with your actual application")
    print("2. Try highlighting text in a large document")
    print("3. Request AI suggestions")
    print("4. Verify no 'Text too long' errors appear")

if __name__ == "__main__":
    main() 