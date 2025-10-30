"""
Vector Store implementation for writing assistant
Optimized for narrative text with semantic chunking
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import hashlib
import json
from datetime import datetime

class VectorStore:
    """
    Manages vector embeddings for document chunks with writing-specific optimizations
    """
    
    def __init__(self, collection_name: str = "writing_docs", persist_directory: str = "./chroma_db"):
        # Initialize embedding model - using smaller, efficient model for memory optimization
        # Changed from 'all-mpnet-base-v2' (400MB, 768-dim) to 'all-MiniLM-L6-v2' (90MB, 384-dim)
        # Trade-off: ~5% accuracy reduction for 75% memory savings
        # Performance impact: 87% → 84% on STS-B benchmark (acceptable for production)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with memory-optimized persistent storage
        # OPTIMIZATION: Always use persistent storage to reduce memory usage
        # Railway ephemeral filesystem: Use /tmp for persistent storage during session
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
        
        try:
            # Correctly disable telemetry using Chroma's settings.
            # This is the modern and recommended way to handle telemetry.
            telemetry_settings = Settings(anonymized_telemetry=False)
            
            if is_railway:
                persist_directory = "/tmp/chroma_db"
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
    
            print("✅ ChromaDB initialized successfully with telemetry disabled.")
    
            
        except Exception as e:
            print(f"⚠️ ChromaDB initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize ChromaDB: {e}")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
    def chunk_document(self, text: str, doc_id: str, chunk_size: int = 512) -> List[Dict[str, Any]]:
        """
        Smart chunking that preserves narrative structure
        
        Args:
            text: Document text
            doc_id: Document identifier
            chunk_size: Target chunk size in tokens
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Split by paragraphs first to maintain narrative boundaries
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for para in paragraphs:
            para_tokens = len(para.split())
            
            # If paragraph fits in current chunk, add it
            if current_tokens + para_tokens <= chunk_size:
                current_chunk += para + "\n\n"
                current_tokens += para_tokens
            else:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunk_id = self._generate_chunk_id(doc_id, chunk_index)
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'doc_id': doc_id,
                        'chunk_index': chunk_index,
                        'token_count': current_tokens,
                        'type': 'narrative'
                    })
                    chunk_index += 1
                
                # Start new chunk with current paragraph
                current_chunk = para + "\n\n"
                current_tokens = para_tokens
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk_id = self._generate_chunk_id(doc_id, chunk_index)
            chunks.append({
                'id': chunk_id,
                'text': current_chunk.strip(),
                'doc_id': doc_id,
                'chunk_index': chunk_index,
                'token_count': current_tokens,
                'type': 'narrative'
            })
        
        return chunks
    
    def add_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None) -> List[str]:
        """
        Add a document to the vector store with smart chunking
        
        Args:
            text: Document text
            doc_id: Unique document identifier
            metadata: Additional metadata
            
        Returns:
            List of chunk IDs
        """
        # Chunk the document
        chunks = self.chunk_document(text, doc_id)
        
        # Prepare data for batch insertion
        texts = []
        embeddings = []
        ids = []
        metadatas = []
        
        for chunk in chunks:
            texts.append(chunk['text'])
            ids.append(chunk['id'])
            
            # Combine chunk metadata with document metadata
            chunk_meta = {
                'doc_id': doc_id,
                'chunk_index': chunk['chunk_index'],
                'token_count': chunk['token_count'],
                'type': chunk['type'],
                'indexed_at': datetime.now().isoformat()
            }
            if metadata:
                chunk_meta.update(metadata)
            metadatas.append(chunk_meta)
        
        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def search(self, query: str, n_results: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant chunks
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Metadata filters
            
        Returns:
            List of results with text, metadata, and scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict
        )
        
        # Format results - optimized using zip for better performance
        formatted_results = [
            {
                'id': id_,
                'text': text,
                'metadata': metadata,
                'distance': distance,
                'score': 1 - distance  # Convert distance to similarity score
            }
            for id_, text, metadata, distance in zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
        
        return formatted_results
    
    def get_context_window(self, chunk_id: str, window_size: int = 2) -> List[Dict[str, Any]]:
        """
        Get surrounding chunks for expanded context
        
        Args:
            chunk_id: Central chunk ID
            window_size: Number of chunks before/after to retrieve
            
        Returns:
            List of chunks in order
        """
        # Get the chunk metadata
        result = self.collection.get(ids=[chunk_id])
        if not result['ids']:
            return []
        
        metadata = result['metadatas'][0]
        doc_id = metadata['doc_id']
        chunk_index = metadata['chunk_index']
        
        # Calculate range
        start_index = max(0, chunk_index - window_size)
        end_index = chunk_index + window_size
        
        # Query for chunks in range
        chunks = self.collection.get(
            where={
                "$and": [
                    {"doc_id": doc_id},
                    {"chunk_index": {"$gte": start_index}},
                    {"chunk_index": {"$lte": end_index}}
                ]
            }
        )
        
        # Format and sort by chunk index - optimized using zip and sorted
        formatted_chunks = sorted(
            [
                {
                    'id': id_,
                    'text': text,
                    'metadata': metadata
                }
                for id_, text, metadata in zip(
                    chunks['ids'],
                    chunks['documents'],
                    chunks['metadatas']
                )
            ],
            key=lambda x: x['metadata']['chunk_index']
        )
        
        return formatted_chunks
    
    def _generate_chunk_id(self, doc_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        content = f"{doc_id}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def delete_document(self, doc_id: str) -> int:
        """
        Delete all chunks for a document
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Number of chunks deleted
        """
        # Get all chunks for the document
        results = self.collection.get(where={"doc_id": doc_id})
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        
        return 0
    
    def update_document(self, text: str, doc_id: str, metadata: Optional[Dict] = None) -> List[str]:
        """
        Update a document by deleting old chunks and adding new ones
        
        Args:
            text: New document text
            doc_id: Document identifier
            metadata: Updated metadata
            
        Returns:
            List of new chunk IDs
        """
        # Delete old chunks
        self.delete_document(doc_id)
        
        # Add new chunks
        return self.add_document(text, doc_id, metadata) 