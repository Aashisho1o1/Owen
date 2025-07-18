#!/usr/bin/env python3
"""
Test Voice Analysis Endpoint

Comprehensive test for /api/character-voice/analyze
"""

import requests
import time
import json
import argparse
import base64

# Configuration - Use environment variables for security
def get_config():
    return {
        'base_url': 'http://localhost:8000',  # Change to production URL for Railway testing
        'email': 'test@example.com',
        'password': 'testpassword'
    }

# Function to get auth token
def get_auth_token(base_url, email, password):
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={'username': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        return data['access_token']
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise

# Function to test analyze endpoint
def test_analyze(token, base_url, text, document_id=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text
    }
    if document_id:
        payload['document_id'] = document_id
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/api/character-voice/analyze",
            json=payload,
            headers=headers,
            timeout=30  # Match frontend timeout
        )
        response.raise_for_status()
        end_time = time.time()
        
        data = response.json()
        print(f"✅ Success - Time: {end_time - start_time:.2f}s")
        print(f"Results: {json.dumps(data, indent=2)}")
        return data
    except requests.exceptions.Timeout:
        print(f"❌ Timeout after {time.time() - start_time:.2f}s")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise

# Sample test data
def get_sample_text():
    return """Alice said, "Hello, how are you?"
Bob replied, "I'm fine, thanks!"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Voice Analysis')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--text', help='Test text')
    args = parser.parse_args()
    
    config = get_config()
    base_url = args.url or config['base_url']
    email = args.email or config['email']
    password = args.password or config['password']
    text = args.text or get_sample_text()
    
    print(f"🔧 Config: URL={base_url}, Email={email}")
    
    try:
        token = get_auth_token(base_url, email, password)
        print(f"✅ Token acquired")
        
        results = test_analyze(token, base_url, text)
    except Exception as e:
        print(f"❌ Test failed: {e}") 