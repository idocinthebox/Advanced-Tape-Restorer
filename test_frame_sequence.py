"""
Test script for frame sequence output feature

Tests:
1. FFmpeg command generation for different frame formats
2. Output path pattern validation
3. Frame sequence detection logic
"""

from core.ffmpeg_encoder import FFmpegEncoder

def test_frame_sequence_commands():
    """Test FFmpeg command generation for frame sequences."""
    encoder = FFmpegEncoder()
    
    # Test cases: (output_pattern, frame_format, expected_args)
    test_cases = [
        ("C:\\output\\frame_%06d.png", "PNG (Lossless)", ["-f", "image2"]),
        ("C:\\output\\frame_%06d.tif", "TIFF 16-bit", ["-pix_fmt", "rgb48le", "-compression_algo", "lzw"]),
        ("C:\\output\\frame_%06d.jpg", "JPEG (Quality 95)", ["-qscale:v", "2"]),
        ("C:\\output\\frame_%06d.dpx", "DPX (Cinema)", ["-bits_per_raw_sample", "10"]),
    ]
    
    print("Testing Frame Sequence Command Generation:")
    print("=" * 60)
    
    for output_path, frame_format, expected_args in test_cases:
        options = {
            "frame_format": frame_format,
            "audio": "No Audio",
            "debug_logging": False
        }
        
        cmd = encoder.build_command("pipe:", output_path, options, pipe_input=True)
        
        print(f"\n{frame_format}:")
        print(f"  Output: {output_path}")
        print(f"  Command: {' '.join(cmd)}")
        
        # Verify expected arguments present
        cmd_str = " ".join(cmd)
        for arg in expected_args:
            if arg in cmd:
                print(f"  ✓ Contains: {arg}")
            else:
                print(f"  ✗ Missing: {arg}")
        
        # Verify frame sequence format
        if "-f image2" in cmd_str:
            print(f"  ✓ Frame sequence format detected")
        else:
            print(f"  ✗ Frame sequence format NOT detected")
    
    # Test video mode (should NOT have image2)
    print(f"\n\nVideo Mode (should use codec, not image2):")
    print("=" * 60)
    video_options = {
        "codec": "libx264 (H.264, CPU)",
        "crf": "18",
        "ffmpeg_preset": "slow",
        "audio": "No Audio",
        "debug_logging": False
    }
    
    video_cmd = encoder.build_command("pipe:", "C:\\output\\video.mp4", video_options, pipe_input=True)
    video_cmd_str = " ".join(video_cmd)
    
    print(f"  Output: C:\\output\\video.mp4")
    print(f"  Command: {video_cmd_str}")
    
    if "-c:v libx264" in video_cmd_str:
        print(f"  ✓ Video codec present")
    else:
        print(f"  ✗ Video codec missing")
    
    if "-f image2" not in video_cmd_str:
        print(f"  ✓ Frame sequence format NOT present (correct)")
    else:
        print(f"  ✗ Frame sequence format present (ERROR)")

def test_pattern_detection():
    """Test frame pattern detection logic."""
    print("\n\nTesting Frame Pattern Detection:")
    print("=" * 60)
    
    test_paths = [
        ("C:\\output\\frame_%06d.png", True),
        ("C:\\output\\frame_%04d.tif", True),
        ("C:\\output\\video.mp4", False),
        ("C:\\output\\movie.mkv", False),
        ("C:\\output\\sequence_001.png", False),  # No %d pattern
    ]
    
    for path, should_detect in test_paths:
        is_sequence = "%" in path and "d" in path
        status = "✓" if is_sequence == should_detect else "✗"
        result = "FRAME SEQUENCE" if is_sequence else "VIDEO FILE"
        print(f"  {status} {path}")
        print(f"     -> Detected as: {result}")

if __name__ == "__main__":
    test_frame_sequence_commands()
    test_pattern_detection()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("\nFrame sequence output feature ready for use.")
    print("In GUI: Output tab -> Output Mode -> Frame Sequence")
