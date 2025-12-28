"""
FFmpeg Encoder - Video encoding with multiple codec support

Performance Optimizations:
- Pre-compiled regex patterns for faster progress parsing
- Immutable codec config dictionary (module-level constant)
- __slots__ for reduced memory footprint
- Efficient string formatting with f-strings
- Reduced subprocess overhead
"""

import subprocess
import re
import sys
import datetime
from typing import Callable, Optional, List
from pathlib import Path

# Pre-compiled regex for faster progress parsing
_PROGRESS_REGEX = re.compile(r"frame=\s*(\d+)\s+fps=\s*([\d\.]+)")
_BITRATE_REGEX = re.compile(r"^\d{2,3}k$")

# Module-level codec configurations (immutable, shared across instances)
_CODEC_CONFIGS = {
    "libx264 (H.264, CPU)": ["-c:v", "libx264", "-crf", "{crf}", "-preset", "{preset}"],
    "libx265 (H.265, CPU)": ["-c:v", "libx265", "-crf", "{crf}", "-preset", "{preset}"],
    "h264_nvenc (NVIDIA H.264)": ["-c:v", "h264_nvenc", "-cq", "{crf}", "-preset", "{preset}"],
    "hevc_nvenc (NVIDIA H.265)": ["-c:v", "hevc_nvenc", "-cq", "{crf}", "-preset", "{preset}"],
    "libsvtav1 (AV1)": ["-c:v", "libsvtav1", "-crf", "{crf}", "-preset", "{preset}"],
    "ProRes 4444 XQ": ["-c:v", "prores_ks", "-profile:v", "5", "-pix_fmt", "yuv444p10le"],
    "ProRes 4444": ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuv444p10le"],
    "ProRes 422 (HQ)": ["-c:v", "prores_ks", "-profile:v", "3"],
    "ProRes 422": ["-c:v", "prores_ks", "-profile:v", "2"],
    "ProRes 422 (LT)": ["-c:v", "prores_ks", "-profile:v", "1"],
    "ProRes 422 (Proxy)": ["-c:v", "prores_ks", "-profile:v", "0"],
    "DNxHD 175": ["-c:v", "dnxhd", "-b:v", "175M"],
    "FFV1 (Lossless)": ["-c:v", "ffv1", "-level", "3", "-g", "1"],
}

# Benign warning patterns to filter (tuple for fast membership check)
_BENIGN_WARNINGS = (
    "codec frame size is not set",
    "Error during demuxing: Invalid data found",
    "Unknown cover type:",
)


