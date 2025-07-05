# 🚀 PathRAG Contextual Understanding System - Usage Guide

## Overview

Your AI writing assistant now includes a sophisticated **PathRAG (Path-based Retrieval-Augmented Generation)** system that provides contextual understanding for your writing. This guide explains how to use and understand the system.

## 🎯 What is PathRAG?

PathRAG is an advanced approach to contextual understanding that combines:
- **Vector Search**: Semantic similarity using embeddings
- **Knowledge Graphs**: Entity relationships and connections
- **Path-based Retrieval**: Finding meaningful paths through your narrative

### Key Benefits for Writing:
- **Contextual Feedback**: Get AI suggestions based on your story's established elements
- **Consistency Checking**: Verify character details, plot points, and world-building
- **Character Arc Analysis**: Track character development across your story
- **Writing Suggestions**: Context-aware recommendations for plot, character, and style

## 🏗️ System Architecture

### Core Components

#### 1. **VectorStore** (`backend/services/indexing/vector_store.py`)
```python
# Creates semantic embeddings for text chunks
vector_store = VectorStore("my_story")
chunks = vector_store.add_document(text, "chapter_1", metadata)
results = vector_store.search("Emma meets Marcus", n_results=5)
```

**What it does:**
- Chunks your text intelligently (preserving paragraph boundaries)
- Creates embeddings using sentence-transformers
- Enables semantic search across your content

#### 2. **GraphBuilder** (`backend/services/indexing/graph_builder.py`)
```python
# Extracts entities and relationships using Gemini LLM
graph_builder = GeminiGraphBuilder(gemini_service)
entities, relationships = await graph_builder.extract_entities_and_relationships(text)
graph = graph_builder.build_graph(entities, relationships)
```

**What it does:**
- Identifies characters, locations, events, themes
- Maps relationships (speaks_to, goes_to, causes, etc.)
- Builds a NetworkX graph for path finding

#### 3. **PathRetriever** (`backend/services/indexing/path_retriever.py`)
```python
# Implements PathRAG algorithm
path_retriever = PathRetriever(graph, vector_store)
paths = path_retriever.retrieve_paths("Emma's character development", top_k=5)
```

**What it does:**
- Finds initial nodes via vector search
- Explores paths up to 4 hops away
- Applies flow-based pruning to remove redundancy
- Generates human-readable narrative paths

#### 4. **HybridIndexer** (`backend/services/indexing/hybrid_indexer.py`)
```python
# Unified interface for all components
indexer = HybridIndexer(collection_name="my_story")
await indexer.index_document("chapter_1", text, metadata)
feedback = await indexer.get_contextual_feedback("highlighted text", "chapter_1")
```

**What it does:**
- Coordinates all components
- Provides unified API for all features
- Handles document indexing and retrieval

## 🚀 How to Use the System

### 1. **Index Your Documents**

```python
from services.indexing.hybrid_indexer import HybridIndexer

# Initialize the system
indexer = HybridIndexer(collection_name="my_novel")

# Index a single document
result = await indexer.index_document(
    document_id="chapter_1",
    content=chapter_text,
    metadata={"type": "chapter", "number": 1, "title": "The Beginning"}
)

# Index multiple documents (e.g., chapters)
documents = [
    ("chapter_1", chapter1_text, {"type": "chapter", "number": 1}),
    ("chapter_2", chapter2_text, {"type": "chapter", "number": 2}),
    ("characters", character_profiles, {"type": "reference"})
]
batch_result = await indexer.index_folder(documents)
```

### 2. **Get Contextual Feedback**

```python
# When user highlights text in your editor
feedback = await indexer.get_contextual_feedback(
    highlighted_text="Emma walked through the dark forest",
    doc_id="chapter_1",
    context_window=500
)

# Response includes:
# - entities_mentioned: Characters, locations, etc. in the text
# - narrative_paths: Relevant story paths from knowledge graph
# - suggestions: Writing improvement suggestions
# - character_contexts: Character arc information
```

### 3. **Check Consistency**

```python
# Verify new content against established facts
consistency = await indexer.check_consistency(
    statement="Emma's blonde hair shimmered in the moonlight",
    doc_id="chapter_1",
    check_type="character"  # or "plot", "setting", "all"
)

# Response includes:
# - is_consistent: True/False
# - conflicts: List of potential inconsistencies
# - confirmations: Supporting evidence
# - recommendation: What to do about conflicts
```

### 4. **Get Writing Suggestions**

```python
# Get AI-powered writing suggestions
suggestions = await indexer.get_writing_suggestions(
    context="Emma stood at the crossroads, uncertain of her path",
    suggestion_type="plot"  # or "character", "style", "all"
)

# Response includes suggestions for:
# - plot: Story development ideas
# - character: Character interaction suggestions
# - style: Writing style consistency
```

### 5. **Search Your Content**

```python
# Multi-modal search
results = indexer.search(
    query="Emma's magical abilities",
    search_type="hybrid",  # or "vector", "graph"
    filters={"type": "chapter"}
)

# Returns both:
# - Text chunks (from vector search)
# - Narrative paths (from graph search)
```

## 🌐 API Endpoints

Your system includes REST API endpoints for web integration:

### Index Documents
```http
POST /api/indexing/index-document
{
    "doc_id": "chapter_1",
    "text": "Chapter content...",
    "metadata": {"type": "chapter", "number": 1}
}
```

