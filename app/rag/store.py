"""
/**
 * This module implements a vector store for policy documents using ChromaDB.
 * Similar to Java's Repository or DAO pattern.
 * 
 * The store handles:
 * - Document storage and retrieval
 * - Vector embeddings management
 * - Similarity search operations
 */
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

class PolicyStore:
    """
    /**
     * A class that manages the storage and retrieval of policy documents.
     * Similar to Java's Repository pattern with search capabilities.
     * 
     * Components:
     * - ChromaDB client for persistent storage
     * - OpenAI embeddings for vector representation
     * - Collection management for document organization
     */
    """
    
    def __init__(self, chroma_dir: str):
        """
        /**
         * Constructor for PolicyStore
         * @param chroma_dir: String path to the ChromaDB storage directory
         * 
         * Initializes:
         * - ChromaDB persistent client
         * - Storage directory path
         * - Collection reference (lazy loaded)
         */
        """
        self.chroma_dir = Path(chroma_dir)
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.collection = None

    def ensure_index(self) -> None:
        """Ensure the index exists and is ready to use."""
        try:
            self.collection = self.client.get_collection("policies")
        except ValueError:
            print("Warning: Policy index not found. Please run ingestion first:")
            print("python -m app.rag.ingest")
            raise

    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get or create the collection for policies."""
        try:
            return self.client.get_collection("policies")
        except Exception:  # Handle any exception, including InvalidCollectionException
            return self.client.create_collection(
                name="policies",
                metadata={"hnsw:space": "cosine"}  # Using cosine similarity for embeddings
            )

    def add_documents(self, documents: List[Dict]) -> None:
        """
        /**
         * Adds or updates documents in the vector store.
         * Similar to Java's Repository.save() or Repository.upsert() pattern.
         * 
         * @param documents: List of document dictionaries containing text and metadata
         * 
         * Processing steps:
         * 1. Get or create collection
         * 2. Extract document properties (IDs, texts, metadata)
         * 3. Generate embeddings using OpenAI
         * 4. Upsert documents with embeddings into ChromaDB
         * 
         * Document format:
         * {
         *     "text": "document content",
         *     "metadata": {
         *         "policy_id": "POL-001",
         *         "section": "Eligibility",
         *         "source": "policy.md"
         *     }
         * }
         */
        """
        collection = self._get_or_create_collection()
        
        # Prepare documents for Chroma (similar to DTO mapping in Java)
        ids = [doc["metadata"]["chunk_id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Upsert to Chroma
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Generate embeddings for texts
        embeddings_list = embeddings.embed_documents(texts)
        
        # Upsert to Chroma
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings_list,
            metadatas=metadatas
        )

    def search(self, query: str, k: int = 4) -> List[Dict]:
        """
        /**
         * Performs semantic search across policy documents.
         * Similar to Java's SearchService with vector similarity search.
         * 
         * @param query: Search query string
         * @param k: Number of results to return (default: 4)
         * @return: List of relevant document chunks with metadata and similarity scores
         * @throws ValueError: If index is not found (needs ingestion)
         * 
         * Return format:
         * [
         *     {
         *         "text": "relevant text chunk",
         *         "source": "policy_file.md",
         *         "section": "section name",
         *         "policy_id": "POL-001",
         *         "score": 0.95  // similarity score
         *     },
         *     ...
         * ]
         */
        """
        if self.collection is None:
            self.ensure_index()
            
        # Create embeddings for the query
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        query_embedding = embeddings.embed_query(query)
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "section": results["metadatas"][0][i].get("section", ""),
                "policy_id": results["metadatas"][0][i]["policy_id"],
                "score": 1.0 - results["distances"][0][i]  # Convert distance to similarity score
            })
            
        return formatted_results
