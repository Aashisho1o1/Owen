"""
Path-based retrieval system inspired by PathRAG
Focuses on relational paths rather than broad subgraphs
"""

from typing import List, Dict, Any, Tuple, Optional, Set
import networkx as nx
import numpy as np
from collections import defaultdict, deque
import heapq

class PathRetriever:
    """
    Implements PathRAG-inspired retrieval focusing on:
    - Flow-based path pruning
    - Reliability scoring
    - Textual path generation
    """
    
    def __init__(self, graph: nx.DiGraph, ector_store):
        self.graph = graph
        self.vector_store = vector_store
        
        # Path configuration
        self.max_path_length = 4
        self.max_paths_per_node = 10
        self.distance_decay = 0.8  # Penalty for longer paths
        
    def retrieve_paths(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Main retrieval method - finds and ranks relevant paths
        
        Args:
            query: User query
            top_k: Number of paths to return
            
        Returns:
            List of ranked paths with metadata
        """
        # Step 1: Initial node retrieval via vector search
        initial_nodes = self._get_initial_nodes(query)
        
        # Step 2: Find all relevant paths from initial nodes
        all_paths = self._find_relevant_paths(initial_nodes)
        
        # Step 3: Apply flow-based pruning
        pruned_paths = self._prune_paths(all_paths)
        
        # Step 4: Score and rank paths
        scored_paths = self._score_paths(pruned_paths, query)
        
        # Step 5: Generate textual representations
        textual_paths = self._generate_textual_paths(scored_paths[:top_k])
        
        return textual_paths
    
    def _get_initial_nodes(self, query: str, n_nodes: int = 5) -> List[str]:
        """
        Retrieve initial nodes using vector similarity
        
        Args:
            query: Search query
            n_nodes: Number of initial nodes
            
        Returns:
            List of node IDs
        """
        # Search in vector store for relevant chunks
        results = self.vector_store.search(query, n_results=n_nodes * 2)
        
        initial_nodes = set()
        
        # Map chunks back to graph nodes
        for result in results:
            doc_id = result['metadata']['doc_id']
            
            # Find nodes mentioned in this document
            for node_id, data in self.graph.nodes(data=True):
                if 'mentions' in data:
                    for mention in data['mentions']:
                        if mention['doc_id'] == doc_id:
                            initial_nodes.add(node_id)
                            break
            
            if len(initial_nodes) >= n_nodes:
                break
        
        return list(initial_nodes)[:n_nodes]
    
    def _find_relevant_paths(self, start_nodes: List[str]) -> List[List[str]]:
        """
        Find all paths up to max_path_length from start nodes
        
        Args:
            start_nodes: Starting node IDs
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        all_paths = []
        
        for start_node in start_nodes:
            if start_node not in self.graph:
                continue
            
            # BFS to find paths
            queue = deque([(start_node, [start_node])])
            node_paths = []
            
            while queue and len(node_paths) < self.max_paths_per_node:
                current_node, path = queue.popleft()
                
                if len(path) > 1:  # Don't include single-node paths
                    node_paths.append(path)
                
                if len(path) < self.max_path_length:
                    # Explore neighbors
                    for neighbor in self.graph.neighbors(current_node):
                        if neighbor not in path:  # Avoid cycles
                            new_path = path + [neighbor]
                            queue.append((neighbor, new_path))
            
            all_paths.extend(node_paths)
        
        return all_paths
    
    def _prune_paths(self, paths: List[List[str]]) -> List[List[str]]:
        """
        Apply flow-based pruning to remove redundant paths
        
        Args:
            paths: List of paths
            
        Returns:
            Pruned list of paths
        """
        if not paths:
            return []
        
        # Calculate path importance scores
        path_scores = []
        
        for path in paths:
            # Calculate edge weights sum
            edge_weight = 0
            for i in range(len(path) - 1):
                if self.graph.has_edge(path[i], path[i+1]):
                    edge_data = self.graph[path[i]][path[i+1]]
                    # Weight based on relationship type and frequency
                    weight = 1.0
                    if 'type' in edge_data:
                        # Prioritize certain relationship types
                        if edge_data['type'] in ['CAUSES', 'LEADS_TO', 'RESULTS_IN']:
                            weight = 2.0
                        elif edge_data['type'] in ['SPEAKS_TO', 'FEELS_ABOUT']:
                            weight = 1.5
                    edge_weight += weight
            
            # Apply distance penalty
            distance_penalty = self.distance_decay ** (len(path) - 2)
            score = edge_weight * distance_penalty
            
            path_scores.append((score, path))
        
        # Sort by score and remove redundant paths
        path_scores.sort(reverse=True, key=lambda x: x[0])
        
        pruned_paths = []
        covered_edges = set()
        
        for score, path in path_scores:
            # Check if this path adds new information
            path_edges = set()
            for i in range(len(path) - 1):
                path_edges.add((path[i], path[i+1]))
            
            # If path has unique edges, keep it
            if not path_edges.issubset(covered_edges):
                pruned_paths.append(path)
                covered_edges.update(path_edges)
            
            if len(pruned_paths) >= 20:  # Limit total paths
                break
        
        return pruned_paths
    
    def _score_paths(self, paths: List[List[str]], query: str) -> List[Tuple[float, List[str]]]:
        """
        Score paths based on relevance to query
        
        Args:
            paths: List of paths
            query: Original query
            
        Returns:
            List of (score, path) tuples sorted by score
        """
        scored_paths = []
        
        for path in paths:
            score = 0.0
            
            # 1. Semantic relevance of nodes to query
            node_relevance = 0.0
            for node_id in path:
                if node_id in self.graph:
                    node_data = self.graph.nodes[node_id]
                    if 'label' in node_data:
                        # Simple keyword matching (can be improved with embeddings)
                        label_lower = node_data['label'].lower()
                        query_lower = query.lower()
                        if any(word in label_lower for word in query_lower.split()):
                            node_relevance += 1.0
            
            # 2. Path coherence (strong relationships)
            path_coherence = 0.0
            for i in range(len(path) - 1):
                if self.graph.has_edge(path[i], path[i+1]):
                    edge_data = self.graph[path[i]][path[i+1]]
                    if edge_data.get('type') in ['CAUSES', 'LEADS_TO', 'SPEAKS_TO']:
                        path_coherence += 1.0
            
            # 3. Entity diversity (different types of entities)
            entity_types = set()
            for node_id in path:
                if node_id in self.graph:
                    entity_types.add(self.graph.nodes[node_id].get('type', 'UNKNOWN'))
            diversity_score = len(entity_types) / len(path)
            
            # 4. Length penalty
            length_penalty = 1.0 / (1.0 + 0.1 * (len(path) - 2))
            
            # Combine scores
            score = (
                node_relevance * 0.4 +
                path_coherence * 0.3 +
                diversity_score * 0.2 +
                length_penalty * 0.1
            )
            
            scored_paths.append((score, path))
        
        # Sort by score (descending)
        scored_paths.sort(reverse=True, key=lambda x: x[0])
        
        return scored_paths
    
    def _generate_textual_paths(self, scored_paths: List[Tuple[float, List[str]]]) -> List[Dict[str, Any]]:
        """
        Convert graph paths to human-readable text
        
        Args:
            scored_paths: List of (score, path) tuples
            
        Returns:
            List of textual path representations
        """
        textual_paths = []
        
        for score, path in scored_paths:
            # Build narrative from path
            narrative_parts = []
            
            for i, node_id in enumerate(path):
                if node_id not in self.graph:
                    continue
                
                node_data = self.graph.nodes[node_id]
                node_label = node_data.get('label', node_id)
                node_type = node_data.get('type', 'ENTITY')
                
                # Add node description
                if i == 0:
                    narrative_parts.append(f"{node_type}: {node_label}")
                
                # Add edge description if not last node
                if i < len(path) - 1:
                    next_node_id = path[i + 1]
                    if self.graph.has_edge(node_id, next_node_id):
                        edge_data = self.graph[node_id][next_node_id]
                        rel_type = edge_data.get('type', 'relates to')
                        
                        next_node_data = self.graph.nodes.get(next_node_id, {})
                        next_label = next_node_data.get('label', next_node_id)
                        next_type = next_node_data.get('type', 'ENTITY')
                        
                        # Format relationship
                        if rel_type == 'SPEAKS_TO':
                            narrative_parts.append(f"→ speaks to {next_label}")
                        elif rel_type == 'GOES_TO':
                            narrative_parts.append(f"→ goes to {next_label}")
                        elif rel_type == 'CAUSES':
                            narrative_parts.append(f"→ causes {next_label}")
                        elif rel_type == 'FEELS_ABOUT':
                            narrative_parts.append(f"→ has feelings about {next_label}")
                        else:
                            narrative_parts.append(f"→ {rel_type.lower().replace('_', ' ')} {next_label}")
            
            # Get supporting text from documents
            supporting_texts = self._get_supporting_texts(path)
            
            textual_path = {
                'path': path,
                'score': score,
                'narrative': ' '.join(narrative_parts),
                'supporting_texts': supporting_texts,
                'entities': self._extract_path_entities(path),
                'relationships': self._extract_path_relationships(path)
            }
            
            textual_paths.append(textual_path)
        
        # Reverse order for LLM prompting (most relevant at end)
        textual_paths.reverse()
        
        return textual_paths
    
    def _get_supporting_texts(self, path: List[str]) -> List[str]:
        """
        Get text chunks that support this path
        
        Args:
            path: List of node IDs
            
        Returns:
            List of relevant text excerpts
        """
        supporting_texts = []
        doc_ids = set()
        
        # Collect all documents mentioning nodes in path
        for node_id in path:
            if node_id in self.graph:
                node_data = self.graph.nodes[node_id]
                if 'mentions' in node_data:
                    for mention in node_data['mentions']:
                        doc_ids.add(mention['doc_id'])
        
        # Get text chunks for these documents
        for doc_id in doc_ids:
            # Search vector store for this document's chunks
            results = self.vector_store.search(
                "",  # Empty query
                filter_dict={'doc_id': doc_id},
                n_results=2
            )
            
            for result in results:
                supporting_texts.append(result['text'][:200] + "...")
        
        return supporting_texts[:3]  # Limit to 3 excerpts
    
    def _extract_path_entities(self, path: List[str]) -> List[Dict[str, str]]:
        """Extract entity information from path"""
        entities = []
        
        for node_id in path:
            if node_id in self.graph:
                node_data = self.graph.nodes[node_id]
                entities.append({
                    'id': node_id,
                    'label': node_data.get('label', ''),
                    'type': node_data.get('type', '')
                })
        
        return entities
    
    def _extract_path_relationships(self, path: List[str]) -> List[Dict[str, str]]:
        """Extract relationship information from path"""
        relationships = []
        
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i+1]):
                edge_data = self.graph[path[i]][path[i+1]]
                relationships.append({
                    'source': path[i],
                    'target': path[i+1],
                    'type': edge_data.get('type', 'RELATED_TO')
                })
        
        return relationships
    
    def get_character_context_paths(self, character_name: str, context_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Get context-specific paths for a character
        
        Args:
            character_name: Character name
            context_type: Type of context ('relationships', 'events', 'locations', 'all')
            
        Returns:
            List of relevant paths
        """
        char_node = f"CHARACTER_{character_name.lower().replace(' ', '_')}"
        
        if char_node not in self.graph:
            return []
        
        # Find paths based on context type
        if context_type == 'relationships':
            target_types = ['CHARACTER']
            rel_types = ['SPEAKS_TO', 'FEELS_ABOUT', 'MEETS']
        elif context_type == 'events':
            target_types = ['EVENT']
            rel_types = ['CAUSES', 'PARTICIPATES_IN', 'WITNESSES']
        elif context_type == 'locations':
            target_types = ['LOCATION']
            rel_types = ['GOES_TO', 'LIVES_IN', 'VISITS']
        else:
            target_types = None
            rel_types = None
        
        # Find relevant paths
        paths = []
        visited = set()
        
        def dfs(node, path, depth):
            if depth > 3 or len(paths) > 10:
                return
            
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    neighbor_data = self.graph.nodes[neighbor]
                    edge_data = self.graph[node][neighbor]
                    
                    # Check if this matches our criteria
                    if (not target_types or neighbor_data.get('type') in target_types) and \
                       (not rel_types or edge_data.get('type') in rel_types):
                        new_path = path + [neighbor]
                        paths.append(new_path)
                        visited.add(neighbor)
                        dfs(neighbor, new_path, depth + 1)
        
        dfs(char_node, [char_node], 0)
        
        # Score and convert to textual paths
        scored_paths = self._score_paths(paths, character_name)
        return self._generate_textual_paths(scored_paths[:5]) 