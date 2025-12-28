"""
Test GFPGAN temporary directory handling
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

print("=== GFPGAN Temp Directory Handler Test ===\n")

# Test 1: Default system temp directory
print("Test 1: Default system temp directory")
print(f"System temp: {tempfile.gettempdir()}")

temp_frames_dir = tempfile.mkdtemp(prefix='gfpgan_frames_')
temp_enhanced_dir = tempfile.mkdtemp(prefix='gfpgan_enhanced_')

print(f"✓ Created frames dir: {temp_frames_dir}")
print(f"✓ Created enhanced dir: {temp_enhanced_dir}")
print(f"  Both exist: {os.path.isdir(temp_frames_dir) and os.path.isdir(temp_enhanced_dir)}")

# Cleanup
shutil.rmtree(temp_frames_dir)
shutil.rmtree(temp_enhanced_dir)
print("✓ Cleaned up default temp directories\n")

# Test 2: Custom temp directory
print("Test 2: Custom temp directory")
custom_temp = Path.home() / "TestGFPGANTemp"
custom_temp.mkdir(exist_ok=True)

print(f"Custom temp: {custom_temp}")
print(f"Custom temp exists: {custom_temp.is_dir()}")

if custom_temp.is_dir():
    temp_frames_dir = tempfile.mkdtemp(prefix='gfpgan_frames_', dir=str(custom_temp))
    temp_enhanced_dir = tempfile.mkdtemp(prefix='gfpgan_enhanced_', dir=str(custom_temp))
    
    print(f"✓ Created frames dir: {temp_frames_dir}")
    print(f"✓ Created enhanced dir: {temp_enhanced_dir}")
    print(f"  Both in custom location: {str(custom_temp) in temp_frames_dir and str(custom_temp) in temp_enhanced_dir}")
    
    # Cleanup
    shutil.rmtree(temp_frames_dir)
    shutil.rmtree(temp_enhanced_dir)
    custom_temp.rmdir()
    print("✓ Cleaned up custom temp directories\n")
else:
    print("✗ Failed to create custom temp directory\n")

# Test 3: Disk space check
print("Test 3: Disk space check")
try:
    # Test on current drive
    current_drive = Path.cwd().drive or str(Path.cwd()).split(os.sep)[0]
    disk_usage = shutil.disk_usage(current_drive)
    
    total_gb = disk_usage.total / (1024**3)
    used_gb = disk_usage.used / (1024**3)
    free_gb = disk_usage.free / (1024**3)
    
    print(f"Drive: {current_drive}")
    print(f"Total: {total_gb:.2f} GB")
    print(f"Used: {used_gb:.2f} GB")
    print(f"Free: {free_gb:.2f} GB")
    
    # Simulate space check for 3240x2160 video (252 frames)
    width, height = 3240, 2160
    frame_count = 252
    bytes_per_pixel = 3
    raw_frame_size = width * height * bytes_per_pixel
    png_compression_ratio = 0.4
    estimated_frame_size_mb = (raw_frame_size * png_compression_ratio) / (1024 * 1024)
    estimated_total_gb = (estimated_frame_size_mb * frame_count * 2) / 1024
    
    print(f"\nEstimated space needed for {width}x{height} video ({frame_count} frames):")
    print(f"  Per frame: ~{estimated_frame_size_mb:.1f} MB")
    print(f"  Total (2x): ~{estimated_total_gb:.2f} GB")
    
    required_with_headroom = estimated_total_gb * 1.2
    if free_gb >= required_with_headroom:
        print(f"✓ Sufficient space available ({free_gb:.2f} GB > {required_with_headroom:.2f} GB)")
    else:
        print(f"⚠️ Low disk space ({free_gb:.2f} GB < {required_with_headroom:.2f} GB recommended)")
    
except Exception as e:
    print(f"✗ Disk space check failed: {e}")

print("\n=== Test Complete ===")
