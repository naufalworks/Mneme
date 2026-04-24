"""Query caching for performance optimization."""

from functools import lru_cache
from typing import Dict, Any
import hashlib
import json


class QueryCache:
    """LRU cache for expensive query operations."""

    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self._cache = {}
        self._access_order = []

    def _make_key(self, *args, **kwargs) -> str:
        """Create cache key from arguments."""
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Any:
        """Get cached value."""
        if key in self._cache:
            # Update access order (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.maxsize:
            # Evict least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._access_order.clear()

    def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries matching pattern."""
        if pattern is None:
            self.clear()
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                self._access_order.remove(key)