class FFmpegEncoder:
    """
    Handle FFmpeg encoding with progress monitoring.
    
    Optimizations:
    - __slots__ for memory efficiency
    - Pre-compiled regex patterns
    - Module-level codec configs
    """
    
    __slots__ = ('process', 'progress_callback', 'log_callback', 'last_logged_frame')
    
    # Expose codec configs as class variable (backward compatibility)
    CODEC_CONFIGS = _CODEC_CONFIGS

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.progress_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None
        self.last_logged_frame: int = 0

    def build_command(
        self,
        input_source: str,
        output_file: str,
        options: dict,
        pipe_input: bool = True,
        original_file: Optional[str] = None,
    ) -> List[str]:
        """
        Build FFmpeg command from options.
        
        Optimization: Efficient list building, reduced string operations
        """
        codec = options.get("codec", "libx264 (H.264, CPU)")
        crf = str(options.get("crf", "18"))
        preset = options.get("ffmpeg_preset", "slow")

        # Check if output is frame sequence (contains %d pattern)
        is_frame_sequence = "%" in output_file and "d" in output_file
        
        # Build command efficiently
        log_level = "info" if options.get("debug_logging") else "warning"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", log_level, "-stats"]

        # Input handling
        if pipe_input:
            cmd.extend(["-f", "yuv4mpegpipe", "-i", "pipe:"])
        else:
            cmd.extend(["-i", input_source])

        # Frame sequence: Skip audio and codec, use image format
        if is_frame_sequence:
            # Get frame format from options
            frame_format = options.get("frame_format", "PNG (Lossless)")
            
            if "TIFF" in frame_format:
                # TIFF 16-bit output
                cmd.extend([
                    "-pix_fmt", "rgb48le",  # 16-bit RGB
                    "-compression_algo", "lzw"  # Lossless compression
                ])
            elif "JPEG" in frame_format:
                # JPEG output with high quality
                cmd.extend([
                    "-qscale:v", "2"  # Quality 2 = ~95% quality
                ])
            elif "DPX" in frame_format:
                # DPX 10-bit cinema format
                cmd.extend([
                    "-pix_fmt", "rgb48le",  # 16-bit for conversion
                    "-bits_per_raw_sample", "10"
                ])
            # PNG uses default settings (lossless, good compression)
            
            # Frame sequence always uses image2 format, no audio
            cmd.extend(["-f", "image2", "-start_number", "0"])
            cmd.extend(["-y", output_file])
            return cmd
        
        # Audio handling (optimized with early returns and minimal branching)
        audio_mode = options.get("audio", "Copy Audio")
        if audio_mode in ("Copy Audio", "Re-encode Audio"):
            audio_source = original_file if (pipe_input and original_file) else input_source
            
            if pipe_input and original_file:
                cmd.extend(["-i", audio_source, "-map", "0:v:0", "-map", "1:a?"])
            elif not pipe_input:
                cmd.extend(["-analyzeduration", "0", "-probesize", "32", "-i", audio_source, "-map", "0:v:0", "-map", "1:a?"])
            else:
                cmd.append("-an")
                audio_mode = "No Audio"

            # Audio codec selection
            if audio_mode == "Copy Audio":
                cmd.extend(["-c:a", "copy"])
            elif audio_mode == "Re-encode Audio":
                sel_acodec = (options.get("audio_codec") or "AAC").upper()
                sel_abitrate = options.get("audio_bitrate") or "192k"
                
                if sel_acodec.startswith("AAC"):
                    ab = sel_abitrate if _BITRATE_REGEX.match(sel_abitrate) else "192k"
                    cmd.extend(["-c:a", "aac", "-b:a", ab])
                elif sel_acodec.startswith("AC3"):
                    ab = sel_abitrate if _BITRATE_REGEX.match(sel_abitrate) else "192k"
                    cmd.extend(["-c:a", "ac3", "-b:a", ab])
                else:
                    cmd.extend(["-c:a", "pcm_s16le"])
        else:
            cmd.append("-an")

        # Video codec (use pre-formatted strings from module constants)
        codec_config = _CODEC_CONFIGS.get(codec, _CODEC_CONFIGS["libx264 (H.264, CPU)"])
        cmd.extend(arg.format(crf=crf, preset=preset) for arg in codec_config)

        # ProRes + AI optimization (reduce memory usage)
        if codec.startswith("ProRes") and (options.get("use_ai_upscaling") or options.get("ai_interpolation")):
            cmd.extend(["-threads", "4", "-max_muxing_queue_size", "1024", "-filter_threads", "1"])

        cmd.extend(["-y", output_file])
        return cmd

    def encode(
        self,
        vspipe_process: subprocess.Popen,
        output_file: str,
        options: dict,
        total_frames: int,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        input_file: Optional[str] = None,
    ) -> bool:
        """
        Encode video from vspipe output.
        
        Optimizations: Pre-compiled regex, reduced string operations, efficient file checking
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        # Ensure container compatibility (ProRes requires .mov)
        codec = options.get("codec", "")
        out_path = Path(output_file)
        if codec.startswith("ProRes") and out_path.suffix.lower() != ".mov":
            output_file = str(out_path.with_suffix(".mov"))
            if log_callback:
                log_callback(f"⚠️ Adjusting output container to QuickTime (.mov) for ProRes codec: {output_file}\n")

        cmd = self.build_command("pipe:", output_file, options, pipe_input=True, original_file=input_file)
        cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        
        # Check if frame sequence mode
        is_frame_sequence = "%" in output_file and "d" in output_file
        
        # Log encoding stage start
        if log_callback:
            log_callback("\n# ========== STAGE 4: Encoding ==========\n")
            if is_frame_sequence:
                frame_format = options.get("frame_format", "PNG (Lossless)")
                log_callback(f"[STAGE 4/4] Outputting frame sequence: {frame_format}\n")
            else:
                log_callback("[STAGE 4/4] Starting final video encoding...\n")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=vspipe_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=cflags,
            )

            # Don't close vspipe stdout - FFmpeg needs to read from it!
            # (The pipe will be closed automatically when processes terminate)

            # Monitor progress (use pre-compiled module regex)
            for line in iter(self.process.stderr.readline, ""):
                line = line.rstrip()
                if not line:
                    continue

                # Filter benign warnings (use module-level tuple)
                if any(msg in line for msg in _BENIGN_WARNINGS):
                    continue

                # Parse progress (pre-compiled regex)
                if total_frames > 0:
                    match = _PROGRESS_REGEX.search(line)
                    if match:
                        try:
                            current_frame = int(match.group(1))
                            
                            # Throttle logging - only log every 10 frames
                            if log_callback and (current_frame - self.last_logged_frame >= 10 or current_frame == 1):
                                log_callback(f"{line}\n")
                                self.last_logged_frame = current_frame
                            current_fps = float(match.group(2)) if match.group(2) else 0.0
                            # FFmpeg encoding is 50-100% of total progress (vspipe was 0-50%)
                            ffmpeg_progress = min(100.0, (current_frame / max(1, total_frames)) * 100)
                            total_progress = 50.0 + (ffmpeg_progress * 0.5)

                            # Calculate ETA
                            if current_fps > 0:
                                eta_seconds = max(0, total_frames - current_frame) / current_fps
                                eta_str = self._format_eta(eta_seconds)
                            else:
                                eta_str = "Calculating..."

                            if progress_callback:
                                # Pass FPS as third parameter for performance monitoring
                                try:
                                    progress_callback(total_progress, f"Encoding: {current_frame}/{total_frames} ({current_fps:.2f} fps) ETA: {eta_str}", current_fps)
                                except TypeError:
                                    # Fallback for old callbacks that don't accept fps
                                    progress_callback(total_progress, eta_str)
                        except Exception:
                            pass

            self.process.wait()

            # Check result
            out_exists = out_path.exists()
            out_size = out_path.stat().st_size if out_exists else 0
            
            if self.process.returncode not in [0, None]:
                if log_callback:
                    log_callback(f"\nFFmpeg exit code: {self.process.returncode}\n")
                if out_exists and out_size > 0:
                    if log_callback:
                        log_callback("Note: FFmpeg reported error, but file was created.\n")
                    return True
                return False

            # Final progress update
            if progress_callback:
                progress_callback(100.0, "Completed")

            # Verify output
            if out_exists:
                if log_callback:
                    log_callback(f"\n✓ Output file created: {output_file}\n")
                    log_callback(f"✓ File size: {out_size / (1024 * 1024):.2f} MB\n")
                return True
            else:
                if log_callback:
                    log_callback(f"\n⚠ Warning: Output file not found at {output_file}\n")
                return False

        except Exception as e:
            if log_callback:
                log_callback(f"\nEncoding error: {str(e)}\n")
            return False
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Terminate FFmpeg process if running.
        
        Optimization: Simplified exception handling
        """
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except (subprocess.TimeoutExpired, Exception):
                try:
                    self.process.kill()
                except Exception:
                    pass

    @staticmethod
    def _format_eta(seconds: float) -> str:
        """
        Format ETA in HH:MM:SS.
        
        Optimization: Fast path for invalid values, reduced imports
        """
        if seconds <= 0 or seconds > 172800:  # > 2 days
            return "--:--:--"
        return str(datetime.timedelta(seconds=int(seconds)))
