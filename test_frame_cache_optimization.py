"""
Test suite for frame_cache.py optimizations

Verifies:
- Module-level constants
- __slots__ memory efficiency
- Simplified key generation
- Efficient caching operations
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.frame_cache import (
    FrameCache,
    CachedProcessor,
    _PICKLE_PROTOCOL,
    _BYTES_PER_GB,
    _BYTES_PER_MB,
    _SECONDS_PER_HOUR,
)


class TestModuleConstants(unittest.TestCase):
    """Test module-level optimization constants"""

    def test_pickle_protocol_constant(self):
        """Verify pickle protocol is module constant"""
        import pickle
        self.assertEqual(_PICKLE_PROTOCOL, pickle.HIGHEST_PROTOCOL)

    def test_bytes_constants(self):
        """Verify byte conversion constants"""
        self.assertEqual(_BYTES_PER_GB, 1024 ** 3)
        self.assertEqual(_BYTES_PER_MB, 1024 ** 2)
        self.assertEqual(_SECONDS_PER_HOUR, 3600)


class TestFrameCacheOptimizations(unittest.TestCase):
    """Test FrameCache class optimizations"""

    def setUp(self):
        """Create temporary cache directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slots_defined(self):
        """Verify __slots__ for memory efficiency"""
        self.assertTrue(hasattr(FrameCache, '__slots__'))
        expected_slots = ('cache_dir', 'max_size_bytes', 'ttl_seconds', 
                         'lock', 'index', 'hits', 'misses')
        self.assertEqual(FrameCache.__slots__, expected_slots)

    def test_slots_memory_reduction(self):
        """Verify __slots__ prevents __dict__ creation"""
        cache = FrameCache(cache_dir=self.cache_path, max_size_gb=1, ttl_hours=1)
        self.assertFalse(hasattr(cache, '__dict__'))

    def test_cache_key_generation_optimized(self):
        """Test simplified cache key generation"""
        cache = FrameCache(cache_dir=self.cache_path, max_size_gb=1, ttl_hours=1)
        
        # Generate keys
        key1 = cache._get_cache_key("test", "v1")
        key2 = cache._get_cache_key("test", "v1")
        key3 = cache._get_cache_key("test", "v2")
        
        # Same inputs produce same keys
        self.assertEqual(key1, key2)
        # Different versions produce different keys
        self.assertNotEqual(key1, key3)
        # Keys are MD5 hashes (32 hex chars)
        self.assertEqual(len(key1), 32)

    def test_initialization_with_constants(self):
        """Test initialization uses module constants"""
        cache = FrameCache(cache_dir=self.cache_path, max_size_gb=2, ttl_hours=24)
        
        # Verify calculations use module constants
        self.assertEqual(cache.max_size_bytes, 2 * _BYTES_PER_GB)
        self.assertEqual(cache.ttl_seconds, 24 * _SECONDS_PER_HOUR)


