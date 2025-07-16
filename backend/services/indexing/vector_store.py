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
        # Initialize embedding model - using a model fine-tuned for narrative text
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize ChromaDB with Railway-optimized settings
        # Use in-memory storage for Railway's ephemeral filesystem
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
        
        try:
            if is_railway:
                # In-memory storage for Railway with comprehensive telemetry disabling
                self.client = chromadb.Client(Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=False,
                    # Additional settings to prevent telemetry initialization
                    chroma_telemetry_enabled=False,
                    chroma_disable_telemetry=True,
                    chroma_anonymized_telemetry=False
                ))
            else:
                # Local persistent storage with comprehensive telemetry disabling
                self.client = chromadb.Client(Settings(
                    persist_directory=persist_directory,
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True,
                    # Additional settings to prevent telemetry initialization
                    chroma_telemetry_enabled=False,
                    chroma_disable_telemetry=True,
                    chroma_anonymized_telemetry=False
                ))
        except Exception as e:
            # Fallback: Create client with minimal settings if comprehensive settings fail
            print(f"⚠️ ChromaDB initialization with full settings failed: {e}")
            print("🔄 Attempting fallback initialization...")
            
            try:
                if is_railway:
                    self.client = chromadb.Client(Settings(
                        anonymized_telemetry=False,
                        is_persistent=False
                    ))
                else:
                    self.client = chromadb.Client(Settings(
                        persist_directory=persist_directory,
                        anonymized_telemetry=False,
                        is_persistent=True
                    ))
                print("✅ ChromaDB fallback initialization successful")
            except Exception as fallback_error:
                print(f"❌ ChromaDB fallback initialization also failed: {fallback_error}")
                raise RuntimeError(f"Failed to initialize ChromaDB: {fallback_error}")
        
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
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity score
            })
        
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
        
        # Format and sort by chunk index
        formatted_chunks = []
        for i in range(len(chunks['ids'])):
            formatted_chunks.append({
                'id': chunks['ids'][i],
                'text': chunks['documents'][i],
                'metadata': chunks['metadatas'][i]
            })
        
        # Sort by chunk index
        formatted_chunks.sort(key=lambda x: x['metadata']['chunk_index'])
        
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