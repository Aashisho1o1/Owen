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
        
        # DEBUG: Log which Gemini model is being used by this service
        model_name = "N/A"
        if self.gemini_service and self.gemini_service.model:
            model_name = self.gemini_service.model.model_name
        logger.info(f"HybridIndexer initialized with Gemini model: {model_name}")
        
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
        try:
            # Check if we have any indexed documents
            if not self.path_retriever and not self.indexed_documents:
                # Provide helpful fallback response instead of error
                return {
                    'highlighted_text': highlighted_text,
                    'semantic_context': [],
                    'entities_mentioned': [],
                    'narrative_paths': [],
                    'suggestions': [
                        "Start by writing more content to build your story's context",
                        "Consider what characters, locations, or events this text relates to",
                        "Think about how this connects to your overall narrative"
                    ],
                    'feedback_type': 'general_guidance',
                    'status': 'limited_context'
                }
            
            # Step 1: Get semantic context from vector store
            semantic_results = []
            try:
                semantic_results = self.vector_store.search(
                    highlighted_text,
                    n_results=5,
                    filter_dict={'doc_id': doc_id} if doc_id else None
                )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
                # Try without filter if doc_id filter fails
                try:
                    semantic_results = self.vector_store.search(
                        highlighted_text,
                        n_results=5
                    )
                except Exception as e2:
                    logger.warning(f"General vector search also failed: {e2}")
                    semantic_results = []
            
            # Step 2: Extract entities from highlighted text
            entities = {}
            try:
                entities = await self._extract_entities_from_text(highlighted_text)
            except Exception as e:
                logger.warning(f"Entity extraction failed: {e}")
                entities = {}
            
            # Step 3: Get relevant paths (if path retriever is available)
            paths = []
            if self.path_retriever:
                try:
                    paths = self.path_retriever.retrieve_paths(highlighted_text, top_k=3)
                except Exception as e:
                    logger.warning(f"Path retrieval failed: {e}")
                    paths = []
            
            # Step 4: Analyze context and provide comprehensive feedback
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
                'suggestions': self._generate_enhanced_suggestions(highlighted_text, entities, paths, semantic_results),
                'feedback_type': 'contextual_analysis',
                'status': 'success'
            }
            
            # Step 5: Add character-specific context if characters are mentioned
            character_contexts = []
            for char_entity in entities.get('CHARACTER', []):
                char_name = char_entity['text']
                try:
                    if self.path_retriever:
                        char_paths = self.path_retriever.get_character_context_paths(char_name, 'all')
                        character_contexts.append({
                            'character': char_name,
                            'arc_summary': self._summarize_character_arc(char_paths[:5]),
                            'relationship_count': len([p for p in char_paths if 'SPEAKS_TO' in str(p)]),
                            'event_count': len([p for p in char_paths if 'PARTICIPATES_IN' in str(p)])
                        })
                    else:
                        character_contexts.append({
                            'character': char_name,
                            'arc_summary': f"Character {char_name} appears in the narrative",
                            'relationship_count': 0,
                            'event_count': 0
                        })
                except Exception as e:
                    logger.warning(f"Character context analysis failed for {char_name}: {e}")
            
            if character_contexts:
                analysis['character_contexts'] = character_contexts
            
            # Step 6: Add writing insights based on context
            analysis['writing_insights'] = self._generate_writing_insights(
                highlighted_text, semantic_results, entities, paths
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Contextual feedback failed: {e}")
            # Return graceful fallback instead of error
            return {
                'highlighted_text': highlighted_text,
                'semantic_context': [],
                'entities_mentioned': [],
                'narrative_paths': [],
                'suggestions': [
                    "Continue writing to build more context for analysis",
                    "Consider how this text relates to your story's themes",
                    "Think about character development and plot progression"
                ],
                'feedback_type': 'fallback_guidance',
                'status': 'analysis_unavailable',
                'error_note': 'Contextual analysis temporarily unavailable'
            }
    
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
    
    def _generate_enhanced_suggestions(self, text: str, entities: Dict, paths: List[Dict], semantic_results: List[Dict]) -> List[str]:
        """Generate enhanced contextual suggestions with better fallbacks"""
        suggestions = []
        
        # Character-based suggestions
        if entities.get('CHARACTER'):
            char_names = [e['text'] for e in entities['CHARACTER']]
            suggestions.append(f"Consider the established traits and relationships of {', '.join(char_names)}")
            suggestions.append("Ensure this dialogue/action aligns with the character's established voice")
        
        # Plot coherence suggestions
        if paths:
            if paths[0].get('score', 0) > 0.8:
                suggestions.append("This connects well with established narrative elements")
            elif paths[0].get('score', 0) > 0.5:
                suggestions.append("Consider how this relates to your existing plot threads")
            else:
                suggestions.append("This seems to introduce new narrative elements - consider foreshadowing")
        
        # Location consistency
        if entities.get('LOCATION'):
            suggestions.append("Verify the spatial consistency with previous mentions of this location")
            suggestions.append("Consider the atmosphere and mood this setting should convey")
        
        # Event/action suggestions
        if entities.get('EVENT'):
            suggestions.append("Consider the cause-and-effect relationships of this event")
            suggestions.append("Think about how this advances your plot or character development")
        
        # Semantic context suggestions
        if semantic_results:
            high_relevance = [r for r in semantic_results if r['score'] > 0.7]
            if high_relevance:
                suggestions.append("This text has strong thematic connections to your existing content")
            else:
                suggestions.append("Consider how this new content fits with your established themes")
        
        # Fallback suggestions if no specific context
        if not suggestions:
            suggestions.extend([
                "Consider how this text advances your story's central conflict",
                "Think about the emotional impact this has on your characters",
                "Ensure this moment serves the larger narrative purpose"
            ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_writing_insights(self, text: str, semantic_results: List[Dict], entities: Dict, paths: List[Dict]) -> Dict[str, Any]:
        """Generate writing insights based on contextual analysis"""
        insights = {
            'content_density': 'medium',
            'narrative_connectivity': 'moderate',
            'character_focus': 'balanced',
            'thematic_resonance': 'developing'
        }
        
        # Analyze content density
        if len(text.split()) > 50:
            insights['content_density'] = 'high'
        elif len(text.split()) < 20:
            insights['content_density'] = 'low'
        
        # Analyze narrative connectivity
        if paths and len(paths) > 2:
            insights['narrative_connectivity'] = 'strong'
        elif not paths:
            insights['narrative_connectivity'] = 'weak'
        
        # Analyze character focus
        char_count = len(entities.get('CHARACTER', []))
        if char_count > 2:
            insights['character_focus'] = 'multi-character'
        elif char_count == 1:
            insights['character_focus'] = 'single-character'
        elif char_count == 0:
            insights['character_focus'] = 'descriptive'
        
        # Analyze thematic resonance
        if semantic_results and semantic_results[0].get('score', 0) > 0.8:
            insights['thematic_resonance'] = 'strong'
        elif not semantic_results:
            insights['thematic_resonance'] = 'emerging'
        
        return insights
    
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
    
    async def get_folder_context(self, user_id: int, query: str, max_documents: int = 5) -> Optional[str]:
        """
        ENHANCED: Retrieve relevant context using vector search + LLM semantic matching as fallback.
        
        Args:
            user_id: The user ID to get documents for
            query: The current user query to find relevant context
            max_documents: Maximum number of documents to include in context
            
        Returns:
            Formatted context string or None if no relevant context found
        """
        try:
            logger.info(f"📁 ========== INTELLIGENT FOLDER SCOPE SEARCH ==========")
            logger.info(f"📁 User: {user_id} | Query: '{query}' | Max docs: {max_documents}")
            
            # OPTIMIZED FIX: Reduced timeout to match frontend (2 minutes instead of 4 minutes)
            context_string = await asyncio.wait_for(
                self._execute_folder_search(user_id, query, max_documents),
                timeout=120  # 2 minutes timeout (was 240 seconds)
            )
            
            if context_string:
                logger.info(f"📁 Total context characters: {len(context_string)}")
                logger.info(f"📁 ========== INTELLIGENT FOLDER SCOPE SEARCH COMPLETE ==========")
                return context_string
            else:
                logger.info(f"📁 No relevant context found after all attempts.")
                logger.info(f"📁 ========== INTELLIGENT FOLDER SCOPE SEARCH COMPLETE ==========")
                return None
        except asyncio.TimeoutError:
            logger.error(f"❌ FolderScope context retrieval timed out after 120 seconds for user {user_id}, query '{query}'")
            return None
        except Exception as e:
            logger.error(f"❌ Error in get_folder_context: {e}", exc_info=True)
            return None

    async def _execute_folder_search(self, user_id: int, query: str, max_documents: int) -> Optional[str]:
        """Internal method to execute the actual folder search logic"""
        try:
            # PERFORMANCE FIX: Skip slow document indexing, go straight to search methods
            logger.info(f"📁 PERFORMANCE MODE: Skipping document indexing to prevent timeout")
            
            # STEP 1: Try LLM semantic search first (fastest for most queries)
            logger.info(f"📁 STEP 1: LLM semantic search with Gemini Flash (FAST)...")
            llm_context = await asyncio.wait_for(
                self._get_llm_semantic_context(user_id, query, max_documents),
                timeout=60.0  # 1 minute timeout for LLM search
            )
            if llm_context:
                logger.info(f"📁 ✅ LLM semantic search found context: {len(llm_context)} chars")
                return llm_context
            else:
                logger.info(f"📁 ⚠️ LLM semantic search returned no results")
            
            # STEP 2: Enhanced keyword search (fallback)
            logger.info(f"📁 STEP 2: Enhanced keyword search (FALLBACK)...")
            keyword_context = await asyncio.wait_for(
                self._get_enhanced_keyword_context(user_id, query, max_documents),
                timeout=45.0  # 45 second timeout for keyword search
            )
            if keyword_context:
                logger.info(f"📁 ✅ Enhanced keyword search found context: {len(keyword_context)} chars")
                return keyword_context
            
            logger.info(f"📁 ❌ No relevant context found")
            return None
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Internal folder search timed out for user {user_id}, query '{query}'")
            return None
        except Exception as e:
            logger.error(f"❌ Error in _execute_folder_search: {e}", exc_info=True)
            return None

    async def _ensure_user_documents_indexed(self, user_id: int):
        """Ensure user's documents are indexed in the vector store"""
        try:
            # Import database service
            from services.database import get_db_service
            db_service = get_db_service()
            
            # Get user's documents
            query_sql = """
            SELECT id, title, content, updated_at 
            FROM documents 
            WHERE user_id = %s 
            AND content IS NOT NULL 
            AND LENGTH(TRIM(content)) > 100
            ORDER BY updated_at DESC
            """
            
            documents = db_service.execute_query(query_sql, (user_id,), fetch='all')
            
            if not documents:
                logger.info(f"📁 No documents found for user {user_id} to index")
                return
            
            # Check which documents need indexing
            for doc in documents:
                doc_id = str(doc[0])
                title = doc[1]
                content = doc[2]
                
                # Quick check if document is already indexed
                try:
                    results = self.vector_store.search(
                        query=f"document_id:{doc_id}",
                        n_results=1,
                        filter_dict={"doc_id": doc_id}
                    )
                    
                    if not results:
                        # Document not indexed, add it
                        logger.info(f"📁 Indexing document: {title} ({doc_id})")
                        self.vector_store.add_document(
                            text=content,
                            doc_id=doc_id,
                            metadata={
                                "title": title,
                                "user_id": user_id,
                                "updated_at": doc[3].isoformat() if doc[3] else None
                            }
                        )
                except Exception as index_error:
                    logger.warning(f"⚠️ Failed to index document {doc_id}: {index_error}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to ensure document indexing: {e}")

    async def _get_vector_context_fixed(self, user_id: int, query: str, max_documents: int) -> Optional[str]:
        """Fixed vector store search using correct API"""
        try:
            # Use the correct search method with user filter
            results = self.vector_store.search(
                query=query,
                n_results=max_documents * 3,  # Get more results to filter
                filter_dict={"user_id": user_id}
            )
            
            if not results:
                logger.info("📁 Vector search returned no results")
                return None
            
            # Group by document and get best excerpts
            doc_contexts = {}
            for result in results:
                if result['score'] < 0.3:  # Skip low-relevance results
                    continue
                    
                metadata = result['metadata']
                doc_id = metadata.get('doc_id')
                title = metadata.get('title', f'Document {doc_id}')
                
                if doc_id not in doc_contexts:
                    doc_contexts[doc_id] = {
                        'title': title,
                        'excerpts': [],
                        'max_score': result['score']
                    }
                
                if len(doc_contexts[doc_id]['excerpts']) < 2:  # Max 2 excerpts per doc
                    doc_contexts[doc_id]['excerpts'].append({
                        'text': result['text'][:800],  # Larger excerpts
                        'score': result['score']
                    })
            
            if not doc_contexts:
                return None
            
            # Sort documents by relevance and create context
            sorted_docs = sorted(doc_contexts.items(), 
                               key=lambda x: x[1]['max_score'], 
                               reverse=True)[:max_documents]
            
            context_parts = []
            for doc_id, doc_data in sorted_docs:
                excerpts_text = "\n".join([ex['text'] for ex in doc_data['excerpts']])
                context_parts.append(f"**{doc_data['title']}**:\n{excerpts_text}")
            
            return "\n\n---\n\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"⚠️ Vector search failed: {e}")
            return None

    async def _get_llm_semantic_context(self, user_id: int, query: str, max_documents: int) -> Optional[str]:
        """OPTIMIZED: Use faster Gemini Flash model for semantic document selection"""
        try:
            logger.info(f"📁 LLM STEP 1: Starting semantic search for user {user_id}")
            
            # Import database service
            from services.database import get_db_service
            db_service = get_db_service()
            
            logger.info(f"📁 LLM STEP 2: Database service obtained successfully")
            
            # PERFORMANCE FIX: Limit to 5 recent documents for speed
            query_sql = """
            SELECT id, title, content, updated_at 
            FROM documents 
            WHERE user_id = %s 
            AND content IS NOT NULL 
            AND LENGTH(TRIM(content)) > 50
            ORDER BY updated_at DESC 
            LIMIT 5
            """
            
            logger.info(f"📁 LLM STEP 3: Executing database query for user {user_id}")
            logger.info(f"📁 LLM STEP 3a: Query: \n{query_sql}")
            logger.info(f"📁 LLM STEP 3b: Params: {(user_id,)}")

            # CRITICAL FIX: Use correct synchronous database service method
            documents = db_service.execute_query(query_sql, (user_id,), fetch='all')
            
            logger.info(f"📁 LLM STEP 4: Database query executed successfully")
            logger.info(f"📁 LLM STEP 4a: Found {len(documents) if documents else 0} documents")
            
            if not documents:
                logger.info(f"📁 LLM Search: No documents found for user {user_id}")
                return None
            
            logger.info(f"📁 LLM STEP 5: Processing documents for summaries")
            
            # PERFORMANCE FIX: Create shorter summaries for faster processing
            doc_summaries = []
            for i, doc in enumerate(documents):
                try:
                    doc_id = doc['id'] if isinstance(doc, dict) else doc[0]
                    title = doc['title'] if isinstance(doc, dict) else doc[1] 
                    content = doc['content'] if isinstance(doc, dict) else doc[2]
                    
                    logger.info(f"📁 LLM STEP 5.{i+1}: Processing doc '{title}' (content length: {len(content)})")
                    
                    # MUCH shorter summary - just first 200 chars
                    summary = content[:200] + "..." if len(content) > 200 else content
                    doc_summaries.append({
                        'id': str(doc_id),
                        'title': title,
                        'summary': summary
                    })
                    
                    logger.info(f"📁 LLM STEP 5.{i+1}: ✅ Summary created (length: {len(summary)})")
                    
                except Exception as doc_error:
                    logger.error(f"📁 LLM STEP 5.{i+1}: ❌ Error processing document: {doc_error}")
                    logger.error(f"📁 LLM STEP 5.{i+1}: Document data: {doc}")
                    continue
            
            logger.info(f"📁 LLM STEP 6: Created {len(doc_summaries)} document summaries")
            
            if not doc_summaries:
                logger.warning(f"📁 LLM Search: No valid document summaries created")
                return None
            
            logger.info(f"📁 LLM STEP 7: Initializing Gemini service")
            
            # PERFORMANCE FIX: Use simpler, faster prompt
            from services.llm.gemini_service import GeminiService
            
            gemini_flash = GeminiService()
            
            logger.info(f"📁 LLM STEP 8: Creating prompt for {len(doc_summaries)} documents")
            
            # PERFORMANCE FIX: Much shorter prompt for faster processing
            prompt = f"""Query: "{query}"

Which documents contain relevant info? Return only the document numbers (1,2,3...) or "NONE".

{chr(10).join([f"{i+1}. {doc['title']}: {doc['summary'][:100]}..." for i, doc in enumerate(doc_summaries)])}

Answer:"""

            logger.info(f"📁 LLM STEP 9: Prompt created (length: {len(prompt)})")
            logger.info(f"📁 LLM STEP 9a: Prompt preview: {prompt[:200]}...")
            
            logger.info(f"📁 LLM Search: Analyzing {len(doc_summaries)} documents for relevance...")
            
            logger.info(f"📁 LLM STEP 10: Calling Gemini Flash model")
            
            response = await gemini_flash.generate_text(prompt)
            
            logger.info(f"📁 LLM STEP 11: ✅ Gemini response received")
            
            # Parse LLM response
            response_text = response.strip()
            logger.info(f"📁 LLM Response: {response_text}")
            
            if response_text == "NONE" or not response_text:
                logger.info(f"📁 LLM Search: No relevant documents identified")
                return None
            
            logger.info(f"📁 LLM STEP 12: Parsing response for document indices")
            
            # Extract document IDs more robustly
            try:
                # Handle various response formats: "1,2,3" or "Documents 1, 2, 3" etc.
                import re
                numbers = re.findall(r'\d+', response_text)
                selected_indices = [int(x) - 1 for x in numbers if x.isdigit()]
                selected_indices = [i for i in selected_indices if 0 <= i < len(doc_summaries)]
                
                logger.info(f"📁 LLM STEP 12a: Found numbers: {numbers}")
                logger.info(f"📁 LLM STEP 12b: Selected indices: {selected_indices}")
                
            except Exception as parse_error:
                logger.error(f"📁 LLM STEP 12: ❌ Failed to parse response: {parse_error}")
                logger.error(f"📁 LLM STEP 12a: Response text: {response_text}")
                return None
            
            if not selected_indices:
                logger.info(f"📁 LLM Search: No valid document indices found")
                return None
            
            logger.info(f"📁 LLM STEP 13: Extracting content for {len(selected_indices)} documents")
            
            # Get full content for selected documents
            context_parts = []
            for idx in selected_indices[:max_documents]:
                try:
                    doc = documents[idx]
                    title = doc['title'] if isinstance(doc, dict) else doc[1]
                    content = doc['content'] if isinstance(doc, dict) else doc[2]
                    
                    logger.info(f"📁 LLM STEP 13.{idx+1}: Extracting from '{title}'")
                    
                    # PERFORMANCE FIX: Extract smaller, more focused excerpts
                    excerpt = self._extract_smart_excerpt(content, query, max_length=600)  # Reduced from 1000
                    context_parts.append(f"**{title}**:\n{excerpt}")
                    
                    logger.info(f"📁 LLM STEP 13.{idx+1}: ✅ Excerpt created (length: {len(excerpt)})")
                    
                except Exception as extract_error:
                    logger.error(f"📁 LLM STEP 13.{idx+1}: ❌ Error extracting content: {extract_error}")
                    continue
            
            logger.info(f"📁 LLM Search: Found {len(context_parts)} relevant documents")
            
            final_context = "\n\n---\n\n".join(context_parts)
            logger.info(f"📁 LLM STEP 14: ✅ Final context created (length: {len(final_context)})")
            
            return final_context
            
        except Exception as e:
            logger.error(f"❌ LLM semantic search failed with detailed error:")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error message: {str(e)}")
            logger.error(f"❌ Error args: {e.args}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return None

    def _extract_smart_excerpt(self, content: str, query: str, max_length: int = 1000) -> str:
        """Extract the most relevant excerpt from content based on query"""
        try:
            # Split into sentences
            sentences = [s.strip() for s in content.replace('\n', ' ').split('.') if s.strip()]
            
            if len(sentences) <= 3:
                return content[:max_length]
            
            # Simple scoring: more query words = higher score
            query_words = set(query.lower().split())
            
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                words = set(sentence.lower().split())
                score = len(query_words.intersection(words))
                # Boost score for sentences in the middle (often contain more context)
                if len(sentences) > 5 and len(sentences) * 0.2 < i < len(sentences) * 0.8:
                    score += 1
                sentence_scores.append((score, i, sentence))
            
            # Sort by score and get top sentences
            sentence_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Take top scoring sentences and some context
            selected_indices = set()
            for score, idx, _ in sentence_scores[:3]:  # Top 3 sentences
                if score > 0:  # Only if there's some relevance
                    # Add context sentences around the selected one
                    for i in range(max(0, idx-1), min(len(sentences), idx+2)):
                        selected_indices.add(i)
            
            if not selected_indices:
                # Fallback: take first part of document
                return content[:max_length]
            
            # Create excerpt from selected sentences
            selected_indices = sorted(selected_indices)
            excerpt_sentences = [sentences[i] for i in selected_indices]
            excerpt = '. '.join(excerpt_sentences) + '.'
            
            return excerpt[:max_length] + "..." if len(excerpt) > max_length else excerpt
            
        except Exception as e:
            logger.warning(f"⚠️ Smart excerpt extraction failed: {e}")
            return content[:max_length]

    async def _get_enhanced_keyword_context(self, user_id: int, query: str, max_documents: int) -> Optional[str]:
        """Enhanced keyword search as last resort - much better than the previous version"""
        try:
            logger.info(f"📁 KEYWORD STEP 1: Starting enhanced keyword search for user {user_id}")
            logger.info(f"📁 KEYWORD STEP 1a: Query: '{query}'")
            logger.info(f"📁 KEYWORD STEP 1b: Max documents: {max_documents}")
            
            # Import database service
            from services.database import get_db_service
            db_service = get_db_service()
            
            logger.info(f"📁 KEYWORD STEP 2: Database service obtained successfully")
            
            # Expand query with synonyms and related terms
            logger.info(f"📁 KEYWORD STEP 3: Expanding query terms")
            expanded_query_terms = self._expand_query_terms(query)
            logger.info(f"📁 KEYWORD STEP 3a: Expanded terms: {expanded_query_terms}")
            
            # CRITICAL FIX: Use simpler SQL query instead of PostgreSQL full-text search
            logger.info(f"📁 KEYWORD STEP 4: Building simplified SQL query")
            
            # Simple LIKE-based search that works on all databases
            like_pattern = f"%{query}%"
            
            query_sql = """
            SELECT id, title, content, updated_at
            FROM documents 
            WHERE user_id = %s 
            AND content IS NOT NULL 
            AND LENGTH(TRIM(content)) > 50
            AND (title ILIKE %s OR content ILIKE %s)
            ORDER BY updated_at DESC
            LIMIT %s
            """
            
            logger.info(f"📁 KEYWORD STEP 5: Executing database query")
            logger.info(f"📁 KEYWORD STEP 5a: Query: \n{query_sql}")
            logger.info(f"📁 KEYWORD STEP 5b: Params: {(user_id, f'%{query}%', f'%{query}%', max_documents)}")

            # CRITICAL FIX: Use correct synchronous database service method
            documents = db_service.execute_query(
                query_sql,
                (user_id, f'%{query}%', f'%{query}%', max_documents),
                fetch='all'
            )
            
            logger.info(f"📁 KEYWORD STEP 6: Database query executed successfully")
            logger.info(f"📁 KEYWORD STEP 6a: Found {len(documents) if documents else 0} documents")
            
            if not documents:
                logger.info(f"📁 KEYWORD Search: No documents found for user {user_id}")
                return None
            
            logger.info(f"📁 KEYWORD STEP 7: Processing {len(documents)} documents")
            
            # Process and rank results
            context_parts = []
            for i, doc in enumerate(documents[:max_documents]):
                try:
                    title = doc['title'] if isinstance(doc, dict) else doc[1]
                    content = doc['content'] if isinstance(doc, dict) else doc[2]
                    
                    logger.info(f"📁 KEYWORD STEP 7.{i+1}: Processing '{title}' (content length: {len(content)})")
                    
                    # Extract smart excerpt
                    excerpt = self._extract_smart_excerpt(content, query, 800)
                    context_parts.append(f"**{title}**:\n{excerpt}")
                    
                    logger.info(f"📁 KEYWORD STEP 7.{i+1}: ✅ Excerpt created (length: {len(excerpt)})")
                    
                except Exception as doc_error:
                    logger.error(f"📁 KEYWORD STEP 7.{i+1}: ❌ Error processing document: {doc_error}")
                    logger.error(f"📁 KEYWORD STEP 7.{i+1}: Document data: {doc}")
                    continue
            
            logger.info(f"📁 KEYWORD STEP 8: Created {len(context_parts)} context parts")
            
            final_context = "\n\n---\n\n".join(context_parts) if context_parts else None
            
            if final_context:
                logger.info(f"📁 KEYWORD STEP 9: ✅ Final context created (length: {len(final_context)})")
            else:
                logger.info(f"📁 KEYWORD STEP 9: No context parts created")
            
            return final_context
            
        except Exception as e:
            logger.error(f"❌ Enhanced keyword search failed with detailed error:")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error message: {str(e)}")
            logger.error(f"❌ Error args: {e.args}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return None

    def _expand_query_terms(self, query: str) -> List[str]:
        """Expand query with related terms for better matching"""
        query_lower = query.lower()
        terms = [query_lower]
        
        # Common expansions for writing-related queries
        expansions = {
            'letter': ['note', 'message', 'correspondence', 'mail', 'writing'],
            'character': ['person', 'protagonist', 'hero', 'villain', 'figure'],
            'gave': ['handed', 'delivered', 'passed', 'sent', 'provided'],
            'received': ['got', 'obtained', 'accepted', 'took'],
            'wrote': ['written', 'penned', 'composed', 'authored'],
            'said': ['told', 'spoke', 'mentioned', 'stated', 'expressed'],
            'went': ['traveled', 'moved', 'headed', 'departed'],
            'found': ['discovered', 'located', 'uncovered', 'encountered'],
        }
        
        # Add expansions for words in the query
        for word in query_lower.split():
            if word in expansions:
                terms.extend(expansions[word])
        
        return list(set(terms))  # Remove duplicates 