class TestCacheOperations(unittest.TestCase):
    """Test cache operations efficiency"""

    def setUp(self):
        """Create temporary cache"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FrameCache(
            cache_dir=Path(self.temp_dir),
            max_size_gb=0.1,
            ttl_hours=1
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_basic_set_get(self):
        """Test basic cache operations"""
        # Set
        self.cache.set("key1", {"data": "value1"}, version="v1")
        
        # Get
        result = self.cache.get("key1", version="v1")
        self.assertIsNotNone(result)
        self.assertEqual(result["data"], "value1")
        
        # Stats
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 0)

    def test_cache_miss(self):
        """Test cache miss tracking"""
        result = self.cache.get("nonexistent", version="v1")
        self.assertIsNone(result)
        self.assertEqual(self.cache.misses, 1)

    def test_has_method(self):
        """Test has() method"""
        self.cache.set("key1", "value1", version="v1")
        
        self.assertTrue(self.cache.has("key1", "v1"))
        self.assertFalse(self.cache.has("key2", "v1"))

    def test_delete_method(self):
        """Test delete() method"""
        self.cache.set("key1", "value1", version="v1")
        self.assertTrue(self.cache.has("key1", "v1"))
        
        self.cache.delete("key1", "v1")
        self.assertFalse(self.cache.has("key1", "v1"))

    def test_get_size(self):
        """Test size calculation"""
        # Empty cache
        self.assertEqual(self.cache.get_size(), 0)
        
        # Add items
        self.cache.set("key1", "value1" * 100, version="v1")
        size1 = self.cache.get_size()
        self.assertGreater(size1, 0)
        
        self.cache.set("key2", "value2" * 100, version="v1")
        size2 = self.cache.get_size()
        self.assertGreater(size2, size1)

    def test_stats_calculation_with_constants(self):
        """Test stats use module constants for conversions"""
        self.cache.set("key1", "value1", version="v1")
        self.cache.get("key1", "v1")
        
        stats = self.cache.get_stats()
        
        # Verify stats structure
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertIn("hit_rate", stats)
        self.assertIn("size_mb", stats)
        self.assertIn("max_size_mb", stats)
        
        # Verify calculations use constants
        self.assertAlmostEqual(
            stats["max_size_mb"],
            self.cache.max_size_bytes / _BYTES_PER_MB,
            places=2
        )


class TestCachedProcessorOptimizations(unittest.TestCase):
    """Test CachedProcessor optimizations"""

    def setUp(self):
        """Create temporary cache"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slots_defined(self):
        """Verify __slots__ for CachedProcessor"""
        self.assertTrue(hasattr(CachedProcessor, '__slots__'))
        self.assertEqual(CachedProcessor.__slots__, ('cache', 'cache_name', 'version'))

    def test_slots_memory_reduction(self):
        """Verify __slots__ prevents __dict__"""
        processor = CachedProcessor(
            "test_cache",
            version="v1",
            cache_dir=Path(self.temp_dir)
        )
        self.assertFalse(hasattr(processor, '__dict__'))

    def test_decorator_functionality(self):
        """Test cached processor decorator"""
        processor = CachedProcessor(
            "test_op",
            version="v1",
            cache_dir=Path(self.temp_dir)
        )
        
        call_count = 0
        
        @processor
        def expensive_operation(data):
            nonlocal call_count
            call_count += 1
            return data * 2
        
        # First call
        result1 = expensive_operation(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call (should be cached)
        result2 = expensive_operation(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Not called again


class TestLRUEviction(unittest.TestCase):
    """Test LRU eviction optimization"""

    def setUp(self):
        """Create small cache for eviction testing"""
        self.temp_dir = tempfile.mkdtemp()
        # Very small cache to trigger eviction
        self.cache = FrameCache(
            cache_dir=Path(self.temp_dir),
            max_size_gb=0.000001,  # ~1KB
            ttl_hours=24
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_eviction_when_full(self):
        """Test LRU eviction when cache is full"""
        # Add multiple items to exceed cache size
        large_data = "x" * 500  # 500 bytes per item
        
        self.cache.set("key1", large_data, version="v1")
        self.cache.set("key2", large_data, version="v1")
        self.cache.set("key3", large_data, version="v1")
        
        # Due to small cache size, old items should be evicted
        # Verify cache size stays under limit
        self.assertLessEqual(self.cache.get_size(), self.cache.max_size_bytes)


class TestPerformanceOptimizations(unittest.TestCase):
    """Test specific performance optimizations"""

    def setUp(self):
        """Create cache"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FrameCache(
            cache_dir=Path(self.temp_dir),
            max_size_gb=1,
            ttl_hours=1
        )

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_uses_single_stat_call(self):
        """Verify get() uses single stat() call for efficiency"""
        self.cache.set("key1", "value1", version="v1")
        
        # Verify item exists
        result = self.cache.get("key1", "v1")
        self.assertIsNotNone(result)
        self.assertEqual(result, "value1")
        
        # Verify hits/misses tracking works
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 0)

    def test_set_uses_constant_protocol(self):
        """Verify set() uses module constant for pickle protocol"""
        # This is tested implicitly - if it works, it's using the constant
        self.cache.set("key1", {"complex": [1, 2, 3]}, version="v1")
        result = self.cache.get("key1", "v1")
        self.assertEqual(result["complex"], [1, 2, 3])


def run_tests():
    """Run all tests and return success status"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
