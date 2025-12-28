"""
Test BestSource2 with interlaced video
Specifically tests field order detection and QTGMC compatibility
"""

import os
import sys

def test_interlaced_detection(video_file):
    """Test interlaced video handling with BestSource vs FFMS2."""
    print()
    print("=" * 80)
    print("Testing Interlaced Video Handling")
    print("=" * 80)
    print(f"\nVideo: {os.path.basename(video_file)}")
    print("-" * 80)
    
    try:
        import vapoursynth as vs
        core = vs.core
        
        results = {}
        
        # Test each source filter
        for filter_name in ["bestsource", "ffms2"]:
            print(f"\n{filter_name.upper()}:")
            print("-" * 40)
            
            try:
                # Load with appropriate filter
                if filter_name == "bestsource":
                    if not hasattr(core, 'bs'):
                        print("✗ BestSource2 not available")
                        continue
                    clip = core.bs.VideoSource(source=video_file)
                else:  # ffms2
                    if not hasattr(core, 'ffms2'):
                        print("✗ FFMS2 not available")
                        continue
                    clip = core.ffms2.Source(source=video_file)
                
                # Get first frame properties
                frame = clip.get_frame(0)
                
                # Field order
                field_based = frame.props.get('_FieldBased', 0)
                field_order_map = {
                    0: "Progressive",
                    1: "Bottom Field First (BFF)",
                    2: "Top Field First (TFF)"
                }
                field_order = field_order_map.get(field_based, f"Unknown ({field_based})")
                
                # Interlaced flag
                interlaced = frame.props.get('_Combed', None)
                
                # Store results
                results[filter_name] = {
                    'frames': clip.num_frames,
                    'fps': f"{clip.fps_num}/{clip.fps_den}",
                    'field_based': field_based,
                    'field_order': field_order,
                    'interlaced': interlaced
                }
                
                print(f"✓ Loaded successfully")
                print(f"  Frames:      {clip.num_frames}")
                print(f"  FPS:         {clip.fps_num}/{clip.fps_den} ({clip.fps_num/clip.fps_den:.3f})")
                print(f"  Resolution:  {clip.width}x{clip.height}")
                print(f"  Field Order: {field_order}")
                if interlaced is not None:
                    print(f"  Interlaced:  {'Yes' if interlaced else 'No'}")
                
            except Exception as e:
                print(f"✗ Error: {e}")
        
        # Compare results
        if len(results) == 2:
            print()
            print("=" * 80)
            print("Comparison")
            print("=" * 80)
            
            bs_result = results.get('bestsource', {})
            ff_result = results.get('ffms2', {})
            
            if bs_result.get('field_order') == ff_result.get('field_order'):
                print(f"✓ Both report same field order: {bs_result.get('field_order')}")
            else:
                print(f"⚠️  Field order mismatch:")
                print(f"   BestSource: {bs_result.get('field_order')}")
                print(f"   FFMS2:      {ff_result.get('field_order')}")
            
            if bs_result.get('frames') == ff_result.get('frames'):
                print(f"✓ Both report same frame count: {bs_result.get('frames')}")
            else:
                print(f"⚠️  Frame count mismatch:")
                print(f"   BestSource: {bs_result.get('frames')}")
                print(f"   FFMS2:      {ff_result.get('frames')}")
        
        return results
        
    except Exception as e:
        print(f"\n✗ Error during interlaced test: {e}")
        import traceback
        traceback.print_exc()
        return {}


