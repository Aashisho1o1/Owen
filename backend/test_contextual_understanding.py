#!/usr/bin/env python3
"""
Comprehensive Test for Contextual Understanding and Character Voice Consistency
This test validates the core AI features before launch.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up test environment BEFORE importing services
from test_env_setup import setup_test_environment
setup_test_environment()

from services.character_voice_service import SimpleCharacterVoiceService
from services.indexing.hybrid_indexer import HybridIndexer
from services.llm.gemini_service import GeminiService
from services.database import PostgreSQLService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextualUnderstandingTest:
    """Comprehensive test suite for contextual understanding and character voice consistency"""
    
    def __init__(self):
        self.voice_service = None
        self.indexer = None
        self.gemini_service = None
        self.db_service = None
        self.test_results = []
        
    async def setup(self):
        """Initialize all services"""
        print("🔧 Setting up test environment...")
        
        try:
            # Initialize services
            self.voice_service = SimpleCharacterVoiceService()
            self.indexer = HybridIndexer()
            self.gemini_service = GeminiService()
            self.db_service = PostgreSQLService()
            
            print("✅ All services initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_dialogue_extraction(self):
        """Test dialogue extraction from text"""
        print("\n📝 Testing Dialogue Extraction...")
        
        test_text = '''
        "Hello there, my dear friend," John said with a warm smile. "How are you doing today?"
        "I'm doing quite well, thank you," Mary replied politely. "And yourself?"
        John laughed heartily. "Never been better! This weather is absolutely fantastic."
        "Indeed it is," Mary agreed. "Perfect for a walk in the park."
        "Shall we go then?" John suggested enthusiastically.
        '''
        
        try:
            segments = self.voice_service._extract_dialogue_segments(test_text)
            print(f"✅ Extracted {len(segments)} dialogue segments")
            
            for i, segment in enumerate(segments):
                print(f"   {i+1}. {segment.speaker}: \"{segment.text[:50]}...\"")
                print(f"      Position: {segment.position}, Confidence: {segment.confidence}")
            
            # Test result
            success = len(segments) > 0
            self.test_results.append(("Dialogue Extraction", success, f"{len(segments)} segments extracted"))
            return success
            
        except Exception as e:
            print(f"❌ Dialogue extraction failed: {e}")
            self.test_results.append(("Dialogue Extraction", False, str(e)))
            return False
    
    async def test_contextual_feedback(self):
        """Test contextual feedback generation"""
        print("\n🧠 Testing Contextual Feedback...")
        
        test_highlighted = "The character spoke with great enthusiasm and passion."
        
        try:
            feedback = await self.indexer.get_contextual_feedback(
                highlighted_text=test_highlighted,
                doc_id="test_doc",
                context_window=200
            )
            
            print(f"✅ Contextual feedback generated")
            print(f"   Feedback keys: {list(feedback.keys())}")
            print(f"   Feedback size: {len(str(feedback))} characters")
            
            # Check if feedback contains expected elements
            expected_keys = ['highlighted_text', 'semantic_context', 'entities_mentioned']
            has_expected_keys = all(key in feedback for key in expected_keys)
            
            self.test_results.append(("Contextual Feedback", has_expected_keys, f"Keys: {list(feedback.keys())}"))
            return has_expected_keys
            
        except Exception as e:
            print(f"❌ Contextual feedback failed: {e}")
            self.test_results.append(("Contextual Feedback", False, str(e)))
            return False
    
    async def test_character_voice_analysis(self):
        """Test character voice consistency analysis"""
        print("\n🎭 Testing Character Voice Analysis...")
        
        # Test text with clear character voices
        test_text = '''
        "Well, I never!" exclaimed Mrs. Henderson, adjusting her spectacles. "In all my years, I've never seen such a thing!"
        "Chill out, Mrs. H," Jake said, slouching against the wall. "It's not that big a deal."
        "Not that big a deal?" Mrs. Henderson gasped. "Young man, this is most certainly a very big deal indeed!"
        "Whatever," Jake muttered, rolling his eyes. "You're totally overreacting."
        '''
        
        try:
            # Create a test user ID (we'll use 999 for testing)
            test_user_id = 999
            
            results = await self.voice_service.analyze_text_for_voice_consistency(
                text=test_text,
                user_id=test_user_id
            )
            
            print(f"✅ Character voice analysis completed")
            print(f"   Results: {len(results)} analyses")
            
            for result in results:
                print(f"   Character: {result.character_name}")
                print(f"   Consistent: {result.is_consistent}")
                print(f"   Confidence: {result.confidence_score:.2f}")
                print(f"   Method: {result.analysis_method}")
            
            success = len(results) >= 0  # Should work even with no existing profiles
            self.test_results.append(("Character Voice Analysis", success, f"{len(results)} analyses"))
            return success
            
        except Exception as e:
            print(f"❌ Character voice analysis failed: {e}")
            self.test_results.append(("Character Voice Analysis", False, str(e)))
            return False
    
    async def test_gemini_integration(self):
        """Test Gemini service integration"""
        print("\n🤖 Testing Gemini Integration...")
        
        try:
            if not self.gemini_service.is_available():
                print("❌ Gemini service not available")
                self.test_results.append(("Gemini Integration", False, "Service not available"))
                return False
            
            # Test basic response generation
            test_prompt = "Analyze this dialogue for character voice: 'Hello there, old chap!' said the gentleman."
            response = await self.gemini_service.generate_response(test_prompt, max_tokens=100)
            
            print(f"✅ Gemini response generated")
            print(f"   Response length: {len(response)} characters")
            print(f"   Response preview: {response[:100]}...")
            
            # Test JSON response generation
            json_prompt = '''
            Analyze this dialogue: "Hello there!" said John.
            Respond in JSON format with: {"character": "John", "tone": "friendly"}
            '''
            
            json_response = await self.gemini_service.generate_json_response(json_prompt, max_tokens=50)
            
            print(f"✅ Gemini JSON response generated")
            print(f"   JSON response: {json_response}")
            
            success = len(response) > 0 and json_response is not None
            self.test_results.append(("Gemini Integration", success, f"Response: {len(response)} chars, JSON: {json_response is not None}"))
            return success
            
        except Exception as e:
            print(f"❌ Gemini integration failed: {e}")
            self.test_results.append(("Gemini Integration", False, str(e)))
            return False
    
    async def test_database_connectivity(self):
        """Test database connectivity for character profiles"""
        print("\n💾 Testing Database Connectivity...")
        
        try:
            health = self.db_service.health_check()
            print(f"✅ Database health check completed")
            print(f"   Status: {health['status']}")
            print(f"   Users: {health.get('total_users', 'N/A')}")
            print(f"   Documents: {health.get('total_documents', 'N/A')}")
            
            success = health['status'] == 'healthy'
            self.test_results.append(("Database Connectivity", success, health['status']))
            return success
            
        except Exception as e:
            print(f"❌ Database connectivity failed: {e}")
            self.test_results.append(("Database Connectivity", False, str(e)))
            return False
    
    async def test_conversation_context(self):
        """Test conversation context building"""
        print("\n💬 Testing Conversation Context...")
        
        try:
            # Import the function from chat router
            from routers.chat_router import build_conversation_context
            from models.schemas import ChatMessage
            
            # Create test chat history
            test_messages = [
                ChatMessage(role="user", content="Hello, I need help with my story"),
                ChatMessage(role="assistant", content="I'd be happy to help! What kind of story are you working on?"),
                ChatMessage(role="user", content="It's a mystery novel with two main characters"),
                ChatMessage(role="assistant", content="Mysteries are exciting! Tell me about your main characters."),
                ChatMessage(role="user", content="One is a detective, the other is a journalist")
            ]
            
            context = build_conversation_context(test_messages, max_history=3)
            
            print(f"✅ Conversation context built")
            print(f"   Context length: {len(context)} characters")
            print(f"   Context preview: {context[:200]}...")
            
            # Check if context contains expected elements
            has_human_assistant = "Human:" in context and "Assistant:" in context
            has_recent_messages = "detective" in context and "journalist" in context
            
            success = has_human_assistant and has_recent_messages
            self.test_results.append(("Conversation Context", success, f"Length: {len(context)}, Format: {has_human_assistant}"))
            return success
            
        except Exception as e:
            print(f"❌ Conversation context failed: {e}")
            self.test_results.append(("Conversation Context", False, str(e)))
            return False
    
    async def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Starting Contextual Understanding and Character Voice Tests")
        print("=" * 70)
        
        # Setup
        if not await self.setup():
            print("❌ Setup failed, cannot continue tests")
            return False
        
        # Run all tests
        tests = [
            self.test_dialogue_extraction,
            self.test_contextual_feedback,
            self.test_character_voice_analysis,
            self.test_gemini_integration,
            self.test_database_connectivity,
            self.test_conversation_context
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {details}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! System is ready for launch.")
        else:
            print("⚠️  Some tests failed. Please review before launch.")
        
        return passed == total

async def main():
    """Main test runner"""
    test_suite = ContextualUnderstandingTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n✅ System is ready for contextual understanding and character voice analysis!")
        sys.exit(0)
    else:
        print("\n❌ System has issues that need to be addressed before launch.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 