# 🚀 Codebase Indexing Implementation Guide for Writing Assistant

## Overview

This guide documents the implementation of an advanced codebase indexing system for your writing assistant, incorporating the latest research from PathRAG (February 2025) and other cutting-edge RAG technologies.

## 🎯 Key Features Implemented

### 1. **Hybrid Indexing System**
- **Vector Store**: Semantic search using ChromaDB with sentence transformers
- **Knowledge Graph**: Entity and relationship extraction using NetworkX
- **Path-Based Retrieval**: PathRAG-inspired relational path finding

### 2. **Writing-Specific Capabilities**
- **Contextual Feedback**: Get AI-powered feedback for highlighted text
- **Consistency Checking**: Verify character, plot, and setting consistency
- **Writing Suggestions**: Context-aware suggestions for plot, character, and style
- **Character Arc Tracking**: Follow character development across documents
- **Plot Thread Analysis**: Identify and track causal relationships

### 3. **Smart Document Processing**
- **Narrative-Aware Chunking**: Preserves paragraph boundaries and story flow
- **Entity Recognition**: Characters, locations, events, and themes
- **Relationship Extraction**: Character interactions, causality, and movements

## 📁 Project Structure

```
backend/
├── services/
│   └── indexing/
│       ├── __init__.py           # Module exports
│       ├── vector_store.py       # Vector embedding storage
│       ├── graph_builder.py      # Knowledge graph construction
│       ├── path_retriever.py     # PathRAG-inspired retrieval
│       └── hybrid_indexer.py     # Unified interface
└── routers/
    └── indexing_router.py        # API endpoints
```

## 🔧 Installation

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Update main.py to include the indexing router**:
```python
from backend.routers import indexing_router

# Add to your FastAPI app
app.include_router(indexing_router.router)
```

## 📊 API Endpoints

### 1. **Index Document**
```http
POST /api/indexing/index-document
{
  "doc_id": "chapter_1",
  "text": "Your document text...",
  "metadata": {
    "title": "Chapter 1: The Beginning",
    "type": "chapter"
  }
}
```

### 2. **Index Folder** (Multiple Documents)
```http
POST /api/indexing/index-folder
{
  "documents": [
    {
      "doc_id": "chapter_1",
      "text": "Chapter 1 text...",
      "metadata": {"title": "Chapter 1"}
    },
    {
      "doc_id": "chapter_2",
      "text": "Chapter 2 text...",
      "metadata": {"title": "Chapter 2"}
    }
  ]
}
```

### 3. **Get Contextual Feedback**
```http
POST /api/indexing/contextual-feedback
{
  "highlighted_text": "Sarah walked into the abandoned mansion",
  "doc_id": "chapter_1",
  "context_window": 500
}
```

Response:
```json
{
  "highlighted_text": "Sarah walked into the abandoned mansion",
  "semantic_context": [...],
  "entities_mentioned": [
    {"text": "Sarah", "type": "CHARACTER"},
    {"text": "abandoned mansion", "type": "LOCATION"}
  ],
  "narrative_paths": [...],
  "suggestions": [
    "Consider the established traits and relationships of Sarah",
    "Verify the spatial consistency with previous mentions of this location"
  ],
  "character_contexts": [...]
}
```

### 4. **Check Consistency**
```http
POST /api/indexing/check-consistency
{
  "statement": "John was in Paris",
  "doc_id": "chapter_5",
  "check_type": "all"
}
```

### 5. **Get Writing Suggestions**
```http
POST /api/indexing/writing-suggestions
{
  "context": "The storm was approaching rapidly...",
  "suggestion_type": "all"
}
```

### 6. **Search**
```http
POST /api/indexing/search
{
  "query": "character interactions with Sarah",
  "search_type": "hybrid",
  "filters": {}
}
```

## 🧠 How It Works

### Phase 1: Document Indexing

1. **Text Chunking**: Documents are split into semantic chunks while preserving narrative structure
2. **Vector Embeddings**: Each chunk is converted to embeddings using sentence-transformers
3. **Entity Extraction**: Characters, locations, events are identified using spaCy NER
4. **Relationship Mining**: Patterns like "X said to Y" are extracted
5. **Graph Construction**: Entities become nodes, relationships become edges

### Phase 2: Retrieval Process

1. **Initial Node Selection**: Query embedding finds relevant starting points
2. **Path Discovery**: BFS explores narrative paths from initial nodes
3. **Flow-Based Pruning**: Removes redundant paths, prioritizes strong relationships
4. **Reliability Scoring**: Paths ranked by relevance, coherence, and length
5. **Textual Generation**: Paths converted to human-readable narratives

