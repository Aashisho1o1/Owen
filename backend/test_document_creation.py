#!/usr/bin/env python3
"""
Test script to verify document creation functionality
"""

import requests
import json
from datetime import datetime

# API configuration
API_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "password123"
}

def test_health_check():
    """Test API health endpoint"""
    print("\n1. Testing API health...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_login():
    """Test user login"""
    print("\n2. Testing login...")
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json=TEST_USER
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful! Token: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print(f"Login failed: {response.text}")
        return None

def test_create_document(token):
    """Test document creation"""
    print("\n3. Testing document creation...")
    
    document_data = {
        "title": f"Test Document {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": "This is a test document created via API.",
        "document_type": "novel",
        "tags": ["test", "api"],
        "status": "draft"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Request data: {json.dumps(document_data, indent=2)}")
    
    response = requests.post(
        f"{API_URL}/api/documents",
        json=document_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Document created successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
        return data['id']
    else:
        print(f"Document creation failed: {response.text}")
        return None

def test_list_documents(token):
    """Test listing documents"""
    print("\n4. Testing document listing...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{API_URL}/api/documents",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['documents'])} documents")
        for doc in data['documents'][:3]:  # Show first 3
            print(f"  - {doc['title']} (ID: {doc['id']})")
    else:
        print(f"Failed to list documents: {response.text}")

def main():
    """Run all tests"""
    print("=== DOG Writer API Test ===")
    
    # Test health check
    if not test_health_check():
        print("\nAPI is not healthy. Check if backend is running.")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("\nLogin failed. Cannot proceed with authenticated tests.")
        return
    
    # Test document creation
    doc_id = test_create_document(token)
    
    # Test listing documents
    test_list_documents(token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 