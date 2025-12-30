"""
Disk Space Management for Advanced Tape Restorer v4.1
Prevents disk space exhaustion during frame extraction (GFPGAN, ProPainter)
"""

import shutil
import tempfile
from pathlib import Path
from typing import Tuple, Optional


def get_disk_space(path: str = None) -> Tuple[int, int, int]:
    """
    Get disk space information for a given path.
    
    Args:
        path: Directory path to check. If None, checks temp directory.
        
    Returns:
        Tuple of (total_bytes, used_bytes, free_bytes)
    """
    if path is None:
        path = tempfile.gettempdir()
    
    path = Path(path)
    
    # Ensure path exists
    if not path.exists():
        path = path.parent
    
    # Get disk usage stats
    stats = shutil.disk_usage(path)
    
    return (stats.total, stats.used, stats.free)


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable string.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def estimate_frame_extraction_size(
    video_path: str,
    duration_seconds: float = None,
    fps: float = None
) -> int:
    """
    Estimate disk space required for frame extraction.
    
    Assumptions:
    - PNG frames: ~15-30 MB per frame (HD), ~5-10 MB (SD)
    - Average: 20 MB per frame for safety
    
    Args:
        video_path: Path to input video
        duration_seconds: Video duration (if known)
        fps: Frames per second (if known)
        
    Returns:
        Estimated bytes required
    """
    try:
        from core import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        info = analyzer.get_video_info(video_path)
        
        # Get duration
        if duration_seconds is None:
            format_info = info.get('format', {})
            duration_seconds = float(format_info.get('duration', 0))
        
        # Get FPS
        if fps is None:
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    fps_str = stream.get('r_frame_rate', '30/1')
                    if '/' in fps_str:
                        num, denom = fps_str.split('/')
                        fps = float(num) / float(denom)
                    break
        
        if fps is None:
            fps = 30.0  # Default assumption
        
        # Get resolution for size estimation
        width = 1920  # Default assumption
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                width = stream.get('width', 1920)
                break
        
        # Calculate total frames
        total_frames = int(duration_seconds * fps)
        
        # Estimate size per frame based on resolution
        if width > 1920:  # 4K+
            bytes_per_frame = 30 * 1024 * 1024  # 30 MB
        elif width > 1280:  # HD
            bytes_per_frame = 20 * 1024 * 1024  # 20 MB
        else:  # SD
            bytes_per_frame = 8 * 1024 * 1024  # 8 MB
        
        estimated_size = total_frames * bytes_per_frame
        
        # Add 20% safety margin
        estimated_size = int(estimated_size * 1.2)
        
        return estimated_size
    
    except Exception as e:
        print(f"[DiskSpaceManager] Error estimating size: {e}")
        # Return conservative estimate: 1 hour of HD video
        return 100 * 1024 * 1024 * 1024  # 100 GB


def check_space_available(
    required_bytes: int,
    target_dir: str = None,
    min_free_gb: int = 5
) -> Tuple[bool, str]:
    """
    Check if sufficient disk space is available.
    
    Args:
        required_bytes: Required space in bytes
        target_dir: Directory to check. If None, checks temp directory.
        min_free_gb: Minimum GB to keep free after operation
        
    Returns:
        Tuple of (is_available, message)
    """
    try:
        total, used, free = get_disk_space(target_dir)
        
        # Calculate what we need
        min_free_bytes = min_free_gb * 1024 * 1024 * 1024
        needed_bytes = required_bytes + min_free_bytes
        
        if free < needed_bytes:
            return (
                False,
                f"Insufficient disk space!\n\n"
                f"Required: {format_bytes(required_bytes)}\n"
                f"Min free buffer: {format_bytes(min_free_bytes)}\n"
                f"Total needed: {format_bytes(needed_bytes)}\n"
                f"Available: {format_bytes(free)}\n"
                f"Shortfall: {format_bytes(needed_bytes - free)}\n\n"
                f"Free up space or select a different temporary directory."
            )
        
        # Warn if less than 20 GB will remain
        remaining_after = free - required_bytes
        if remaining_after < 20 * 1024 * 1024 * 1024:
            return (
                True,
                f"Warning: Low disk space after operation\n\n"
                f"Required: {format_bytes(required_bytes)}\n"
                f"Available: {format_bytes(free)}\n"
                f"Remaining after: {format_bytes(remaining_after)}\n\n"
                f"Continue anyway?"
            )
        
        return (
            True,
            f"Disk space check passed\n\n"
            f"Required: {format_bytes(required_bytes)}\n"
            f"Available: {format_bytes(free)}\n"
            f"Remaining after: {format_bytes(remaining_after)}"
        )
    
    except Exception as e:
        return (
            False,
            f"Error checking disk space: {str(e)}"
        )


def get_temp_directory_with_space(
    required_bytes: int,
    custom_dir: Optional[str] = None
) -> Tuple[Optional[Path], str]:
    """
    Get a temporary directory with sufficient space.
    
    Tries custom_dir first, then system temp, then common locations.
    
    Args:
        required_bytes: Required space in bytes
        custom_dir: Custom directory to try first
        
    Returns:
        Tuple of (path, message)
    """
    candidates = []
    
    # Add custom directory first
    if custom_dir:
        candidates.append(Path(custom_dir))
    
    # Add system temp
    candidates.append(Path(tempfile.gettempdir()))
    
    # Add common Windows temp locations
    if shutil.which('cmd'):  # Windows
        import os
        # Try user temp
        user_temp = os.getenv('TEMP') or os.getenv('TMP')
        if user_temp:
            candidates.append(Path(user_temp))
        
        # Try other drives
        for drive_letter in 'DEFGHIJKLMNOPQRSTUVWXYZ':
            temp_path = Path(f"{drive_letter}:\\Temp")
            if temp_path.exists():
                candidates.append(temp_path)
            
            # Try root of drive
            drive_root = Path(f"{drive_letter}:\\")
            if drive_root.exists():
                candidates.append(drive_root / "ATR_Temp")
    
    # Check each candidate
    for candidate in candidates:
        try:
            # Create if doesn't exist
            if not candidate.exists():
                candidate.mkdir(parents=True, exist_ok=True)
            
            # Check space
            _, _, free = get_disk_space(str(candidate))
            
            if free > required_bytes * 1.2:  # 20% safety margin
                return (
                    candidate,
                    f"Using: {candidate}\n"
                    f"Available: {format_bytes(free)}"
                )
        
        except Exception as e:
            continue
    
    return (
        None,
        f"No location found with {format_bytes(required_bytes)} available.\n"
        f"Please free up disk space or specify a custom directory."
    )


# CLI testing
if __name__ == "__main__":
    import sys
    
    print("=== Disk Space Manager Test ===")
    print()
    
    # Check system temp
    print("System Temp Directory:")
    total, used, free = get_disk_space()
    print(f"  Total: {format_bytes(total)}")
    print(f"  Used:  {format_bytes(used)}")
    print(f"  Free:  {format_bytes(free)}")
    print()
    
    # Estimate frame extraction for sample video
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"Estimating frame extraction size for: {video_path}")
        estimated = estimate_frame_extraction_size(video_path)
        print(f"  Estimated: {format_bytes(estimated)}")
        print()
        
        # Check if space available
        available, msg = check_space_available(estimated)
        print(msg)
        print()
        
        if not available:
            # Try to find alternative
            alt_dir, alt_msg = get_temp_directory_with_space(estimated)
            if alt_dir:
                print(f"Alternative location found:")
                print(f"  {alt_msg}")
            else:
                print(f"No alternative found:")
                print(f"  {alt_msg}")
