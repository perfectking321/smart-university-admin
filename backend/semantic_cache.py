"""
Semantic caching using sentence transformers and FAISS for similarity search
Provides intelligent cache lookup based on question semantics
"""

import numpy as np
from typing import Optional, Dict, Any
import json
from collections import OrderedDict

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️ sentence-transformers or faiss not installed. Using basic cache only.")

class SemanticCache:
    def __init__(self, max_size=100, similarity_threshold=0.90):
        """
        Initialize semantic cache with FAISS index
        
        Args:
            max_size: Maximum number of cached items
            similarity_threshold: Minimum similarity score (0-1) for cache hit
        """
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.cache = OrderedDict()
        
        if DEPS_AVAILABLE:
            # Load lightweight embedding model
            print("🔄 Loading embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384  # Dimension of all-MiniLM-L6-v2
            
            # Initialize FAISS index for fast similarity search
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            self.id_to_question = {}
            self.current_id = 0
            print("✅ Semantic cache initialized")
        else:
            self.model = None
            self.index = None
    
    def _normalize_vector(self, vector):
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if not DEPS_AVAILABLE or self.model is None:
            return None
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return self._normalize_vector(embedding)
    
    def get(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result using semantic similarity
        
        Args:
            question: User's natural language question
            
        Returns:
            Cached result dict or None if not found
        """
        question_lower = question.lower().strip()
        
        # Try exact match first (fastest)
        if question_lower in self.cache:
            self.cache.move_to_end(question_lower)
            result = self.cache[question_lower].copy()
            result["cached"] = True
            result["cache_type"] = "exact"
            print(f"✅ Exact cache hit")
            return result
        
        # Try semantic similarity if available
        if DEPS_AVAILABLE and self.model and self.index.ntotal > 0:
            embedding = self._get_embedding(question)
            if embedding is not None:
                # Search for similar questions
                embedding_2d = embedding.reshape(1, -1).astype('float32')
                distances, indices = self.index.search(embedding_2d, k=1)
                
                if len(distances[0]) > 0:
                    similarity = float(distances[0][0])
                    
                    if similarity >= self.similarity_threshold:
                        idx = int(indices[0][0])
                        similar_question = self.id_to_question.get(idx)
                        
                        if similar_question and similar_question in self.cache:
                            result = self.cache[similar_question].copy()
                            result["cached"] = True
                            result["cache_type"] = "semantic"
                            result["similarity_score"] = similarity
                            print(f"✅ Semantic cache hit (similarity: {similarity:.3f})")
                            return result
        
        print(f"❌ Cache miss")
        return None
    
    def set(self, question: str, sql: str, results: Dict[str, Any]):
        """
        Save result to cache with semantic indexing
        
        Args:
            question: User's natural language question
            sql: Generated SQL query
            results: Query execution results
        """
        question_lower = question.lower().strip()
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_question = next(iter(self.cache))
            self.cache.popitem(last=False)
            
            # Remove from FAISS index if applicable
            if DEPS_AVAILABLE and oldest_question in self.id_to_question.values():
                # Note: FAISS doesn't support easy deletion, so we rebuild periodically
                pass
        
        # Store in cache
        self.cache[question_lower] = {
            "sql": sql,
            "results": results,
            "cached": True,
            "cache_type": "stored"
        }
        
        # Add to FAISS index
        if DEPS_AVAILABLE and self.model:
            embedding = self._get_embedding(question)
            if embedding is not None:
                embedding_2d = embedding.reshape(1, -1).astype('float32')
                self.index.add(embedding_2d)
                self.id_to_question[self.current_id] = question_lower
                self.current_id += 1
        
        print(f"💾 Cached: '{question[:50]}...'")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        if DEPS_AVAILABLE and self.index:
            self.index.reset()
        self.id_to_question.clear()
        self.current_id = 0
        print("🗑️ Cache cleared")
    
    def size(self):
        """Get cache size"""
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "semantic_enabled": DEPS_AVAILABLE and self.model is not None,
            "similarity_threshold": self.similarity_threshold,
            "indexed_questions": len(self.id_to_question)
        }

# Global semantic cache instance
semantic_cache = SemanticCache()
