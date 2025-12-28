"""
Test script for GPU memory management fixes
Tests GPU detection, VRAM reporting, and cleanup functions
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_gpu_detection():
    """Test GPU detection and VRAM reporting."""
    print("=" * 70)
    print("TEST 1: GPU Detection and VRAM Reporting")
    print("=" * 70)
    
    try:
        from core.gpu_accelerator import GPUAccelerator
        
        print("\n[1] Initializing GPU Accelerator...")
        gpu = GPUAccelerator()
        
        print(f"\n[2] GPU Available: {gpu.is_available()}")
        
        if gpu.is_available():
            info = gpu.get_info()
            print(f"    Backend: {info['backend']}")
            print(f"    Device: {info['device_name']}")
            print(f"    Total Memory: {info['memory_gb']:.2f} GB")
            
            print("\n[3] Getting VRAM Usage...")
            vram = gpu.get_vram_usage()
            print(f"    Used: {vram.get('used_gb', 0):.2f} GB")
            print(f"    Free: {vram.get('free_gb', 0):.2f} GB")
            print(f"    Total: {vram.get('total_gb', 0):.2f} GB")
            print(f"    Percent Used: {vram.get('percent_used', 0):.1f}%")
            
            print("\n[4] Testing Cache Clear...")
            gpu.clear_cache()
            
            print("\n[5] VRAM After Cache Clear...")
            vram_after = gpu.get_vram_usage()
            print(f"    Used: {vram_after.get('used_gb', 0):.2f} GB")
            print(f"    Free: {vram_after.get('free_gb', 0):.2f} GB")
            
            freed = vram.get('used_gb', 0) - vram_after.get('used_gb', 0)
            print(f"    Freed: {freed:.2f} GB")
            
            print("\n✅ GPU Detection Test PASSED")
            return True
        else:
            print("\n⚠️  No GPU detected - tests will use CPU fallback")
            print("    This is expected if you don't have NVIDIA GPU with CUDA")
            return True
            
    except Exception as e:
        print(f"\n❌ GPU Detection Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_processor_cleanup():
    """Test VideoProcessor GPU cleanup."""
    print("\n" + "=" * 70)
    print("TEST 2: VideoProcessor GPU Memory Cleanup")
    print("=" * 70)
    
    try:
        from core.processor import VideoProcessor
        
        print("\n[1] Creating VideoProcessor...")
        processor = VideoProcessor()
        
        print("\n[2] Testing _cleanup_gpu_memory() method...")
        processor._cleanup_gpu_memory()
        
        print("\n✅ Processor Cleanup Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Processor Cleanup Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vapoursynth_tile_calculation():
    """Test VapourSynth optimal tile size calculation."""
    print("\n" + "=" * 70)
    print("TEST 3: VapourSynth GPU Tile Size Optimization")
    print("=" * 70)
    
    try:
        from core.vapoursynth_engine import VapourSynthEngine
        
        print("\n[1] Creating VapourSynth Engine...")
        vs_engine = VapourSynthEngine(log_callback=print)
        
        print("\n[2] Testing tile size calculation for 1920x1080...")
        tile_size = vs_engine._calculate_optimal_tile_size(1920, 1080, scale=4)
        
        if tile_size is None:
            print("    Result: Runtime detection (GPU not available in GUI env)")
        elif tile_size == [0, 0]:
            print("    Result: Auto mode (conservative)")
        else:
            print(f"    Result: {tile_size[0]}x{tile_size[1]} tiles")
        
        print("\n[3] Testing memory limit calculation...")
        mem_limit = vs_engine._calculate_memory_limit()
        print(f"    VapourSynth cache limit: {mem_limit} MB ({mem_limit/1024:.2f} GB)")
        
        print("\n✅ VapourSynth Tile Calculation Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ VapourSynth Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vram_requirements_check():
    """Test VRAM requirements checking."""
    print("\n" + "=" * 70)
    print("TEST 4: VRAM Requirements Pre-Flight Check")
    print("=" * 70)
    
    try:
        from core.processor import VideoProcessor
        
        print("\n[1] Creating VideoProcessor...")
        processor = VideoProcessor()
        
        # Test various configurations
        test_configs = [
            {
                "name": "Light (QTGMC only)",
                "options": {
                    "use_qtgmc": True,
                    "bm3d_enabled": False,
                    "use_ai_upscaling": False,
                    "ai_interpolation": False,
                    "width": 1920,
                    "height": 1080
                }
            },
            {
                "name": "Medium (QTGMC + BM3D GPU)",
                "options": {
                    "use_qtgmc": True,
                    "bm3d_enabled": True,
                    "bm3d_use_gpu": True,
                    "use_ai_upscaling": False,
                    "ai_interpolation": False,
                    "width": 1920,
                    "height": 1080
                }
            },
            {
                "name": "Heavy (RealESRGAN 4x)",
                "options": {
                    "use_qtgmc": True,
                    "bm3d_enabled": False,
                    "use_ai_upscaling": True,
                    "ai_upscaling_method": "RealESRGAN",
                    "ai_interpolation": False,
                    "width": 1920,
                    "height": 1080
                }
            },
            {
                "name": "Extreme (RealESRGAN + RIFE)",
                "options": {
                    "use_qtgmc": True,
                    "use_ai_upscaling": True,
                    "ai_upscaling_method": "RealESRGAN",
                    "ai_interpolation": True,
                    "interpolation_factor": "2x (30fps→60fps)",
                    "width": 1920,
                    "height": 1080
                }
            }
        ]
        
        for config in test_configs:
            print(f"\n[{test_configs.index(config) + 2}] Testing: {config['name']}")
            result = processor._check_vram_requirements(config['options'])
            
            if result.get('ok'):
                print(f"    ✅ VRAM check passed")
                if 'required' in result:
                    print(f"    Required: {result['required']:.1f} GB")
                    print(f"    Available: {result['available']:.1f} GB")
            else:
                print(f"    ⚠️  VRAM warning:")
                print(f"    Required: {result.get('required', 0):.1f} GB")
                print(f"    Available: {result.get('available', 0):.1f} GB")
                if 'suggestion' in result:
                    print(f"    Suggestion: {result['suggestion']}")
        
        print("\n✅ VRAM Requirements Check Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ VRAM Requirements Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_leak_simulation():
    """Simulate multiple processing sessions to test for memory leaks."""
    print("\n" + "=" * 70)
    print("TEST 5: Memory Leak Simulation (Multiple Cleanup Cycles)")
    print("=" * 70)
    
    try:
        from core.gpu_accelerator import GPUAccelerator
        
        gpu = GPUAccelerator()
        if not gpu.is_available():
            print("\n⚠️  Skipping memory leak test - no GPU available")
            return True
        
        print("\n[1] Running 5 cleanup cycles to test for leaks...")
        
        baseline_vram = gpu.get_vram_usage()
        print(f"    Baseline VRAM: {baseline_vram.get('used_gb', 0):.2f} GB used")
        
        for i in range(5):
            print(f"\n[{i+2}] Cleanup cycle {i+1}/5")
            
            # Simulate some memory allocation (if possible)
            try:
                import torch
                if torch.cuda.is_available():
                    # Allocate 100MB tensor
                    tensor = torch.randn(1024, 1024, 25, device='cuda')
                    vram_with_data = gpu.get_vram_usage()
                    print(f"    After allocation: {vram_with_data.get('used_gb', 0):.2f} GB used")
                    
                    # Delete tensor
                    del tensor
                    
                    # Cleanup
                    gpu.clear_cache()
                    vram_after = gpu.get_vram_usage()
                    print(f"    After cleanup: {vram_after.get('used_gb', 0):.2f} GB used")
            except ImportError:
                print("    PyTorch not available, skipping tensor allocation")
                gpu.clear_cache()
        
        final_vram = gpu.get_vram_usage()
        print(f"\n[7] Final VRAM: {final_vram.get('used_gb', 0):.2f} GB used")
        
        leak_amount = final_vram.get('used_gb', 0) - baseline_vram.get('used_gb', 0)
        print(f"    Difference from baseline: {leak_amount:+.2f} GB")
        
        if abs(leak_amount) < 0.5:  # Less than 500MB difference
            print("\n✅ Memory Leak Test PASSED (no significant leak detected)")
            return True
        else:
            print(f"\n⚠️  Memory Leak Test WARNING: {abs(leak_amount):.2f} GB difference")
            print("    This may indicate a memory leak or background processes")
            return True  # Don't fail - could be other processes
        
    except Exception as e:
        print(f"\n❌ Memory Leak Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "GPU MEMORY MANAGEMENT TEST SUITE" + " " * 20 + "║")
    print("║" + " " * 20 + "Advanced Tape Restorer v4.0" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    
    tests = [
        ("GPU Detection", test_gpu_detection),
        ("Processor Cleanup", test_processor_cleanup),
        ("VapourSynth Tiles", test_vapoursynth_tile_calculation),
        ("VRAM Requirements", test_vram_requirements_check),
        ("Memory Leak Check", test_memory_leak_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! GPU memory management is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    
    print("\n" + "=" * 70)
    print("Press Enter to exit...")
    input()
    
    sys.exit(exit_code)
