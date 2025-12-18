"""In-memory cache with TTL (time-to-live) support.

Provides InMemoryCache for fast caching of parsed data with
automatic expiration.
"""

import time
from typing import Any, Dict, Optional

from utils.logger import Logger

logger = Logger()


class InMemoryCache:
    """In-memory cache with TTL support.

    Stores data in memory with optional time-to-live expiration.

    Example:
        >>> cache = InMemoryCache()
        >>> cache.set("key1", "value1", ttl=60)
        >>> cache.get("key1")
        'value1'
        >>> cache.exists("key1")
        True
    """

    def __init__(self) -> None:
        """Initialize InMemoryCache."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.debug("Initialized InMemoryCache")

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = no expiration)

        Example:
            >>> cache = InMemoryCache()
            >>> cache.set("session", {"user_id": 123}, ttl=3600)
        """
        expiry = None
        if ttl is not None:
            expiry = time.time() + ttl

        self._cache[key] = {
            'value': value,
            'expiry': expiry,
        }
        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")

    def get(self, key: str) -> Optional[Any]:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired

        Example:
            >>> cache = InMemoryCache()
            >>> cache.set("user", "John")
            >>> cache.get("user")
            'John'
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if expired
        if entry['expiry'] is not None and time.time() > entry['expiry']:
            del self._cache[key]
            logger.debug(f"Cache entry expired: {key}")
            return None

        return entry['value']

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired, False otherwise
        """
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Delete cache entry.

        Args:
            key: Cache key to delete
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache entry: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.debug(f"Cleared cache ({count} entries removed)")

    def get_count(self) -> int:
        """Get number of cache entries.

        Returns:
            Count of cache entries (including expired)
        """
        return len(self._cache)

    def cleanup(self) -> int:
        """Remove expired entries.

        Returns:
            Count of removed entries
        """
        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if entry['expiry'] is not None and current_time > entry['expiry']:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)

    def __repr__(self) -> str:
        """String representation."""
        return f"InMemoryCache(entries={len(self._cache)})"
