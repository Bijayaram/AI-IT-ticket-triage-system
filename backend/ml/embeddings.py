"""
Local embedding generation using SentenceTransformers.
NO GEMINI - uses multilingual local models only.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import pickle
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class LocalEmbedder:
    """
    Local embedding generator using SentenceTransformers.
    Supports multilingual text with high-quality embeddings.
    
    Uses BAAI/bge-m3 by default (multilingual, high quality).
    Fallback: intfloat/multilingual-e5-large
    """
    
    DEFAULT_MODEL = "BAAI/bge-m3"
    FALLBACK_MODEL = "intfloat/multilingual-e5-large"
    CACHE_DIR = "./embeddings_cache"
    
    def __init__(self, model_name: Optional[str] = None, cache_enabled: bool = True):
        """
        Initialize local embedder.
        
        Args:
            model_name: Model name (default: BAAI/bge-m3)
            cache_enabled: Enable embedding caching
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(self.CACHE_DIR)
        
        if self.cache_enabled:
            self.cache_dir.mkdir(exist_ok=True)
            
        # Load model
        logger.info(f"Loading local embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✓ Model loaded successfully: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to load {self.model_name}, trying fallback: {e}")
            self.model_name = self.FALLBACK_MODEL
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✓ Fallback model loaded: {self.model_name}")
    
    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            normalize: L2 normalize embeddings
            show_progress: Show progress bar
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def embed_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string
            normalize: L2 normalize embedding
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        return embedding
    
    def save_embeddings(self, embeddings: np.ndarray, filename: str):
        """
        Save embeddings to cache.
        
        Args:
            embeddings: Numpy array of embeddings
            filename: Cache filename (without extension)
        """
        if not self.cache_enabled:
            return
        
        cache_path = self.cache_dir / f"{filename}.pkl"
        with open(cache_path, 'wb') as f:
            pickle.dump(embeddings, f)
        logger.info(f"✓ Saved embeddings to {cache_path}")
    
    def load_embeddings(self, filename: str) -> Optional[np.ndarray]:
        """
        Load embeddings from cache.
        
        Args:
            filename: Cache filename (without extension)
            
        Returns:
            Numpy array of embeddings or None if not found
        """
        if not self.cache_enabled:
            return None
        
        cache_path = self.cache_dir / f"{filename}.pkl"
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'rb') as f:
            embeddings = pickle.load(f)
        logger.info(f"✓ Loaded embeddings from {cache_path}")
        return embeddings
    
    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()


# Global embedder instance
_embedder = None


def get_embedder(model_name: Optional[str] = None) -> LocalEmbedder:
    """
    Get global embedder instance (singleton pattern).
    
    Args:
        model_name: Model name (optional)
        
    Returns:
        LocalEmbedder instance
    """
    global _embedder
    if _embedder is None:
        _embedder = LocalEmbedder(model_name=model_name)
    return _embedder
