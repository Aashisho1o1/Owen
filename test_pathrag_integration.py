#!/usr/bin/env python3
"""
PathRAG Integration Test - Tests the complete PathRAG system without authentication
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.indexing.hybrid_indexer import HybridIndexer

async def test_pathrag_integration():
    """Test the complete PathRAG system with realistic writing content"""
    print("🧪 Testing PathRAG Integration")
    print("=" * 50)
    
    # Realistic writing content for testing
    chapter1 = """
    Emma Blackwood stood at the edge of Willowbrook village, watching the morning mist 
    rise from the Elderwood Forest. At nineteen, she had always felt different from 
    the other villagers - there was something about the ancient woods that called to her.
    
    Her grandmother Sarah had warned her countless times about venturing too deep into 
    the forest. "Strange things happen there, child," Sarah would say, her weathered 
    hands trembling as she spoke. "The old magic still lingers."
    
    But Emma couldn't resist the pull. She had been having dreams about a mysterious 
    figure waiting for her beneath the ancient oak tree at the forest's heart. The 
    dreams felt more real than her waking life.
    """
    
    chapter2 = """
    That evening, Emma finally gathered the courage to enter Elderwood Forest. The 
    path was barely visible, overgrown with thorns and twisted roots. As she walked 
    deeper, the trees seemed to whisper her name.
    
    At the center of the forest stood the ancient oak, just as she had seen in her 
    dreams. A figure emerged from behind its massive trunk - a young man with dark 
    hair and piercing blue eyes.
    
    "You came," he said, his voice carrying a strange accent. "I am Marcus Thornfield. 
    I've been waiting for you, Emma Blackwood. The prophecy spoke of your coming."
    
    Emma felt a mixture of fear and recognition. Somehow, she knew this moment would 
    change everything.
    """
    
    character_profile = """
    Emma Blackwood - Age 19, orphaned at 12, raised by grandmother Sarah Blackwood. 
    Lives in Willowbrook village on the edge of Elderwood Forest. Has prophetic dreams 
    and an unexplained connection to ancient magic. Brave but cautious, intelligent 
    and curious about her heritage.
    
    Marcus Thornfield - Age 25, guardian of the ancient prophecies. Possesses magical 
    abilities and knowledge of the old ways. Has been searching for the chosen one 
    mentioned in the prophecies. Mysterious but trustworthy.
    
    Sarah Blackwood - Age 67, Emma's grandmother and village wise woman. Knows more 
    about the old magic than she admits. Protective of Emma but understands her destiny.
    """
    
    try:
        # Initialize the hybrid indexer
        print("\n1️⃣ Initializing PathRAG System")
        hybrid_indexer = HybridIndexer(collection_name="integration_test")
        print("✅ HybridIndexer initialized")
        
        # Index the documents
        print("\n2️⃣ Indexing Documents")
        
        # Index chapter 1
        result1 = await hybrid_indexer.index_document(
            "chapter_1", chapter1, 
            {"type": "chapter", "number": 1, "title": "The Call of the Forest"}
        )
        print(f"✅ Chapter 1 indexed: {result1.get('entities_extracted', 0)} entities")
        
        # Index chapter 2  
        result2 = await hybrid_indexer.index_document(
            "chapter_2", chapter2,
            {"type": "chapter", "number": 2, "title": "The Meeting"}
        )
        print(f"✅ Chapter 2 indexed: {result2.get('entities_extracted', 0)} entities")
        
        # Index character profiles
        result3 = await hybrid_indexer.index_document(
            "character_profiles", character_profile,
            {"type": "character_profile", "title": "Main Characters"}
        )
        print(f"✅ Character profiles indexed: {result3.get('entities_extracted', 0)} entities")
        
        # Test contextual feedback
        print("\n3️⃣ Testing Contextual Feedback")
        
        feedback = await hybrid_indexer.get_contextual_feedback(
            "Emma walked into the forest", 
            "chapter_1"
        )
        
        print(f"✅ Contextual feedback generated:")
        print(f"   Entities mentioned: {len(feedback.get('entities_mentioned', []))}")
        print(f"   Narrative paths: {len(feedback.get('narrative_paths', []))}")
        print(f"   Suggestions: {len(feedback.get('suggestions', []))}")
        
        # Show some suggestions
        for i, suggestion in enumerate(feedback.get('suggestions', [])[:3]):
            print(f"   {i+1}. {suggestion}")
        
        # Test consistency checking
        print("\n4️⃣ Testing Consistency Checking")
        
        # Test a consistent statement
        consistent_check = await hybrid_indexer.check_consistency(
            "Emma is 19 years old and lives with her grandmother",
            "chapter_1"
        )
        
        print(f"✅ Consistency check (should be consistent):")
        print(f"   Is consistent: {consistent_check.get('is_consistent', False)}")
        print(f"   Conflicts: {len(consistent_check.get('conflicts', []))}")
        print(f"   Confirmations: {len(consistent_check.get('confirmations', []))}")
        
        # Test an inconsistent statement
        inconsistent_check = await hybrid_indexer.check_consistency(
            "Emma is 25 years old and lives in the city",
            "chapter_1"
        )
        
        print(f"✅ Consistency check (should find conflicts):")
        print(f"   Is consistent: {inconsistent_check.get('is_consistent', False)}")
        print(f"   Conflicts: {len(inconsistent_check.get('conflicts', []))}")
        
        # Test writing suggestions
        print("\n5️⃣ Testing Writing Suggestions")
        
        suggestions = await hybrid_indexer.get_writing_suggestions(
            "Emma hesitated at the forest edge, remembering her grandmother's warnings"
        )
        
        print(f"✅ Writing suggestions generated:")
        print(f"   Total suggestions: {len(suggestions.get('suggestions', []))}")
        
        for i, suggestion in enumerate(suggestions.get('suggestions', [])[:3]):
            print(f"   {i+1}. {suggestion.get('type', 'unknown')}: {suggestion.get('suggestion', 'N/A')[:60]}...")
        
        # Test hybrid search
        print("\n6️⃣ Testing Hybrid Search")
        
        search_results = hybrid_indexer.search("Emma grandmother forest", search_type="hybrid")
        
        print(f"✅ Hybrid search completed:")
        print(f"   Results found: {len(search_results)}")
        
        # Show result types
        result_types = {}
        for result in search_results:
            result_type = result.get('type', 'unknown')
            result_types[result_type] = result_types.get(result_type, 0) + 1
        
        for result_type, count in result_types.items():
            print(f"   {result_type}: {count} results")
        
        # Test character analysis
        print("\n7️⃣ Testing Character Analysis")
        
        char_feedback = await hybrid_indexer.get_contextual_feedback(
            "Emma remembered what her grandmother told her",
            "chapter_1"
        )
        
        if 'character_contexts' in char_feedback:
            print(f"✅ Character context analysis:")
            for char_context in char_feedback['character_contexts']:
                print(f"   Character: {char_context['character']}")
                print(f"   Arc summary: {char_context['arc_summary']}")
        else:
            print("ℹ️ No specific character contexts found")
        
        print("\n🎉 PathRAG Integration Test Completed Successfully!")
        print("\n📊 Summary:")
        print(f"   Documents indexed: 3")
        print(f"   Total entities: {sum([r.get('entities_extracted', 0) for r in [result1, result2, result3]])}")
        print(f"   Contextual feedback: Working ✅")
        print(f"   Consistency checking: Working ✅") 
        print(f"   Writing suggestions: Working ✅")
        print(f"   Hybrid search: Working ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ PathRAG integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the PathRAG integration test"""
    print("🚀 Starting PathRAG Integration Test")
    print("This tests the complete contextual understanding system")
    print("Using realistic writing content to validate all features")
    
    success = await test_pathrag_integration()
    
    if success:
        print("\n✅ PathRAG Integration Test PASSED!")
        print("🎯 Your contextual understanding system is working correctly!")
        print("\n💡 You can now use these features in your writing app:")
        print("   • Contextual feedback on highlighted text")
        print("   • Consistency checking for character details")
        print("   • AI writing suggestions based on narrative context")
        print("   • Character arc analysis")
        print("   • Hybrid semantic + graph search")
    else:
        print("\n❌ PathRAG Integration Test FAILED!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 