### Phase 3: Context Generation

1. **Path Reversal**: Most relevant paths placed at end (for LLM attention)
2. **Supporting Text**: Original document excerpts added for context
3. **Structured Output**: Entities, relationships, and suggestions formatted

## 💡 Best Practices

### 1. **Document Preparation**
- Use clear chapter/section divisions
- Maintain consistent character naming
- Include metadata (title, type, date)

### 2. **Indexing Strategy**
- Index related documents together (e.g., all chapters)
- Re-index after major edits
- Use meaningful document IDs

### 3. **Query Optimization**
- Be specific in queries for better results
- Use character names for character-related queries
- Specify check types for consistency checks

## 🔄 Integration with Existing Features

### 1. **With Document Management**
```javascript
// Frontend integration example
const indexDocument = async (docId, content, metadata) => {
  const response = await api.post('/api/indexing/index-document', {
    doc_id: docId,
    text: content,
    metadata: metadata
  });
  return response.data;
};
```

### 2. **With Chat Interface**
```javascript
// Get contextual feedback for highlighted text
const getContextualFeedback = async (highlightedText, docId) => {
  const response = await api.post('/api/indexing/contextual-feedback', {
    highlighted_text: highlightedText,
    doc_id: docId
  });
  return response.data;
};
```

### 3. **With Editor**
```javascript
// Check consistency while writing
const checkConsistency = async (statement, docId) => {
  const response = await api.post('/api/indexing/check-consistency', {
    statement: statement,
    doc_id: docId,
    check_type: 'all'
  });
  return response.data;
};
```

## 🚀 Advanced Features

### 1. **Character Arc Visualization**
```python
# Get character development over time
char_arc = graph_builder.get_character_arc("Sarah")
# Returns chronological sequence of events/relationships
```

### 2. **Plot Thread Analysis**
```python
# Identify main plot threads
plot_threads = graph_builder.get_plot_threads()
# Returns causal chains of events
```

### 3. **Cross-Document Relationships**
```python
# Find connections between chapters
paths = path_retriever.retrieve_paths("the ancient artifact", top_k=5)
# Returns paths spanning multiple documents
```

## 📈 Performance Considerations

### 1. **Chunking Strategy**
- Default: 512 tokens per chunk
- Adjust based on your narrative style
- Smaller chunks = more precise retrieval
- Larger chunks = better context preservation

### 2. **Graph Complexity**
- Limit path length (default: 4 nodes)
- Prune redundant relationships
- Use reliability scoring for efficiency

### 3. **Vector Store Optimization**
- Use metadata filters to narrow search
- Batch document indexing when possible
- Consider persistent storage for large projects

## 🔍 Troubleshooting

### Common Issues

1. **"No documents indexed yet"**
   - Solution: Index at least one document first

2. **Slow indexing for large documents**
   - Solution: Break into smaller documents
   - Use batch indexing for multiple files

3. **Inconsistent entity recognition**
   - Solution: Use consistent character naming
   - Consider custom entity rules

## 🎯 Future Enhancements

### Phase 2: Multi-File Context (Coming Soon)
- Automatic folder watching
- Real-time index updates
- Cross-project knowledge transfer

### Phase 3: Advanced Analytics
- Writing style analysis
- Theme tracking
- Automated plot hole detection

### Phase 4: Collaborative Features
- Shared knowledge bases
- Multi-author consistency checking
- Version-aware indexing

## 📚 Additional Resources

1. **PathRAG Paper**: [arXiv:2502.14902](https://arxiv.org/abs/2502.14902)
2. **ChromaDB Documentation**: [docs.trychroma.com](https://docs.trychroma.com)
3. **NetworkX Guide**: [networkx.org](https://networkx.org)
4. **spaCy NER**: [spacy.io/usage/linguistic-features](https://spacy.io/usage/linguistic-features)

## 🤝 Contributing

To extend the indexing system:

1. Add new entity types in `graph_builder.py`
2. Create custom relationship patterns
3. Implement domain-specific scoring
4. Add visualization capabilities

## ⚠️ Important Notes

1. **Privacy**: All indexing is local to your instance
2. **Storage**: Indexed data persists in `./indexing_data`
3. **Updates**: Re-index documents after major edits
4. **Limits**: Current implementation optimized for <100 documents

---

**Remember**: This is a Phase 1 implementation focused on single-file context. The architecture is designed to scale to multi-file and cross-project indexing in future phases. 