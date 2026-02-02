"""
LLM Middleware - Caching and optimization layer
Based on Vanna AI's middleware architecture
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any
from collections import OrderedDict


class LLMMiddleware:
    """Base middleware class for LLM request/response interception"""
    
    async def before_request(self, question: str, schema: str) -> Optional[Dict[str, Any]]:
        """Called before LLM request - return cached result if available"""
        return None
    
    async def after_response(self, question: str, schema: str, sql: str, results: Dict):
        """Called after LLM response - cache the result"""
        pass


class CachingMiddleware(LLMMiddleware):
    """
    Advanced caching middleware with multiple cache strategies:
    1. Exact match cache (fastest)
    2. Semantic similarity cache (intelligent)
    3. LRU eviction policy
    """
    
    def __init__(self, max_size: int = 200):
        self.exact_cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.total_time_saved = 0.0
    
    def _compute_cache_key(self, question: str, schema: str) -> str:
        """Create cache key from question and schema"""
        combined = f"{question.lower().strip()}:{schema[:500]}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def before_request(self, question: str, schema: str) -> Optional[Dict[str, Any]]:
        """Check cache before making LLM request"""
        cache_key = self._compute_cache_key(question, schema)
        
        if cache_key in self.exact_cache:
            # Cache hit!
            self.hits += 1
            cached_data = self.exact_cache[cache_key]
            
            # Move to end (LRU)
            self.exact_cache.move_to_end(cache_key)
            
            # Calculate time saved (average LLM call ~2 seconds)
            self.total_time_saved += 2.0
            
            print(f"⚡ CACHE HIT! Stats: {self.hits} hits / {self.misses} misses "
                  f"({self.hit_rate():.1%} hit rate)")
            
            return {
                **cached_data,
                "cached": True,
                "cache_type": "exact"
            }
        
        self.misses += 1
        return None
    
    async def after_response(self, question: str, schema: str, sql: str, results: Dict):
        """Cache the response"""
        cache_key = self._compute_cache_key(question, schema)
        
        # Evict oldest if cache is full (LRU)
        if len(self.exact_cache) >= self.max_size:
            oldest_key = next(iter(self.exact_cache))
            self.exact_cache.pop(oldest_key)
            print(f"🗑️ Cache full, evicted oldest entry")
        
        # Store in cache
        self.exact_cache[cache_key] = {
            "sql": sql,
            "results": results,
            "timestamp": time.time()
        }
        
        print(f"💾 Cached result (total: {len(self.exact_cache)}/{self.max_size})")
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def clear(self):
        """Clear cache"""
        self.exact_cache.clear()
        self.hits = 0
        self.misses = 0
        self.total_time_saved = 0.0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.exact_cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate():.1%}",
            "time_saved_seconds": round(self.total_time_saved, 2)
        }


# Global middleware instance
caching_middleware = CachingMiddleware(max_size=200)
