from collections import OrderedDict
from config import config

class SimpleCache:
    def __init__(self, max_size=100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, question):
        """Retrieve cached result"""
        question_lower = question.lower().strip()
        if question_lower in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(question_lower)
            return self.cache[question_lower]
        return None
    
    def set(self, question, sql, results):
        """Save result to cache"""
        question_lower = question.lower().strip()
        
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[question_lower] = {
            "sql": sql,
            "results": results,
            "cached": True
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
    
    def size(self):
        """Get cache size"""
        return len(self.cache)

# Global cache instance
cache = SimpleCache(max_size=config.CACHE_SIZE)
