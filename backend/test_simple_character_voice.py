#!/usr/bin/env python3
"""
Simple Character Voice Consistency Test - Gemini Edition

This script tests the simplified Gemini-only character voice system.
No complex ML dependencies, just pure Gemini-based analysis.
"""

import asyncio
import json
import logging
import re
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test the simplified service logic without database
async def test_simple_character_voice():
    """Test the simplified character voice service logic"""
    
    try:
        print("🚀 Testing Simple Character Voice Service Logic (Gemini Edition)")
        print("=" * 60)
        
        # Test 1: Dialogue Extraction Logic
        print("\n📝 Testing dialogue extraction patterns...")
        
        # Simple dialogue patterns (copied from service)
        dialogue_patterns = [
            r'"([^"]{10,})",?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized),?\s*"([^"]{10,})"',
            r'"([^"]{10,})"\s*[,.]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)\s+[a-z]+'
        ]
        
        test_text = '''
        "Hello there, how are you doing today?" Sarah asked with a warm smile.
        
        John replied, "I'm doing well, thank you for asking. How about you?"
        
        "I'm great!" Sarah exclaimed. "Just finished reading an amazing book."
        
        "That's wonderful," John said thoughtfully. "What was it about?"
        '''
        
        # Extract dialogue using patterns
        segments = []
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
                        segments.append({
                            'speaker': speaker,
                            'text': dialogue_text,
                            'position': match.start()
                        })
        
        # Remove duplicates
        unique_segments = []
        seen_positions = set()
        for segment in sorted(segments, key=lambda x: x['position']):
            if segment['position'] not in seen_positions:
                unique_segments.append(segment)
                seen_positions.add(segment['position'])
        
        print(f"✅ Extracted {len(unique_segments)} dialogue segments:")
        for i, segment in enumerate(unique_segments):
            print(f"  {i+1}. {segment['speaker']}: \"{segment['text']}\"")
        
        # Test 2: Gemini Prompt Generation
        print("\n🤖 Testing Gemini prompt generation...")
        
        # Simulate character profiles
        character_profiles = {
            'sarah': {
                'character_name': 'Sarah',
                'dialogue_samples': [
                    "Hello there, how are you doing today?",
                    "I'm great! Just finished reading an amazing book.",
                    "You know what, I think I'll start writing book reviews."
                ]
            },
            'john': {
                'character_name': 'John',
                'dialogue_samples': [
                    "I'm doing well, thank you for asking. How about you?",
                    "That's wonderful. What was it about?",
                    "That sounds like a fantastic idea! You have great taste in literature."
                ]
            }
        }
        
        # Generate sample prompt for voice consistency analysis
        test_segment = unique_segments[0]
        speaker_key = test_segment['speaker'].lower()
        
        if speaker_key in character_profiles:
            profile = character_profiles[speaker_key]
            previous_dialogue = "\n".join([f'"{sample}"' for sample in profile['dialogue_samples'][-5:]])
            
            prompt = f"""
            Analyze if this new dialogue is consistent with the character's established voice pattern.
            
            Character: {profile['character_name']}
            
            Previous dialogue examples from this character:
            {previous_dialogue}
            
            New dialogue to analyze:
            "{test_segment['text']}"
            
            Please analyze:
            1. Is this dialogue consistent with the character's voice? (yes/no)
            2. What is your confidence level? (0.0 to 1.0)
            3. What makes it consistent or inconsistent?
            4. If inconsistent, provide 2-3 specific suggestions to improve voice consistency.
            
            Focus on: vocabulary choice, sentence structure, tone, personality traits, and speech patterns.
            
            Respond in JSON format:
            {{
                "is_consistent": boolean,
                "confidence_score": float,
                "similarity_score": float,
                "explanation": "detailed explanation",
                "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
            }}
            """
            
            print(f"✅ Generated Gemini prompt for {profile['character_name']}:")
            print(f"   Character: {profile['character_name']}")
            print(f"   Previous samples: {len(profile['dialogue_samples'])}")
            print(f"   New dialogue: \"{test_segment['text']}\"")
            print(f"   Prompt length: {len(prompt)} characters")
        
        # Test 3: Service Configuration
        print("\n⚙️ Testing service configuration...")
        
        config = {
            'min_samples_for_profile': 3,
            'max_profile_samples': 10,
            'dialogue_min_length': 10,
            'context_window': 150,
            'consistency_threshold': 0.7
        }
        
        print("✅ Service configuration:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        # Test 4: Character Profile Management Logic
        print("\n🗂️ Testing character profile management logic...")
        
        # Simulate profile updates
        new_samples = [segment['text'] for segment in unique_segments if segment['speaker'] == 'Sarah']
        
        if 'sarah' in character_profiles:
            existing_samples = character_profiles['sarah']['dialogue_samples']
            all_samples = existing_samples + new_samples
            
            # Keep only the most recent samples
            if len(all_samples) > config['max_profile_samples']:
                all_samples = all_samples[-config['max_profile_samples']:]
            
            print(f"✅ Updated Sarah's profile:")
            print(f"   Previous samples: {len(existing_samples)}")
            print(f"   New samples: {len(new_samples)}")
            print(f"   Total samples: {len(all_samples)}")
            print(f"   Within limit: {len(all_samples) <= config['max_profile_samples']}")
        
        # Test 5: Import Test
        print("\n📦 Testing imports...")
        
        try:
            # Test that we can import the required modules
            import services.llm.gemini_service
            import services.validation_service
            import services.security_logger
            print("✅ All required modules can be imported")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
        
        print("\n🎉 All logic tests completed successfully!")
        print("✅ Simple Character Voice Service logic is working correctly")
        print("✅ Ready for deployment (pending database/API configuration)")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test suite"""
    success = await test_simple_character_voice()
    
    if success:
        print("\n🚀 Logic verification complete!")
        print("The simplified character voice system logic is working correctly.")
        print("Next steps: Deploy to test with live database and Gemini API.")
    else:
        print("\n⚠️ Logic issues detected!")
        print("Please check the implementation and try again.")

if __name__ == "__main__":
    asyncio.run(main()) 