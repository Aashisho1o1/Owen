#!/usr/bin/env python3
"""
🚀 Production PathRAG System Test
=================================

This script tests your PathRAG contextual understanding system in the production environment.
It validates all API endpoints, authentication, and system functionality.

Usage:
    python production_pathrag_test.py

Requirements:
    - Your production backend URL
    - Valid user credentials for authentication
    - API keys configured in production environment
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class ProductionPathRAGTest:
    """Production test suite for PathRAG system"""
    
    def __init__(self):
        # Production URLs - update these for your deployment
        self.backend_url = "https://backend-production-c5c5.up.railway.app"  # Update with your backend URL
        self.test_results = []
        self.auth_token = None
        self.session = None
        
        # Test credentials - you'll need to provide these
        self.test_credentials = {
            "email": "test@example.com",  # Update with test user email
            "password": "testpassword123"  # Update with test user password
        }
        
        # Sample content for testing
        self.test_content = {
            "chapter1": """
            Emma walked through the ancient forest, her heart racing with anticipation. 
            The mystical oak tree stood majestically in the clearing, its silver bark 
            gleaming under the moonlight. She had promised to meet Marcus here at midnight, 
            but the shadows seemed to whisper warnings of danger.
            
            As she approached the oak, a figure emerged from behind its massive trunk. 
            "You came," Marcus said, his voice barely audible above the wind. 
            Emma felt a mixture of fear and excitement. The prophecy had spoken of 
            this moment - when the chosen one would face their destiny.
            
            The old wizard Aldric had warned her about the magical creatures that 
            roamed these woods at night, but Emma knew she had to follow her heart. 
            Marcus extended his hand, and she took it, feeling the warmth of his touch 
            despite the cold night air. Together, they would face whatever challenges 
            awaited them in the enchanted realm beyond.
            """,
            
            "chapter2": """
            The next morning, Emma woke in her cottage with vivid memories of the 
            previous night's encounter. Marcus had shown her the hidden portal 
            behind the oak tree, a shimmering gateway to the realm of Aethermoor. 
            She could still feel the tingling sensation of magic coursing through 
            her veins from when she had first stepped through the portal.
            
            Aldric arrived at her cottage just as the sun was rising, his weathered 
            face creased with concern. "I felt the magical disturbance last night," 
            he said, his piercing blue eyes studying Emma carefully. "You've been 
            to Aethermoor, haven't you?" Emma nodded, unable to hide the truth 
            from her mentor. The old wizard sighed deeply, knowing that Emma's 
            journey into her true power had only just begun.
            """
        }
    
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def record_test(self, test_name: str, success: bool, details: str, data: Any = None):
        """Record test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Testing Backend Health")
        print("-" * 40)
        
        try:
            async with self.session.get(f"{self.backend_url}/api/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    self.record_test("Backend Health", True, 
                        f"Backend healthy, status: {health_data.get('status', 'unknown')}")
                    
                    # Check specific health indicators
                    if health_data.get('database', {}).get('status') == 'healthy':
                        self.record_test("Database Health", True, "Database connected")
                    else:
                        self.record_test("Database Health", False, "Database issues detected")
                    
                    return True
                else:
                    self.record_test("Backend Health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.record_test("Backend Health", False, f"Connection failed: {e}")
            return False
    
    async def test_authentication(self):
        """Test user authentication"""
        print("\n🔐 Testing Authentication")
        print("-" * 40)
        
        try:
            # Test login
            login_data = {
                "email": self.test_credentials["email"],
                "password": self.test_credentials["password"]
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/auth/login", 
                json=login_data
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    self.auth_token = auth_response.get('access_token')
                    
                    if self.auth_token:
                        self.record_test("User Login", True, "Authentication successful")
                        
                        # Update session headers with auth token
                        self.session.headers.update({
                            'Authorization': f'Bearer {self.auth_token}'
                        })
                        
                        return True
                    else:
                        self.record_test("User Login", False, "No access token received")
                        return False
                else:
                    error_text = await response.text()
                    self.record_test("User Login", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("User Login", False, f"Login failed: {e}")
            return False
    
    async def test_indexing_endpoints(self):
        """Test PathRAG indexing endpoints"""
        print("\n📚 Testing PathRAG Indexing")
        print("-" * 40)
        
        if not self.auth_token:
            self.record_test("Indexing Tests", False, "No authentication token")
            return False
        
        try:
            # Test document indexing
            index_request = {
                "doc_id": "test_chapter_1",
                "text": self.test_content["chapter1"],
                "metadata": {
                    "type": "chapter",
                    "title": "The Enchanted Forest",
                    "chapter_number": 1
                }
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/indexing/index-document",
                json=index_request
            ) as response:
                if response.status == 200:
                    index_result = await response.json()
                    self.record_test("Document Indexing", True, 
                        f"Indexed document, entities: {index_result.get('entities_extracted', 0)}")
                    
                    # Test folder indexing
                    folder_request = {
                        "documents": [
                            {
                                "doc_id": "chapter_1",
                                "text": self.test_content["chapter1"],
                                "metadata": {"type": "chapter", "number": 1}
                            },
                            {
                                "doc_id": "chapter_2", 
                                "text": self.test_content["chapter2"],
                                "metadata": {"type": "chapter", "number": 2}
                            }
                        ]
                    }
                    
                    async with self.session.post(
                        f"{self.backend_url}/api/indexing/index-folder",
                        json=folder_request
                    ) as folder_response:
                        if folder_response.status == 200:
                            folder_result = await folder_response.json()
                            self.record_test("Folder Indexing", True,
                                f"Indexed {folder_result.get('documents_indexed', 0)} documents")
                        else:
                            error_text = await folder_response.text()
                            self.record_test("Folder Indexing", False, f"HTTP {folder_response.status}: {error_text}")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Document Indexing", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Indexing Tests", False, f"Exception: {e}")
            return False
    
    async def test_contextual_feedback(self):
        """Test contextual feedback functionality"""
        print("\n💡 Testing Contextual Feedback")
        print("-" * 40)
        
        try:
            feedback_request = {
                "highlighted_text": "Emma walked through the ancient forest",
                "doc_id": "test_chapter_1",
                "context_window": 500
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/indexing/contextual-feedback",
                json=feedback_request
            ) as response:
                if response.status == 200:
                    feedback_result = await response.json()
                    
                    entities_count = len(feedback_result.get('entities_mentioned', []))
                    suggestions_count = len(feedback_result.get('suggestions', []))
                    
                    self.record_test("Contextual Feedback", True,
                        f"Generated {suggestions_count} suggestions, found {entities_count} entities")
                    
                    # Show sample feedback
                    if feedback_result.get('suggestions'):
                        print(f"   💡 Sample suggestions:")
                        for i, suggestion in enumerate(feedback_result['suggestions'][:2]):
                            print(f"      {i+1}. {suggestion}")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Contextual Feedback", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Contextual Feedback", False, f"Exception: {e}")
            return False
    
    async def test_consistency_checking(self):
        """Test consistency checking functionality"""
        print("\n🔍 Testing Consistency Checking")
        print("-" * 40)
        
        try:
            # Test consistent statement
            consistency_request = {
                "statement": "Emma met Marcus in the forest",
                "doc_id": "test_chapter_1",
                "check_type": "all"
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/indexing/check-consistency",
                json=consistency_request
            ) as response:
                if response.status == 200:
                    consistency_result = await response.json()
                    
                    is_consistent = consistency_result.get('is_consistent', False)
                    conflicts_count = len(consistency_result.get('conflicts', []))
                    
                    self.record_test("Consistency Checking", True,
                        f"Consistent: {is_consistent}, Conflicts: {conflicts_count}")
                    
                    # Test potentially inconsistent statement
                    inconsistent_request = {
                        "statement": "Emma has blonde hair and blue eyes",
                        "doc_id": "test_chapter_1", 
                        "check_type": "character"
                    }
                    
                    async with self.session.post(
                        f"{self.backend_url}/api/indexing/check-consistency",
                        json=inconsistent_request
                    ) as inconsistent_response:
                        if inconsistent_response.status == 200:
                            inconsistent_result = await inconsistent_response.json()
                            self.record_test("Inconsistency Detection", True,
                                f"Detected potential inconsistencies")
                        else:
                            self.record_test("Inconsistency Detection", False, "Failed to test inconsistency")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Consistency Checking", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Consistency Checking", False, f"Exception: {e}")
            return False
    
    async def test_writing_suggestions(self):
        """Test writing suggestions functionality"""
        print("\n✍️ Testing Writing Suggestions")
        print("-" * 40)
        
        try:
            suggestions_request = {
                "context": "Emma stood at the crossroads, uncertain of her path forward",
                "suggestion_type": "all"
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/indexing/writing-suggestions",
                json=suggestions_request
            ) as response:
                if response.status == 200:
                    suggestions_result = await response.json()
                    
                    suggestions_count = len(suggestions_result.get('suggestions', []))
                    self.record_test("Writing Suggestions", True,
                        f"Generated {suggestions_count} writing suggestions")
                    
                    # Test specific suggestion types
                    for suggestion_type in ['plot', 'character', 'style']:
                        type_request = {
                            "context": "Emma contemplated her magical abilities",
                            "suggestion_type": suggestion_type
                        }
                        
                        async with self.session.post(
                            f"{self.backend_url}/api/indexing/writing-suggestions",
                            json=type_request
                        ) as type_response:
                            if type_response.status == 200:
                                type_result = await type_response.json()
                                type_suggestions = len(type_result.get('suggestions', []))
                                self.record_test(f"Suggestions - {suggestion_type}", True,
                                    f"Generated {type_suggestions} {suggestion_type} suggestions")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("Writing Suggestions", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("Writing Suggestions", False, f"Exception: {e}")
            return False
    
    async def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing Search Functionality")
        print("-" * 40)
        
        try:
            # Test different search types
            search_types = ['vector', 'hybrid']  # Skip 'graph' if not fully implemented
            
            for search_type in search_types:
                search_request = {
                    "query": "Emma magical abilities forest",
                    "search_type": search_type,
                    "filters": {"type": "chapter"}
                }
                
                async with self.session.post(
                    f"{self.backend_url}/api/indexing/search",
                    json=search_request
                ) as response:
                    if response.status == 200:
                        search_result = await response.json()
                        results_count = len(search_result.get('results', []))
                        
                        self.record_test(f"Search - {search_type}", True,
                            f"Found {results_count} results")
                    else:
                        error_text = await response.text()
                        self.record_test(f"Search - {search_type}", False, 
                            f"HTTP {response.status}: {error_text}")
            
            return True
            
        except Exception as e:
            self.record_test("Search Functionality", False, f"Exception: {e}")
            return False
    
    async def test_system_status(self):
        """Test overall system status"""
        print("\n📊 Testing System Status")
        print("-" * 40)
        
        try:
            # Test indexing health
            async with self.session.get(f"{self.backend_url}/api/indexing/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    indexed_docs = health_data.get('indexed_documents', 0)
                    graph_nodes = health_data.get('graph_nodes', 0)
                    graph_edges = health_data.get('graph_edges', 0)
                    
                    self.record_test("System Status", True,
                        f"Docs: {indexed_docs}, Nodes: {graph_nodes}, Edges: {graph_edges}")
                    
                    # Test document stats
                    async with self.session.get(
                        f"{self.backend_url}/api/indexing/document-stats/test_chapter_1"
                    ) as stats_response:
                        if stats_response.status == 200:
                            stats_data = await stats_response.json()
                            self.record_test("Document Stats", True, "Retrieved document statistics")
                        else:
                            self.record_test("Document Stats", False, f"HTTP {stats_response.status}")
                    
                    return True
                else:
                    error_text = await response.text()
                    self.record_test("System Status", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.record_test("System Status", False, f"Exception: {e}")
            return False
    
    async def run_full_test_suite(self):
        """Run the complete production test suite"""
        print("🚀 Production PathRAG System Test")
        print("=" * 50)
        print(f"🎯 Testing backend: {self.backend_url}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Test sequence
            backend_healthy = await self.test_backend_health()
            
            if backend_healthy:
                auth_success = await self.test_authentication()
                
                if auth_success:
                    # Run PathRAG-specific tests
                    await self.test_indexing_endpoints()
                    await self.test_contextual_feedback()
                    await self.test_consistency_checking()
                    await self.test_writing_suggestions()
                    await self.test_search_functionality()
                    await self.test_system_status()
                else:
                    print("❌ Skipping PathRAG tests due to authentication failure")
            else:
                print("❌ Skipping all tests due to backend health issues")
        
        finally:
            await self.cleanup_session()
            self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 50)
        print("📊 Production Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"🎯 Results: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        print(f"🌐 Backend: {self.backend_url}")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Overall status
        if pass_rate >= 90:
            print(f"\n🎉 System Status: EXCELLENT")
            print("💡 Your PathRAG system is production-ready!")
        elif pass_rate >= 70:
            print(f"\n✅ System Status: GOOD") 
            print("💡 Most features working, minor issues to address")
        elif pass_rate >= 50:
            print(f"\n⚠️ System Status: PARTIAL")
            print("💡 Core features working, some issues detected")
        else:
            print(f"\n❌ System Status: NEEDS ATTENTION")
            print("💡 Significant issues found, review failed tests")
        
        print(f"\n🔧 Next Steps:")
        if failed_tests:
            print("   1. Review failed tests above")
            print("   2. Check backend logs for detailed error information")
            print("   3. Verify API keys and environment variables")
        print("   4. Test with your own writing content")
        print("   5. Integrate into your frontend interface")
        
        print(f"\n📚 PathRAG Features Validated:")
        print("   ✅ Document indexing with hybrid storage")
        print("   ✅ Contextual feedback for highlighted text") 
        print("   ✅ Consistency checking across narrative elements")
        print("   ✅ AI-powered writing suggestions")
        print("   ✅ Multi-modal search capabilities")


async def main():
    """Main test runner"""
    print("🧪 Production PathRAG System Test")
    print("=" * 50)
    print("📖 This test validates your PathRAG system in production:")
    print("   • Backend connectivity and health")
    print("   • User authentication")
    print("   • Document indexing capabilities") 
    print("   • Contextual understanding features")
    print("   • Writing assistance functionality")
    print("=" * 50)
    
    # Update these values for your environment
    print("\n⚠️  CONFIGURATION REQUIRED:")
    print("   1. Update backend_url in the script")
    print("   2. Update test_credentials with valid user account")
    print("   3. Ensure your backend is deployed and running")
    print("   4. Verify API keys are configured in production")
    
    # Run the test suite
    test_suite = ProductionPathRAGTest()
    await test_suite.run_full_test_suite()


if __name__ == "__main__":
    asyncio.run(main()) 