# Codebase Indexing System - Detailed Overview

## Introduction

The codebase indexing system is an advanced document understanding framework that implements PathRAG (Path-based Retrieval Augmented Generation) concepts. It's designed to help writers maintain consistency, track narrative elements, and get contextual feedback on their writing.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                   (React Frontend)                           │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│                   Indexing Router                            │
│               (/api/indexing/*)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Hybrid Indexer                             │
│            (Orchestration Layer)                             │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
┌──────┴────┐  ┌─────┴─────┐  ┌────┴──────┐
│  Vector   │  │   Graph   │  │   Path    │
│   Store   │  │  Builder  │  │ Retriever │
└───────────┘  └───────────┘  └───────────┘
       │              │              │
┌──────┴────────────────────────────┴──────┐
│            Storage Layer                  │
│  (ChromaDB)    (NetworkX)    (Memory)     │
└───────────────────────────────────────────┘
```

## Core Components

### 1. Vector Store (`vector_store.py`)

The Vector Store manages document embeddings and enables semantic search.

**Key Features:**
- **Smart Chunking**: Splits documents by paragraphs to preserve narrative structure
- **Embedding Generation**: Uses Sentence Transformers (`all-mpnet-base-v2`) to create 768-dimensional vectors
- **ChromaDB Storage**: Persists embeddings with metadata for efficient retrieval
- **Context Windows**: Can retrieve surrounding chunks for expanded context

**How it works:**
```python
# Example usage
vector_store = VectorStore()

# Index a document
chunk_ids = vector_store.add_document(
    text="Alice met Bob at the old library...",
    doc_id="chapter_1",
    metadata={"title": "The Meeting", "author": "Jane Doe"}
)

# Search for relevant content
results = vector_store.search(
    query="Where did Alice and Bob meet?",
    n_results=5
)
```

### 2. Graph Builder (`graph_builder.py`)

The Graph Builder extracts entities and relationships to create a knowledge graph.

**Key Features:**
- **Entity Extraction**: Identifies characters, locations, events, and themes using spaCy NER
- **Relationship Detection**: Uses regex patterns to find relationships like "speaks_to", "goes_to", "causes"
- **Character Arc Tracking**: Follows character development across documents
- **Plot Thread Analysis**: Identifies causal chains in the narrative

**Entity Types:**
- `CHARACTER`: People in the story
- `LOCATION`: Places and settings
- `EVENT`: Actions and plot points
- `THEME`: Concepts and motifs

**Relationship Types:**
- Character interactions: `SPEAKS_TO`, `FEELS_ABOUT`, `MEETS`
- Movement: `GOES_TO`, `LIVES_IN`
- Causality: `CAUSES`, `LEADS_TO`, `RESULTS_IN`

### 3. Path Retriever (`path_retriever.py`)

The Path Retriever implements PathRAG concepts for finding relevant narrative paths.

**Key Features:**
- **Initial Node Retrieval**: Uses vector search to find starting points
- **Path Finding**: Explores connections up to 4 hops away
- **Flow-Based Pruning**: Removes redundant paths using reliability scoring
- **Textual Path Generation**: Converts graph paths to human-readable narratives

**Path Scoring Algorithm:**
```python
score = (
    node_relevance * 0.4 +      # How well nodes match query
    path_coherence * 0.3 +      # Strength of relationships
    diversity_score * 0.2 +     # Variety of entity types
    length_penalty * 0.1        # Preference for shorter paths
)
```

### 4. Hybrid Indexer (`hybrid_indexer.py`)

The Hybrid Indexer orchestrates all components and provides a unified interface.

**Main Methods:**

1. **`index_document()`**: Indexes a single document
   - Chunks the text
   - Creates embeddings
   - Extracts entities and relationships
   - Updates the knowledge graph

2. **`get_contextual_feedback()`**: Analyzes highlighted text
   - Finds similar passages
   - Identifies mentioned entities
   - Retrieves relevant narrative paths
   - Generates suggestions

3. **`check_consistency()`**: Verifies statement accuracy
   - Checks character consistency
   - Validates plot coherence
   - Ensures setting consistency

4. **`get_writing_suggestions()`**: Provides AI-powered suggestions
   - Analyzes plot patterns
   - Suggests character developments
   - Recommends style improvements

5. **`search()`**: Unified search interface
   - Vector search for semantic similarity
   - Graph search for narrative paths
   - Hybrid search combining both

## API Endpoints

The system exposes the following REST endpoints:

1. **POST `/api/indexing/index-document`**
   - Index a single document
   - Required: `doc_id`, `text`
   - Optional: `metadata`

2. **POST `/api/indexing/index-folder`**
   - Index multiple related documents
   - Required: `documents` array

3. **POST `/api/indexing/contextual-feedback`**
   - Get feedback for highlighted text
   - Required: `highlighted_text`, `doc_id`

4. **POST `/api/indexing/check-consistency`**
   - Verify statement consistency
   - Required: `statement`, `doc_id`

5. **POST `/api/indexing/writing-suggestions`**
   - Get writing suggestions
   - Required: `context`

6. **POST `/api/indexing/search`**
   - Search indexed content
   - Required: `query`
   - Optional: `search_type` (vector/graph/hybrid)

7. **GET `/api/indexing/document-stats/{doc_id}`**
   - Get statistics for indexed document

8. **GET `/api/indexing/export-graph`**
   - Export knowledge graph for visualization

## How Components Connect

### Document Indexing Flow

```
1. User uploads document via API
2. Hybrid Indexer receives request
3. Vector Store chunks the document
4. Embeddings are generated for each chunk
5. Graph Builder extracts entities and relationships
6. Knowledge graph is updated
7. Path Retriever is reinitialized with new graph
8. Success response returned to user
```

### Query Processing Flow

```
1. User submits query
2. Query is embedded into vector
3. Vector Store finds similar chunks
4. Graph nodes are identified from chunks
5. Path Retriever finds relevant paths
6. Paths are scored and ranked
7. Textual narratives are generated
8. Results returned to user
```

## Use Cases

### 1. Contextual Feedback
When a writer highlights "Alice went to Paris", the system:
- Finds all mentions of Alice and Paris
- Retrieves Alice's character arc
- Checks if this movement is consistent
- Suggests related plot points

### 2. Consistency Checking
For the statement "Bob is afraid of water", the system:
- Searches for previous mentions of Bob and water
- Checks if this contradicts established facts
- Provides evidence for or against the statement

### 3. Writing Suggestions
Given current context, the system:
- Analyzes narrative patterns
- Suggests logical next events
- Recommends character interactions
- Proposes thematic developments

## Technical Details

### Embeddings
- **Model**: `all-mpnet-base-v2` (768 dimensions)
- **Similarity**: Cosine similarity
- **Normalization**: Vectors are L2-normalized

### Knowledge Graph
- **Framework**: NetworkX (directed graph)
- **Storage**: In-memory (can be persisted to disk)
- **Visualization**: Exportable as JSON or GEXF

### Chunking Strategy
- **Method**: Paragraph-based splitting
- **Size**: Target 512 tokens per chunk
- **Overlap**: Minimal (preserves paragraph boundaries)

### Performance Optimizations
- **Batch Operations**: Embeddings generated in batches
- **Caching**: Frequently accessed paths cached
- **Async Processing**: Non-blocking API operations
- **Incremental Updates**: Only new content is processed

## Integration with LLMs

While the current system doesn't directly use LLMs for processing, it's designed to support LLM integration:

1. **Enhanced Entity Extraction**: LLMs can improve entity recognition
2. **Semantic Chunking**: LLMs can identify topic boundaries
3. **Relationship Inference**: LLMs can detect implicit relationships
4. **Summary Generation**: LLMs can create document summaries

## Best Practices

1. **Document Preparation**
   - Use clear paragraph breaks
   - Maintain consistent character names
   - Include descriptive headings

2. **Indexing Strategy**
   - Index related documents together (e.g., book chapters)
   - Update metadata for better filtering
   - Re-index after major edits

3. **Query Optimization**
   - Use specific character/location names
   - Include context in queries
   - Combine vector and graph search

## Future Enhancements

1. **Multi-Model Embeddings**: Support for OpenAI, Cohere, and custom models
2. **Semantic Chunking**: Use LLMs to identify natural boundaries
3. **Cross-Encoder Reranking**: Improve result precision
4. **Distributed Storage**: Scale to millions of documents
5. **Real-time Collaboration**: Support multiple writers

## Conclusion

The codebase indexing system provides a sophisticated framework for understanding and analyzing narrative content. By combining vector search with knowledge graphs and PathRAG techniques, it offers writers powerful tools for maintaining consistency, exploring relationships, and enhancing their creative process.

The modular architecture ensures easy maintenance and future enhancements, while the REST API enables seamless integration with any frontend application. 