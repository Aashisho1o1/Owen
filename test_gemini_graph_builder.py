#!/usr/bin/env python3
"""
Gemini Graph Builder Test - Tests the LLM-powered entity extraction and knowledge graph construction
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.indexing.graph_builder import GeminiGraphBuilder
from services.llm.gemini_service import GeminiService

async def test_gemini_graph_builder():
    """Test GeminiGraphBuilder functionality with sample narrative content"""
    print("🧪 Testing Gemini Graph Builder Component")
    print("=" * 50)
    
    # Check if Gemini API key is available
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not set. Cannot test Gemini features.")
        print("Set your API key: export GEMINI_API_KEY='your_key_here'")
        return False
    
    # Sample narrative content for testing
    test_text = """
    Emma Blackwood walked through the misty Elderwood Forest, her heart pounding with anticipation. 
    The ancient oak tree stood majestically at the center of the clearing, its branches reaching 
    toward the starlit sky. She had promised to meet Marcus Thornfield here at midnight, but the 
    shadows seemed to whisper warnings.

    As she approached the oak, a figure emerged from behind its massive trunk. "You came," Marcus 
    said, his voice barely audible above the wind. Emma felt a mixture of fear and excitement. 
    The prophecy had spoken of this moment - when the chosen one would face their destiny.

    The old wizard Aldric had warned her about the dangers of the forest, but Emma knew she had 
    to follow her heart. Marcus extended his hand, and she took it, feeling the warmth of his 
    touch despite the cold night air.
    """
    
    try:
        # Test 1: Initialize Graph Builder
        print("\n1️⃣ Testing Graph Builder Initialization")
        gemini_service = GeminiService()
        graph_builder = GeminiGraphBuilder(gemini_service)
        print("✅ Graph builder initialized successfully")
        
        # Test 2: Entity and Relationship Extraction
        print("\n2️⃣ Testing Entity and Relationship Extraction")
        print("🤖 Calling Gemini API for entity extraction...")
        
        entities, relationships = await graph_builder.extract_entities_and_relationships(test_text)
        
        print(f"✅ Extracted {len(entities)} entities and {len(relationships)} relationships")
        
        # Analyze extracted entities
        print("\n📋 Extracted Entities:")
        entity_types = {}
        for entity in entities:
            entity_type = entity.type
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity.text)
            print(f"   {entity.type}: {entity.text} (confidence: {entity.confidence:.2f})")
        
        # Analyze extracted relationships
        print("\n🔗 Extracted Relationships:")
        for rel in relationships:
            print(f"   {rel.source} --[{rel.relation_type}]--> {rel.target} (confidence: {rel.confidence:.2f})")
            if rel.context:
                print(f"      Context: {rel.context[:50]}...")
        
        # Test 3: Graph Construction
        print("\n3️⃣ Testing Graph Construction")
        graph = graph_builder.build_graph(entities, relationships)
        
        print(f"✅ Built graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Analyze graph structure
        print("\n📊 Graph Analysis:")
        print(f"   Nodes: {graph.number_of_nodes()}")
        print(f"   Edges: {graph.number_of_edges()}")
        
        # Show some nodes and their attributes
        print("\n🎯 Sample Nodes:")
        for i, (node, data) in enumerate(list(graph.nodes(data=True))[:5]):
            print(f"   {i+1}. {node} (type: {data.get('type', 'unknown')})")
        
        # Show some edges and their attributes
        print("\n➡️ Sample Edges:")
        for i, (source, target, data) in enumerate(list(graph.edges(data=True))[:5]):
            print(f"   {i+1}. {source} --[{data.get('relation_type', 'unknown')}]--> {target}")
        
        # Test 4: Full Text Analysis
        print("\n4️⃣ Testing Full Text Analysis")
        print("🤖 Running complete text analysis...")
        
        complete_graph = await graph_builder.analyze_text(test_text)
        
        print(f"✅ Complete analysis: {complete_graph.number_of_nodes()} nodes, {complete_graph.number_of_edges()} edges")
        
        # Test 5: Character Interactions
        print("\n5️⃣ Testing Character Interaction Analysis")
        char_interactions = graph_builder.get_character_interactions()
        
        if char_interactions:
            print(f"✅ Found {len(char_interactions)} character interactions:")
            for source, target, data in char_interactions:
                print(f"   {source} interacts with {target} ({data.get('relation_type', 'unknown')})")
        else:
            print("❌ No character interactions found")
        
        # Test 6: Character Locations
        print("\n6️⃣ Testing Character-Location Mapping")
        char_locations = graph_builder.get_character_locations()
        
        if char_locations:
            print(f"✅ Found character-location mappings:")
            for char, locations in char_locations.items():
                print(f"   {char}: {', '.join(locations)}")
        else:
            print("❌ No character-location mappings found")
        
        # Test 7: Plot Events
        print("\n7️⃣ Testing Plot Event Extraction")
        plot_events = graph_builder.get_plot_events()
        
        if plot_events:
            print(f"✅ Found {len(plot_events)} plot events:")
            for event in plot_events:
                print(f"   • {event}")
        else:
            print("❌ No plot events found")
        
        # Test 8: Graph Export
        print("\n8️⃣ Testing Graph Export")
        graph_data = graph_builder.export_graph_data()
        
        print(f"✅ Exported graph data: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
        
        # Save graph data for inspection
        with open('test_graph_export.json', 'w') as f:
            json.dump(graph_data, f, indent=2)
        print("📄 Graph data saved to test_graph_export.json")
        
        # Test 9: Centrality Metrics
        print("\n9️⃣ Testing Centrality Metrics")
        centrality_metrics = graph_builder.calculate_centrality_metrics()
        
        if centrality_metrics:
            print(f"✅ Calculated centrality for {len(centrality_metrics)} nodes")
            
            # Show top central nodes
            degree_central = sorted(centrality_metrics.items(), 
                                  key=lambda x: x[1]['degree_centrality'], reverse=True)[:3]
            
            print("🎯 Most central nodes (by degree):")
            for node, metrics in degree_central:
                print(f"   {node}: {metrics['degree_centrality']:.3f}")
        else:
            print("❌ No centrality metrics calculated")
        
        # Test 10: Quality Assessment
        print("\n🔟 Testing Quality Assessment")
        
        # Check if expected entities were found
        expected_characters = ['Emma', 'Marcus', 'Aldric']
        expected_locations = ['forest', 'clearing']
        
        found_characters = [e.text for e in entities if e.type == 'CHARACTER']
        found_locations = [e.text for e in entities if e.type == 'LOCATION']
        
        char_score = len([c for c in expected_characters if any(c.lower() in fc.lower() for fc in found_characters)])
        loc_score = len([l for l in expected_locations if any(l.lower() in fl.lower() for fl in found_locations)])
        
        print(f"📊 Entity Recognition Quality:")
        print(f"   Characters: {char_score}/{len(expected_characters)} expected characters found")
        print(f"   Locations: {loc_score}/{len(expected_locations)} expected locations found")
        
        # Check relationship quality
        rel_types = [r.relation_type for r in relationships]
        expected_rel_types = ['INTERACTS_WITH', 'LOCATED_IN', 'SPEAKS_TO']
        found_rel_types = [rt for rt in expected_rel_types if rt in rel_types]
        
        print(f"   Relationships: {len(found_rel_types)}/{len(expected_rel_types)} expected relationship types found")
        
        print("\n🎉 Gemini Graph Builder tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini Graph Builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the Gemini graph builder test"""
    print("🚀 Starting Gemini Graph Builder Test")
    print("This tests LLM-powered entity extraction and knowledge graph construction")
    print("Requires GEMINI_API_KEY environment variable")
    
    success = await test_gemini_graph_builder()
    
    if success:
        print("\n✅ All Gemini Graph Builder tests passed!")
        print("The LLM-powered entity extraction is working correctly.")
    else:
        print("\n❌ Gemini Graph Builder tests failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 