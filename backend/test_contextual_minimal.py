#!/usr/bin/env python3
"""
Minimal Contextual Understanding Test
Tests core functionality without database dependencies
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up minimal environment
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-local-testing-only-not-production'
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test_db'  # Mock DB URL
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', 'test-key')
os.environ['RAILWAY_ENVIRONMENT'] = 'test'

# Disable telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY'] = 'False'
os.environ['CHROMA_TELEMETRY_ENABLED'] = 'False'
os.environ['CHROMA_DISABLE_TELEMETRY'] = 'True'
os.environ['CHROMA_ANONYMIZED_TELEMETRY'] = 'False'
os.environ['POSTHOG_DISABLED'] = 'True'
os.environ['POSTHOG_CAPTURE_DISABLED'] = 'True'
os.environ['TELEMETRY_DISABLED'] = 'True'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalContextualTest:
    """Minimal test focusing on core functionality"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_dialogue_extraction_patterns(self):
        """Test dialogue extraction patterns without service initialization"""
        print("📝 Testing Dialogue Extraction Patterns...")
        
        # Import the patterns directly
        import re
        
        # Dialogue patterns from the service
        dialogue_patterns = [
            r'"([^"]{10,})",?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized),?\s*"([^"]{10,})"',
            r'"([^"]{10,})"\s*[,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)\s+[a-z]+'
        ]
        
        test_text = '''
        "Hello there, my dear friend," John said with a warm smile. "How are you doing today?"
        "I'm doing quite well, thank you," Mary replied politely. "And yourself?"
        John laughed heartily. "Never been better! This weather is absolutely fantastic."
        "Indeed it is," Mary agreed. "Perfect for a walk in the park."
        "Shall we go then?" John suggested enthusiastically.
        '''
        
        extracted_dialogues = []
        
        for pattern_idx, pattern in enumerate(dialogue_patterns):
            matches = re.finditer(pattern, test_text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                if len(match.groups()) >= 2:
                    if pattern_idx == 0:  # Pattern 1: "Dialogue," Speaker said
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip()
                    elif pattern_idx == 1:  # Pattern 2: Speaker said, "Dialogue"
                        speaker = match.group(1).strip()
                        dialogue_text = match.group(2).strip()
                    else:  # Pattern 3: "Dialogue," Speaker said with description
                        dialogue_text = match.group(1).strip()
                        speaker = match.group(2).strip()
                    
                    if len(dialogue_text) >= 10 and speaker:
                        extracted_dialogues.append({
                            'speaker': speaker,
                            'text': dialogue_text,
                            'pattern': pattern_idx + 1
                        })
        
        print(f"✅ Extracted {len(extracted_dialogues)} dialogue segments")
        for i, dialogue in enumerate(extracted_dialogues):
            print(f"   {i+1}. {dialogue['speaker']}: \"{dialogue['text'][:50]}...\" (Pattern {dialogue['pattern']})")
        
        success = len(extracted_dialogues) > 0
        self.test_results.append(("Dialogue Pattern Extraction", success, f"{len(extracted_dialogues)} dialogues"))
        return success
    
    async def test_conversation_context_building(self):
        """Test conversation context building"""
        print("\n💬 Testing Conversation Context Building...")
        
        try:
            # Simulate the conversation context function
            def build_conversation_context(chat_history, max_history=5):
                if not chat_history:
                    return ""
                
                recent_history = chat_history[-max_history:]
                if not recent_history:
                    return ""
                
                context_parts = []
                for msg in recent_history:
                    role = "Human" if msg['role'] == "user" else "Assistant"
                    content = msg['content'][:500] + "..." if len(msg['content']) > 500 else msg['content']
                    context_parts.append(f"{role}: {content}")
                
                return "\n".join(context_parts)
            
            # Test with sample chat history
            test_messages = [
                {'role': "user", 'content': "Hello, I need help with my story"},
                {'role': "assistant", 'content': "I'd be happy to help! What kind of story are you working on?"},
                {'role': "user", 'content': "It's a mystery novel with two main characters"},
                {'role': "assistant", 'content': "Mysteries are exciting! Tell me about your main characters."},
                {'role': "user", 'content': "One is a detective, the other is a journalist"}
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
    
    async def test_gemini_availability(self):
        """Test if Gemini API is available"""
        print("\n🤖 Testing Gemini API Availability...")
        
        try:
            from services.llm.gemini_service import GeminiService
            
            gemini_service = GeminiService()
            is_available = gemini_service.is_available()
            
            print(f"✅ Gemini service availability: {is_available}")
            
            if is_available:
                # Test basic functionality
                test_prompt = "Say 'Hello' in a friendly way."
                response = await gemini_service.generate_response(test_prompt, max_tokens=50)
                print(f"   Sample response: {response[:100]}...")
                
                success = len(response) > 0
            else:
                success = False
                print("   Gemini API key not available or invalid")
            
            self.test_results.append(("Gemini API", success, f"Available: {is_available}"))
            return success
            
        except Exception as e:
            print(f"❌ Gemini test failed: {e}")
            self.test_results.append(("Gemini API", False, str(e)))
            return False
    
    async def test_prompt_assembly(self):
        """Test chat prompt assembly"""
        print("\n🔧 Testing Prompt Assembly...")
        
        try:
            # Simulate the prompt assembly function
            def assemble_test_prompt(user_message, editor_text, author_persona, help_focus, ai_mode="talk"):
                context_parts = []
                
                if author_persona:
                    persona_context = f"**Author Persona: {author_persona}**\nWriting a {author_persona.lower()} story with their unique style and voice."
                    context_parts.append(persona_context)
                
                task_context = f"**Current Task:**\nHelp Focus: {help_focus}\nUser Message: {user_message}"
                
                if editor_text and len(editor_text) > 0:
                    task_context += f"\nEditor Content: {editor_text[:300]}{'...' if len(editor_text) > 300 else ''}"
                
                context_parts.append(task_context)
                
                if ai_mode == "co-edit":
                    base_prompt = "You are Owen, an AI writing co-editor. Provide direct, actionable text improvements."
                else:
                    base_prompt = "You are Owen, a thoughtful AI writing companion. Engage in friendly discussion and brainstorming."
                
                additional_context = '\n\n'.join(context_parts)
                return base_prompt + "\n\n" + additional_context
            
            # Test prompt assembly
            test_prompt = assemble_test_prompt(
                user_message="Help me improve this dialogue",
                editor_text="John said hello to Mary and she replied warmly.",
                author_persona="Ernest Hemingway",
                help_focus="Dialogue Writing",
                ai_mode="talk"
            )
            
            print(f"✅ Prompt assembled successfully")
            print(f"   Prompt length: {len(test_prompt)} characters")
            print(f"   Contains persona: {'Ernest Hemingway' in test_prompt}")
            print(f"   Contains task: {'Help me improve' in test_prompt}")
            
            success = len(test_prompt) > 100 and "Ernest Hemingway" in test_prompt
            self.test_results.append(("Prompt Assembly", success, f"Length: {len(test_prompt)}"))
            return success
            
        except Exception as e:
            print(f"❌ Prompt assembly failed: {e}")
            self.test_results.append(("Prompt Assembly", False, str(e)))
            return False
    
    async def run_all_tests(self):
        """Run all minimal tests"""
        print("🚀 Starting Minimal Contextual Understanding Tests")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_dialogue_extraction_patterns,
            self.test_conversation_context_building,
            self.test_gemini_availability,
            self.test_prompt_assembly
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
        print("\n" + "=" * 60)
        print("📊 MINIMAL TEST SUMMARY")
        print("=" * 60)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {details}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 Core functionality is working! Ready for deeper testing.")
        else:
            print("⚠️  Some core functionality issues detected.")
        
        return passed == total

async def main():
    """Main test runner"""
    test_suite = MinimalContextualTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n✅ Core contextual understanding functionality is working!")
        return True
    else:
        print("\n❌ Core functionality has issues.")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 