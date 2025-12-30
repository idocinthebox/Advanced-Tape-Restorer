"""
Disk Caching System for Processed Frames
Speeds up re-processing and enables resume functionality

Features:
- LRU (Least Recently Used) cache
- Automatic cache size management
- Fast pickle-based serialization
- Thread-safe operations
- User-configurable cache location

Performance Optimizations:
- __slots__ for reduced memory footprint
- Simplified key generation with f-strings
- Reduced method allocations
- Efficient size calculations
- Fast path for cache hits
"""

import pickle
import hashlib
import shutil
import time
from pathlib import Path
from typing import Any, Optional, Callable, Dict
from collections import OrderedDict
import threading

# Constants for cache key generation
_PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL
_BYTES_PER_GB = 1024 ** 3
_BYTES_PER_MB = 1024 ** 2
_SECONDS_PER_HOUR = 3600


class FrameCache:
    """
    Disk-based cache for processed video frames.
    
    Optimizations: __slots__, simplified key generation, efficient size tracking
    """
    
    __slots__ = ('cache_dir', 'max_size_bytes', 'ttl_seconds', 'lock', 'index', 'hits', 'misses', 
                 'current_size_bytes', 'index_dirty', 'last_index_save', 'operations_since_save')

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_size_gb: Optional[float] = None,
        ttl_hours: Optional[int] = None,
    ):
        """Initialize frame cache. Optimization: Use module constants, simplified config loading."""
        # Load from config if not specified
        if cache_dir is None or max_size_gb is None or ttl_hours is None:
            try:
                from core.config import get_config
                config = get_config()
                cache_dir = cache_dir or config.get_cache_dir()
                max_size_gb = max_size_gb or config.get_cache_max_size_gb()
                ttl_hours = ttl_hours or config.get_cache_ttl_hours()
            except ImportError:
                # Fallback to defaults
                cache_dir = cache_dir or Path("./cache")
                max_size_gb = max_size_gb or 10.0
                ttl_hours = ttl_hours or 24

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_size_bytes = int(max_size_gb * _BYTES_PER_GB)
        self.ttl_seconds = ttl_hours * _SECONDS_PER_HOUR

        # Thread safety
        self.lock = threading.Lock()

        # In-memory index for fast lookups
        self.index = self._load_index()

        # Stats
        self.hits = 0
        self.misses = 0
        
        # Debounced index persistence
        self.current_size_bytes = sum(item.get('size', 0) for item in self.index.values())
        self.index_dirty = False
        self.last_index_save = time.time()
        self.operations_since_save = 0

        print(f"Frame cache initialized: {cache_dir}")
        print(f"  Max size: {max_size_gb:.1f} GB")
        print(f"  TTL: {ttl_hours} hours")

    def _load_index(self) -> OrderedDict:
        """Load cache index from disk."""
        index_file = self.cache_dir / "cache_index.pkl"
        if index_file.exists():
            try:
                with open(index_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠ Failed to load cache index: {e}")

        return OrderedDict()

    def _save_index(self, force: bool = False):
        """Save cache index to disk (debounced)."""
        if not force:
            # Debounce: save every 5 seconds OR 100 operations
            time_since_save = time.time() - self.last_index_save
            if time_since_save < 5.0 and self.operations_since_save < 100:
                self.index_dirty = True
                return
        
        if not self.index_dirty and not force:
            return
            
        index_file = self.cache_dir / "cache_index.pkl"
        try:
            with open(index_file, "wb") as f:
                pickle.dump(self.index, f)
            self.index_dirty = False
            self.last_index_save = time.time()
            self.operations_since_save = 0
        except Exception as e:
            print(f"⚠ Failed to save cache index: {e}")

    def _get_cache_key(self, key: str, version: str = "v1") -> str:
        """Generate cache key. Optimization: Single f-string expression."""
        return hashlib.md5(f"{key}_{version}".encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        # Distribute files across subdirectories (first 2 chars of hash)
        subdir = cache_key[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(exist_ok=True)
        return cache_subdir / f"{cache_key}.pkl"

    def get(self, key: str, version: str = "v1") -> Optional[Any]:
        """Get cached item. Optimization: Early returns, single stat call, narrow lock scope."""
        cache_key = self._get_cache_key(key, version)
        
        # Check index (minimal lock)
        with self.lock:
            if cache_key not in self.index:
                self.misses += 1
                return None
            cache_path = self._get_cache_path(cache_key)

        # Check existence and TTL (outside lock - read-only filesystem operation)
        try:
            file_stat = cache_path.stat()
            file_age = time.time() - file_stat.st_mtime
            
            if file_age > self.ttl_seconds:
                # Expired - remove with lock
                with self.lock:
                    cache_path.unlink()
                    del self.index[cache_key]
                    self.operations_since_save += 1
                    self._save_index()
                    self.misses += 1
                return None
                
        except FileNotFoundError:
            # Remove stale index entry
            with self.lock:
                if cache_key in self.index:
                    del self.index[cache_key]
                    self.operations_since_save += 1
                    self._save_index()
                self.misses += 1
            return None

        # Load from disk (outside lock - independent I/O)
        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)

            # Update access time (LRU) - lock for index mutation
            with self.lock:
                self.index.move_to_end(cache_key)
                self.operations_since_save += 1
                self._save_index()
                self.hits += 1
            return data

        except Exception as e:
            print(f"⚠ Cache read error: {e}")
            # Remove corrupted cache
            with self.lock:
                try:
                    cache_path.unlink()
                except FileNotFoundError:
                    pass
                if cache_key in self.index:
                    del self.index[cache_key]
                    self.operations_since_save += 1
                    self._save_index()
                self.misses += 1
            return None

    def set(self, key: str, data: Any, version: str = "v1"):
        """Store item in cache. Optimization: Use module constant for protocol, reduced operations."""
        cache_key = self._get_cache_key(key, version)
        cache_path = self._get_cache_path(cache_key)

        # Save to disk (outside lock - independent I/O)
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(data, f, protocol=_PICKLE_PROTOCOL)

            # Update index (lock for mutation)
            file_size = cache_path.stat().st_size
            with self.lock:
                # Update size tracking
                if cache_key in self.index:
                    self.current_size_bytes -= self.index[cache_key].get('size', 0)
                
                self.index[cache_key] = {
                    "key": key,
                    "version": version,
                    "path": str(cache_path),
                    "size": file_size,
                    "time": time.time(),
                }
                self.current_size_bytes += file_size
                self.operations_since_save += 1
                self._save_index()

                # Check cache size
                self._evict_if_needed()

        except Exception as e:
            print(f"⚠ Cache write error: {e}")

    def has(self, key: str, version: str = "v1") -> bool:
        """Check if key exists in cache."""
        return self.get(key, version) is not None

    def delete(self, key: str, version: str = "v1"):
        """Delete cached item."""
        with self.lock:
            cache_key = self._get_cache_key(key, version)

            if cache_key in self.index:
                item = self.index[cache_key]
                cache_path = Path(item["path"])
                if cache_path.exists():
                    cache_path.unlink()
                self.current_size_bytes -= item.get('size', 0)
                del self.index[cache_key]
                self.operations_since_save += 1
                self._save_index(force=True)

    def clear(self):
        """Clear entire cache."""
        with self.lock:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.index = OrderedDict()
            self.current_size_bytes = 0
            self.operations_since_save = 0
            self._save_index(force=True)
            print("✓ Cache cleared")

    def get_size(self) -> int:
        """Get current cache size in bytes."""
        return self.current_size_bytes

    def _evict_if_needed(self):
        """Evict old items if cache exceeds max size (LRU)."""
        while self.current_size_bytes > self.max_size_bytes and self.index:
            # Remove oldest item (FIFO from OrderedDict)
            cache_key, item = self.index.popitem(last=False)

            cache_path = Path(item["path"])
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    self.current_size_bytes -= item["size"]
                except FileNotFoundError:
                    pass

        self._save_index()

    def get_stats(self) -> Dict[str, float]:
        """Get cache statistics. Optimization: Use module constants."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_items": len(self.index),
            "size_mb": self.get_size() / _BYTES_PER_MB,
            "max_size_mb": self.max_size_bytes / _BYTES_PER_MB,
        }

    def print_stats(self):
        """Print cache statistics."""
        stats = self.get_stats()
        print("\n=== Cache Statistics ===")
        print(f"Hits: {stats['hits']}")
        print(f"Misses: {stats['misses']}")
        print(f"Hit rate: {stats['hit_rate']:.1%}")
        print(f"Items: {stats['total_items']}")
        print(f"Size: {stats['size_mb']:.1f} / {stats['max_size_mb']:.1f} MB")


class CachedProcessor:
    """
    Wrapper that automatically caches expensive processing operations.
    
    Optimizations: __slots__ for reduced memory footprint
    """
    
    __slots__ = ('cache', 'cache_name', 'version')

    def __init__(
        self, cache_name: str, version: str = "v1", cache_dir: Optional[Path] = None
    ):
        """Initialize cached processor."""
        self.cache = FrameCache(cache_dir=cache_dir)
        self.cache_name = cache_name
        self.version = version

    def __call__(self, func: Callable) -> Callable:
        """Decorator to cache function results."""

        def wrapper(data, **kwargs):
            # Generate cache key from data hash
            data_hash = hashlib.md5(str(data).encode()).hexdigest()
            cache_key = f"{self.cache_name}_{data_hash}"

            # Check cache
            result = self.cache.get(cache_key, version=self.version)
            if result is not None:
                return result

            # Compute and cache
            result = func(data, **kwargs)
            self.cache.set(cache_key, result, version=self.version)

            return result

        return wrapper


# Decorator shorthand
def cached_processor(cache_name: str, version: str = "v1"):
    """Decorator for caching expensive operations."""
    return CachedProcessor(cache_name, version)


# Example usage
if __name__ == "__main__":
    print("=== Frame Cache Test ===\n")

    # Create cache
    cache = FrameCache(cache_dir=Path("./test_cache"), max_size_gb=0.1)

    # Test basic operations
    print("Testing basic cache operations...")

    # Set
    cache.set("frame_001", {"data": "test frame 1"}, version="v1.0")
    cache.set("frame_002", {"data": "test frame 2"}, version="v1.0")

    # Get
    result = cache.get("frame_001", version="v1.0")
    print(f"Retrieved: {result}")

    # Has
    exists = cache.has("frame_002", version="v1.0")
    print(f"Frame 002 exists: {exists}")

    # Stats
    cache.print_stats()

    # Test cached decorator
    print("\n\nTesting cached decorator...")

    @cached_processor("test_filter", version="v1.0")
    def slow_operation(data):
        """Simulate slow processing."""
        import time

        print(f"  Computing {data}...")
        time.sleep(0.1)  # Simulate work
        return data * 2

    # First call - slow
    start = time.perf_counter()
    result1 = slow_operation(5)
    time1 = time.perf_counter() - start

    # Second call - cached, instant
    start = time.perf_counter()
    result2 = slow_operation(5)
    time2 = time.perf_counter() - start

    print(f"\nFirst call: {time1 * 1000:.1f}ms")
    print(f"Second call (cached): {time2 * 1000:.1f}ms")
    print(f"Speedup: {time1 / time2:.1f}x faster")

    # Cleanup
    cache.clear()

    print("\n✓ Cache tests complete")
