"""
LLM Response Cache Manager
Location: tcs_poc/utils/cache_manager.py
Caches LLM responses to reduce API calls and improve speed

SAVES IT TO:
Folder: ./cache/
File: response_cache.json
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
import os


class ResponseCache:
    """Caches LLM responses with TTL (Time To Live)"""
    
    def __init__(self, cache_dir: str = "./cache", ttl_hours: int = 24):
        """
        Initialize response cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live in hours (default 24)
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = {}  # In-memory cache: key -> response
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache from disk
        self._load_cache()
        
        print(f"🗂️ Cache Manager initialized (TTL: {ttl_hours}h, Entries: {len(self.cache)})")
    
    
    def _generate_key(self, query: str, agent_type: str, filters: Optional[Dict] = None) -> str:
        """Generate cache key from query + context"""
        # Create unique key from query, agent type, and filters
        key_parts = [query.lower().strip(), agent_type]
        
        if filters:
            key_parts.append(json.dumps(filters, sort_keys=True))
        
        key_string = "|".join(key_parts)
        
        # Hash to fixed length
        return hashlib.md5(key_string.encode()).hexdigest()
    
    
    def get(self, query: str, agent_type: str, filters: Optional[Dict] = None) -> Optional[str]:
        """
        Get cached response if exists and not expired
        
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(query, agent_type, filters)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        cached_time = datetime.fromisoformat(entry['timestamp'])
        if datetime.now() - cached_time > self.ttl:
            # Expired - remove from cache
            del self.cache[key]
            self._save_cache()
            return None
        
        print(f"💚 Cache HIT: {query[:50]}...")
        return entry['response']
    
    
    def set(self, query: str, agent_type: str, response: str, filters: Optional[Dict] = None):
        """Cache a response"""
        key = self._generate_key(query, agent_type, filters)
        
        self.cache[key] = {
            'query': query,
            'agent_type': agent_type,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'filters': filters
        }
        
        # Persist to disk
        self._save_cache()
        
        print(f"💾 Cache SAVED: {query[:50]}...")
    
    
    def clear(self):
        """Clear entire cache"""
        self.cache = {}
        self._save_cache()
        print("🗑️ Cache cleared!")
    
    
    def clear_expired(self):
        """Remove expired entries"""
        original_count = len(self.cache)
        
        keys_to_remove = []
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        removed_count = len(keys_to_remove)
        if removed_count > 0:
            self._save_cache()
            print(f"🧹 Removed {removed_count} expired entries")
        
        return removed_count
    
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        
        # Count by agent type
        agent_counts = {}
        for entry in self.cache.values():
            agent_type = entry['agent_type']
            agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
        
        return {
            'total_entries': total_entries,
            'by_agent': agent_counts,
            'ttl_hours': self.ttl.total_seconds() / 3600
        }
    
    
    def _save_cache(self):
        """Persist cache to disk"""
        filepath = os.path.join(self.cache_dir, "response_cache.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    
    def _load_cache(self):
        """Load cache from disk"""
        filepath = os.path.join(self.cache_dir, "response_cache.json")
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
            
            # Clean expired on load
            self.clear_expired()
            
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
            self.cache = {}


if __name__ == "__main__":
    # Test cache manager
    cache = ResponseCache(ttl_hours=1)
    
    # Test cache miss
    result = cache.get("What is home loan?", "knowledge")
    print(f"First lookup: {result}")  # None
    
    # Cache a response
    cache.set(
        query="What is home loan?",
        agent_type="knowledge",
        response="A home loan is a secured loan..."
    )
    
    # Test cache hit
    result = cache.get("What is home loan?", "knowledge")
    print(f"Second lookup: {result[:50]}...")  # Should return cached
    
    # Stats
    print("\n" + "="*70)
    print("CACHE STATS:")
    print(json.dumps(cache.get_stats(), indent=2))
