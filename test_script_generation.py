"""
Test VapourSynth script generation with GPU optimization
Verifies that generated .vpy scripts contain correct GPU memory management
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_script_generation():
    """Test VapourSynth script generation with various configurations."""
    print("=" * 70)
    print("VapourSynth Script Generation Test")
    print("=" * 70)
    
    try:
        from core.vapoursynth_engine import VapourSynthEngine
        
        # Create temporary script file
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "test_restoration_script.vpy")
        
        # Mock input file (doesn't need to exist for script generation test)
        mock_input = "C:/test_input.avi"
        
        test_configs = [
            {
                "name": "Basic QTGMC + BM3D",
                "options": {
                    "use_qtgmc": True,
                    "qtgmc_preset": "Medium",
                    "field_order": "TFF",
                    "bm3d_enabled": True,
                    "bm3d_use_gpu": True,
                    "bm3d_sigma": 3.0,
                    "use_ai_upscaling": False,
                    "ai_interpolation": False,
                    "width": 1920,
                    "height": 1080,
                }
            },
            {
                "name": "RealESRGAN 4x Upscaling",
                "options": {
                    "use_qtgmc": True,
                    "qtgmc_preset": "Fast",
                    "field_order": "TFF",
                    "bm3d_enabled": False,
                    "use_ai_upscaling": True,
                    "ai_upscaling_method": "RealESRGAN",
                    "realesrgan_scale": "4x",
                    "ai_interpolation": False,
                    "width": 1920,
                    "height": 1080,
                }
            },
            {
                "name": "RIFE Frame Interpolation",
                "options": {
                    "use_qtgmc": True,
                    "qtgmc_preset": "Fast",
                    "field_order": "TFF",
                    "bm3d_enabled": False,
                    "use_ai_upscaling": False,
                    "ai_interpolation": True,
                    "interpolation_factor": "2x (30fps→60fps)",
                    "width": 1920,
                    "height": 1080,
                }
            },
            {
                "name": "All Features (Kitchen Sink)",
                "options": {
                    "use_qtgmc": True,
                    "qtgmc_preset": "Medium",
                    "field_order": "TFF",
                    "bm3d_enabled": True,
                    "bm3d_use_gpu": True,
                    "bm3d_sigma": 2.5,
                    "use_ai_upscaling": True,
                    "ai_upscaling_method": "RealESRGAN",
                    "realesrgan_scale": "4x",
                    "ai_interpolation": True,
                    "interpolation_factor": "2x (30fps→60fps)",
                    "width": 1920,
                    "height": 1080,
                }
            }
        ]
        
        for config in test_configs:
            print(f"\n{'=' * 70}")
            print(f"Testing: {config['name']}")
            print('=' * 70)
            
            # Create engine
            vs_engine = VapourSynthEngine(script_file=script_path, log_callback=print)
            
            # Generate script
            print("\n[1] Generating VapourSynth script...")
            vs_engine.create_script(mock_input, config['options'])
            
            # Read and verify script
            print("\n[2] Verifying generated script...")
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Check for critical components
            checks = [
                ("Import VapourSynth", "import vapoursynth as vs" in script_content),
                ("Core initialization", "core = vs.core" in script_content),
                ("Video source", "core.ffms2.Source" in script_content or "video = core.std.BlankClip" in script_content),
                ("Final output", "video.set_output()" in script_content),
            ]
            
            # Configuration-specific checks
            if config['options'].get('use_qtgmc'):
                checks.append(("QTGMC deinterlacing", "havsfunc.QTGMC" in script_content or "QTGMC" in script_content))
            
            if config['options'].get('bm3d_enabled'):
                checks.append(("BM3D denoising", "bm3dcuda" in script_content or "BM3D" in script_content))
            
            if config['options'].get('use_ai_upscaling'):
                checks.append(("RealESRGAN upscaling", "realesrgan" in script_content.lower()))
            
            if config['options'].get('ai_interpolation'):
                checks.append(("RIFE interpolation", "rife" in script_content.lower()))
            
            # Memory optimization checks
            checks.append(("Memory limit set", "core.max_cache_size" in script_content))
            
            # Print check results
            all_passed = True
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"    {status} {check_name}")
                if not check_result:
                    all_passed = False
            
            # Show script snippet
            print(f"\n[3] Script preview (first 30 lines):")
            print("-" * 70)
            lines = script_content.split('\n')[:30]
            for i, line in enumerate(lines, 1):
                print(f"{i:3d} | {line}")
            if len(script_content.split('\n')) > 30:
                print(f"... ({len(script_content.split('\n')) - 30} more lines)")
            print("-" * 70)
            
            if all_passed:
                print(f"\n✅ {config['name']} script generation PASSED")
            else:
                print(f"\n❌ {config['name']} script generation FAILED (missing components)")
                return False
        
        print("\n" + "=" * 70)
        print("✅ All script generation tests PASSED")
        print("=" * 70)
        
        # Cleanup
        if os.path.exists(script_path):
            os.remove(script_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Script generation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tile_size_in_script():
    """Test that optimal tile sizes are correctly embedded in scripts."""
    print("\n" + "=" * 70)
    print("Tile Size Optimization in Generated Scripts")
    print("=" * 70)
    
    try:
        from core.vapoursynth_engine import VapourSynthEngine
        
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "test_tile_optimization.vpy")
        
        mock_input = "C:/test_input.avi"
        
        # Test with RealESRGAN to verify tile optimization
        options = {
            "use_qtgmc": True,
            "qtgmc_preset": "Fast",
            "field_order": "TFF",
            "use_ai_upscaling": True,
            "ai_upscaling_method": "RealESRGAN",
            "realesrgan_scale": "4x",
            "width": 1920,
            "height": 1080,
        }
        
        print("\n[1] Generating script with RealESRGAN...")
        vs_engine = VapourSynthEngine(script_file=script_path, log_callback=print)
        vs_engine.create_script(mock_input, options)
        
        print("\n[2] Checking for tile size optimization...")
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Look for tile_w and tile_h parameters
        has_tile_params = "tile_w=" in script_content or "tile=" in script_content
        
        if has_tile_params:
            print("    ✅ Tile size parameters found in script")
            
            # Extract tile size from script
            for line in script_content.split('\n'):
                if 'tile' in line.lower() and ('=' in line or ':' in line):
                    print(f"    Found: {line.strip()}")
        else:
            print("    ⚠️  No explicit tile parameters (using defaults)")
        
        print("\n[3] Checking for memory optimization...")
        has_memory_limit = "max_cache_size" in script_content
        
        if has_memory_limit:
            print("    ✅ Memory cache limit set")
            for line in script_content.split('\n'):
                if 'max_cache_size' in line:
                    print(f"    Found: {line.strip()}")
        else:
            print("    ❌ No memory cache limit found")
            return False
        
        print("\n✅ Tile size optimization test PASSED")
        
        # Cleanup
        if os.path.exists(script_path):
            os.remove(script_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Tile size test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all script generation tests."""
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "VAPOURSYNTH SCRIPT GENERATION TEST" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝\n")
    
    tests = [
        ("Script Generation", test_script_generation),
        ("Tile Optimization", test_tile_size_in_script),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
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
        print("\n🎉 All script generation tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    
    print("\n" + "=" * 70)
    print("Press Enter to exit...")
    input()
    
    sys.exit(exit_code)
