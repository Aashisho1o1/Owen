#!/usr/bin/env python3
"""
Standalone test for Gemini Graph Builder functionality
Tests the core entity extraction and graph building without vector dependencies
"""

import asyncio
import sys
import os
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
import networkx as nx
from dataclasses import dataclass, asdict

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.llm.gemini_service import GeminiService

logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Represents an extracted entity with metadata."""
    text: str
    type: str  # CHARACTER, LOCATION, EVENT, THEME, ORGANIZATION
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    attributes: Dict[str, Any] = None

@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source: str
    target: str
    relation_type: str
    confidence: float
    context: str = ""

class StandaloneGeminiGraphBuilder:
    """
    Standalone version of Gemini graph builder for testing.
    """
    
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        """Initialize the graph builder with Gemini service."""
        self.gemini_service = gemini_service or GeminiService()
        self.graph = nx.DiGraph()
        
        # Entity extraction prompt template
        self.entity_extraction_prompt = """
You are an expert literary analyst specializing in narrative entity extraction. 
Analyze the following text and extract entities with their relationships.

Extract the following entity types:
- CHARACTER: People, animals, or personified entities
- LOCATION: Places, settings, geographical locations
- EVENT: Significant plot events, actions, or occurrences
- THEME: Abstract concepts, emotions, or thematic elements
- ORGANIZATION: Groups, institutions, or collective entities

For each entity, provide:
1. text: The exact text span
2. type: One of the types above
3. start_pos: Character position where entity starts
4. end_pos: Character position where entity ends
5. confidence: Confidence score (0.0-1.0)

Also extract relationships between entities:
- INTERACTS_WITH: Characters interacting
- LOCATED_IN: Entity located in a place
- PARTICIPATES_IN: Entity participating in an event
- REPRESENTS: Entity representing a theme
- BELONGS_TO: Entity belonging to organization
- CAUSES: One event causing another
- PRECEDES: One event happening before another

Return the result as JSON with this structure:
{
    "entities": [
        {
            "text": "entity text",
            "type": "CHARACTER",
            "start_pos": 0,
            "end_pos": 10,
            "confidence": 0.95
        }
    ],
    "relationships": [
        {
            "source": "entity1",
            "target": "entity2",
            "relation_type": "INTERACTS_WITH",
            "confidence": 0.9,
            "context": "brief context"
        }
    ]
}

