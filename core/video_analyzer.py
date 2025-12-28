"""
Video Analyzer - Metadata extraction and field order detection

Performance Optimizations:
- LRU cache for video metadata to avoid redundant ffprobe calls
- Pre-compiled regex patterns for faster field detection
- Module-level import optimization
- Extracted constants for magic numbers
- Optimized JSON parsing and error handling
"""

import json
import re
import subprocess
import sys
import traceback
from functools import lru_cache
from typing import Dict, Tuple

# Performance constants
DEFAULT_FPS = 25.0
DEFAULT_PAR = "1:1"
DEFAULT_TIMEOUT = 10
IDET_TIMEOUT = 30
MAX_CACHE_SIZE = 128  # Cache up to 128 video files

# Pre-compiled regex patterns for field detection (optimization: compile once)
REGEX_TFF = re.compile(r"Multi frame detection: TFF:\s*(\d+)")
REGEX_BFF = re.compile(r"BFF:\s*(\d+)")
REGEX_PROG = re.compile(r"Progressive:\s*(\d+)")


class VideoAnalyzer:
    """
    Analyze video files for metadata and field order.

    Optimizations:
    - Cached results for get_video_info and get_codec_info
    - Pre-compiled regex patterns
    - Streamlined error handling
    """

    @staticmethod
    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def get_video_info(input_file: str) -> Tuple[int, int, str, int, float]:
        """
        Get video information using ffprobe with LRU caching.

        Optimization: Results are cached to avoid redundant ffprobe calls

        Args:
            input_file: Path to video file

        Returns:
            tuple: (width, height, PAR, frame_count, fps)
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-show_entries", "format=duration",
                "-of", "json",
                input_file,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT
            )

            if result.returncode != 0:
                print(f"ffprobe error: {result.stderr}")
                return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS

            if not result.stdout.strip():
                print(f"ffprobe returned empty output for: {input_file}")
                return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS

            data = json.loads(result.stdout)

            if not data.get("streams"):
                print(f"No streams found in video file: {input_file}")
                return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS

            stream = data["streams"][0]
            width = stream.get("width", 0)
            height = stream.get("height", 0)

            # Parse frame rate (optimization: inline calculation)
            r_frame_rate = stream.get("r_frame_rate", f"{DEFAULT_FPS}/1")
            if "/" in r_frame_rate:
                num, den = map(float, r_frame_rate.split("/", 1))
                fps = num / den if den != 0 else DEFAULT_FPS
            else:
                fps = float(r_frame_rate)

            duration = float(data["format"].get("duration", 0))
            par_str = stream.get("sample_aspect_ratio", DEFAULT_PAR)
            frame_count = int(duration * fps) if duration > 0 else 0

            print(
                f"Video info: {width}x{height}, {fps:.2f}fps, "
                f"{duration:.1f}s, {frame_count} frames"
            )
            return width, height, par_str, frame_count, fps

        except subprocess.TimeoutExpired:
            print(f"Warning: ffprobe timeout for {input_file}")
            return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Could not parse video info: {e}")
            return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS
        except Exception as e:
            print(f"Warning: Could not get video info: {e}")
            traceback.print_exc()
            return 0, 0, DEFAULT_PAR, 0, DEFAULT_FPS

    @staticmethod
    def detect_field_order(
        input_file: str,
        probe_frames: int = 900,
        prog_dom_ratio: float = 1.5,
        prog_min: int = 150,
        field_dom_ratio: float = 1.3,
        field_min: int = 80,
        field_fallback_min: int = 200,
    ) -> str:
        """
        Auto-detect field order using FFmpeg idet filter.

        Optimizations:
        - Pre-compiled regex patterns
        - Early returns for efficiency
        - Streamlined logic flow

        Args:
            input_file: Path to video file
            probe_frames: Number of frames to analyze
            prog_dom_ratio: Progressive must be this ratio above interlaced sum
            prog_min: Minimum progressive frames required
            field_dom_ratio: Dominant field must be this ratio above other
            field_min: Minimum frames of dominant field required
            field_fallback_min: Minimum frames for fallback field selection

        Returns:
            str: 'TFF (Top Field First)', 'BFF (Bottom Field First)',
                 or 'Disabled (Progressive)'
        """
        try:
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-i", input_file,
                "-vf", f"idet,select='between(n\\,0\\,{probe_frames})'",
                "-f", "null",
                "-",
            ]

            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=IDET_TIMEOUT,
                creationflags=cflags
            )

            stderr = result.stderr

            # Parse idet statistics using pre-compiled regex (optimization)
            tff_match = REGEX_TFF.search(stderr)
            bff_match = REGEX_BFF.search(stderr)
            prog_match = REGEX_PROG.search(stderr)

            if not (tff_match and bff_match and prog_match):
                print("Could not parse idet output")
                return "TFF (Top Field First)"

            tff_count = int(tff_match.group(1))
            bff_count = int(bff_match.group(1))
            prog_count = int(prog_match.group(1))

            print(
                f"idet results: TFF={tff_count}, BFF={bff_count}, "
                f"Progressive={prog_count}"
            )

            # Check for progressive (optimization: early return)
            interlaced_sum = tff_count + bff_count
            if prog_count >= prog_min and prog_count > interlaced_sum * prog_dom_ratio:
                print("Detected: Progressive")
                return "Disabled (Progressive)"

            # Check for dominant field order (optimization: early returns)
            if tff_count > bff_count * field_dom_ratio and tff_count >= field_min:
                print("Detected: TFF")
                return "TFF (Top Field First)"

            if bff_count > tff_count * field_dom_ratio and bff_count >= field_min:
                print("Detected: BFF")
                return "BFF (Bottom Field First)"

            # Fallback: pick larger field if above threshold
            if tff_count >= field_fallback_min and tff_count > bff_count:
                print(f"Fallback: TFF (count={tff_count} >= {field_fallback_min})")
                return "TFF (Top Field First)"

            if bff_count >= field_fallback_min and bff_count > tff_count:
                print(f"Fallback: BFF (count={bff_count} >= {field_fallback_min})")
                return "BFF (Bottom Field First)"

            # Default
            print("Detection inconclusive, defaulting to TFF")
            return "TFF (Top Field First)"

        except subprocess.TimeoutExpired:
            print(f"Field order detection timeout for {input_file}")
            return "TFF (Top Field First)"
        except Exception as e:
            print(f"Field order detection failed: {e}")
            return "TFF (Top Field First)"

    @staticmethod
    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def get_codec_info(input_file: str) -> Dict[str, str]:
        """
        Get codec information from video file with LRU caching.

        Optimization: Results are cached to avoid redundant ffprobe calls

        Args:
            input_file: Path to video file

        Returns:
            dict: Codec information (codec_name, codec_long_name, pix_fmt)
        """
        default_info = {
            "codec_name": "unknown",
            "codec_long_name": "unknown",
            "pix_fmt": "unknown",
        }

        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,codec_long_name,pix_fmt",
                "-of", "json",
                input_file,
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT
            )

            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                if data.get("streams"):
                    stream = data["streams"][0]
                    return {
                        "codec_name": stream.get("codec_name", "unknown"),
                        "codec_long_name": stream.get("codec_long_name", "unknown"),
                        "pix_fmt": stream.get("pix_fmt", "unknown"),
                    }

        except subprocess.TimeoutExpired:
            print(f"Warning: ffprobe timeout for {input_file}")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Warning: Could not parse codec info: {e}")
        except Exception as e:
            print(f"Could not get codec info: {e}")

        return default_info

    @staticmethod
    def clear_cache():
        """
        Clear the LRU cache for video info and codec info.

        Useful when video files are modified or to free memory.
        """
        VideoAnalyzer.get_video_info.cache_clear()
        VideoAnalyzer.get_codec_info.cache_clear()
        print("VideoAnalyzer cache cleared")

    @staticmethod
    def get_cache_info() -> Dict[str, any]:
        """
        Get cache statistics for performance monitoring.

        Returns:
            dict: Cache statistics (hits, misses, size, maxsize)
        """
        video_info_cache = VideoAnalyzer.get_video_info.cache_info()
        codec_info_cache = VideoAnalyzer.get_codec_info.cache_info()

        return {
            "video_info": {
                "hits": video_info_cache.hits,
                "misses": video_info_cache.misses,
                "size": video_info_cache.currsize,
                "maxsize": video_info_cache.maxsize,
            },
            "codec_info": {
                "hits": codec_info_cache.hits,
                "misses": codec_info_cache.misses,
                "size": codec_info_cache.currsize,
                "maxsize": codec_info_cache.maxsize,
            },
        }
