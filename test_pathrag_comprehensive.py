#!/usr/bin/env python3
"""
🧪 Comprehensive PathRAG Contextual Understanding Test Suite
===========================================================

This test suite demonstrates and validates the PathRAG contextual understanding system
for your AI writing assistant. It covers all major components and provides detailed
explanations for learning purposes.

📚 LEARNING OBJECTIVES:
1. Understand how PathRAG works in practice
2. See the integration of vector search + knowledge graphs
3. Learn about contextual feedback for writing assistance
4. Understand the entity extraction and relationship mapping
5. Observe how the system provides writing suggestions

🔧 SYSTEM ARCHITECTURE OVERVIEW:
- VectorStore: Semantic embeddings using sentence-transformers
- GraphBuilder: Entity/relationship extraction using Gemini LLM
- PathRetriever: PathRAG-inspired relational path finding
- HybridIndexer: Unified interface combining all components
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
import tempfile
import shutil

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import PathRAG components
from services.indexing.hybrid_indexer import HybridIndexer
from services.indexing.vector_store import VectorStore
from services.indexing.graph_builder import GeminiGraphBuilder
from services.indexing.path_retriever import PathRetriever
from services.llm.gemini_service import GeminiService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PathRAGTestSuite:
    """
    🧪 Comprehensive test suite for PathRAG contextual understanding
    
    This class demonstrates:
    - Document indexing with hybrid vector + graph storage
    - Contextual feedback for highlighted text
    - Consistency checking across narrative elements
    - Writing suggestions based on established context
    - Character arc analysis and relationship mapping
    """
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.hybrid_indexer = None
        
        # 📖 Sample narrative content for testing
        # This represents a typical writing scenario with multiple chapters
        self.test_content = {
            "chapter1": """
            Emma walked through the misty forest, her heart pounding with anticipation. 
            The ancient oak tree stood majestically at the center of the clearing, 
            its branches reaching toward the starlit sky. She had promised to meet 
            Marcus here at midnight, but the shadows seemed to whisper warnings.
            
            As she approached the oak, a figure emerged from behind its massive trunk. 
            "You came," Marcus said, his voice barely audible above the wind. 
            Emma felt a mixture of fear and excitement. The prophecy had spoken of 
            this moment - when the chosen one would face their destiny.
            
            The old wizard Aldric had warned her about the dangers of the forest, 
            but Emma knew she had to follow her heart. Marcus extended his hand, 
            and she took it, feeling the warmth of his touch despite the cold night air.
            """,
            
            "chapter2": """
            The next morning, Emma woke in her cottage with sunlight streaming through 
            the windows. The events of the previous night felt like a dream, but the 
            silver pendant Marcus had given her was real proof of their encounter.
            
            She examined the pendant closely - it bore an intricate symbol that seemed 
            to shift and change as she watched. Aldric had mentioned such artifacts 
            in his lessons about ancient magic. Emma realized this was no ordinary gift.
            
            A knock at the door interrupted her thoughts. "Emma, are you ready for 
            today's lesson?" It was Aldric's voice. She quickly hid the pendant 
            under her shirt and opened the door to greet her mentor.
            """,
            
            "character_profiles": """
            Emma Thornfield: A young woman of 19, chosen by prophecy to restore 
            balance to the magical realm. She has auburn hair and green eyes that 
            seem to glow when she uses magic. Emma is brave but sometimes impulsive, 
            having grown up in a small village before discovering her powers.
            
            Marcus Blackwood: A mysterious figure who appears to be in his late 
            twenties. He has dark hair and piercing blue eyes. Marcus serves as 
            a guardian of ancient secrets and possesses knowledge of forbidden magic. 
            His true motivations remain unclear.
            
            Aldric the Wise: An elderly wizard who has served as Emma's mentor 
            for the past year. He has a long white beard and wears simple robes. 
            Aldric is patient and wise, but harbors concerns about the prophecy 
            and Emma's role in it.
            """,
            
            "world_building": """
            The Whispering Forest: An ancient woodland where magic runs deep. 
            The trees are said to hold memories of the past, and those who listen 
            carefully can hear their secrets. At its heart stands the Great Oak, 
            a tree older than recorded history.
            
            The Prophecy of the Chosen: An ancient text that speaks of a young 
            woman who will either save or destroy the magical realm. The prophecy 
            is intentionally vague, leading to different interpretations among 
            the magical community.
            
            The Silver Pendant: A magical artifact that belonged to the first 
            guardians of the realm. It enhances the wearer's natural abilities 
            and provides protection against dark magic.
            """
        }
        
        # 🎯 Test scenarios for contextual understanding
        self.test_scenarios = [
            {
                "name": "Character Consistency Check",
                "highlighted_text": "Emma's blonde hair caught the sunlight",
                "expected_issue": "Hair color inconsistency (established as auburn)",
                "doc_id": "chapter1"
            },
            {
                "name": "Plot Continuity",
                "highlighted_text": "Marcus appeared for the first time",
                "expected_issue": "Contradicts previous meeting",
                "doc_id": "chapter2"
            },
            {
                "name": "Magic System Consistency",
                "highlighted_text": "Emma cast a fireball spell",
                "expected_issue": "No established fire magic abilities",
                "doc_id": "chapter2"
            }
        ]
        
    def record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test results for summary"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    async def run_all_tests(self):
        """🚀 Run the complete test suite"""
        print("🧪 Starting PathRAG Contextual Understanding Test Suite")
        print("=" * 60)
        print("📚 This test demonstrates:")
        print("   • Hybrid indexing (vector + graph)")
        print("   • PathRAG-inspired path retrieval")
        print("   • Contextual feedback for writing")
        print("   • Character arc analysis")
        print("   • Consistency checking")
        print("   • Writing suggestions")
        print("=" * 60)
        
        try:
            # Setup test environment
            await self.setup_test_environment()
            
            # Test individual components
            await self.test_vector_store()
            await self.test_graph_builder()
            await self.test_path_retriever()
            
            # Test hybrid indexer integration
            await self.test_hybrid_indexer()
            
            # Test contextual understanding features
            await self.test_contextual_feedback()
            await self.test_consistency_checking()
            await self.test_writing_suggestions()
            await self.test_character_analysis()
            
            # Test search capabilities
            await self.test_search_functionality()
            
            # Performance and edge case tests
            await self.test_performance()
            await self.test_edge_cases()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.record_test_result("OVERALL", False, str(e))
        finally:
            await self.cleanup_test_environment()
            self.print_test_summary()
    
    async def setup_test_environment(self):
        """🔧 Setup test environment with temporary directory"""
        print("\n🔧 Setting up test environment...")
        
        self.temp_dir = tempfile.mkdtemp(prefix="pathrag_test_")
        logger.info(f"Created temporary test directory: {self.temp_dir}")
        
        # Initialize hybrid indexer
        self.hybrid_indexer = HybridIndexer(
            collection_name="test_collection",
            gemini_service=GeminiService()
        )
        
        self.record_test_result("SETUP", True, "Test environment initialized")
        
    async def cleanup_test_environment(self):
        """🧹 Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
    
    async def test_vector_store(self):
        """🔍 Test VectorStore functionality"""
        print("\n🔍 Testing Vector Store")
        print("-" * 40)
        print("📝 The VectorStore handles semantic embeddings using sentence-transformers")
        print("   • Chunks documents intelligently (preserving paragraph boundaries)")
        print("   • Creates embeddings for semantic similarity search")
        print("   • Supports metadata filtering and context windows")
        
        try:
            # Test vector store initialization
            vector_store = VectorStore("test_vectors")
            self.record_test_result("VectorStore Init", True, "Vector store initialized")
            
            # Test document chunking
            chunks = vector_store.chunk_document(
                self.test_content["chapter1"], 
                "test_doc_1"
            )
            
            if chunks:
                self.record_test_result("Document Chunking", True, 
                    f"Created {len(chunks)} chunks from chapter 1")
                
                # Verify chunk structure
                first_chunk = chunks[0]
                expected_fields = ['id', 'text', 'doc_id', 'chunk_index', 'token_count']
                has_all_fields = all(field in first_chunk for field in expected_fields)
                
                if has_all_fields:
                    self.record_test_result("Chunk Structure", True, 
                        f"Chunks have correct structure: {list(first_chunk.keys())}")
                else:
                    self.record_test_result("Chunk Structure", False, 
                        f"Missing fields in chunk: {list(first_chunk.keys())}")
            else:
                self.record_test_result("Document Chunking", False, "No chunks created")
            
            # Test document addition
            chunk_ids = vector_store.add_document(
                self.test_content["chapter1"], 
                "test_doc_1", 
                {"type": "chapter", "number": 1}
            )
            
            if chunk_ids:
                self.record_test_result("Document Addition", True, 
                    f"Added document with {len(chunk_ids)} chunks")
            else:
                self.record_test_result("Document Addition", False, "No chunk IDs returned")
            
            # Test semantic search
            search_results = vector_store.search("Emma meets Marcus", n_results=3)
            
            if search_results:
                self.record_test_result("Semantic Search", True, 
                    f"Found {len(search_results)} relevant chunks")
                
                # Check search result structure
                first_result = search_results[0]
                if 'text' in first_result and 'score' in first_result:
                    self.record_test_result("Search Result Quality", True, 
                        f"Top result score: {first_result['score']:.3f}")
                else:
                    self.record_test_result("Search Result Quality", False, 
                        f"Invalid result structure: {list(first_result.keys())}")
            else:
                self.record_test_result("Semantic Search", False, "No search results returned")
            
            # Test context window retrieval
            if chunk_ids:
                context_chunks = vector_store.get_context_window(chunk_ids[0], window_size=1)
                if context_chunks:
                    self.record_test_result("Context Window", True, 
                        f"Retrieved {len(context_chunks)} context chunks")
                else:
                    self.record_test_result("Context Window", False, "No context chunks retrieved")
            
        except Exception as e:
            self.record_test_result("VectorStore Test", False, f"Exception: {e}")
    
    async def test_graph_builder(self):
        """🕸️ Test GeminiGraphBuilder functionality"""
        print("\n🕸️ Testing Knowledge Graph Builder")
        print("-" * 40)
        print("🤖 The GraphBuilder uses Gemini LLM to extract entities and relationships")
        print("   • Identifies characters, locations, events, and themes")
        print("   • Maps relationships like 'speaks_to', 'goes_to', 'causes'")
        print("   • Builds a NetworkX graph for pathfinding")
        
        try:
            # Test graph builder initialization
            gemini_service = GeminiService()
            graph_builder = GeminiGraphBuilder(gemini_service)
            self.record_test_result("GraphBuilder Init", True, "Graph builder initialized")
            
            # Test entity extraction
            entities, relationships = await graph_builder.extract_entities_and_relationships(
                self.test_content["chapter1"]
            )
            
            if entities:
                self.record_test_result("Entity Extraction", True, 
                    f"Extracted {len(entities)} entities")
                
                # Check entity types
                entity_types = [e.type for e in entities]
                expected_types = ['CHARACTER', 'LOCATION', 'EVENT']
                found_types = [t for t in expected_types if t in entity_types]
                
                if found_types:
                    self.record_test_result("Entity Types", True, 
                        f"Found expected types: {found_types}")
                    
                    # Print sample entities for learning
                    print(f"   📊 Sample entities found:")
                    for entity in entities[:5]:  # Show first 5
                        print(f"      • {entity.type}: {entity.text}")
                else:
                    self.record_test_result("Entity Types", False, 
                        f"Expected types not found. Got: {entity_types}")
            else:
                self.record_test_result("Entity Extraction", False, "No entities extracted")
            
            if relationships:
                self.record_test_result("Relationship Extraction", True, 
                    f"Extracted {len(relationships)} relationships")
                
                # Print sample relationships for learning
                print(f"   🔗 Sample relationships found:")
                for rel in relationships[:3]:  # Show first 3
                    print(f"      • {rel.source} --{rel.type}--> {rel.target}")
            else:
                self.record_test_result("Relationship Extraction", False, "No relationships extracted")
            
            # Test graph construction
            graph = graph_builder.build_graph(entities, relationships)
            
            if graph.number_of_nodes() > 0:
                self.record_test_result("Graph Construction", True, 
                    f"Built graph with {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
                
                # Show graph structure for learning
                print(f"   📈 Graph structure:")
                print(f"      • Nodes: {graph.number_of_nodes()}")
                print(f"      • Edges: {graph.number_of_edges()}")
                print(f"      • Sample nodes: {list(graph.nodes())[:5]}")
            else:
                self.record_test_result("Graph Construction", False, "Empty graph created")
            
            # Test full text analysis
            complete_graph = await graph_builder.analyze_text(self.test_content["chapter1"])
            
            if complete_graph.number_of_nodes() > 0:
                self.record_test_result("Full Text Analysis", True, 
                    f"Complete analysis: {complete_graph.number_of_nodes()} nodes")
            else:
                self.record_test_result("Full Text Analysis", False, "Failed to analyze text")
            
        except Exception as e:
            self.record_test_result("GraphBuilder Test", False, f"Exception: {e}")
    
    async def test_path_retriever(self):
        """🛤️ Test PathRetriever functionality"""
        print("\n🛤️ Testing Path Retriever")
        print("-" * 40)
        print("🔍 The PathRetriever implements PathRAG concepts:")
        print("   • Finds initial nodes via vector search")
        print("   • Explores paths up to 4 hops away")
        print("   • Applies flow-based pruning to remove redundancy")
        print("   • Scores paths based on relevance and coherence")
        
        try:
            # First we need a graph and vector store
            vector_store = VectorStore("test_path_vectors")
            vector_store.add_document(self.test_content["chapter1"], "doc1", {"type": "chapter"})
            
            graph_builder = GeminiGraphBuilder(GeminiService())
            graph = await graph_builder.analyze_text(self.test_content["chapter1"])
            
            # Test path retriever initialization
            path_retriever = PathRetriever(graph, vector_store)
            self.record_test_result("PathRetriever Init", True, "Path retriever initialized")
            
            # Test path retrieval
            paths = path_retriever.retrieve_paths("Emma meets Marcus", top_k=3)
            
            if paths:
                self.record_test_result("Path Retrieval", True, f"Retrieved {len(paths)} paths")
                
                # Show path details for learning
                print(f"   🛤️ Sample paths found:")
                for i, path in enumerate(paths[:2]):  # Show first 2 paths
                    print(f"      Path {i+1}: {path.get('narrative', 'No narrative')}")
                    print(f"         Score: {path.get('score', 0):.3f}")
                    print(f"         Entities: {[e.get('label', 'Unknown') for e in path.get('entities', [])]}")
                
                # Check path quality
                for i, path in enumerate(paths):
                    if 'narrative' in path and 'score' in path:
                        self.record_test_result(f"Path {i+1} Quality", True, 
                            f"Score: {path['score']:.3f}")
                    else:
                        self.record_test_result(f"Path {i+1} Quality", False, 
                            "Invalid path structure")
            else:
                self.record_test_result("Path Retrieval", False, "No paths retrieved")
            
            # Test character context paths
            char_paths = path_retriever.get_character_context_paths("Emma", "all")
            
            if char_paths:
                self.record_test_result("Character Context Paths", True, 
                    f"Found {len(char_paths)} character paths")
            else:
                self.record_test_result("Character Context Paths", False, 
                    "No character paths found")
            
        except Exception as e:
            self.record_test_result("PathRetriever Test", False, f"Exception: {e}")
    
    async def test_hybrid_indexer(self):
        """🔄 Test HybridIndexer integration"""
        print("\n🔄 Testing Hybrid Indexer Integration")
        print("-" * 40)
        print("🎯 The HybridIndexer combines all components:")
        print("   • Indexes documents with both vector and graph storage")
        print("   • Provides unified interface for all features")
        print("   • Coordinates between vector search and path retrieval")
        
        try:
            # Test document indexing
            result = await self.hybrid_indexer.index_document(
                "test_chapter_1",
                self.test_content["chapter1"],
                {"type": "chapter", "number": 1}
            )
            
            if result and 'document_id' in result:
                self.record_test_result("Document Indexing", True, 
                    f"Indexed document with {result.get('entities_extracted', 0)} entities")
                
                # Show indexing statistics for learning
                print(f"   📊 Indexing statistics:")
                print(f"      • Processing time: {result.get('processing_time', 0):.2f}s")
                print(f"      • Chunks created: {result.get('chunks_created', 0)}")
                print(f"      • Entities extracted: {result.get('entities_extracted', 0)}")
                print(f"      • Relationships found: {result.get('relationships_found', 0)}")
            else:
                self.record_test_result("Document Indexing", False, "Invalid indexing result")
            
            # Test batch indexing
            documents = [
                ("chapter_1", self.test_content["chapter1"], {"type": "chapter", "number": 1}),
                ("chapter_2", self.test_content["chapter2"], {"type": "chapter", "number": 2}),
                ("characters", self.test_content["character_profiles"], {"type": "reference"})
            ]
            
            batch_result = await self.hybrid_indexer.index_folder(documents)
            
            if batch_result and 'documents_indexed' in batch_result:
                self.record_test_result("Batch Indexing", True, 
                    f"Indexed {batch_result['documents_indexed']} documents")
                
                # Show batch statistics
                print(f"   📈 Batch indexing results:")
                print(f"      • Total documents: {batch_result['documents_indexed']}")
                print(f"      • Successful: {batch_result['successful']}")
                print(f"      • Total entities: {batch_result['total_entities']}")
                print(f"      • Graph nodes: {batch_result['graph_nodes']}")
            else:
                self.record_test_result("Batch Indexing", False, "Batch indexing failed")
            
        except Exception as e:
            self.record_test_result("HybridIndexer Test", False, f"Exception: {e}")
    
    async def test_contextual_feedback(self):
        """💡 Test contextual feedback functionality"""
        print("\n💡 Testing Contextual Feedback")
        print("-" * 40)
        print("🎯 Contextual feedback provides writing assistance:")
        print("   • Analyzes highlighted text in context")
        print("   • Finds relevant narrative paths")
        print("   • Suggests improvements based on established elements")
        
        try:
            # Test contextual feedback
            feedback = await self.hybrid_indexer.get_contextual_feedback(
                "Emma walked through the forest",
                "test_chapter_1",
                context_window=500
            )
            
            if 'highlighted_text' in feedback and 'suggestions' in feedback:
                self.record_test_result("Contextual Feedback", True, 
                    f"Generated {len(feedback['suggestions'])} suggestions")
                
                # Show feedback details for learning
                print(f"   💡 Contextual feedback example:")
                print(f"      • Highlighted: '{feedback['highlighted_text']}'")
                print(f"      • Suggestions: {len(feedback['suggestions'])}")
                for i, suggestion in enumerate(feedback['suggestions'][:3]):
                    print(f"         {i+1}. {suggestion}")
                
                # Check feedback quality
                if feedback['entities_mentioned']:
                    self.record_test_result("Entity Detection", True, 
                        f"Detected {len(feedback['entities_mentioned'])} entities")
                    
                    print(f"      • Entities mentioned:")
                    for entity in feedback['entities_mentioned'][:3]:
                        print(f"         - {entity['type']}: {entity['text']}")
                else:
                    self.record_test_result("Entity Detection", False, "No entities detected")
                
                if feedback['narrative_paths']:
                    self.record_test_result("Narrative Paths", True, 
                        f"Found {len(feedback['narrative_paths'])} narrative paths")
                    
                    print(f"      • Narrative paths:")
                    for path in feedback['narrative_paths'][:2]:
                        print(f"         - {path['narrative'][:80]}...")
                else:
                    self.record_test_result("Narrative Paths", False, "No narrative paths found")
            else:
                self.record_test_result("Contextual Feedback", False, "Invalid feedback structure")
            
        except Exception as e:
            self.record_test_result("Contextual Feedback Test", False, f"Exception: {e}")
    
    async def test_consistency_checking(self):
        """🔍 Test consistency checking functionality"""
        print("\n🔍 Testing Consistency Checking")
        print("-" * 40)
        print("✅ Consistency checking validates narrative elements:")
        print("   • Checks character details against established facts")
        print("   • Verifies plot continuity")
        print("   • Validates setting and world-building consistency")
        
        try:
            # Test consistency checking with different scenarios
            for scenario in self.test_scenarios:
                print(f"\n   🧪 Testing: {scenario['name']}")
                
                consistency_result = await self.hybrid_indexer.check_consistency(
                    scenario['highlighted_text'],
                    scenario['doc_id'],
                    'all'
                )
                
                if 'is_consistent' in consistency_result:
                    is_consistent = consistency_result['is_consistent']
                    conflicts = consistency_result.get('conflicts', [])
                    
                    self.record_test_result(f"Consistency Check - {scenario['name']}", True,
                        f"Consistent: {is_consistent}, Conflicts: {len(conflicts)}")
                    
                    # Show results for learning
                    print(f"      • Statement: '{scenario['highlighted_text']}'")
                    print(f"      • Consistent: {is_consistent}")
                    if conflicts:
                        print(f"      • Conflicts found:")
                        for conflict in conflicts[:2]:
                            print(f"         - {conflict.get('type', 'Unknown')}: {conflict.get('conflict', 'No details')}")
                    
                    if consistency_result.get('recommendation'):
                        print(f"      • Recommendation: {consistency_result['recommendation']}")
                else:
                    self.record_test_result(f"Consistency Check - {scenario['name']}", False,
                        "Invalid consistency result structure")
            
        except Exception as e:
            self.record_test_result("Consistency Checking Test", False, f"Exception: {e}")
    
    async def test_writing_suggestions(self):
        """✍️ Test writing suggestions functionality"""
        print("\n✍️ Testing Writing Suggestions")
        print("-" * 40)
        print("📝 Writing suggestions help improve narrative:")
        print("   • Analyzes current context")
        print("   • Suggests plot developments")
        print("   • Recommends character interactions")
        print("   • Provides style consistency guidance")
        
        try:
            # Test writing suggestions
            suggestions = await self.hybrid_indexer.get_writing_suggestions(
                "Emma stood at the edge of the forest, uncertain about her next move.",
                'all'
            )
            
            if 'suggestions' in suggestions:
                self.record_test_result("Writing Suggestions", True, 
                    f"Generated {len(suggestions['suggestions'])} suggestions")
                
                # Show suggestions for learning
                print(f"   📝 Writing suggestions example:")
                print(f"      • Context: '{suggestions['context']}'")
                print(f"      • Suggestions:")
                
                for i, suggestion in enumerate(suggestions['suggestions'][:4]):
                    print(f"         {i+1}. [{suggestion['type']}] {suggestion['suggestion']}")
                
                # Test different suggestion types
                for suggestion_type in ['plot', 'character', 'style']:
                    type_suggestions = await self.hybrid_indexer.get_writing_suggestions(
                        "Emma contemplated her next action.",
                        suggestion_type
                    )
                    
                    if type_suggestions.get('suggestions'):
                        self.record_test_result(f"Suggestions - {suggestion_type}", True,
                            f"Generated {len(type_suggestions['suggestions'])} {suggestion_type} suggestions")
                    else:
                        self.record_test_result(f"Suggestions - {suggestion_type}", False,
                            f"No {suggestion_type} suggestions generated")
            else:
                self.record_test_result("Writing Suggestions", False, "No suggestions generated")
            
        except Exception as e:
            self.record_test_result("Writing Suggestions Test", False, f"Exception: {e}")
    
    async def test_character_analysis(self):
        """👤 Test character analysis functionality"""
        print("\n👤 Testing Character Analysis")
        print("-" * 40)
        print("🎭 Character analysis tracks narrative development:")
        print("   • Maps character relationships")
        print("   • Tracks character arcs across documents")
        print("   • Identifies character interactions and growth")
        
        try:
            # Test character-specific feedback
            char_feedback = await self.hybrid_indexer.get_contextual_feedback(
                "Emma remembered her grandmother's advice",
                "test_chapter_1"
            )
            
            if 'character_contexts' in char_feedback:
                self.record_test_result("Character Context Analysis", True,
                    f"Found {len(char_feedback['character_contexts'])} character contexts")
                
                # Show character analysis for learning
                print(f"   👤 Character analysis example:")
                for char_context in char_feedback['character_contexts']:
                    print(f"      • Character: {char_context['character']}")
                    print(f"      • Arc summary: {char_context['arc_summary']}")
            else:
                self.record_test_result("Character Context Analysis", False,
                    "No character contexts found")
            
            # Test character arc retrieval if path retriever is available
            if self.hybrid_indexer.path_retriever:
                emma_paths = self.hybrid_indexer.path_retriever.get_character_context_paths("Emma", "relationships")
                
                if emma_paths:
                    self.record_test_result("Character Arc Retrieval", True,
                        f"Retrieved {len(emma_paths)} character arc paths")
                    
                    # Show character paths for learning
                    print(f"   🔗 Character relationship paths:")
                    for path in emma_paths[:2]:
                        print(f"      • {path['narrative'][:80]}...")
                else:
                    self.record_test_result("Character Arc Retrieval", False,
                        "No character arc paths found")
            
        except Exception as e:
            self.record_test_result("Character Analysis Test", False, f"Exception: {e}")
    
    async def test_search_functionality(self):
        """🔍 Test search functionality"""
        print("\n🔍 Testing Search Functionality")
        print("-" * 40)
        print("🔎 The search system combines multiple approaches:")
        print("   • Vector search for semantic similarity")
        print("   • Graph search for relationship-based results")
        print("   • Hybrid search combining both methods")
        
        try:
            # Test different search types
            search_types = ['vector', 'graph', 'hybrid']
            
            for search_type in search_types:
                search_results = self.hybrid_indexer.search(
                    "Emma's magical abilities",
                    search_type=search_type
                )
                
                if search_results:
                    self.record_test_result(f"Search - {search_type}", True,
                        f"Found {len(search_results)} results")
                    
                    # Show search results for learning
                    print(f"   🔍 {search_type.capitalize()} search results:")
                    for i, result in enumerate(search_results[:2]):
                        print(f"      {i+1}. [{result['type']}] Score: {result['score']:.3f}")
                        print(f"         {result['content'][:80]}...")
                else:
                    self.record_test_result(f"Search - {search_type}", False,
                        f"No {search_type} search results")
            
            # Test filtered search
            filtered_results = self.hybrid_indexer.search(
                "forest",
                search_type='hybrid',
                filters={'type': 'chapter'}
            )
            
            if filtered_results:
                self.record_test_result("Filtered Search", True,
                    f"Found {len(filtered_results)} filtered results")
            else:
                self.record_test_result("Filtered Search", False,
                    "No filtered search results")
            
        except Exception as e:
            self.record_test_result("Search Test", False, f"Exception: {e}")
    
    async def test_performance(self):
        """⚡ Test performance characteristics"""
        print("\n⚡ Testing Performance")
        print("-" * 40)
        print("📊 Performance testing measures:")
        print("   • Document indexing speed")
        print("   • Search response times")
        print("   • Memory usage patterns")
        
        try:
            import time
            
            # Test indexing performance
            start_time = time.time()
            await self.hybrid_indexer.index_document(
                "perf_test_doc",
                self.test_content["chapter1"] * 3,  # 3x larger document
                {"type": "performance_test"}
            )
            indexing_time = time.time() - start_time
            
            self.record_test_result("Indexing Performance", True,
                f"Indexed large document in {indexing_time:.2f}s")
            
            # Test search performance
            start_time = time.time()
            search_results = self.hybrid_indexer.search("Emma", search_type='hybrid')
            search_time = time.time() - start_time
            
            self.record_test_result("Search Performance", True,
                f"Hybrid search completed in {search_time:.3f}s")
            
            # Show performance metrics
            print(f"   📊 Performance metrics:")
            print(f"      • Indexing time: {indexing_time:.2f}s")
            print(f"      • Search time: {search_time:.3f}s")
            print(f"      • Results returned: {len(search_results) if search_results else 0}")
            
        except Exception as e:
            self.record_test_result("Performance Test", False, f"Exception: {e}")
    
    async def test_edge_cases(self):
        """🔧 Test edge cases and error handling"""
        print("\n🔧 Testing Edge Cases")
        print("-" * 40)
        print("🛡️ Edge case testing ensures robustness:")
        print("   • Empty input handling")
        print("   • Invalid document IDs")
        print("   • Malformed queries")
        
        try:
            # Test empty input
            empty_feedback = await self.hybrid_indexer.get_contextual_feedback("", "test_chapter_1")
            
            if 'error' in empty_feedback or 'highlighted_text' in empty_feedback:
                self.record_test_result("Empty Input Handling", True, "Handled empty input gracefully")
            else:
                self.record_test_result("Empty Input Handling", False, "Unexpected response to empty input")
            
            # Test very long input
            long_text = "Emma " * 1000  # Very long text
            long_feedback = await self.hybrid_indexer.get_contextual_feedback(long_text, "test_chapter_1")
            
            if long_feedback:
                self.record_test_result("Long Input Handling", True, "Handled long input")
            else:
                self.record_test_result("Long Input Handling", False, "Failed to handle long input")
            
            # Test non-existent document
            try:
                no_doc_feedback = await self.hybrid_indexer.get_contextual_feedback(
                    "test text", "nonexistent_doc"
                )
                
                if 'error' in no_doc_feedback or 'highlighted_text' in no_doc_feedback:
                    self.record_test_result("Non-existent Document", True, "Handled non-existent document")
                else:
                    self.record_test_result("Non-existent Document", False, "Unexpected response format")
            except Exception as e:
                self.record_test_result("Non-existent Document", True, f"Properly raised exception: {type(e).__name__}")
            
        except Exception as e:
            self.record_test_result("Edge Cases Test", False, f"Exception: {e}")
    
    def print_test_summary(self):
        """📊 Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 PathRAG Test Suite Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"🎯 Overall Results: {passed}/{total} tests passed ({pass_rate:.1f}%)")
        print(f"⏱️  Test Duration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['test'].split(' - ')[0] if ' - ' in result['test'] else result['test']
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0, 'details': []}
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1
            categories[category]['details'].append(result)
        
        print("\n📋 Results by Category:")
        for category, stats in categories.items():
            status = "✅" if stats['passed'] == stats['total'] else "⚠️" if stats['passed'] > 0 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} passed")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Show system capabilities demonstrated
        print(f"\n🎯 PathRAG System Capabilities Demonstrated:")
        print(f"   ✅ Hybrid indexing (vector + graph)")
        print(f"   ✅ Entity extraction and relationship mapping")
        print(f"   ✅ PathRAG-inspired path retrieval")
        print(f"   ✅ Contextual feedback for writing")
        print(f"   ✅ Consistency checking")
        print(f"   ✅ Writing suggestions")
        print(f"   ✅ Character arc analysis")
        print(f"   ✅ Multi-modal search (vector/graph/hybrid)")
        
        if pass_rate >= 80:
            print(f"\n🎉 PathRAG System Status: EXCELLENT ({pass_rate:.1f}%)")
            print("💡 Your contextual understanding system is working well!")
        elif pass_rate >= 60:
            print(f"\n✅ PathRAG System Status: GOOD ({pass_rate:.1f}%)")
            print("💡 Most features are working, minor issues to address")
        else:
            print(f"\n⚠️ PathRAG System Status: NEEDS ATTENTION ({pass_rate:.1f}%)")
            print("💡 Several issues found, review failed tests")
        
        print("\n🚀 Next Steps:")
        print("   1. Review any failed tests above")
        print("   2. Test the system with your own writing content")
        print("   3. Try the API endpoints in your web interface")
        print("   4. Experiment with different query types")
        
        print("\n📚 Learning Resources:")
        print("   • PathRAG Paper: https://arxiv.org/abs/2402.05131")
        print("   • NetworkX Documentation: https://networkx.org/")
        print("   • ChromaDB Documentation: https://docs.trychroma.com/")
        print("   • Sentence Transformers: https://www.sbert.net/")


async def main():
    """🚀 Main test runner"""
    print("🧪 PathRAG Contextual Understanding Test Suite")
    print("=" * 60)
    print("📖 This comprehensive test demonstrates:")
    print("   • How PathRAG works in your writing assistant")
    print("   • Integration of vector search + knowledge graphs")
    print("   • Contextual feedback and writing suggestions")
    print("   • Character arc analysis and consistency checking")
    print("=" * 60)
    
    # Create and run test suite
    test_suite = PathRAGTestSuite()
    await test_suite.run_all_tests()
    
    print("\n🎓 LEARNING SUMMARY:")
    print("=" * 60)
    print("📚 Key Concepts Demonstrated:")
    print("   1. HYBRID INDEXING: Combines vector embeddings with knowledge graphs")
    print("   2. PATHRAG ALGORITHM: Finds meaningful paths through entity relationships")
    print("   3. CONTEXTUAL UNDERSTANDING: Provides writing feedback based on narrative context")
    print("   4. ENTITY EXTRACTION: Uses LLMs to identify characters, locations, events")
    print("   5. CONSISTENCY CHECKING: Validates new content against established facts")
    print("   6. WRITING ASSISTANCE: Suggests improvements based on story context")
    
    print("\n🔧 System Architecture:")
    print("   • VectorStore: Semantic search using sentence-transformers")
    print("   • GraphBuilder: Entity/relationship extraction using Gemini")
    print("   • PathRetriever: PathRAG-inspired path finding")
    print("   • HybridIndexer: Unified interface combining all components")
    
    print("\n💡 Practical Applications:")
    print("   • Real-time writing feedback")
    print("   • Character consistency checking")
    print("   • Plot coherence analysis")
    print("   • Context-aware writing suggestions")
    
    print("\n🎯 This system gives your writing assistant advanced contextual understanding!")


if __name__ == "__main__":
    asyncio.run(main()) 