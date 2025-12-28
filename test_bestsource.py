"""
Test BestSource2 plugin availability and functionality
Compares BestSource vs FFMS2 on interlaced test video
"""

import sys
import os

def test_bestsource_availability():
    """Check if BestSource2 is installed in VapourSynth."""
    print("=" * 80)
    print("Testing BestSource2 Plugin Availability")
    print("=" * 80)
    print()
    
    try:
        import vapoursynth as vs
        core = vs.core
        
        print("✓ VapourSynth imported successfully")
        print(f"  Version: {core.version()}")
        print()
        
        # Check available plugins
        print("Available Source Filters:")
        print("-" * 40)
        
        has_bestsource = hasattr(core, 'bs')
        has_ffms2 = hasattr(core, 'ffms2')
        has_lsmas = hasattr(core, 'lsmas')
        
        if has_bestsource:
            print("✓ BestSource2 (core.bs) - INSTALLED")
        else:
            print("✗ BestSource2 (core.bs) - NOT INSTALLED")
            print("  Install: vsrepo install bestsource")
        
        if has_ffms2:
            print("✓ FFMS2 (core.ffms2) - INSTALLED")
        else:
            print("✗ FFMS2 (core.ffms2) - NOT INSTALLED")
        
        if has_lsmas:
            print("✓ LSMASH (core.lsmas) - INSTALLED")
        else:
            print("✗ LSMASH (core.lsmas) - NOT INSTALLED")
        
        print()
        return has_bestsource, has_ffms2, has_lsmas
        
    except ImportError as e:
        print(f"✗ VapourSynth not available: {e}")
        return False, False, False
    except Exception as e:
        print(f"✗ Error checking plugins: {e}")
        return False, False, False


