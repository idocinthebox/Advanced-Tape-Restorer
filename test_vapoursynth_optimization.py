"""
Test suite for optimized vapoursynth_engine.py (v3.3)
Verifies all functionality remains intact after optimization
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.vapoursynth_engine import VapourSynthEngine

def test_instantiation():
    """Test class can be instantiated"""
    print("TEST 1: Class Instantiation")
    vs = VapourSynthEngine()
    assert vs.script_file == "temp_restoration_script.vpy"
    assert vs.log_callback is None
    print("  ✅ PASSED - Class instantiates correctly")
    return True

def test_custom_callback():
    """Test custom log callback"""
    print("\nTEST 2: Custom Log Callback")
    messages = []
    vs = VapourSynthEngine(log_callback=lambda msg: messages.append(msg))
    vs._log("Test message")
    assert len(messages) == 1
    assert messages[0] == "Test message"
    print("  ✅ PASSED - Log callback works")
    return True

def test_script_generation():
    """Test VapourSynth script generation"""
    print("\nTEST 3: Script Generation")
    
    # Create a minimal test script
    vs = VapourSynthEngine(script_file="test_temp_script.vpy")
    
    test_options = {
        "field_order": "TFF (Top Field First)",
        "qtgmc_preset": "Fast",
        "crop_top": 0,
        "crop_bottom": 0,
        "crop_left": 0,
        "crop_right": 0,
        "use_ai_upscaling": False,
        "ai_interpolation": False,
        "frame_rate": "Keep Original"
    }
    
    try:
        vs.create_script("C:\\test_video.mp4", test_options)
        
        # Verify script was created
        assert os.path.exists("test_temp_script.vpy"), "Script file not created"
        
        # Read and verify script content
        with open("test_temp_script.vpy", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for key elements
        assert "import vapoursynth as vs" in content
        assert "core = vs.core" in content
        assert "QTGMC" in content
        assert "video.set_output()" in content
        
        print("  ✅ PASSED - Script generated correctly")
        
        # Cleanup
        os.remove("test_temp_script.vpy")
        if os.path.exists("last_generated_script.vpy"):
            os.remove("last_generated_script.vpy")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        # Cleanup on failure
        try:
            if os.path.exists("test_temp_script.vpy"):
                os.remove("test_temp_script.vpy")
        except:
            pass
        return False

def test_crop_filter():
    """Test crop filter generation"""
    print("\nTEST 4: Crop Filter")
    vs = VapourSynthEngine()
    
    # Test with crops
    options = {"crop_top": 10, "crop_bottom": 10, "crop_left": 5, "crop_right": 5}
    result = vs._generate_crop_filter(options)
    assert len(result) == 1, "Should return 1 line with crops"
    assert "Crop" in result[0]
    
    # Test without crops
    options_no_crop = {"crop_top": 0, "crop_bottom": 0, "crop_left": 0, "crop_right": 0}
    result_empty = vs._generate_crop_filter(options_no_crop)
    assert len(result_empty) == 0, "Should return empty list without crops"
    
    print("  ✅ PASSED - Crop filter optimized correctly")
    return True

def test_deinterlace_filter():
    """Test deinterlace filter generation"""
    print("\nTEST 5: Deinterlace Filter")
    vs = VapourSynthEngine()
    
    # Test TFF
    options_tff = {"field_order": "TFF (Top Field First)", "qtgmc_preset": "Medium"}
    result = vs._generate_deinterlace_filter(options_tff)
    assert len(result) == 1
    assert "QTGMC" in result[0]
    assert "TFF=True" in result[0]
    
    # Test disabled
    options_disabled = {"field_order": "Disabled (Progressive)"}
    result_disabled = vs._generate_deinterlace_filter(options_disabled)
    assert len(result_disabled) == 0
    
    print("  ✅ PASSED - Deinterlace filter works")
    return True

def test_source_filter():
    """Test source filter generation"""
    print("\nTEST 6: Source Filter")
    vs = VapourSynthEngine()
    
    # Test auto-detect AVI
    options_auto = {"source_filter": "Auto"}
    result_avi = vs._generate_source_filter("test.avi", options_auto)
    assert any("ffms2" in line for line in result_avi)
    
    # Test bestsource
    options_bs = {"source_filter": "bestsource"}
    result_bs = vs._generate_source_filter("test.mp4", options_bs)
    assert any("bs.VideoSource" in line for line in result_bs)
    
    print("  ✅ PASSED - Source filter selection works")
    return True

def test_framerate_filter():
    """Test framerate filter generation"""
    print("\nTEST 7: Framerate Filter")
    vs = VapourSynthEngine()
    
    # Test with keep original + deinterlace
    options = {"field_order": "TFF (Top Field First)", "frame_rate": "Keep Original"}
    result = vs._generate_framerate_filter(options)
    assert len(result) == 1
    assert "SelectEven" in result[0]
    
    # Test progressive (no filter)
    options_prog = {"field_order": "Disabled (Progressive)", "frame_rate": "Keep Original"}
    result_prog = vs._generate_framerate_filter(options_prog)
    assert len(result_prog) == 0
    
    print("  ✅ PASSED - Framerate filter conditional works")
    return True

def test_ai_inpainting():
    """Test AI inpainting comment generation"""
    print("\nTEST 8: AI Inpainting")
    vs = VapourSynthEngine()
    
    # With inpainting
    options = {"ai_inpainting": True}
    result = vs._generate_ai_inpainting(options)
    assert len(result) == 1
    assert "ProPainter" in result[0]
    
    # Without inpainting
    options_no = {"ai_inpainting": False}
    result_no = vs._generate_ai_inpainting(options_no)
    assert len(result_no) == 0
    
    print("  ✅ PASSED - AI inpainting comment generation works")
    return True

def test_cleanup():
    """Test cleanup method"""
    print("\nTEST 9: Cleanup")
    
    # Create a test file
    test_file = "test_cleanup_script.vpy"
    with open(test_file, "w") as f:
        f.write("test")
    
    vs = VapourSynthEngine(script_file=test_file)
    vs.cleanup()
    
    assert not os.path.exists(test_file), "File should be deleted"
    print("  ✅ PASSED - Cleanup removes files correctly")
    return True

def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("  VAPOURSYNTH ENGINE v3.3 - OPTIMIZATION VERIFICATION")
    print("="*70)
    
    tests = [
        test_instantiation,
        test_custom_callback,
        test_script_generation,
        test_crop_filter,
        test_deinterlace_filter,
        test_source_filter,
        test_framerate_filter,
        test_ai_inpainting,
        test_cleanup
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
        print("🎉 ALL TESTS PASSED! Optimization is successful and functional.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review optimization.")
    print("="*70)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
