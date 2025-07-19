#!/usr/bin/env python3
"""
Authentication Flow Test Script
Tests the complete authentication flow to verify token storage and refresh fixes.
"""

import requests
import time
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"  # Change to production URL for Railway testing
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def log_test(test_name, success, details=None):
    """Log test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def test_auth_flow():
    """Test complete authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test 1: Login
    print("\n1. Testing Login...")
    try:
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data.get('access_token')
            refresh_token = login_data.get('refresh_token')
            expires_in = login_data.get('expires_in')
            
            log_test("Login", True, f"expires_in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
            
            # Verify token format
            if access_token and refresh_token:
                log_test("Token format", True, f"Access token length: {len(access_token)}")
            else:
                log_test("Token format", False, "Missing access or refresh token")
                return
                
        else:
            log_test("Login", False, f"Status: {login_response.status_code}")
            return
            
    except Exception as e:
        log_test("Login", False, str(e))
        return
    
    # Test 2: Protected endpoint access
    print("\n2. Testing Protected Endpoint Access...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = session.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            log_test("Protected endpoint", True, f"User ID: {profile_data.get('id')}")
        else:
            log_test("Protected endpoint", False, f"Status: {profile_response.status_code}")
            
    except Exception as e:
        log_test("Protected endpoint", False, str(e))
    
    # Test 3: Token refresh
    print("\n3. Testing Token Refresh...")
    try:
        refresh_response = session.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        if refresh_response.status_code == 200:
            refresh_data = refresh_response.json()
            new_access_token = refresh_data.get('access_token')
            new_expires_in = refresh_data.get('expires_in')
            
            log_test("Token refresh", True, f"New expires_in: {new_expires_in} seconds")
            
            # Test new token works
            headers = {"Authorization": f"Bearer {new_access_token}"}
            test_response = session.get(f"{BASE_URL}/api/auth/profile", headers=headers)
            
            if test_response.status_code == 200:
                log_test("New token validation", True)
            else:
                log_test("New token validation", False, f"Status: {test_response.status_code}")
                
        else:
            log_test("Token refresh", False, f"Status: {refresh_response.status_code}")
            
    except Exception as e:
        log_test("Token refresh", False, str(e))
    
    # Test 4: Documents endpoint (was failing with 500 errors)
    print("\n4. Testing Documents Endpoint...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        docs_response = session.get(f"{BASE_URL}/api/documents", headers=headers)
        
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            log_test("Documents endpoint", True, f"Found {len(docs_data.get('documents', []))} documents")
        else:
            log_test("Documents endpoint", False, f"Status: {docs_response.status_code}")
            
    except Exception as e:
        log_test("Documents endpoint", False, str(e))
    
    print("\n" + "=" * 50)
    print("🎯 Authentication Flow Test Complete")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}") 