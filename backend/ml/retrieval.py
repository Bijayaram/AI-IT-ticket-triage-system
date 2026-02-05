"""
FAISS-based retrieval system for finding similar historical tickets.
Uses LOCAL embeddings for vector search (RAG-lite).
"""
import faiss
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import pickle
import logging

from backend.ml.embeddings import get_embedder

logger = logging.getLogger(__name__)


class TicketRetriever:
    """
    FAISS-based retrieval system for similar tickets.
    Builds index on training data and retrieves similar examples.
    """
    
    INDEX_DIR = Path("./faiss_index")
    
    def __init__(self, embedder=None):
        """
        Initialize retriever.
        
        Args:
            embedder: LocalEmbedder instance (optional)
        """
        self.embedder = embedder or get_embedder()
        self.INDEX_DIR.mkdir(exist_ok=True)
        
        self.index = None
        self.tickets_df = None
        self.indexed = False
    
    def build_index(self, dataset_path: str, embeddings: Optional[np.ndarray] = None):
        """
        Build FAISS index from dataset.
        
        Args:
            dataset_path: Path to CSV dataset
            embeddings: Pre-computed embeddings (optional)
        """
        logger.info(f"Building FAISS index from {dataset_path}")
        
        # Load dataset
        df = pd.read_csv(dataset_path)
        df['text'] = df['subject'].fillna('') + "\n\n" + df['body'].fillna('')
        df = df[df['text'].notna()].copy()
        
        self.tickets_df = df[['text', 'subject', 'body', 'answer', 'queue', 'priority', 'language']].copy()
        
        # Generate or use provided embeddings
        if embeddings is None:
            logger.info("Generating embeddings for indexing...")
            embeddings = self.embedder.embed_texts(
                self.tickets_df['text'].tolist(),
                batch_size=32,
                normalize=True,
                show_progress=True
            )
        
        # Build FAISS index
        embedding_dim = embeddings.shape[1]
        logger.info(f"Building FAISS index with {len(embeddings)} vectors (dim={embedding_dim})")
        
        # Use IndexFlatIP for cosine similarity (embeddings are normalized)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        self.indexed = True
        logger.info(f"✓ FAISS index built: {self.index.ntotal} vectors")
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        index_path = self.INDEX_DIR / "tickets.index"
        metadata_path = self.INDEX_DIR / "metadata.pkl"
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata (tickets dataframe)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.tickets_df, f)
        
        logger.info(f"✓ Saved FAISS index to {self.INDEX_DIR}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        index_path = self.INDEX_DIR / "tickets.index"
        metadata_path = self.INDEX_DIR / "metadata.pkl"
        
        if not index_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found. Please build index first using scripts/build_index.py"
            )
        
        logger.info(f"Loading FAISS index from {self.INDEX_DIR}")
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            self.tickets_df = pickle.load(f)
        
        self.indexed = True
        logger.info(f"✓ Loaded FAISS index: {self.index.ntotal} vectors")
    
    def search(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar tickets.
        
        Args:
            query_text: Query text (subject + body)
            k: Number of results to return
            
        Returns:
            List of similar tickets with scores
        """
        if not self.indexed:
            self.load_index()
        
        # Generate query embedding
        query_embedding = self.embedder.embed_single(query_text, normalize=True)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.tickets_df):
                ticket = self.tickets_df.iloc[idx]
                results.append({
                    "score": float(score),
                    "subject": ticket['subject'],
                    "body": ticket['body'],
                    "answer": ticket['answer'],
                    "queue": ticket['queue'],
                    "priority": ticket['priority'],
                    "language": ticket['language']
                })
        
        return results
    
    def search_by_embedding(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search using pre-computed embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of similar tickets with scores
        """
        if not self.indexed:
            self.load_index()
        
        # Normalize and reshape
        query_embedding = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.tickets_df):
                ticket = self.tickets_df.iloc[idx]
                results.append({
                    "score": float(score),
                    "subject": ticket['subject'],
                    "body": ticket['body'],
                    "answer": ticket['answer'],
                    "queue": ticket['queue'],
                    "priority": ticket['priority'],
                    "language": ticket['language']
                })
        
        return results


# Global retriever instance
_retriever = None


def get_retriever() -> TicketRetriever:
    """
    Get global retriever instance (singleton pattern).
    
    Returns:
        TicketRetriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = TicketRetriever()
    return _retriever
