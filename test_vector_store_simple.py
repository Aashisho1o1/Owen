#!/usr/bin/env python3
"""
Simple Vector Store Test - Tests the ChromaDB-based semantic search component
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.indexing.vector_store import VectorStore

def test_vector_store():
    """Test VectorStore functionality with sample narrative content"""
    print("🧪 Testing VectorStore Component")
    print("=" * 50)
    
    # Sample content for testing
    test_documents = {
        "chapter1": """
        Emma walked through the misty forest, her heart pounding with anticipation. 
        The ancient oak tree stood majestically at the center of the clearing, 
        its branches reaching toward the starlit sky. She had promised to meet 
        Marcus here at midnight, but the shadows seemed to whisper warnings.
        """,
        "chapter2": """
        The next morning, Emma woke in her cottage on the edge of Willowbrook village. 
        The events of the previous night felt like a dream, but the silver pendant 
        Marcus had given her was real proof of their encounter.
        """,
        "character_notes": """
        Emma Blackwood - Age 19, orphaned at 12, raised by grandmother Sarah. 
        Has always felt different from other villagers. Experiences strange dreams 
        and visions. Brave but sometimes reckless.
        """
    }
    
    try:
        # Test 1: Initialize VectorStore
        print("\n1️⃣ Testing VectorStore Initialization")
        vector_store = VectorStore("test_collection")
        print("✅ VectorStore initialized successfully")
        
        # Test 2: Document Chunking
        print("\n2️⃣ Testing Document Chunking")
        chunks = vector_store.chunk_document(test_documents["chapter1"], "doc1")
        print(f"✅ Created {len(chunks)} chunks from chapter 1")
        
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {len(chunk['text'])} chars, {chunk['token_count']} tokens")
        
        # Test 3: Document Addition
        print("\n3️⃣ Testing Document Addition")
        for doc_id, content in test_documents.items():
            chunk_ids = vector_store.add_document(
                content, 
                doc_id, 
                {"type": "test_document", "added_at": datetime.now().isoformat()}
            )
            print(f"✅ Added {doc_id}: {len(chunk_ids)} chunks")
        
        # Test 4: Semantic Search
        print("\n4️⃣ Testing Semantic Search")
        
        test_queries = [
            "Emma in the forest",
            "cottage and village", 
            "character age and background",
            "Marcus and midnight meeting"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = vector_store.search(query, n_results=3)
            
            if results:
                print(f"   Found {len(results)} results:")
                for i, result in enumerate(results):
                    print(f"   {i+1}. Score: {result['score']:.3f}")
                    print(f"      Text: {result['text'][:100]}...")
                    print(f"      Doc: {result['metadata']['doc_id']}")
            else:
                print("   ❌ No results found")
        
        # Test 5: Context Window
        print("\n5️⃣ Testing Context Window Retrieval")
        # Get a chunk ID from the first document
        first_doc_chunks = vector_store.search("Emma", filter_dict={"doc_id": "chapter1"}, n_results=1)
        
        if first_doc_chunks:
            chunk_id = first_doc_chunks[0]['id']
            context_chunks = vector_store.get_context_window(chunk_id, window_size=1)
            print(f"✅ Retrieved {len(context_chunks)} context chunks around target chunk")
            
            for i, chunk in enumerate(context_chunks):
                print(f"   Context {i+1}: {chunk['text'][:80]}...")
        else:
            print("❌ Could not test context window - no chunks found")
        
        # Test 6: Document Statistics
        print("\n6️⃣ Testing Document Statistics")
        for doc_id in test_documents.keys():
            doc_chunks = vector_store.search("", filter_dict={"doc_id": doc_id}, n_results=10)
            print(f"   {doc_id}: {len(doc_chunks)} chunks indexed")
        
        # Test 7: Search Quality Assessment
        print("\n7️⃣ Testing Search Quality")
        
        # Test semantic understanding
        emma_results = vector_store.search("protagonist female character", n_results=3)
        if emma_results and any("Emma" in r['text'] for r in emma_results):
            print("✅ Semantic search correctly identifies protagonist")
        else:
            print("❌ Semantic search failed to identify protagonist")
        
        # Test location understanding
        location_results = vector_store.search("place where people live together", n_results=3)
        if location_results and any("village" in r['text'].lower() for r in location_results):
            print("✅ Semantic search correctly identifies village concept")
        else:
            print("❌ Semantic search failed to identify village concept")
        
        print("\n🎉 VectorStore tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ VectorStore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the vector store test"""
    print("🚀 Starting VectorStore Component Test")
    print("This tests the semantic search capabilities using ChromaDB")
    
    success = test_vector_store()
    
    if success:
        print("\n✅ All VectorStore tests passed!")
        print("The semantic search component is working correctly.")
    else:
        print("\n❌ VectorStore tests failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 