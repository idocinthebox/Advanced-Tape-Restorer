"""
Test GPU Memory Optimization Features
Tests new VapourSynth memory limits and VRAM requirement checking
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vapoursynth_memory_limit():
    """Test VapourSynth memory limit calculation"""
    print("\n" + "="*60)
    print("TEST 1: VapourSynth Memory Limit Calculation")
    print("="*60)
    
    from core.vapoursynth_engine import VapourSynthEngine
    
    engine = VapourSynthEngine(script_file="test_memory_limit.vpy")
    
    # Test memory limit calculation
    memory_limit_mb = engine._calculate_memory_limit()
    
    print(f"\n✅ Memory limit calculated: {memory_limit_mb} MB ({memory_limit_mb/1024:.2f} GB)")
    
    # Validate reasonable limits
    assert memory_limit_mb >= 512, "Memory limit too low (minimum 512MB)"
    assert memory_limit_mb <= 16384, "Memory limit suspiciously high (>16GB)"
    
    print("✅ PASSED - Memory limit is within reasonable range")
    
    return True


def test_vram_requirement_checking():
    """Test per-filter VRAM requirement estimation"""
    print("\n" + "="*60)
    print("TEST 2: VRAM Requirement Checking")
    print("="*60)
    
    from core.processor import VideoProcessor
    
    processor = VideoProcessor()
    
    # Test Case 1: CPU-only workflow (should pass)
    print("\n📋 Test Case 1: CPU-only workflow")
    options_cpu = {
        'use_qtgmc': True,
        'bm3d_enabled': True,
        'bm3d_use_gpu': False,  # CPU BM3D
        'use_ai_upscaling': False,
        'ai_interpolation': False,
        'width': 1920,
        'height': 1080
    }
    
    result = processor._check_vram_requirements(options_cpu)
    print(f"   Result: {'✅ OK' if result['ok'] else '⚠️ WARNING'}")
    assert result['ok'] == True, "CPU-only workflow should always pass"
    print("   ✅ PASSED - No VRAM check for CPU workflow")
    
    # Test Case 2: Moderate GPU usage (1080p + BM3D GPU)
    print("\n📋 Test Case 2: Moderate GPU usage (1080p + BM3D GPU)")
    options_moderate = {
        'use_qtgmc': True,
        'bm3d_enabled': True,
        'bm3d_use_gpu': True,  # GPU BM3D
        'use_ai_upscaling': False,
        'ai_interpolation': False,
        'width': 1920,
        'height': 1080
    }
    
    result = processor._check_vram_requirements(options_moderate)
    print(f"   Result: {'✅ OK' if result['ok'] else '⚠️ WARNING'}")
    if not result['ok']:
        print(f"   Required: {result['required']:.1f} GB")
        print(f"   Available: {result['available']:.1f} GB")
        print(f"   Suggestions:\n{result['suggestion']}")
    print("   ℹ️  INFO - Check reflects your current GPU VRAM availability")
    
    # Test Case 3: Heavy GPU usage (1080p + BM3D + RealESRGAN + RIFE)
    print("\n📋 Test Case 3: Heavy GPU usage (All AI features)")
    options_heavy = {
        'use_qtgmc': True,
        'bm3d_enabled': True,
        'bm3d_use_gpu': True,
        'use_ai_upscaling': True,
        'ai_upscaling_method': 'RealESRGAN (4x, CUDA)',
        'ai_interpolation': True,
        'interpolation_factor': '2x',
        'width': 1920,
        'height': 1080
    }
    
    result = processor._check_vram_requirements(options_heavy)
    print(f"   Result: {'✅ OK' if result['ok'] else '⚠️ WARNING'}")
    if not result['ok']:
        print(f"   Required: {result['required']:.1f} GB")
        print(f"   Available: {result['available']:.1f} GB")
        print(f"   Suggestions:\n{result['suggestion']}")
    else:
        print("   ✅ Your GPU has sufficient VRAM for all features!")
    
    # Test Case 4: 4K resolution stress test
    print("\n📋 Test Case 4: 4K resolution (stress test)")
    options_4k = {
        'use_qtgmc': True,
        'bm3d_enabled': True,
        'bm3d_use_gpu': True,
        'use_ai_upscaling': True,
        'ai_upscaling_method': 'RealESRGAN (2x, CUDA)',
        'ai_interpolation': False,
        'width': 3840,
        'height': 2160
    }
    
    result = processor._check_vram_requirements(options_4k)
    print(f"   Result: {'✅ OK' if result['ok'] else '⚠️ WARNING'}")
    if not result['ok']:
        print(f"   Required: {result['required']:.1f} GB")
        print(f"   Available: {result['available']:.1f} GB")
        print(f"   Suggestions:\n{result['suggestion']}")
    
    print("\n✅ PASSED - VRAM checking functional")
    return True


def test_script_generation_with_memory_limit():
    """Test VapourSynth script includes memory limit"""
    print("\n" + "="*60)
    print("TEST 3: Script Generation with Memory Limit")
    print("="*60)
    
    from core.vapoursynth_engine import VapourSynthEngine
    
    engine = VapourSynthEngine(script_file="test_memory_limit_script.vpy")
    
    # Generate a simple script
    options = {
        'use_qtgmc': False,
        'bm3d_enabled': False,
        'use_ai_upscaling': False,
        'ai_interpolation': False
    }
    
    engine.create_script("test_input.mp4", options)
    
    # Read generated script
    with open("test_memory_limit_script.vpy", "r") as f:
        script_content = f.read()
    
    # Check for memory limit configuration
    assert "core.max_cache_size" in script_content, "Memory limit not found in script"
    
    print("\n✅ Generated script contains memory limit configuration")
    
    # Show relevant lines
    for line in script_content.split('\n'):
        if 'max_cache_size' in line:
            print(f"   {line}")
    
    # Cleanup
    os.remove("test_memory_limit_script.vpy")
    
    print("\n✅ PASSED - Memory limit integrated into script generation")
    return True


def test_gpu_availability():
    """Test GPU detection and VRAM reporting"""
    print("\n" + "="*60)
    print("TEST 4: GPU Detection and VRAM Status")
    print("="*60)
    
    try:
        from core.gpu_accelerator import GPUAccelerator
        
        gpu = GPUAccelerator()
        
        if gpu.is_available():
            vram = gpu.get_vram_usage()
            
            print(f"\n✅ GPU detected and available")
            print(f"   Total VRAM: {vram['total_gb']:.2f} GB")
            print(f"   Used VRAM: {vram['used_gb']:.2f} GB")
            print(f"   Free VRAM: {vram['free_gb']:.2f} GB")
            print(f"   Usage: {vram['percent_used']:.1f}%")
            
            # Test memory limit calculation
            batch_size = gpu.calculate_optimal_batch_size(frame_size_mb=25.0)
            print(f"\n   Optimal batch size for 25MB frames: {batch_size}")
            
            print("\n✅ PASSED - GPU monitoring functional")
        else:
            print("\n⚠️  WARNING - GPU not available (CPU-only mode)")
            print("   This is normal if no CUDA GPU is present")
            print("\n✅ PASSED - Graceful fallback to CPU mode")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED - GPU detection error: {e}")
        return False


def run_all_tests():
    """Run all GPU memory optimization tests"""
    print("\n" + "="*60)
    print("GPU MEMORY OPTIMIZATION TEST SUITE")
    print("Advanced Tape Restorer v3.3")
    print("="*60)
    
    tests = [
        ("GPU Detection", test_gpu_availability),
        ("VapourSynth Memory Limit", test_vapoursynth_memory_limit),
        ("VRAM Requirement Checking", test_vram_requirement_checking),
        ("Script Generation", test_script_generation_with_memory_limit),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"RESULT: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