### Get Contextual Feedback
```http
POST /api/indexing/contextual-feedback
{
    "highlighted_text": "Emma walked through the forest",
    "doc_id": "chapter_1",
    "context_window": 500
}
```

### Check Consistency
```http
POST /api/indexing/check-consistency
{
    "statement": "Emma's blonde hair...",
    "doc_id": "chapter_1",
    "check_type": "character"
}
```

### Get Writing Suggestions
```http
POST /api/indexing/writing-suggestions
{
    "context": "Emma stood at the crossroads...",
    "suggestion_type": "all"
}
```

### Search
```http
POST /api/indexing/search
{
    "query": "Emma's character development",
    "search_type": "hybrid",
    "filters": {"type": "chapter"}
}
```

## 🧪 Testing the System

### Option 1: Simple Test
```bash
cd /Users/aahishsunar/Desktop/DOG
python test_pathrag_simple.py
```

### Option 2: Comprehensive Test
```bash
cd /Users/aahishsunar/Desktop/DOG
python test_pathrag_comprehensive.py
```

### Option 3: Integration Test
```bash
cd /Users/aahishsunar/Desktop/DOG
python test_pathrag_integration.py
```

## 🔧 Understanding the PathRAG Algorithm

### Step-by-Step Process:

1. **Initial Node Retrieval**
   ```python
   # Vector search finds semantically similar content
   initial_nodes = self._get_initial_nodes(query)
   ```

2. **Path Finding**
   ```python
   # Explore connections up to 4 hops away
   all_paths = self._find_relevant_paths(initial_nodes)
   ```

3. **Flow-based Pruning**
   ```python
   # Remove redundant paths using reliability scoring
   pruned_paths = self._prune_paths(all_paths)
   ```

4. **Path Scoring**
   ```python
   # Score paths based on:
   # - Node relevance to query (40%)
   # - Path coherence (30%)
   # - Entity diversity (20%)
   # - Length penalty (10%)
   scored_paths = self._score_paths(pruned_paths, query)
   ```

5. **Textual Generation**
   ```python
   # Convert graph paths to human-readable narratives
   textual_paths = self._generate_textual_paths(scored_paths)
   ```

## 📊 Example Output

### Contextual Feedback Example:
```json
{
    "highlighted_text": "Emma walked through the forest",
    "entities_mentioned": [
        {"text": "Emma", "type": "CHARACTER"},
        {"text": "forest", "type": "LOCATION"}
    ],
    "narrative_paths": [
        {
            "narrative": "CHARACTER: Emma → goes to forest → meets Marcus",
            "score": 0.85,
            "entities": ["Emma", "forest", "Marcus"]
        }
    ],
    "suggestions": [
        "Consider the established traits and relationships of Emma",
        "This connects well with established narrative elements"
    ]
}
```

### Consistency Check Example:
```json
{
    "statement": "Emma's blonde hair shimmered",
    "is_consistent": false,
    "conflicts": [
        {
            "type": "character_appearance",
            "conflict": "Emma's hair color established as auburn",
            "evidence": "Emma's auburn hair caught the sunlight"
        }
    ],
    "recommendation": "Minor inconsistency detected: Hair color contradiction"
}
```

## 💡 Best Practices

### 1. **Document Organization**
- Index chapters separately for better context
- Include character profiles and world-building documents
- Use descriptive metadata for better filtering

### 2. **Query Optimization**
- Use specific, descriptive queries
- Include character names and key terms
- Test different search types (vector vs hybrid)

### 3. **Consistency Checking**
- Check major character details regularly
- Verify plot continuity between chapters
- Validate world-building consistency

### 4. **Performance**
- Index documents in batches when possible
- Use appropriate chunk sizes (default 512 tokens)
- Consider caching for frequently accessed content

## 🔍 Troubleshooting

### Common Issues:

1. **No entities extracted**
   - Check Gemini API configuration
   - Verify text content has identifiable entities
   - Review entity extraction patterns

2. **Poor search results**
   - Ensure documents are properly indexed
   - Try different search types
   - Check query phrasing

3. **Inconsistent feedback**
   - Verify document relationships in graph
   - Check path retrieval parameters
   - Review entity linking

### Debug Commands:
```python
# Check indexing status
stats = indexer.get_document_stats("chapter_1")

# Export knowledge graph for visualization
graph_data = indexer.export_knowledge_graph("json")

# Test individual components
vector_results = indexer.vector_store.search("query")
```

## 📚 Learning Resources

- **PathRAG Paper**: [Path-based Retrieval-Augmented Generation](https://arxiv.org/abs/2402.05131)
- **NetworkX Documentation**: [Graph algorithms and analysis](https://networkx.org/)
- **ChromaDB Documentation**: [Vector database operations](https://docs.trychroma.com/)
- **Sentence Transformers**: [Embedding models](https://www.sbert.net/)

## 🎯 Next Steps

1. **Test the system** with your own writing content
2. **Integrate the API endpoints** into your web interface
3. **Experiment with different query types** and parameters
4. **Customize entity types** and relationships for your genre
5. **Optimize performance** for your specific use case

Your PathRAG contextual understanding system is now ready to enhance your writing assistant with sophisticated narrative awareness! 