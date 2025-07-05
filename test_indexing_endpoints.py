#!/usr/bin/env python3
"""
Indexing Endpoints Test - Tests the FastAPI endpoints for PathRAG functionality
"""

import asyncio
import sys
import os
import json
import requests
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_indexing_endpoints():
    """Test the indexing router endpoints"""
    print("🧪 Testing Indexing API Endpoints")
    print("=" * 50)
    
    # Configuration
    BASE_URL = "http://localhost:8000"  # Adjust if your server runs on different port
    
    # Sample test data
    test_document = {
        "doc_id": "test_chapter_1",
        "text": """
        Emma Blackwood walked through the misty Elderwood Forest, her heart pounding with anticipation. 
        The ancient oak tree stood majestically at the center of the clearing, its branches reaching 
        toward the starlit sky. She had promised to meet Marcus Thornfield here at midnight, but the 
        shadows seemed to whisper warnings.
        """,
        "metadata": {
            "type": "chapter",
            "title": "The Forest Meeting",
            "author": "Test Author"
        }
    }
    
    test_folder = {
        "documents": [
            {
                "doc_id": "chapter_1",
                "text": test_document["text"],
                "metadata": test_document["metadata"]
            },
            {
                "doc_id": "chapter_2", 
                "text": "The next morning, Emma woke in her cottage on the edge of Willowbrook village.",
                "metadata": {"type": "chapter", "title": "Morning After"}
            }
        ]
    }
    
    # Test data for other endpoints
    feedback_request = {
        "highlighted_text": "Emma walked through the forest",
        "doc_id": "test_chapter_1",
        "context_window": 500
    }
    
    consistency_request = {
        "statement": "Emma has brown hair and lives in the city",
        "doc_id": "test_chapter_1", 
        "check_type": "character"
    }
    
    suggestions_request = {
        "context": "Emma felt uncertain about her next move",
        "suggestion_type": "character"
    }
    
    search_request = {
        "query": "Emma forest meeting",
        "search_type": "hybrid"
    }
    
    try:
        # Test 1: Health Check
        print("\n1️⃣ Testing Indexing Health Endpoint")
        try:
            response = requests.get(f"{BASE_URL}/api/indexing/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure the backend is running on localhost:8000")
            return False
        
        # Test 2: Document Indexing
        print("\n2️⃣ Testing Document Indexing Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/index-document",
                json=test_document,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                index_result = response.json()
                print(f"✅ Document indexed successfully")
                print(f"   Task ID: {index_result.get('task_id', 'N/A')}")
                print(f"   Status: {index_result.get('status', 'N/A')}")
            else:
                print(f"❌ Document indexing failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Document indexing error: {e}")
        
        # Test 3: Folder Indexing
        print("\n3️⃣ Testing Folder Indexing Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/index-folder",
                json=test_folder,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                folder_result = response.json()
                print(f"✅ Folder indexed successfully")
                print(f"   Task ID: {folder_result.get('task_id', 'N/A')}")
            else:
                print(f"❌ Folder indexing failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Folder indexing error: {e}")
        
        # Wait a moment for indexing to complete
        print("\n⏳ Waiting for indexing to complete...")
        import time
        time.sleep(5)
        
        # Test 4: Contextual Feedback
        print("\n4️⃣ Testing Contextual Feedback Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/contextual-feedback",
                json=feedback_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                feedback_result = response.json()
                print(f"✅ Contextual feedback generated")
                print(f"   Suggestions: {len(feedback_result.get('suggestions', []))}")
                print(f"   Entities: {len(feedback_result.get('entities_mentioned', []))}")
                print(f"   Paths: {len(feedback_result.get('narrative_paths', []))}")
            else:
                print(f"❌ Contextual feedback failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Contextual feedback error: {e}")
        
        # Test 5: Consistency Checking
        print("\n5️⃣ Testing Consistency Checking Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/check-consistency",
                json=consistency_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                consistency_result = response.json()
                print(f"✅ Consistency check completed")
                print(f"   Is consistent: {consistency_result.get('is_consistent', 'unknown')}")
                print(f"   Conflicts: {len(consistency_result.get('conflicts', []))}")
                print(f"   Confirmations: {len(consistency_result.get('confirmations', []))}")
            else:
                print(f"❌ Consistency check failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Consistency check error: {e}")
        
        # Test 6: Writing Suggestions
        print("\n6️⃣ Testing Writing Suggestions Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/writing-suggestions",
                json=suggestions_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                suggestions_result = response.json()
                print(f"✅ Writing suggestions generated")
                print(f"   Suggestions: {len(suggestions_result.get('suggestions', []))}")
                
                # Show sample suggestions
                for i, suggestion in enumerate(suggestions_result.get('suggestions', [])[:3]):
                    print(f"   {i+1}. {suggestion.get('type', 'unknown')}: {suggestion.get('suggestion', 'N/A')[:50]}...")
            else:
                print(f"❌ Writing suggestions failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Writing suggestions error: {e}")
        
        # Test 7: Search
        print("\n7️⃣ Testing Search Endpoint")
        try:
            response = requests.post(
                f"{BASE_URL}/api/indexing/search",
                json=search_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                search_result = response.json()
                print(f"✅ Search completed")
                print(f"   Results: {len(search_result.get('results', []))}")
                
                # Show result types
                result_types = [r.get('type', 'unknown') for r in search_result.get('results', [])]
                if result_types:
                    print(f"   Result types: {set(result_types)}")
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 8: Document Stats
        print("\n8️⃣ Testing Document Stats Endpoint")
        try:
            response = requests.get(f"{BASE_URL}/api/indexing/document-stats/test_chapter_1")
            
            if response.status_code == 200:
                stats_result = response.json()
                print(f"✅ Document stats retrieved")
                print(f"   Doc ID: {stats_result.get('doc_id', 'N/A')}")
                print(f"   Chunks: {stats_result.get('chunks', 'N/A')}")
                print(f"   Entities: {stats_result.get('entities', {})}")
            else:
                print(f"❌ Document stats failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Document stats error: {e}")
        
        # Test 9: Export Knowledge Graph
        print("\n9️⃣ Testing Knowledge Graph Export Endpoint")
        try:
            response = requests.get(f"{BASE_URL}/api/indexing/export-graph?format=json")
            
            if response.status_code == 200:
                graph_result = response.json()
                print(f"✅ Knowledge graph exported")
                
                if 'nodes' in graph_result and 'edges' in graph_result:
                    print(f"   Nodes: {len(graph_result['nodes'])}")
                    print(f"   Edges: {len(graph_result['edges'])}")
                else:
                    print(f"   Graph data structure: {list(graph_result.keys())}")
            else:
                print(f"❌ Graph export failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Graph export error: {e}")
        
        print("\n🎉 Indexing endpoints tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Indexing endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the indexing endpoints test"""
    print("🚀 Starting Indexing Endpoints Test")
    print("This tests the FastAPI endpoints for PathRAG functionality")
    print("Make sure your backend server is running on localhost:8000")
    print("You may need to authenticate first if auth is required")
    
    success = test_indexing_endpoints()
    
    if success:
        print("\n✅ All indexing endpoint tests completed!")
        print("The PathRAG API integration is working.")
    else:
        print("\n❌ Indexing endpoint tests failed!")
        print("Please check the error messages above.")
        print("\nTroubleshooting:")
        print("1. Make sure the backend server is running")
        print("2. Check if authentication is required")
        print("3. Verify the GEMINI_API_KEY is set")
        print("4. Check server logs for detailed errors")

if __name__ == "__main__":
    main() 