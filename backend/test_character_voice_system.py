#!/usr/bin/env python3
"""
Character Voice Consistency System Integration Test - TinyStyler Edition

This script tests the complete character voice consistency detection system
with TinyStyler integration to ensure all components work together correctly.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.character_voice_service import CharacterVoiceService, TinyStylerVoiceAnalyzer
from services.database import PostgreSQLService
from services.auth_service import AuthService

class TinyStylerVoiceSystemTest:
    """Test suite for the TinyStyler-based character voice consistency detection system"""
    
    def __init__(self):
        self.voice_service = CharacterVoiceService()
        self.db_service = PostgreSQLService()
        self.auth_service = AuthService()
        self.style_analyzer = TinyStylerVoiceAnalyzer()
        self.test_user_id = None
        self.test_results = []
        
    async def setup_test_environment(self):
        """Set up test environment with a test user"""
        print("🔧 Setting up TinyStyler test environment...")
        
        # Create a test user
        try:
            test_user = self.auth_service.register_user(
                username="tinystyler_test_user",
                email="tinystyler_test@example.com",
                password="test_password_123",
                name="TinyStyler Test User"
            )
            self.test_user_id = test_user['user']['id']
            print(f"✅ Created test user with ID: {self.test_user_id}")
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
            
        # Initialize database (ensure tables exist)
        try:
            self.db_service.init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False
            
        return True
    
    async def test_tinystyler_model_loading(self):
        """Test TinyStyler model loading and initialization"""
        print("\n🤖 Testing TinyStyler model loading...")
        
        try:
            # Test model loading
            self.style_analyzer.ensure_model_loaded()
            
            # Verify model is loaded
            model_loaded = self.style_analyzer.initialized
            tokenizer_loaded = self.style_analyzer.tokenizer is not None
            model_available = self.style_analyzer.model is not None
            
            print(f"📊 Model Status:")
            print(f"  - Initialized: {'✅' if model_loaded else '❌'}")
            print(f"  - Tokenizer: {'✅' if tokenizer_loaded else '❌'}")
            print(f"  - Model: {'✅' if model_available else '❌'}")
            print(f"  - Device: {self.style_analyzer.device}")
            
            success = model_loaded and tokenizer_loaded and model_available
            
            self.test_results.append({
                'test': 'tinystyler_model_loading',
                'success': success,
                'details': f"Model loaded: {model_loaded}, Device: {self.style_analyzer.device}"
            })
            
            if success:
                print("✅ TinyStyler model loading test passed")
            else:
                print("❌ TinyStyler model loading test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ TinyStyler model loading failed: {e}")
            self.test_results.append({
                'test': 'tinystyler_model_loading',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def test_style_embedding_generation(self):
        """Test TinyStyler style embedding generation"""
        print("\n🎨 Testing TinyStyler style embedding generation...")
        
        try:
            # Test dialogue samples for different character styles
            formal_character_samples = [
                "I must express my profound disagreement with your proposal, sir.",
                "Such behavior is entirely inappropriate for a gentleman of your standing.",
                "I would be most grateful if you could reconsider your position."
            ]
            
            casual_character_samples = [
                "Nah, I don't think that's gonna work, dude.",
                "Whatever, I'm cool with that. No big deal.",
                "Hey, wanna grab some pizza later?"
            ]
            
            # Generate embeddings
            formal_embedding = self.style_analyzer.get_style_embedding(formal_character_samples)
            casual_embedding = self.style_analyzer.get_style_embedding(casual_character_samples)
            
            # Verify embeddings
            formal_valid = isinstance(formal_embedding, list) and len(formal_embedding) > 0
            casual_valid = isinstance(casual_embedding, list) and len(casual_embedding) > 0
            
            print(f"📊 Embedding Results:")
            print(f"  - Formal embedding length: {len(formal_embedding)}")
            print(f"  - Casual embedding length: {len(casual_embedding)}")
            print(f"  - Embeddings are different: {formal_embedding != casual_embedding}")
            
            # Test similarity calculation
            similarity = self.style_analyzer.calculate_style_similarity(formal_embedding, casual_embedding)
            print(f"  - Style similarity: {similarity:.3f}")
            
            success = formal_valid and casual_valid and similarity < 0.8  # Different styles should have low similarity
            
            self.test_results.append({
                'test': 'style_embedding_generation',
                'success': success,
                'details': f"Embeddings generated, similarity: {similarity:.3f}"
            })
            
            if success:
                print("✅ Style embedding generation test passed")
            else:
                print("❌ Style embedding generation test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ Style embedding generation failed: {e}")
            self.test_results.append({
                'test': 'style_embedding_generation',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def test_style_transfer_analysis(self):
        """Test TinyStyler style transfer analysis"""
        print("\n🔄 Testing TinyStyler style transfer analysis...")
        
        try:
            # Test style transfer analysis
            source_text = "I disagree with your assessment of the situation."
            target_samples = [
                "Nah, that's totally wrong, man.",
                "Dude, you're way off base here.",
                "No way, that's not how it is at all."
            ]
            
            # Perform style analysis
            analysis = self.style_analyzer.analyze_style_transfer(source_text, target_samples)
            
            # Verify analysis results
            has_consistency_score = 'consistency_score' in analysis
            has_is_consistent = 'is_consistent' in analysis
            has_transferred_text = 'style_transferred_text' in analysis
            has_analysis_method = 'analysis_method' in analysis
            
            print(f"📊 Style Transfer Analysis:")
            print(f"  - Consistency Score: {analysis.get('consistency_score', 'N/A')}")
            print(f"  - Is Consistent: {analysis.get('is_consistent', 'N/A')}")
            print(f"  - Original: {analysis.get('original_text', 'N/A')}")
            print(f"  - Transferred: {analysis.get('style_transferred_text', 'N/A')[:50]}...")
            print(f"  - Method: {analysis.get('analysis_method', 'N/A')}")
            
            success = all([has_consistency_score, has_is_consistent, has_transferred_text, has_analysis_method])
            
            self.test_results.append({
                'test': 'style_transfer_analysis',
                'success': success,
                'details': f"Analysis completed, consistency: {analysis.get('consistency_score', 0):.3f}"
            })
            
            if success:
                print("✅ Style transfer analysis test passed")
            else:
                print("❌ Style transfer analysis test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ Style transfer analysis failed: {e}")
            self.test_results.append({
                'test': 'style_transfer_analysis',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def test_dialogue_extraction(self):
        """Test dialogue extraction from text"""
        print("\n📝 Testing dialogue extraction...")
        
        test_text = '''
        "I simply cannot believe what you're telling me!" Alice exclaimed with indignation. "This is absolutely preposterous!"
        
        Bob looked up from his book. "Hey, what's the big deal? It's not that serious, dude."
        
        "The big deal," Alice replied coldly, "is that proper etiquette demands certain standards of behavior."
        
        "Whatever, Alice," Bob said with a shrug. "I'm just gonna do my own thing."
        '''
        
        # Extract dialogue segments
        segments = self.voice_service._extract_dialogue_segments(test_text)
        
        print(f"📊 Extracted {len(segments)} dialogue segments:")
        for i, segment in enumerate(segments):
            print(f"  {i+1}. {segment.speaker}: \"{segment.text[:50]}...\"")
            
        # Verify we found the expected dialogues
        expected_speakers = ["Alice", "Bob"]
        found_speakers = [seg.speaker for seg in segments if seg.speaker]
        
        success = len(segments) >= 3 and all(speaker in found_speakers for speaker in expected_speakers)
        
        self.test_results.append({
            'test': 'dialogue_extraction',
            'success': success,
            'details': f"Found {len(segments)} segments with speakers: {found_speakers}"
        })
        
        if success:
            print("✅ Dialogue extraction test passed")
        else:
            print("❌ Dialogue extraction test failed")
            
        return success
    
    async def test_character_voice_profiling(self):
        """Test character voice profile creation with TinyStyler"""
        print("\n👤 Testing TinyStyler character voice profiling...")
        
        try:
            # Sample dialogue for building character profiles
            character_texts = {
                "Alice": [
                    "I simply cannot believe what you're telling me! This is absolutely preposterous!",
                    "Well, I never! Such behavior is completely unacceptable in polite society.",
                    "My dear fellow, you must understand that proper etiquette demands certain standards.",
                    "I am profoundly disappointed by this turn of events, I must say."
                ],
                "Bob": [
                    "Hey, what's up? Just chillin' here, you know?",
                    "Dude, that's totally awesome! I'm so stoked about this.",
                    "Yeah, whatever. I'm cool with that, no worries.",
                    "Nah, I don't think that's gonna work, man."
                ]
            }
            
            for character_name, dialogues in character_texts.items():
                # Create mock dialogue segments
                segments = []
                for dialogue in dialogues:
                    segment = self.voice_service.DialogueSegment(
                        text=dialogue,
                        speaker=character_name,
                        context_before="",
                        context_after="",
                        position=0,
                        confidence=0.9
                    )
                    segments.append(segment)
                
                # Update character profile using TinyStyler
                await self.voice_service._update_character_profiles_tinystyler(segments, self.test_user_id)
            
            # Verify profiles were created
            profiles = await self.voice_service.get_character_profiles(self.test_user_id)
            
            success = len(profiles) >= 2
            profile_names = [p['character_name'] for p in profiles]
            
            print(f"📊 Created {len(profiles)} character profiles:")
            for profile in profiles:
                print(f"  - {profile['character_name']}: {profile['sample_count']} samples")
            
            self.test_results.append({
                'test': 'character_voice_profiling',
                'success': success,
                'details': f"Created profiles for: {profile_names}"
            })
            
            if success:
                print("✅ Character voice profiling test passed")
            else:
                print("❌ Character voice profiling test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ Character voice profiling failed: {e}")
            self.test_results.append({
                'test': 'character_voice_profiling',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def test_voice_consistency_analysis(self):
        """Test TinyStyler voice consistency analysis"""
        print("\n🎭 Testing TinyStyler voice consistency analysis...")
        
        try:
            # Test text with consistent and inconsistent dialogue
            test_text = '''
            "I simply cannot believe this outrageous behavior!" Alice exclaimed. "This is absolutely unacceptable!"
            
            "Yeah, whatever dude," Alice said casually. "I'm totally cool with it."
            
            "Hey there, buddy!" Bob said cheerfully. "What's happening, man?"
            
            "I must express my profound disappointment," Bob declared formally. "Such conduct is most unseemly."
            '''
            
            # Analyze voice consistency using TinyStyler
            results = await self.voice_service.analyze_text_for_voice_consistency(
                text=test_text,
                user_id=self.test_user_id
            )
            
            print(f"📊 TinyStyler analysis results: {len(results)} segments analyzed")
            
            # Check results
            inconsistent_found = False
            tinystyler_method_used = False
            
            for result in results:
                consistency_status = "✅ Consistent" if result.is_consistent else "❌ Inconsistent"
                print(f"  {result.character_name}: {consistency_status} (confidence: {result.confidence_score:.2f})")
                print(f"    Method: {result.analysis_method}")
                
                if not result.is_consistent:
                    inconsistent_found = True
                    print(f"    Explanation: {result.explanation}")
                    if result.suggestions:
                        print(f"    Suggestion: {result.suggestions[0]}")
                
                if 'tinystyler' in result.analysis_method:
                    tinystyler_method_used = True
            
            # We expect to find inconsistencies and TinyStyler method usage
            success = len(results) > 0 and inconsistent_found and tinystyler_method_used
            
            self.test_results.append({
                'test': 'voice_consistency_analysis',
                'success': success,
                'details': f"Analyzed {len(results)} segments, found inconsistencies: {inconsistent_found}, TinyStyler used: {tinystyler_method_used}"
            })
            
            if success:
                print("✅ TinyStyler voice consistency analysis test passed")
            else:
                print("❌ TinyStyler voice consistency analysis test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ TinyStyler voice consistency analysis failed: {e}")
            self.test_results.append({
                'test': 'voice_consistency_analysis',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def test_service_health(self):
        """Test service health check with TinyStyler"""
        print("\n🏥 Testing service health with TinyStyler...")
        
        try:
            health_status = await self.voice_service.get_service_health()
            
            success = health_status['status'] == 'healthy'
            
            print(f"Service status: {health_status['status']}")
            print(f"Database: {'✅' if health_status.get('database') else '❌'}")
            print(f"TinyStyler model: {'✅' if health_status.get('tinystyler_model') else '❌'}")
            print(f"Gemini service: {'✅' if health_status.get('gemini_service') else '❌'}")
            print(f"Device: {health_status.get('device', 'unknown')}")
            
            self.test_results.append({
                'test': 'service_health',
                'success': success,
                'details': f"Status: {health_status['status']}, Device: {health_status.get('device', 'unknown')}"
            })
            
            if success:
                print("✅ Service health test passed")
            else:
                print("❌ Service health test failed")
                
            return success
            
        except Exception as e:
            print(f"❌ Service health test failed: {e}")
            self.test_results.append({
                'test': 'service_health',
                'success': False,
                'details': f"Exception: {str(e)}"
            })
            return False
    
    async def cleanup_test_environment(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            # Delete test user and all associated data
            if self.test_user_id:
                # Delete character profiles
                profiles = await self.voice_service.get_character_profiles(self.test_user_id)
                for profile in profiles:
                    await self.voice_service.delete_character_profile(
                        self.test_user_id, profile['character_name']
                    )
                
                # Delete user (cascades to all related data)
                self.db_service.execute_query(
                    "DELETE FROM users WHERE id = %s",
                    (self.test_user_id,)
                )
                
                print(f"✅ Cleaned up test user {self.test_user_id}")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    async def run_all_tests(self):
        """Run all TinyStyler tests and report results"""
        print("🚀 Starting TinyStyler Character Voice Consistency System Tests")
        print("=" * 70)
        
        # Setup
        if not await self.setup_test_environment():
            print("❌ Failed to set up test environment")
            return False
        
        # Run tests
        tests = [
            self.test_tinystyler_model_loading,
            self.test_style_embedding_generation,
            self.test_style_transfer_analysis,
            self.test_dialogue_extraction,
            self.test_character_voice_profiling,
            self.test_voice_consistency_analysis,
            self.test_service_health
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                self.test_results.append({
                    'test': test.__name__,
                    'success': False,
                    'details': f"Exception: {str(e)}"
                })
        
        # Cleanup
        await self.cleanup_test_environment()
        
        # Report results
        print("\n" + "=" * 70)
        print("📊 TINYSTYLER TEST RESULTS SUMMARY")
        print("=" * 70)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} | {result['test']}: {result['details']}")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! TinyStyler character voice system is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the TinyStyler system configuration.")
            return False

async def main():
    """Main test runner"""
    test_suite = TinyStylerVoiceSystemTest()
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 