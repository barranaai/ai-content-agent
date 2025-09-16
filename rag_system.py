import json
import os
import logging
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from openai import OpenAI

class BarranaRAGSystem:
    """
    Retrieval-Augmented Generation system for Barrana content.
    
    This system loads Barrana's knowledge corpus, generates embeddings,
    and provides semantic search capabilities to enhance content generation.
    """
    
    def __init__(self, corpus_path: str = "barrana_rag_corpus.jsonl", 
                 embedding_model: str = "text-embedding-3-large"):
        """
        Initialize the RAG system.
        
        Args:
            corpus_path: Path to the JSONL corpus file
            embedding_model: OpenAI embedding model to use
        """
        self.corpus_path = corpus_path
        self.embedding_model = embedding_model
        self.chunks = []
        self.embeddings = None
        self.index = None
        self.is_loaded = False
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        logging.info(f"🔧 RAG System initialized with corpus: {corpus_path}")
    
    def load_corpus(self) -> bool:
        """
        Load chunks from JSONL corpus file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.corpus_path):
                logging.warning(f"⚠️ Corpus file not found: {self.corpus_path}")
                return False
            
            self.chunks = []
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            chunk = json.loads(line)
                            self.chunks.append(chunk)
                        except json.JSONDecodeError as e:
                            logging.error(f"❌ JSON decode error on line {line_num}: {e}")
                            continue
            
            logging.info(f"✅ Loaded {len(self.chunks)} chunks from corpus")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error loading corpus: {e}")
            return False
    
    def generate_embeddings(self) -> bool:
        """
        Generate embeddings for all chunks.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.chunks:
                logging.error("❌ No chunks loaded. Call load_corpus() first.")
                return False
            
            logging.info(f"🔄 Generating embeddings for {len(self.chunks)} chunks...")
            
            # Extract texts for embedding
            texts = [chunk['text'] for chunk in self.chunks]
            
            # Generate embeddings in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logging.info(f"🔄 Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
                
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch_texts
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            self.embeddings = np.array(all_embeddings)
            logging.info(f"✅ Generated embeddings: {self.embeddings.shape}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error generating embeddings: {e}")
            return False
    
    def build_index(self) -> bool:
        """
        Build FAISS index for similarity search.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.embeddings is None:
                logging.error("❌ No embeddings available. Call generate_embeddings() first.")
                return False
            
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            embeddings_normalized = self.embeddings.astype('float32')
            faiss.normalize_L2(embeddings_normalized)
            self.index.add(embeddings_normalized)
            
            logging.info(f"✅ Built FAISS index with {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error building index: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize the complete RAG system.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logging.info("🚀 Initializing RAG system...")
            
            # Load corpus
            if not self.load_corpus():
                return False
            
            # Generate embeddings
            if not self.generate_embeddings():
                return False
            
            # Build index
            if not self.build_index():
                return False
            
            self.is_loaded = True
            logging.info("✅ RAG system initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error initializing RAG system: {e}")
            return False
    
    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.7) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            if not self.is_loaded or self.index is None:
                logging.warning("⚠️ RAG system not initialized. Returning empty results.")
                return []
            
            # Embed the query
            query_response = self.client.embeddings.create(
                model=self.embedding_model,
                input=[query]
            )
            query_embedding = np.array([query_response.data[0].embedding])
            
            # Normalize query embedding
            query_embedding_normalized = query_embedding.astype('float32')
            faiss.normalize_L2(query_embedding_normalized)
            
            # Search
            scores, indices = self.index.search(query_embedding_normalized, top_k)
            
            # Return relevant chunks
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks) and score >= min_score:
                    chunk = self.chunks[idx].copy()
                    chunk['similarity_score'] = float(score)
                    chunk['rank'] = i + 1
                    results.append(chunk)
            
            logging.info(f"🔍 Retrieved {len(results)} relevant chunks for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logging.error(f"❌ Error retrieving chunks: {e}")
            return []
    
    def get_context(self, query: str, top_k: int = 3, min_score: float = 0.7) -> str:
        """
        Get formatted context string from retrieved chunks.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            Formatted context string
        """
        chunks = self.retrieve(query, top_k, min_score)
        
        if not chunks:
            return ""
        
        context_parts = []
        for chunk in chunks:
            context_parts.append(f"[Source: {chunk.get('source_title', 'Unknown')} - {chunk.get('section', 'Unknown Section')}]\n{chunk['text']}")
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary with system stats
        """
        return {
            "is_loaded": self.is_loaded,
            "chunks_count": len(self.chunks),
            "embeddings_shape": self.embeddings.shape if self.embeddings is not None else None,
            "index_size": self.index.ntotal if self.index is not None else 0,
            "corpus_path": self.corpus_path,
            "embedding_model": self.embedding_model
        }
    
    def reload_corpus(self) -> bool:
        """
        Reload the corpus and rebuild the system.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logging.info("🔄 Reloading RAG corpus...")
        self.is_loaded = False
        self.chunks = []
        self.embeddings = None
        self.index = None
        return self.initialize()
