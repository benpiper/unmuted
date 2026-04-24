"""In-memory LRU cache for VLM API responses.

Caches responses keyed by a hash of the frame image bytes and text prompt,
so re-analyzing the same frame with the same context is instant and free.
"""

import hashlib
import logging
import os
from collections import OrderedDict
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default max entries. Each entry is ~2KB of JSON text, so 500 entries ~ 1MB.
DEFAULT_MAX_SIZE = int(os.getenv("VLM_CACHE_MAX_SIZE", "500"))


class VLMCache:
    """Thread-safe LRU cache for VLM API responses."""

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_frame(frame_path: str) -> str:
        """Generate a stable hash from the frame file contents."""
        h = hashlib.sha256()
        with open(frame_path, "rb") as f:
            # Read in 64KB chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def make_key(frame_path: str, prompt: str, context: str, synopsis: str, tools_context: str) -> str:
        """Build a cache key from the frame content hash and text inputs."""
        frame_hash = VLMCache._hash_frame(frame_path)
        text_hash = hashlib.sha256(
            f"{prompt}|{context}|{synopsis}|{tools_context}".encode()
        ).hexdigest()[:16]
        return f"{frame_hash}:{text_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached response. Returns None on miss."""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                logger.debug(f"VLM cache HIT (hits={self._hits}, misses={self._misses})")
                return self._cache[key]
            self._misses += 1
            return None

    def put(self, key: str, value: Any) -> None:
        """Store a response in the cache, evicting oldest if at capacity."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = value
                return
            if len(self._cache) >= self._max_size:
                evicted_key, _ = self._cache.popitem(last=False)
                logger.debug(f"VLM cache evicted oldest entry: {evicted_key[:16]}...")
            self._cache[key] = value

    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict:
        """Return cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_pct": round(hit_rate, 1),
            }


# Module-level singleton
vlm_cache = VLMCache()