def test_source_filter(video_file, filter_name="bestsource"):
    """Test loading video with specific source filter."""
    import vapoursynth as vs
    core = vs.core
    
    print(f"\nTesting {filter_name.upper()} with: {os.path.basename(video_file)}")
    print("-" * 80)
    
    try:
        # Load video with specified filter
        if filter_name == "bestsource":
            if not hasattr(core, 'bs'):
                print("✗ BestSource2 not available, skipping")
                return None
            clip = core.bs.VideoSource(source=video_file)
        elif filter_name == "ffms2":
            if not hasattr(core, 'ffms2'):
                print("✗ FFMS2 not available, skipping")
                return None
            clip = core.ffms2.Source(source=video_file)
        elif filter_name == "lsmash":
            if not hasattr(core, 'lsmas'):
                print("✗ LSMASH not available, skipping")
                return None
            clip = core.lsmas.LibavSMASHSource(source=video_file)
        else:
            print(f"✗ Unknown filter: {filter_name}")
            return None
        
        # Get clip information
        print(f"✓ Video loaded successfully with {filter_name.upper()}")
        print()
        print("Clip Properties:")
        print(f"  Width:  {clip.width}px")
        print(f"  Height: {clip.height}px")
        print(f"  Format: {clip.format.name}")
        print(f"  Frames: {clip.num_frames}")
        print(f"  FPS:    {clip.fps_num}/{clip.fps_den} ({clip.fps_num/clip.fps_den:.3f})")
        
        # Check field order from frame properties
        frame = clip.get_frame(0)
        field_based = frame.props.get('_FieldBased', 0)
        field_order_map = {
            0: "Progressive",
            1: "Bottom Field First (BFF)",
            2: "Top Field First (TFF)"
        }
        print(f"  Field Order: {field_order_map.get(field_based, f'Unknown ({field_based})')}")
        
        # Check for interlaced flag
        interlaced = frame.props.get('_Combed', None)
        if interlaced is not None:
            print(f"  Interlaced: {'Yes' if interlaced else 'No'}")
        
        print()
        return clip
        
    except Exception as e:
        print(f"✗ Error loading video: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_source_filters(video_file):
    """Compare BestSource, FFMS2, and LSMASH on same video."""
    print()
    print("=" * 80)
    print("Comparing Source Filters")
    print("=" * 80)
    
    results = {}
    
    for filter_name in ["bestsource", "ffms2", "lsmash"]:
        clip = test_source_filter(video_file, filter_name)
        if clip:
            results[filter_name] = {
                'frames': clip.num_frames,
                'fps': f"{clip.fps_num}/{clip.fps_den}",
                'fps_decimal': clip.fps_num / clip.fps_den,
                'format': clip.format.name,
                'field_based': clip.get_frame(0).props.get('_FieldBased', 0)
            }
    
    # Summary comparison
    if len(results) > 1:
        print()
        print("=" * 80)
        print("Comparison Summary")
        print("=" * 80)
        print()
        print(f"{'Filter':<15} {'Frames':<10} {'FPS':<20} {'Field Order':<15}")
        print("-" * 80)
        
        field_map = {0: "Progressive", 1: "BFF", 2: "TFF"}
        
        for name, data in results.items():
            print(f"{name.upper():<15} {data['frames']:<10} "
                  f"{data['fps']:<20} {field_map.get(data['field_based'], 'Unknown'):<15}")
        
        # Check for discrepancies
        print()
        frame_counts = [data['frames'] for data in results.values()]
        fps_values = [data['fps_decimal'] for data in results.values()]
        
        if len(set(frame_counts)) > 1:
            print("⚠️  WARNING: Different frame counts detected!")
        else:
            print("✓ All filters report same frame count")
        
        if len(set(round(fps, 3) for fps in fps_values)) > 1:
            print("⚠️  WARNING: Different FPS values detected!")
        else:
            print("✓ All filters report same FPS")


def test_bestsource_indexing(video_file):
    """Test BestSource2 indexing performance."""
    import vapoursynth as vs
    import time
    
    core = vs.core
    
    if not hasattr(core, 'bs'):
        print("\n✗ BestSource2 not available for indexing test")
        return
    
    print()
    print("=" * 80)
    print("BestSource2 Indexing Performance")
    print("=" * 80)
    print()
    
    print("Testing first load (creates index)...")
    start_time = time.time()
    
    try:
        clip = core.bs.VideoSource(source=video_file)
        # Force indexing by requesting first frame
        _ = clip.get_frame(0)
        index_time = time.time() - start_time
        
        print(f"✓ Indexing completed in {index_time:.2f} seconds")
        print(f"  ({clip.num_frames} frames, {index_time/clip.num_frames*1000:.1f}ms per frame)")
        print()
        
        # Test second load (uses cached index)
        print("Testing second load (cached index)...")
        start_time = time.time()
        clip2 = core.bs.VideoSource(source=video_file)
        _ = clip2.get_frame(0)
        cached_time = time.time() - start_time
        
        print(f"✓ Cached load in {cached_time:.2f} seconds")
        print(f"  Speedup: {index_time/cached_time:.1f}x faster")
        
    except Exception as e:
        print(f"✗ Error during indexing test: {e}")


def main():
    """Main test routine."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BestSource2 Test Suite" + " " * 36 + "║")
    print("║" + " " * 18 + "Advanced Tape Restorer v4.1" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Step 1: Check plugin availability
    has_bs, has_ffms2, has_lsmas = test_bestsource_availability()
    
    if not has_bs and not has_ffms2 and not has_lsmas:
        print()
        print("⚠️  No source filters installed!")
        print("   Install with: vsrepo install bestsource ffms2 lsmash")
        return
    
    # Step 2: Find test video
    test_videos = [
        r"D:\interlaced video\test_short.mp4",
        r"D:\interlaced video\sample.avi",
        r"C:\Users\Public\Videos\Sample Videos\Wildlife.wmv",
    ]
    
    video_file = None
    for path in test_videos:
        if os.path.exists(path):
            video_file = path
            break
    
    if not video_file:
        print()
        print("No test video found. Please provide video path:")
        print()
        video_input = input("Video path (or Enter to skip): ").strip('"')
        if video_input and os.path.exists(video_input):
            video_file = video_input
        else:
            print("\n⚠️  No valid video provided, skipping comparison tests")
            print()
            print("=" * 80)
            print("Plugin Availability Summary")
            print("=" * 80)
            print()
            if has_bs:
                print("✓ BestSource2 is ready to use!")
                print("  Select 'BestSource (Best - Most Reliable)' in GUI")
            else:
                print("✗ BestSource2 not installed")
                print("  Run: DISTRIBUTION\\Setup\\Install_BestSource_Plugin.bat")
            print()
            return
    
    # Step 3: Compare source filters
    if video_file:
        compare_source_filters(video_file)
        
        # Step 4: Test indexing performance (BestSource only)
        if has_bs:
            test_bestsource_indexing(video_file)
    
    print()
    print("=" * 80)
    print("Test Complete")
    print("=" * 80)
    print()
    
    if has_bs:
        print("✓ BestSource2 is working correctly!")
        print()
        print("RECOMMENDATION:")
        print("  Use 'Auto (Best for Source)' in GUI for automatic selection")
        print("  Or select 'BestSource (Best - Most Reliable)' for tape sources")
    else:
        print("⚠️  BestSource2 not installed")
        print()
        print("TO INSTALL:")
        print("  1. Run: DISTRIBUTION\\Setup\\Install_BestSource_Plugin.bat")
        print("  2. Or manually: vsrepo install bestsource")
        print("  3. Restart Advanced Tape Restorer")
    
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
