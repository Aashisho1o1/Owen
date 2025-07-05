"""
Hybrid Indexer - Combines vector store, knowledge graph, and path retrieval
Main interface for the writing assistant's contextual understanding
"""

from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime
import json
import logging
import time

from .vector_store import VectorStore
from .graph_builder import GeminiGraphBuilder
from .path_retriever import PathRetriever
from ..llm.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class HybridIndexer:
    """
    Unified interface for hybrid document indexing combining:
    - Vector-based semantic search
    - Knowledge graph relationships  
    - PathRAG-inspired path retrieval
    - LLM-enhanced entity extraction using Gemini
    """
    
    def __init__(self, 
                 collection_name: str = "documents",
                 gemini_service: Optional[GeminiService] = None):
        """
        Initialize the hybrid indexer with all components.
        
        Args:
            collection_name: Name for the vector collection
            gemini_service: Optional Gemini service instance
        """
        self.vector_store = VectorStore(collection_name)
        self.gemini_service = gemini_service or GeminiService()
        self.graph_builder = GeminiGraphBuilder(self.gemini_service)
        self.path_retriever = None  # Will be initialized after we have a graph
        
        # Track indexed documents
        self.indexed_documents = {}
        
        logger.info("HybridIndexer initialized with Gemini-powered entity extraction")

    async def index_document(self, 
                           document_id: str, 
                           content: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Index a single document with full hybrid processing.
        
        Args:
            document_id: Unique identifier for the document
            content: Document text content
            metadata: Optional metadata dictionary
            
        Returns:
            Indexing results and statistics
        """
        try:
            start_time = time.time()
            
            # Prepare metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                'document_id': document_id,
                'indexed_at': datetime.now().isoformat(),
                'content_length': len(content)
            })
            
            # 1. Vector indexing with narrative-aware chunking
            logger.info(f"Starting vector indexing for document {document_id}")
            vector_chunk_ids = self.vector_store.add_document(content, document_id, doc_metadata)
            
            # 2. Knowledge graph construction using Gemini
            logger.info(f"Building knowledge graph for document {document_id}")
            graph = await self.graph_builder.analyze_text(content)
            
            # 3. Store graph data
            graph_data = self.graph_builder.export_graph_data()
            
            # 4. Initialize path retriever with the graph (if not already initialized)
            if self.path_retriever is None:
                self.path_retriever = PathRetriever(graph, self.vector_store)
            else:
                # Update the path retriever with the new graph
                self.path_retriever.graph = graph
            
            # 5. Calculate document statistics
            stats = {
                'document_id': document_id,
                'processing_time': time.time() - start_time,
                'chunks_created': len(vector_chunk_ids),
                'entities_extracted': len(graph_data['nodes']),
                'relationships_found': len(graph_data['edges']),
                'graph_nodes': len(graph.nodes),
                'graph_edges': len(graph.edges)
            }
            
            # Store document info
            self.indexed_documents[document_id] = {
                'metadata': doc_metadata,
                'stats': stats,
                'graph_data': graph_data,
                'indexed_at': datetime.now()
            }
            
            logger.info(f"Document {document_id} indexed successfully: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            raise
    
    async def index_folder(self, documents: List[Tuple[str, str, Dict]]) -> Dict[str, Any]:
        """
        Index multiple documents as a related collection (e.g., chapters in a book)
        
        Args:
            documents: List of (doc_id, text, metadata) tuples
            
        Returns:
            Batch indexing results
        """
        results = []
        
        # Index each document
        for doc_id, text, metadata in documents:
            result = await self.index_document(doc_id, text, metadata)
            results.append(result)
        
        # Build unified graph from all documents
        doc_texts = [(doc_id, text) for doc_id, text, _ in documents]
        self.graph_builder.build_narrative_graph(doc_texts)
        
        # Reinitialize path retriever with complete graph
        self.path_retriever = PathRetriever(self.graph_builder.graph, self.vector_store)
        
        # Calculate statistics
        successful = len(results)  # All results that completed without exception
        total_entities = sum(r.get('entities_extracted', 0) for r in results)
        total_relationships = sum(r.get('relationships_found', 0) for r in results)
        
        return {
            'documents_indexed': len(documents),
            'successful': successful,
            'failed': len(documents) - successful,
            'total_entities': total_entities,
            'total_relationships': total_relationships,
            'graph_nodes': self.graph_builder.graph.number_of_nodes(),
            'graph_edges': self.graph_builder.graph.number_of_edges(),
            'results': results
        }
    
    async def get_contextual_feedback(self, 
                                    highlighted_text: str,
                                    doc_id: str,
                                    context_window: int = 500) -> Dict[str, Any]:
        """
        Get contextual feedback for highlighted text
        
        Args:
            highlighted_text: The text user highlighted
            doc_id: Document containing the highlight
            context_window: Characters of context around highlight
            
        Returns:
            Contextual analysis and suggestions
        """
        if not self.path_retriever:
            return {
                'error': 'No documents indexed yet'
            }
        
        # Step 1: Get semantic context from vector store
        semantic_results = self.vector_store.search(
            highlighted_text,
            n_results=5,
            filter_dict={'doc_id': doc_id}
        )
        
        # Step 2: Extract entities from highlighted text
        entities = await self._extract_entities_from_text(highlighted_text)
        
        # Step 3: Get relevant paths
        paths = self.path_retriever.retrieve_paths(highlighted_text, top_k=3)
        
        # Step 4: Analyze context
        analysis = {
            'highlighted_text': highlighted_text,
            'semantic_context': [
                {
                    'text': r['text'],
                    'relevance_score': r['score']
                } for r in semantic_results[:3]
            ],
            'entities_mentioned': self._format_entities(entities),
            'narrative_paths': self._format_paths(paths),
            'suggestions': self._generate_suggestions(highlighted_text, entities, paths)
        }
        
        # Step 5: Get character-specific context if a character is mentioned
        character_contexts = []
        for char_entity in entities.get('CHARACTER', []):
            char_name = char_entity['text']
            # For now, skip character arc analysis as the method doesn't exist
            character_contexts.append({
                'character': char_name,
                'arc_summary': f"Character {char_name} appears in the narrative"
            })
        
        if character_contexts:
            analysis['character_contexts'] = character_contexts
        
        return analysis
    
    async def check_consistency(self, 
                              statement: str,
                              doc_id: str,
                              check_type: str = 'all') -> Dict[str, Any]:
        """
        Check consistency of a statement against the knowledge base
        
        Args:
            statement: Statement to verify
            doc_id: Current document ID
            check_type: Type of check ('character', 'plot', 'setting', 'all')
            
        Returns:
            Consistency analysis with potential conflicts
        """
        if not self.path_retriever:
            return {
                'error': 'No documents indexed yet'
            }
        
        # Extract entities from statement
        entities = await self._extract_entities_from_text(statement)
        
        conflicts = []
        confirmations = []
        
        # Check different aspects based on check_type
        if check_type in ['character', 'all']:
            char_conflicts = await self._check_character_consistency(entities, statement)
            conflicts.extend(char_conflicts)
        
        if check_type in ['plot', 'all']:
            plot_conflicts = await self._check_plot_consistency(entities, statement)
            conflicts.extend(plot_conflicts)
        
        if check_type in ['setting', 'all']:
            setting_conflicts = await self._check_setting_consistency(entities, statement)
            conflicts.extend(setting_conflicts)
        
        # Find supporting evidence
        supporting_paths = self.path_retriever.retrieve_paths(statement, top_k=3)
        for path in supporting_paths:
            if path['score'] > 0.7:  # High confidence
                confirmations.append({
                    'type': 'supporting_evidence',
                    'narrative': path['narrative'],
                    'confidence': path['score']
                })
        
        return {
            'statement': statement,
            'is_consistent': len(conflicts) == 0,
            'conflicts': conflicts,
            'confirmations': confirmations,
            'recommendation': self._generate_consistency_recommendation(conflicts, confirmations)
        }
    
    async def get_writing_suggestions(self,
                                    context: str,
                                    suggestion_type: str = 'all') -> Dict[str, Any]:
        """
        Get AI-powered writing suggestions based on context
        
        Args:
            context: Current writing context
            suggestion_type: Type of suggestions ('plot', 'character', 'style', 'all')
            
        Returns:
            Writing suggestions based on the knowledge base
        """
        if not self.path_retriever:
            return {
                'error': 'No documents indexed yet'
            }
        
        suggestions = {
            'context': context[:200] + '...' if len(context) > 200 else context,
            'suggestions': []
        }
        
        # Get relevant paths for context
        paths = self.path_retriever.retrieve_paths(context, top_k=5)
        
        # Extract patterns from paths
        if suggestion_type in ['plot', 'all']:
            plot_patterns = self._analyze_plot_patterns(paths)
            suggestions['suggestions'].extend([
                {
                    'type': 'plot_development',
                    'suggestion': pattern,
                    'based_on': 'narrative_patterns'
                } for pattern in plot_patterns
            ])
        
        if suggestion_type in ['character', 'all']:
            # Analyze character interactions in paths
            char_suggestions = self._analyze_character_patterns(paths)
            suggestions['suggestions'].extend(char_suggestions)
        
        if suggestion_type in ['style', 'all']:
            # Get similar passages for style consistency
            similar_passages = self.vector_store.search(context, n_results=3)
            style_suggestions = self._analyze_style_patterns(similar_passages)
            suggestions['suggestions'].extend(style_suggestions)
        
        return suggestions
    
    def search(self, query: str, search_type: str = 'hybrid', filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Unified search interface
        
        Args:
            query: Search query
            search_type: 'vector', 'graph', or 'hybrid'
            filters: Optional filters (doc_id, entity_type, etc.)
            
        Returns:
            Search results
        """
        results = []
        
        if search_type in ['vector', 'hybrid']:
            # Vector search
            vector_results = self.vector_store.search(query, n_results=10, filter_dict=filters)
            for vr in vector_results:
                results.append({
                    'type': 'text_chunk',
                    'content': vr['text'],
                    'score': vr['score'],
                    'metadata': vr['metadata']
                })
        
        if search_type in ['graph', 'hybrid'] and self.path_retriever:
            # Path-based search
            paths = self.path_retriever.retrieve_paths(query, top_k=5)
            for path in paths:
                results.append({
                    'type': 'narrative_path',
                    'content': path['narrative'],
                    'score': path['score'],
                    'entities': path['entities'],
                    'relationships': path['relationships']
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:10]  # Return top 10
    
    def get_document_stats(self, doc_id: str) -> Dict[str, Any]:
        """Get statistics for an indexed document"""
        if doc_id not in self.indexed_documents:
            return {'error': 'Document not found'}
        
        doc_info = self.indexed_documents[doc_id]
        
        # Count entities by type in graph
        entity_counts = {}
        for node, data in self.graph_builder.graph.nodes(data=True):
            if 'mentions' in data:
                for mention in data['mentions']:
                    if mention['doc_id'] == doc_id:
                        entity_type = data.get('type', 'UNKNOWN')
                        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
                        break
        
        return {
            'doc_id': doc_id,
            'metadata': doc_info['metadata'],
            'chunks': len(doc_info['chunk_ids']),
            'entities': entity_counts,
            'total_entities': doc_info['entity_count'],
            'relationships': doc_info['relationship_count'],
            'indexed_at': doc_info['indexed_at']
        }
    
    def export_knowledge_graph(self, format: str = 'json') -> Any:
        """Export the knowledge graph"""
        if not self.graph_builder.graph:
            return {'error': 'No graph built yet'}
        
        return self.graph_builder.export_graph(format)
    
    # Helper methods
    
    async def _extract_entities_from_text(self, text: str) -> Dict[str, List[Dict]]:
        """Helper method to extract entities from text and format them properly"""
        try:
            entities, _ = await self.graph_builder.extract_entities_and_relationships(text)
            
            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                entity_type = entity.type
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append({
                    'text': entity.text,
                    'confidence': entity.confidence
                })
            
            return entities_by_type
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    def _format_entities(self, entities: Dict[str, List[Dict]]) -> List[Dict[str, str]]:
        """Format entities for output"""
        formatted = []
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                formatted.append({
                    'text': entity['text'],
                    'type': entity_type
                })
        return formatted
    
    def _format_paths(self, paths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format paths for output"""
        return [
            {
                'narrative': path['narrative'],
                'score': path['score'],
                'entities': [e['label'] for e in path['entities']]
            } for path in paths
        ]
    
    def _generate_suggestions(self, text: str, entities: Dict, paths: List[Dict]) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        # Character-based suggestions
        if 'CHARACTER' in entities:
            char_names = [e['text'] for e in entities['CHARACTER']]
            suggestions.append(f"Consider the established traits and relationships of {', '.join(char_names)}")
        
        # Plot coherence suggestions
        if paths and paths[0]['score'] > 0.8:
            suggestions.append("This connects well with established narrative elements")
        
        # Location consistency
        if 'LOCATION' in entities:
            suggestions.append("Verify the spatial consistency with previous mentions of this location")
        
        return suggestions
    
    def _summarize_character_arc(self, arc: List[Dict]) -> str:
        """Summarize a character's arc"""
        if not arc:
            return "No significant events found"
        
        # Group by relationship type
        interactions = [a for a in arc if a['type'] in ['SPEAKS_TO', 'MEETS', 'FEELS_ABOUT']]
        movements = [a for a in arc if a['type'] in ['GOES_TO', 'LIVES_IN']]
        events = [a for a in arc if a['type'] in ['CAUSES', 'PARTICIPATES_IN']]
        
        summary_parts = []
        if interactions:
            summary_parts.append(f"{len(interactions)} character interactions")
        if movements:
            summary_parts.append(f"{len(movements)} location changes")
        if events:
            summary_parts.append(f"{len(events)} plot events")
        
        return f"Character involved in: {', '.join(summary_parts)}"
    
    async def _check_character_consistency(self, entities: Dict, statement: str) -> List[Dict]:
        """Check character consistency"""
        conflicts = []
        
        for char_entity in entities.get('CHARACTER', []):
            char_name = char_entity['text']
            
            # Get character's established patterns
            char_paths = self.path_retriever.get_character_context_paths(char_name, 'all')
            
            # Check for contradictions
            for path in char_paths:
                # Simple contradiction detection (can be enhanced)
                if 'dead' in path['narrative'].lower() and 'alive' in statement.lower():
                    conflicts.append({
                        'type': 'character_state',
                        'character': char_name,
                        'conflict': 'Character previously marked as dead',
                        'evidence': path['narrative']
                    })
        
        return conflicts
    
    async def _check_plot_consistency(self, entities: Dict, statement: str) -> List[Dict]:
        """Check plot consistency"""
        conflicts = []
        
        # Get event patterns
        event_paths = self.path_retriever.retrieve_paths(statement, top_k=5)
        
        # Check for causal inconsistencies
        for path in event_paths:
            if path['score'] > 0.6:
                # Check if events follow logical order
                for rel in path['relationships']:
                    if rel['type'] == 'CAUSES':
                        # Verify causality makes sense
                        pass  # Implement specific checks
        
        return conflicts
    
    async def _check_setting_consistency(self, entities: Dict, statement: str) -> List[Dict]:
        """Check setting/location consistency"""
        conflicts = []
        
        for loc_entity in entities.get('LOCATION', []):
            loc_name = loc_entity['text']
            
            # Check if characters can be in this location
            # based on their previous movements
            # This is simplified - real implementation would be more sophisticated
            
        return conflicts
    
    def _generate_consistency_recommendation(self, conflicts: List[Dict], confirmations: List[Dict]) -> str:
        """Generate recommendation based on consistency check"""
        if not conflicts:
            return "Statement appears consistent with established narrative"
        
        if len(conflicts) == 1:
            return f"Minor inconsistency detected: {conflicts[0]['conflict']}"
        
        return f"Multiple inconsistencies detected. Review {len(conflicts)} potential conflicts."
    
    def _analyze_plot_patterns(self, paths: List[Dict]) -> List[str]:
        """Analyze plot patterns from paths"""
        patterns = []
        
        # Look for causal chains
        for path in paths:
            for rel in path.get('relationships', []):
                if rel['type'] in ['CAUSES', 'LEADS_TO']:
                    patterns.append(f"Consider the consequences of this action")
                    break
        
        return patterns[:3]  # Limit suggestions
    
    def _analyze_character_patterns(self, paths: List[Dict]) -> List[Dict]:
        """Analyze character patterns"""
        suggestions = []
        
        # Extract character interactions
        for path in paths:
            for entity in path.get('entities', []):
                if entity['type'] == 'CHARACTER':
                    suggestions.append({
                        'type': 'character_development',
                        'suggestion': f"Develop {entity['label']}'s role in this scene",
                        'based_on': 'character_presence'
                    })
        
        return suggestions[:2]
    
    def _analyze_style_patterns(self, similar_passages: List[Dict]) -> List[Dict]:
        """Analyze writing style patterns"""
        suggestions = []
        
        # Simple style analysis (can be enhanced)
        avg_length = sum(len(p['text'].split()) for p in similar_passages) / len(similar_passages)
        
        suggestions.append({
            'type': 'style_consistency',
            'suggestion': f"Similar passages average {int(avg_length)} words",
            'based_on': 'passage_analysis'
        })
        
        return suggestions 