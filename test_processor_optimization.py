"""
Test suite for optimized processor.py (v3.2 → v3.3)
Verifies processor optimizations are working correctly
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.processor import VideoProcessor

def test_instantiation():
    """Test VideoProcessor instantiation with optimizations"""
    print("TEST 1: Class Instantiation")
    
    processor = VideoProcessor()
    
    # Verify __slots__ or optimized attributes
    assert hasattr(processor, 'analyzer')
    assert hasattr(processor, 'encoder')
    assert hasattr(processor, 'propainter')
    assert hasattr(processor, '_temp_files')
    assert hasattr(processor, '_video_info_cache')
    
    # Verify temp files is a set (O(1) lookups)
    assert isinstance(processor._temp_files, set), "_temp_files should be a set for O(1) operations"
    
    # Verify video info cache is initialized
    assert isinstance(processor._video_info_cache, dict)
    
    print("  ✅ PASSED - Processor instantiates with optimized data structures")
    return True

def test_check_prerequisites_static():
    """Test check_prerequisites is static method"""
    print("\nTEST 2: Static Method Optimization")
    
    # Should be callable without instance
    with patch('shutil.which', return_value='/usr/bin/vspipe'):
        try:
            VideoProcessor.check_prerequisites()
            print("  ✅ PASSED - check_prerequisites is static (no self needed)")
            return True
        except TypeError:
            print("  ❌ FAILED - Method requires self (not properly static)")
            return False

def test_video_info_caching():
    """Test video info caching optimization"""
    print("\nTEST 3: Video Info Caching")
    
    processor = VideoProcessor()
    
    # Mock analyzer
    mock_info = (1920, 1080, 1.0, 1000, 30.0)
    processor.analyzer.get_video_info = Mock(return_value=mock_info)
    
    # First call should hit analyzer
    result1 = processor._get_cached_video_info("test_video.mp4")
    assert processor.analyzer.get_video_info.call_count == 1
    assert result1 == mock_info
    
    # Second call should use cache (no additional analyzer call)
    result2 = processor._get_cached_video_info("test_video.mp4")
    assert processor.analyzer.get_video_info.call_count == 1  # Still 1!
    assert result2 == mock_info
    
    # Different file should call analyzer again
    result3 = processor._get_cached_video_info("different_video.mp4")
    assert processor.analyzer.get_video_info.call_count == 2
    
    print("  ✅ PASSED - Video info caching prevents redundant ffprobe calls")
    return True

def test_ai_settings_precomputation():
    """Test AI settings pre-calculation optimization"""
    print("\nTEST 4: AI Settings Pre-computation")
    
    processor = VideoProcessor()
    
    options = {
        'use_ai_upscaling': True,
        'ai_upscaling_method': 'RealESRGAN (4x, CUDA)',
        'ai_interpolation': True,
        'interpolation_factor': '2x',
        'codec': 'ProRes 422'
    }
    
    # Should return pre-computed dict
    ai_settings = processor._calculate_ai_settings(options, 1280, 720, 30.0)
    
    assert isinstance(ai_settings, dict)
    assert 'uses_ai' in ai_settings
    assert 'output_width' in ai_settings
    assert 'output_height' in ai_settings
    assert 'output_fps' in ai_settings
    assert 'buffer_size' in ai_settings
    
    # Verify values are computed correctly
    assert ai_settings['uses_ai'] == True
    assert ai_settings['output_width'] == 2560  # 1280 * 2 (upscaling)
    assert ai_settings['output_height'] == 1440  # 720 * 2 (upscaling)
    assert ai_settings['output_fps'] == 60.0  # 30 * 2 (interpolation)
    
    from core.processor import BUFFER_SIZE_PRORES_AI
    assert ai_settings['buffer_size'] == BUFFER_SIZE_PRORES_AI
    
    print("  ✅ PASSED - AI settings pre-computed (avoid repeated checks)")
    return True

def test_temp_file_tracking():
    """Test temp file tracking with set (O(1) operations)"""
    print("\nTEST 5: Temp File Tracking (Set-based)")
    
    processor = VideoProcessor()
    
    # Add files to tracking
    file1 = "temp_file_1.tmp"
    file2 = "temp_file_2.tmp"
    
    processor._temp_files.add(file1)
    processor._temp_files.add(file2)
    
    # Verify set operations
    assert len(processor._temp_files) == 2
    assert file1 in processor._temp_files  # O(1) membership check
    assert file2 in processor._temp_files
    
    # Duplicate add should not increase size
    processor._temp_files.add(file1)
    assert len(processor._temp_files) == 2
    
    # Remove operation
    processor._temp_files.discard(file1)
    assert file1 not in processor._temp_files
    assert len(processor._temp_files) == 1
    
    print("  ✅ PASSED - Temp file tracking uses set (O(1) operations)")
    return True

def test_constants_defined():
    """Test performance constants are defined"""
    print("\nTEST 6: Performance Constants")
    
    from core.processor import (
        BUFFER_SIZE_PRORES_AI,
        BUFFER_SIZE_STANDARD,
        MIN_VALID_FILE_SIZE,
        VSPIPE_TERMINATE_TIMEOUT
    )
    
    # Verify constants exist and have reasonable values
    assert BUFFER_SIZE_PRORES_AI > 0
    assert BUFFER_SIZE_STANDARD > 0
    assert MIN_VALID_FILE_SIZE > 0
    assert VSPIPE_TERMINATE_TIMEOUT > 0
    
    # Verify they're actually constants (right sizes)
    assert BUFFER_SIZE_PRORES_AI == 2097152  # 2MB
    assert BUFFER_SIZE_STANDARD == 10485760  # 10MB
    
    print("  ✅ PASSED - Performance constants defined (avoid magic numbers)")
    return True

def test_memory_efficiency():
    """Test memory-efficient patterns"""
    print("\nTEST 7: Memory Efficiency Checks")
    
    processor = VideoProcessor()
    
    # Test lazy initialization - vs_engine should be None initially
    assert processor.vs_engine is None, "vs_engine should be lazily initialized"
    
    # Test that caches are properly sized (empty at start)
    assert len(processor._video_info_cache) == 0
    assert len(processor._temp_files) == 0
    
    print("  ✅ PASSED - Memory-efficient patterns (lazy init, proper caching)")
    return True

def test_optimized_docstrings():
    """Test that optimization notes are in docstrings"""
    print("\nTEST 8: Optimization Documentation")
    
    # Check module docstring
    from core import processor
    assert "Performance Optimizations" in processor.__doc__ or "Optimizations" in processor.__doc__
    
    # Check VideoProcessor docstring
    assert "Optimization" in VideoProcessor.__doc__ or "optimization" in VideoProcessor.__doc__
    
    # Check method docstrings have optimization notes
    assert "Optimization" in VideoProcessor.check_prerequisites.__doc__
    assert "Optimization" in VideoProcessor._get_cached_video_info.__doc__
    
    print("  ✅ PASSED - Optimization notes documented in docstrings")
    return True

def test_buffer_size_selection():
    """Test buffer size logic uses constants"""
    print("\nTEST 9: Buffer Size Selection Logic")
    
    from core.processor import BUFFER_SIZE_PRORES_AI, BUFFER_SIZE_STANDARD
    
    # Create mock options
    options_prores_ai = {
        'output_codec': 'prores',
        'use_ai_upscaling': True
    }
    
    options_standard = {
        'output_codec': 'libx264',
        'use_ai_upscaling': False
    }
    
    processor = VideoProcessor()
    
    # Test that the constants would be used correctly
    # (we can't directly test _select_buffer_size without running full processing,
    # but we verify the constants are correct values)
    
    assert BUFFER_SIZE_PRORES_AI < BUFFER_SIZE_STANDARD, \
        "ProRes+AI should use smaller buffer to reduce memory"
    
    print("  ✅ PASSED - Buffer size constants optimized for different codecs")
    return True

def test_error_handling_preserved():
    """Test that optimizations didn't break error handling"""
    print("\nTEST 10: Error Handling Integrity")
    
    processor = VideoProcessor()
    
    # Test that check_prerequisites raises on missing tools
    with patch('shutil.which', return_value=None):
        try:
            VideoProcessor.check_prerequisites()
            print("  ❌ FAILED - Should raise RuntimeError for missing tools")
            return False
        except RuntimeError as e:
            assert "Missing external tools" in str(e)
            print("  ✅ PASSED - Error handling preserved in optimized code")
            return True

def run_all_tests():
    """Run all processor optimization tests"""
    print("="*70)
    print("  PROCESSOR.PY v3.2/v3.3 - OPTIMIZATION VERIFICATION")
    print("="*70)
    
    tests = [
        test_instantiation,
        test_check_prerequisites_static,
        test_video_info_caching,
        test_ai_settings_precomputation,
        test_temp_file_tracking,
        test_constants_defined,
        test_memory_efficiency,
        test_optimized_docstrings,
        test_buffer_size_selection,
        test_error_handling_preserved
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ FAILED - Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Processor optimizations verified!")
    else:
        print(f"⚠️  {failed} test(s) failed. Review optimizations.")
    print("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