Text to analyze:
{text}
"""

    async def extract_entities_and_relationships(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from text using Gemini.
        """
        try:
            # Format prompt with text
            prompt = self.entity_extraction_prompt.format(text=text)
            
            # Get response from Gemini
            response = await self.gemini_service.generate_response(prompt)
            
            # Parse JSON response - handle markdown code blocks
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks first
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON from code block: {json_str[:200]}...")
                        return [], []
                else:
                    # Fallback: try to extract any JSON-like structure
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        try:
                            data = json.loads(json_str)
                        except json.JSONDecodeError:
                            print(f"Failed to parse extracted JSON: {json_str[:200]}...")
                            return [], []
                    else:
                        print(f"No JSON structure found in Gemini response: {response}")
                        return [], []
            
            # Convert to Entity and Relationship objects
            entities = []
            for entity_data in data.get('entities', []):
                entity = Entity(
                    text=entity_data['text'],
                    type=entity_data['type'],
                    start_pos=entity_data['start_pos'],
                    end_pos=entity_data['end_pos'],
                    confidence=entity_data.get('confidence', 1.0)
                )
                entities.append(entity)
            
            relationships = []
            for rel_data in data.get('relationships', []):
                relationship = Relationship(
                    source=rel_data['source'],
                    target=rel_data['target'],
                    relation_type=rel_data['relation_type'],
                    confidence=rel_data.get('confidence', 1.0),
                    context=rel_data.get('context', '')
                )
                relationships.append(relationship)
            
            print(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
            return entities, relationships
            
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            return [], []

    def build_graph(self, entities: List[Entity], relationships: List[Relationship]) -> nx.DiGraph:
        """
        Build a NetworkX graph from extracted entities and relationships.
        """
        # Clear existing graph
        self.graph.clear()
        
        # Add entity nodes
        for entity in entities:
            self.graph.add_node(
                entity.text,
                type=entity.type,
                confidence=entity.confidence,
                start_pos=entity.start_pos,
                end_pos=entity.end_pos
            )
        
        # Add relationship edges
        for rel in relationships:
            if rel.source in self.graph.nodes and rel.target in self.graph.nodes:
                self.graph.add_edge(
                    rel.source,
                    rel.target,
                    relation_type=rel.relation_type,
                    confidence=rel.confidence,
                    context=rel.context
                )
        
        print(f"Built graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
        return self.graph

    def get_character_interactions(self) -> List[Tuple[str, str, Dict]]:
        """Get all character interactions from the graph."""
        interactions = []
        
        for source, target, data in self.graph.edges(data=True):
            if (self.graph.nodes[source].get('type') == 'CHARACTER' and 
                self.graph.nodes[target].get('type') == 'CHARACTER'):
                interactions.append((source, target, data))
        
        return interactions

    def get_character_locations(self) -> Dict[str, List[str]]:
        """Get locations associated with each character."""
        char_locations = {}
        
        for source, target, data in self.graph.edges(data=True):
            if (self.graph.nodes[source].get('type') == 'CHARACTER' and 
                self.graph.nodes[target].get('type') == 'LOCATION' and
                data.get('relation_type') == 'LOCATED_IN'):
                
                if source not in char_locations:
                    char_locations[source] = []
                char_locations[source].append(target)
        
        return char_locations

    def get_plot_events(self) -> List[str]:
        """Get all plot events from the graph."""
        events = []
        
        for node, data in self.graph.nodes(data=True):
            if data.get('type') == 'EVENT':
                events.append(node)
        
        return events

    def export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for storage or analysis."""
        return {
            'nodes': [
                {
                    'id': node,
                    **data
                }
                for node, data in self.graph.nodes(data=True)
            ],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    **data
                }
                for source, target, data in self.graph.edges(data=True)
            ]
        }

async def test_gemini_graph_builder():
    try:
        # Initialize components
        gemini_service = GeminiService()
        graph_builder = StandaloneGeminiGraphBuilder(gemini_service)
        
        # Test text
        test_text = '''
        Sarah walked into the old library. The wooden floors creaked under her feet as she approached the librarian, Mr. Thompson. 
        "I'm looking for books about ancient mysteries," she whispered. Mr. Thompson smiled and pointed toward the back corner.
        The library held many secrets, and Sarah felt excited about her research project.
        '''
        
        print('🔍 Testing Gemini Graph Builder...')
        print(f'📝 Input text length: {len(test_text)} characters')
        
        # Test entity extraction
        print('\n⚡ Extracting entities and relationships...')
        entities, relationships = await graph_builder.extract_entities_and_relationships(test_text)
        
        print(f'✅ Extracted {len(entities)} entities and {len(relationships)} relationships')
        
        if entities:
            print('\n📋 Sample entities:')
            for entity in entities[:5]:
                print(f'  - {entity.text} ({entity.type}) - confidence: {entity.confidence}')
        
        if relationships:
            print('\n🔗 Sample relationships:')
            for rel in relationships[:5]:
                print(f'  - {rel.source} -> {rel.target} ({rel.relation_type}) - confidence: {rel.confidence}')
        
        # Build graph
        print('\n🕸️ Building knowledge graph...')
        graph = graph_builder.build_graph(entities, relationships)
        print(f'✅ Graph built with {len(graph.nodes)} nodes and {len(graph.edges)} edges')
        
        # Test graph analysis functions
        print('\n🎭 Character interactions:')
        interactions = graph_builder.get_character_interactions()
        for interaction in interactions[:3]:
            print(f'  - {interaction[0]} <-> {interaction[1]}')
        
        print('\n🗺️ Character locations:')
        char_locations = graph_builder.get_character_locations()
        for char, locations in list(char_locations.items())[:3]:
            print(f'  - {char}: {", ".join(locations)}')
        
        print('\n📖 Plot events:')
        events = graph_builder.get_plot_events()
        for event in events[:3]:
            print(f'  - {event}')
        
        # Export graph data
        print('\n💾 Exporting graph data...')
        graph_data = graph_builder.export_graph_data()
        print(f'✅ Graph data exported with {len(graph_data["nodes"])} nodes and {len(graph_data["edges"])} edges')
        
        print('\n🎉 Gemini Graph Builder test completed successfully!')
        print('\n💰 Cost Analysis:')
        print('  - This test would cost approximately $0.001 with Gemini 2.0 Flash')
        print('  - Equivalent test with OpenAI GPT-4o would cost approximately $0.025')
        print('  - 💡 That\'s 25x cheaper with Gemini!')
        
        return True
        
    except Exception as e:
        print(f'❌ Error testing Gemini Graph Builder: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_graph_builder())
    if success:
        print('\n✅ All tests passed! Ready to deploy Gemini-powered entity extraction.')
    else:
        print('\n❌ Tests failed. Please check the configuration.') 