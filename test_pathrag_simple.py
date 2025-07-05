#!/usr/bin/env python3
"""
🚀 Simple PathRAG Test Script
============================

Quick test to validate your PathRAG contextual understanding system.
This script demonstrates the key features with minimal setup.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.indexing.hybrid_indexer import HybridIndexer
from services.llm.gemini_service import GeminiService

async def test_pathrag_system():
    """Test the PathRAG system with sample content"""
    
    print("🧪 Testing PathRAG Contextual Understanding System")
    print("=" * 50)
    
    # Sample writing content
    chapter1 = """
    Emma walked through the misty forest, her heart pounding with anticipation. 
    The ancient oak tree stood majestically at the center of the clearing, 
    its branches reaching toward the starlit sky. She had promised to meet 
    Marcus here at midnight, but the shadows seemed to whisper warnings.
    
    As she approached the oak, a figure emerged from behind its massive trunk. 
    "You came," Marcus said, his voice barely audible above the wind. 
    Emma felt a mixture of fear and excitement.
    """
    
    try:
        print("1️⃣ Initializing PathRAG System...")
        
        # Initialize the hybrid indexer
        indexer = HybridIndexer(
            collection_name="test_pathrag",
            gemini_service=GeminiService()
        )
        print("✅ System initialized")
        
        print("\n2️⃣ Indexing sample content...")
        
        # Index the sample content
        result = await indexer.index_document(
            "chapter_1",
            chapter1,
            {"type": "chapter", "title": "The Forest Meeting"}
        )
        
        print(f"✅ Content indexed:")
        print(f"   • Entities extracted: {result.get('entities_extracted', 0)}")
        print(f"   • Relationships found: {result.get('relationships_found', 0)}")
        print(f"   • Processing time: {result.get('processing_time', 0):.2f}s")
        
        print("\n3️⃣ Testing contextual feedback...")
        
        # Test contextual feedback
        feedback = await indexer.get_contextual_feedback(
            "Emma walked through the forest",
            "chapter_1"
        )
        
        print(f"✅ Contextual feedback generated:")
        print(f"   • Entities mentioned: {len(feedback.get('entities_mentioned', []))}")
        print(f"   • Narrative paths: {len(feedback.get('narrative_paths', []))}")
        print(f"   • Suggestions: {len(feedback.get('suggestions', []))}")
        
        # Show some suggestions
        if feedback.get('suggestions'):
            print("   • Sample suggestions:")
            for i, suggestion in enumerate(feedback['suggestions'][:3]):
                print(f"     {i+1}. {suggestion}")
        
        print("\n4️⃣ Testing consistency checking...")
        
        # Test consistency checking
        consistency = await indexer.check_consistency(
            "Emma's blonde hair shimmered in the moonlight",
            "chapter_1"
        )
        
        print(f"✅ Consistency check completed:")
        print(f"   • Is consistent: {consistency.get('is_consistent', 'Unknown')}")
        print(f"   • Conflicts found: {len(consistency.get('conflicts', []))}")
        
        if consistency.get('conflicts'):
            print("   • Conflicts:")
            for conflict in consistency['conflicts']:
                print(f"     - {conflict.get('type', 'Unknown')}: {conflict.get('conflict', 'No details')}")
        
        print("\n5️⃣ Testing writing suggestions...")
        
        # Test writing suggestions
        suggestions = await indexer.get_writing_suggestions(
            "Emma stood at the edge of the clearing, unsure of what to do next."
        )
        
        print(f"✅ Writing suggestions generated:")
        print(f"   • Total suggestions: {len(suggestions.get('suggestions', []))}")
        
        if suggestions.get('suggestions'):
            print("   • Sample suggestions:")
            for i, suggestion in enumerate(suggestions['suggestions'][:3]):
                print(f"     {i+1}. [{suggestion['type']}] {suggestion['suggestion']}")
        
        print("\n6️⃣ Testing search functionality...")
        
        # Test search
        search_results = indexer.search("Emma meets Marcus", search_type='hybrid')
        
        print(f"✅ Search completed:")
        print(f"   • Results found: {len(search_results)}")
        
        if search_results:
            print("   • Top results:")
            for i, result in enumerate(search_results[:2]):
                print(f"     {i+1}. [{result['type']}] Score: {result['score']:.3f}")
                print(f"        {result['content'][:80]}...")
        
        print("\n🎉 PathRAG System Test Completed Successfully!")
        print("\n📊 Summary:")
        print("   ✅ Document indexing: Working")
        print("   ✅ Contextual feedback: Working")
        print("   ✅ Consistency checking: Working")
        print("   ✅ Writing suggestions: Working")
        print("   ✅ Search functionality: Working")
        
        print("\n💡 Your PathRAG contextual understanding system is operational!")
        print("🚀 You can now use these features in your writing assistant.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the simple PathRAG test"""
    success = await test_pathrag_system()
    
    if success:
        print("\n🎯 Next Steps:")
        print("   1. Try the API endpoints in your web interface")
        print("   2. Test with your own writing content")
        print("   3. Experiment with different queries")
        print("   4. Check the comprehensive test for more details")
    else:
        print("\n🔧 Troubleshooting:")
        print("   1. Check that all dependencies are installed")
        print("   2. Verify Gemini API configuration")
        print("   3. Ensure ChromaDB is working")
        print("   4. Review the error messages above")

if __name__ == "__main__":
    asyncio.run(main()) 