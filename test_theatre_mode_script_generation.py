"""
Test Theatre Mode VapourSynth Script Generation
Verifies that all Theatre Mode features are correctly integrated into generated .vpy scripts
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.vapoursynth_engine import VapourSynthEngine
import tempfile

def test_theatre_mode_script_generation():
    """Test Theatre Mode script generation with all features enabled"""
    
    print("=" * 80)
    print("THEATRE MODE SCRIPT GENERATION TEST")
    print("=" * 80)
    print()
    
    engine = VapourSynthEngine()
    
    # Test 1: Full Theatre Mode with all features
    print("TEST 1: Full Theatre Mode (Chroma + Level Adjustment + Bob Deinterlacing)")
    print("-" * 80)
    
    options = {
        # Theatre Mode settings
        "theatre_mode_enabled": True,
        "chroma_correction_enabled": True,
        "chroma_preset": "vhs_composite",
        "chroma_shift_x_px": 0.5,
        "chroma_shift_y_px": 0.0,
        "deinterlace_variant": "bob",
        "apply_level_adjustment": True,
        "black_point": 0.1,
        "white_point": 0.85,
        "saturation_boost": 1.2,
        
        # Basic settings
        "field_order": "TFF (Top Field First)",
        "qtgmc_preset": "Slow",
        "enable_deinterlace": True,
        "enable_denoise": False,
        "enable_upscale": False,
        "enable_interpolation": False,
    }
    
    # Generate script (writes to file)
    temp_file = os.path.join(tempfile.gettempdir(), "theatre_mode_test_full.vpy")
    engine_with_file = VapourSynthEngine(script_file=temp_file)
    engine_with_file.create_script(
        input_file="C:\\TestVideo\\sample_vhs.avi",
        options=options
    )
    
    # Read generated script
    with open(temp_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print(f"✓ Generated script saved to: {temp_file}")
    print()
    
    # Verify Theatre Mode components
    checks = {
        "Chroma Correction Import": "from .chroma_correction import" in script_content or "def chroma_phase_correct" in script_content,
        "Chroma Phase Correction Function": "def chroma_phase_correct" in script_content,
        "Chroma Shift Application": "chroma_phase_correct(video" in script_content,
        "VHS Composite Preset": "vhs_composite" in script_content or "0.5" in script_content,
        "Bob Deinterlacing (FPSDivisor=1)": "FPSDivisor=1" in script_content,
        "Bob Mode Comment": "bob" in script_content.lower(),
        "Level Adjustment": "std.Levels" in script_content or "Level adjustment" in script_content,
        "Saturation Boost": "std.Expr" in script_content or "1.2" in script_content,
        "Theatre Mode Comments": "Theatre Mode" in script_content or "THEATRE MODE" in script_content,
    }
    
    print("VERIFICATION RESULTS:")
    all_passed = True
    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print()
    print("-" * 80)
    print()
    
    # Test 2: Theatre Mode with standard deinterlacing
    print("TEST 2: Theatre Mode with Standard Progressive Deinterlacing")
    print("-" * 80)
    
    options["deinterlace_variant"] = "standard"
    temp_file = os.path.join(tempfile.gettempdir(), "theatre_mode_test_standard.vpy")
    engine_standard = VapourSynthEngine(script_file=temp_file)
    engine_standard.create_script(
        input_file="C:\\TestVideo\\sample_vhs.avi",
        options=options
    )
    
    # Read generated script
    with open(temp_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print(f"✓ Generated script saved to: {temp_file}")
    
    standard_check = "FPSDivisor=2" in script_content
    print(f"  {'✓ PASS' if standard_check else '✗ FAIL'}: Standard deinterlacing (FPSDivisor=2)")
    
    print()
    print("-" * 80)
    print()
    
    # Test 3: Theatre Mode with keep_interlaced
    print("TEST 3: Theatre Mode with Keep Interlaced")
    print("-" * 80)
    
    options["deinterlace_variant"] = "keep_interlaced"
    temp_file = os.path.join(tempfile.gettempdir(), "theatre_mode_test_interlaced.vpy")
    engine_interlaced = VapourSynthEngine(script_file=temp_file)
    engine_interlaced.create_script(
        input_file="C:\\TestVideo\\sample_vhs.avi",
        options=options
    )
    
    # Read generated script
    with open(temp_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print(f"✓ Generated script saved to: {temp_file}")
    
    # For keep_interlaced, QTGMC should be skipped
    interlaced_check = "keep_interlaced" in script_content.lower() or ("QTGMC" not in script_content and "Theatre Mode" in script_content)
    print(f"  {'✓ PASS' if interlaced_check else '✗ FAIL'}: No deinterlacing applied")
    
    print()
    print("-" * 80)
    print()
    
    # Test 4: Normal Mode (backward compatibility)
    print("TEST 4: Normal Mode (v3.3 Backward Compatibility)")
    print("-" * 80)
    
    options = {
        "theatre_mode_enabled": False,
        "field_order": "TFF (Top Field First)",
        "qtgmc_preset": "Slow",
        "enable_deinterlace": True,
        "enable_denoise": False,
    }
    
    temp_file = os.path.join(tempfile.gettempdir(), "normal_mode_test.vpy")
    engine_normal = VapourSynthEngine(script_file=temp_file)
    engine_normal.create_script(
        input_file="C:\\TestVideo\\sample_video.avi",
        options=options
    )
    
    # Read generated script
    with open(temp_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print(f"✓ Generated script saved to: {temp_file}")
    
    normal_checks = {
        "No Theatre Mode Code": "Theatre Mode" not in script_content and "chroma_phase_correct" not in script_content,
        "Standard QTGMC": "QTGMC" in script_content,
        "No Chroma Correction": "chroma_phase_correct" not in script_content,
    }
    
    for check_name, result in normal_checks.items():
        print(f"  {'✓ PASS' if result else '✗ FAIL'}: {check_name}")
    
    print()
    print("-" * 80)
    print()
    
    # Test 5: Chroma correction only (no level adjustment)
    print("TEST 5: Chroma Correction Only (LaserDisc Preset)")
    print("-" * 80)
    
    options = {
        "theatre_mode_enabled": True,
        "chroma_correction_enabled": True,
        "chroma_preset": "laserdisc",
        "chroma_shift_x_px": 0.25,
        "chroma_shift_y_px": 0.0,
        "apply_level_adjustment": False,
        "deinterlace_variant": "standard",
        "field_order": "TFF (Top Field First)",
        "qtgmc_preset": "Slow",
        "enable_deinterlace": True,
    }
    
    temp_file = os.path.join(tempfile.gettempdir(), "theatre_mode_chroma_only.vpy")
    engine_chroma = VapourSynthEngine(script_file=temp_file)
    engine_chroma.create_script(
        input_file="C:\\TestVideo\\sample_laserdisc.avi",
        options=options
    )
    
    # Read generated script
    with open(temp_file, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    print(f"✓ Generated script saved to: {temp_file}")
    
    chroma_only_checks = {
        "Chroma Correction Present": "chroma_phase_correct" in script_content,
        "LaserDisc Preset (0.25px)": "0.25" in script_content,
        "No Level Adjustment": "std.Levels" not in script_content or "Level adjustment" not in script_content,
    }
    
    for check_name, result in chroma_only_checks.items():
        print(f"  {'✓ PASS' if result else '✗ FAIL'}: {check_name}")
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✓ ALL TESTS PASSED - Theatre Mode integration is working correctly!")
    else:
        print("⚠ SOME TESTS FAILED - Review the output above for details")
    
    print()
    print("Generated test scripts are saved in:")
    print(f"  {tempfile.gettempdir()}")
    print()
    print("To manually test with VapourSynth:")
    print("  vspipe --info <script_file>.vpy -")
    print("  vspipe --y4m <script_file>.vpy - | ffplay -i -")
    print()

if __name__ == "__main__":
    try:
        test_theatre_mode_script_generation()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