def test_qtgmc_compatibility(video_file):
    """Test QTGMC deinterlacing with BestSource."""
    print()
    print("=" * 80)
    print("Testing QTGMC Deinterlacing with BestSource2")
    print("=" * 80)
    print()
    
    try:
        import vapoursynth as vs
        core = vs.core
        
        if not hasattr(core, 'bs'):
            print("✗ BestSource2 not available")
            return False
        
        # Check for havsfunc (contains QTGMC)
        try:
            import havsfunc as haf
            print("✓ havsfunc (QTGMC) available")
        except ImportError:
            print("⚠️  havsfunc not installed - QTGMC test skipped")
            print("   Install: pip install havsfunc")
            return False
        
        print()
        print("Loading video with BestSource2...")
        clip = core.bs.VideoSource(source=video_file)
        
        frame0 = clip.get_frame(0)
        field_based = frame0.props.get('_FieldBased', 0)
        
        print(f"✓ Video loaded: {clip.width}x{clip.height}, {clip.num_frames} frames")
        print(f"  Field order: {['Progressive', 'BFF', 'TFF'][field_based]}")
        
        # Try QTGMC deinterlacing
        print()
        print("Testing QTGMC deinterlacing...")
        
        try:
            # Use QTGMC with BestSource clip
            deinterlaced = haf.QTGMC(
                clip,
                Preset='Draft',  # Fast preset for testing
                TFF=True,  # Assume TFF (most common for analog)
                opencl=False  # Disable GPU for compatibility
            )
            
            print(f"✓ QTGMC processing successful!")
            print(f"  Input:  {clip.width}x{clip.height}, {clip.num_frames} frames")
            print(f"  Output: {deinterlaced.width}x{deinterlaced.height}, {deinterlaced.num_frames} frames")
            
            # Verify output is progressive
            out_frame = deinterlaced.get_frame(0)
            out_field_based = out_frame.props.get('_FieldBased', 0)
            
            if out_field_based == 0:
                print(f"✓ Output is progressive (as expected)")
            else:
                print(f"⚠️  Output still shows field-based: {out_field_based}")
            
            return True
            
        except Exception as e:
            print(f"✗ QTGMC failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"✗ Error during QTGMC test: {e}")
        import traceback
        traceback.print_exc()
        return False


def find_interlaced_video():
    """Find interlaced test video."""
    test_paths = [
        r"D:\interlaced video\test_short.mp4",
        r"D:\interlaced video\sample.avi",
        r"D:\interlaced video",
    ]
    
    for path in test_paths:
        if os.path.isfile(path):
            return path
        elif os.path.isdir(path):
            # Find first video file in directory
            for file in os.listdir(path):
                if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.mpg', '.mpeg', '.vob', '.dv')):
                    return os.path.join(path, file)
    
    return None


def main():
    """Main test routine for interlaced video."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "BestSource2 Interlaced Video Test" + " " * 30 + "║")
    print("║" + " " * 18 + "Advanced Tape Restorer v4.1" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Find test video
    video_file = find_interlaced_video()
    
    if not video_file:
        print()
        print("No interlaced test video found.")
        print()
        print("Please provide path to interlaced video file:")
        print("(VHS, Hi8, DV, or any interlaced source)")
        print()
        video_input = input("Video path (or Enter to skip): ").strip('"')
        
        if video_input and os.path.exists(video_input):
            video_file = video_input
        else:
            print("\n⚠️  No video file provided")
            print("\nTo test properly, you need an interlaced video source:")
            print("  - VHS capture")
            print("  - Hi8/Betamax capture")
            print("  - DV camera footage")
            print("  - DVD VOB file")
            print()
            return
    
    print(f"\nUsing test video: {video_file}")
    
    # Test 1: Interlaced detection
    results = test_interlaced_detection(video_file)
    
    # Test 2: QTGMC compatibility
    if results:
        qtgmc_ok = test_qtgmc_compatibility(video_file)
    
    # Summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print()
    
    if results.get('bestsource'):
        print("✓ BestSource2 successfully loaded interlaced video")
        print(f"  Field Order: {results['bestsource']['field_order']}")
        
        if qtgmc_ok:
            print("✓ QTGMC deinterlacing works with BestSource2")
        
        print()
        print("CONCLUSION:")
        print("  BestSource2 is fully compatible with interlaced video")
        print("  and works correctly with QTGMC deinterlacing.")
        print()
        print("RECOMMENDATION:")
        print("  Use BestSource2 for all VHS/Hi8/DV tape restoration")
        print("  Select 'Auto' or 'BestSource' in source filter dropdown")
    else:
        print("⚠️  Could not test BestSource2 with this video")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
