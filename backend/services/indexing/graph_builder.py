"""
Advanced graph builder for narrative analysis using Gemini for entity extraction.
Implements PathRAG-inspired knowledge graph construction with LLM-enhanced NER.
"""

import asyncio
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
import networkx as nx
import json
from dataclasses import dataclass, asdict

# Import Gemini service instead of spaCy
from ..llm.gemini_service import GeminiService

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

class GeminiGraphBuilder:
    """
    Advanced graph builder using Gemini for entity extraction and relationship detection.
    Optimized for narrative analysis and character tracking.
    """
    
    def __init__(self, gemini_service: Optional[GeminiService] = None):
        """Initialize the graph builder with Gemini service."""
        self.gemini_service = gemini_service or GeminiService()
        self.graph = nx.DiGraph()
        
        # Entity extraction prompt template
        self.entity_extraction_prompt = """You must return ONLY valid JSON, no other text or explanation.

Extract entities and relationships from the text below.

Entity types: CHARACTER, LOCATION, EVENT, THEME, ORGANIZATION
Relationship types: INTERACTS_WITH, LOCATED_IN, PARTICIPATES_IN, REPRESENTS, BELONGS_TO, CAUSES, PRECEDES

Return exactly this JSON format:
{{
    "entities": [
        {{
            "text": "entity text",
            "type": "CHARACTER",
            "start_pos": 0,
            "end_pos": 10,
            "confidence": 0.95
        }}
    ],
    "relationships": [
        {{
            "source": "entity1",
            "target": "entity2",
            "relation_type": "INTERACTS_WITH",
            "confidence": 0.9,
            "context": "brief context"
        }}
    ]
}}

Text to analyze:
{text}"""

    async def extract_entities_and_relationships(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        """
        Extract entities and relationships from text using Gemini.
        
        Args:
            text: Input text for analysis
            
        Returns:
            Tuple of (entities, relationships)
        """
        try:
            # Format prompt with text
            prompt = self.entity_extraction_prompt.format(text=text)
            
            # Get response from Gemini
            response = await self.gemini_service.generate_response(prompt)
            
            # Parse JSON response - handle markdown code blocks and clean formatting
            try:
                # Clean the response first
                response_text = response.strip()
                
                # Remove common markdown formatting
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                # Remove any leading/trailing text that's not JSON
                start_brace = response_text.find('{')
                end_brace = response_text.rfind('}')
                if start_brace != -1 and end_brace != -1:
                    response_text = response_text[start_brace:end_brace+1]
                
                data = json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response[:200]}...")
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
            
            logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
            return entities, relationships
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return [], []

    def build_graph(self, entities: List[Entity], relationships: List[Relationship]) -> nx.DiGraph:
        """
        Build a NetworkX graph from extracted entities and relationships.
        
        Args:
            entities: List of extracted entities
            relationships: List of extracted relationships
            
        Returns:
            NetworkX directed graph
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
        
        logger.info(f"Built graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
        return self.graph

    async def analyze_text(self, text: str, chunk_size: int = 2000) -> nx.DiGraph:
        """
        Analyze text and build a complete knowledge graph.
        
        Args:
            text: Input text to analyze
            chunk_size: Size of text chunks for processing
            
        Returns:
            Complete knowledge graph
        """
        # Split text into manageable chunks if needed
        chunks = self._split_text(text, chunk_size)
        
        all_entities = []
        all_relationships = []
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            entities, relationships = await self.extract_entities_and_relationships(chunk)
            all_entities.extend(entities)
            all_relationships.extend(relationships)
        
        # Merge duplicate entities and relationships
        merged_entities = self._merge_entities(all_entities)
        merged_relationships = self._merge_relationships(all_relationships)
        
        # Build final graph
        return self.build_graph(merged_entities, merged_relationships)

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        overlap = chunk_size // 4  # 25% overlap
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks

    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge duplicate entities based on text similarity."""
        merged = {}
        
        for entity in entities:
            key = entity.text.lower().strip()
            if key not in merged:
                merged[key] = entity
            else:
                # Keep entity with higher confidence
                if entity.confidence > merged[key].confidence:
                    merged[key] = entity
        
        return list(merged.values())

    def _merge_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Merge duplicate relationships."""
        merged = {}
        
        for rel in relationships:
            key = (rel.source.lower(), rel.target.lower(), rel.relation_type)
            if key not in merged:
                merged[key] = rel
            else:
                # Keep relationship with higher confidence
                if rel.confidence > merged[key].confidence:
                    merged[key] = rel
        
        return list(merged.values())

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

    def calculate_centrality_metrics(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality metrics for nodes."""
        metrics = {}
        
        # Only calculate if graph has nodes
        if len(self.graph.nodes) == 0:
            return metrics
        
        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness_centrality = nx.betweenness_centrality(self.graph)
            
            # Convert to undirected for closeness centrality
            undirected_graph = self.graph.to_undirected()
            closeness_centrality = nx.closeness_centrality(undirected_graph)
            
            for node in self.graph.nodes:
                metrics[node] = {
                    'degree_centrality': degree_centrality.get(node, 0.0),
                    'betweenness_centrality': betweenness_centrality.get(node, 0.0),
                    'closeness_centrality': closeness_centrality.get(node, 0.0)
                }
        
        except Exception as e:
            logger.error(f"Error calculating centrality metrics: {e}")
        
        return metrics 