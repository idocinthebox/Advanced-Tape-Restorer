"""
Advanced Tape Restorer v3.0 - Test Suite
Run tests for core and capture modules
"""

from capture import CaptureDeviceManager
from core import VideoProcessor, VideoAnalyzer, VapourSynthEngine, FFmpegEncoder
import sys
import os

from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_core_module(use_mocks=True):
    """Test core processing module."""
    print("=" * 60)
    print("TESTING CORE MODULE")
    print("=" * 60)

    # Test VideoProcessor initialization
    print("\n1. Testing VideoProcessor initialization...")
    try:
        processor = VideoProcessor()
        print("   ✓ VideoProcessor created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create VideoProcessor: {e}")
        assert False, f"Failed to create VideoProcessor: {e}"

    # Test VideoAnalyzer
    print("\n2. Testing VideoAnalyzer...")
    analyzer = VideoAnalyzer()
    print("   ✓ VideoAnalyzer created successfully")

    # Mock the subprocess call to simulate ffprobe output
    mock_ffprobe_output = (
        '{"streams":[{"codec_type":"video","width":720,"height":480}]}'
    )
    with patch(
        "subprocess.check_output", return_value=mock_ffprobe_output
    ) as mock_check_output:
        try:
            info = analyzer.get_video_info("dummy_video.mp4")
            assert info["streams"][0]["width"] == 720
            print("   ✓ get_video_info correctly parsed mocked ffprobe output")
        except Exception as e:
            print(f"   ✗ Failed to test get_video_info: {e}")
            assert False, "get_video_info test failed"

    # Test prerequisites check
    print("\n3. Testing prerequisites check...")
    if use_mocks:
        # Mock shutil.which to simulate that the tools exist
        with patch("shutil.which", side_effect=lambda cmd: f"/fake/path/to/{cmd}"):
            try:
                processor.check_prerequisites()
                print("   ✓ check_prerequisites passed with mocked dependencies")
            except RuntimeError as e:
                print(f"   ✗ check_prerequisites failed with mocked dependencies: {e}")
                assert False, "check_prerequisites failed with mocks"
    else:
        # Run the actual check if not using mocks
        processor.check_prerequisites()
        print("   ✓ check_prerequisites ran (result depends on environment)")

    # Test VapourSynthEngine
    print("\n4. Testing VapourSynthEngine...")
    try:
        VapourSynthEngine("test_script.vpy")
        print("   ✓ VapourSynthEngine created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create VapourSynthEngine: {e}")
        assert False, f"Failed to create VapourSynthEngine: {e}"

    # Test FFmpegEncoder
    print("\n5. Testing FFmpegEncoder...")
    try:
        encoder = FFmpegEncoder()
        print("   ✓ FFmpegEncoder created successfully")

        # Test command building
        test_options = {
            "codec": "libx264 (H.264, CPU)",
            "crf": "18",
            "ffmpeg_preset": "slow",
            "audio": "No Audio",
            "debug_logging": False,
        }
        cmd = encoder.build_command(
            "test.avi", "output.mp4", test_options, pipe_input=False
        )
        print(f"   ✓ FFmpeg command built: {len(cmd)} arguments")
    except Exception as e:
        print(f"   ✗ Failed FFmpegEncoder test: {e}")
        assert False, f"Failed FFmpegEncoder test: {e}"

    print("\n✅ Core module tests passed!")
    return True


def test_capture_module():
    """Test capture module."""
    print("\n" + "=" * 60)
    print("TESTING CAPTURE MODULE")
    print("=" * 60)

    # Test CaptureDeviceManager
    print("\n1. Testing CaptureDeviceManager...")
    try:
        manager = CaptureDeviceManager()
        print("   ✓ CaptureDeviceManager created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create CaptureDeviceManager: {e}")
        assert False, f"Failed to create CaptureDeviceManager: {e}"

    # Test device detection
    print("\n2. Testing device detection...")
    try:
        devices = manager.refresh_devices()
        print(f"   ✓ Device scan completed")
        print(f"   Found {len(devices)} device(s)")

        if devices:
            print("\n   Detected devices:")
            for device in devices:
                print(f"     - {device}")
        else:
            print(
                "   ⚠ No capture devices detected (this is okay if no hardware connected)"
            )
    except Exception as e:
        print(f"   ✗ Device detection failed: {e}")
        assert False, f"Device detection failed: {e}"

    # Test analog device filtering
    print("\n3. Testing device filtering...")
    try:
        analog_devices = manager.get_analog_devices()
        dv_devices = manager.get_dv_devices()
        print(f"   ✓ Analog devices: {len(analog_devices)}")
        print(f"   ✓ DV devices: {len(dv_devices)}")
    except Exception as e:
        print(f"   ✗ Device filtering failed: {e}")
        assert False, f"Device filtering failed: {e}"

    print("\n✅ Capture module tests passed!")
    return True


def test_api():
    """Test API examples from documentation."""
    print("\n" + "=" * 60)
    print("TESTING API EXAMPLES")
    print("=" * 60)

    # Test simple import
    print("\n1. Testing module imports...")
    try:
        from core import VideoProcessor
        from capture import CaptureDeviceManager

        print("   ✓ All modules imported successfully")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        assert False, f"Import failed: {e}"

    # Test API consistency
    print("\n2. Testing API method presence...")
    all_methods_found = True
    try:
        processor = VideoProcessor()
        methods = [
            "check_prerequisites",
            "process_video",
            "get_video_info",
            "request_stop",
            "cleanup",
        ]
        for method in methods:
            if not hasattr(processor, method):
                print(f"   ✗ VideoProcessor.{method}() missing")
                all_methods_found = False

        manager = CaptureDeviceManager()
        methods = ["refresh_devices", "get_analog_devices", "get_dv_devices"]
        for method in methods:
            if not hasattr(manager, method):
                print(f"   ✗ CaptureDeviceManager.{method}() missing")
                all_methods_found = False

        assert all_methods_found, "One or more API methods are missing."
        print("   ✓ All checked API methods are present.")
    except Exception as e:
        print(f"   ✗ API test failed: {e}")
        assert False, f"API test failed: {e}"

    print("\n✅ API tests passed!")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ADVANCED TAPE RESTORER v3.0 - TEST SUITE")
    print("=" * 60)

    results = []

    # Run tests, catching exceptions to allow all tests to run
    for name, test_func in [
        ("Core Module", test_core_module),
        ("Capture Module", test_capture_module),
        ("API", test_api),
    ]:
        try:
            if test_func():
                results.append((name, True))
            else:
                results.append((name, False))
        except Exception as e:
            print(f"\n--- ERROR IN {name} ---")
            print(f"{e}")
            print("-------------------------\n")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0
    else:
        print("SOME TESTS FAILED ❌")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
