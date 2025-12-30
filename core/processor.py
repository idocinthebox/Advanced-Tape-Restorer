"""
Video Processor - Main orchestration layer for video restoration

Performance Optimizations:
- Cached video info to avoid redundant ffprobe calls
- Pre-calculated AI settings to eliminate duplicate computations
- Optimized imports (moved to module level)
- Efficient temp file tracking with set-based lookups
- Reduced string allocations in logging paths
- Constants for buffer sizes and magic numbers
"""

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional, Tuple

from .video_analyzer import VideoAnalyzer
from .vapoursynth_engine import VapourSynthEngine
from .ffmpeg_encoder import FFmpegEncoder
from .propainter_engine import ProPainterEngine
from .propainter_checkpoint_processor import process_propainter_with_checkpoints

# Performance constants
BUFFER_SIZE_PRORES_AI = 2097152  # 2MB for ProRes+AI (reduced memory usage)
BUFFER_SIZE_STANDARD = 10485760  # 10MB for standard processing
MIN_VALID_FILE_SIZE = 1024  # 1KB minimum for valid video output
VSPIPE_TERMINATE_TIMEOUT = 5  # Seconds to wait before force-killing vspipe


class VideoProcessor:
    """
    Main video processing orchestrator.
    Coordinates analysis, VapourSynth filtering, and FFmpeg encoding.

    Optimizations:
    - Video info caching to avoid repeated ffprobe calls
    - Efficient temp file tracking with set
    - Pre-computed AI settings
    - Lazy component initialization
    """

    def __init__(self, propainter_path: Optional[str] = None):
        self.analyzer = VideoAnalyzer()
        self.vs_engine = None  # Lazy initialization in process_video
        self.encoder = FFmpegEncoder()
        self.propainter = ProPainterEngine(propainter_path)
        self.vspipe_process = None
        self.stop_requested = False
        self._temp_files = set()  # Set for O(1) membership checks
        self._video_info_cache = {}  # Cache for video metadata

    @staticmethod
    def check_prerequisites() -> None:
        """
        Check for required external tools.

        Optimization: Static method (no self access needed), direct shutil import
        """
        required_tools = [
            ("vspipe", "VapourSynth"),
            ("ffmpeg", "FFmpeg"),
            ("ffprobe", "FFprobe"),
        ]

        missing_tools = [
            f"{name} ({tool})"
            for tool, name in required_tools
            if not shutil.which(tool)
        ]

        if missing_tools:
            raise RuntimeError(
                f"Missing external tools: {', '.join(missing_tools)}\n"
                "Please install them and add to PATH."
            )

    def _get_cached_video_info(self, input_file: str) -> Tuple[int, int, float, int, float]:
        """
        Get video info with caching to avoid redundant ffprobe calls.

        Optimization: Caches video metadata per file path

        Returns:
            (width, height, par, frame_count, fps)
        """
        if input_file not in self._video_info_cache:
            self._video_info_cache[input_file] = self.analyzer.get_video_info(input_file)
        return self._video_info_cache[input_file]

    def _calculate_ai_settings(self, options: dict, width: int, height: int, fps: float) -> dict:
        """
        Pre-calculate all AI-related settings to avoid duplicate computations.

        Optimization: Single computation instead of repeated checks

        Returns:
            dict with 'uses_ai', 'output_width', 'output_height', 'output_fps', 'buffer_size'
        """
        uses_ai_upscaling = options.get("use_ai_upscaling", False)
        uses_ai_interpolation = options.get("ai_interpolation", False)
        uses_ai = uses_ai_upscaling or uses_ai_interpolation

        # Calculate output dimensions
        output_width = width
        output_height = height
        output_fps = fps

        if uses_ai_upscaling:
            scale_factor = 2  # RealESRGAN/ZNEDI3 2x upscaling
            output_width *= scale_factor
            output_height *= scale_factor

        if uses_ai_interpolation:
            factor_str = options.get("interpolation_factor", "2x (30fps→60fps)")
            if "2x" in factor_str:
                output_fps *= 2
            elif "3x" in factor_str:
                output_fps *= 3
            elif "4x" in factor_str:
                output_fps *= 4

        # Calculate optimal buffer size
        codec = options.get("codec", "")
        buffer_size = (
            BUFFER_SIZE_PRORES_AI if (codec.startswith("ProRes") and uses_ai)
            else BUFFER_SIZE_STANDARD
        )

        return {
            "uses_ai": uses_ai,
            "output_width": int(output_width),
            "output_height": int(output_height),
            "output_fps": float(output_fps),
            "buffer_size": buffer_size,
        }
    
    def _check_vram_requirements(self, options: dict) -> dict:
        """Pre-flight VRAM requirement check for GPU-accelerated filters.
        
        Args:
            options: Processing options
            
        Returns:
            dict with 'ok' (bool), 'required' (GB), 'available' (GB), 'suggestion' (str)
        """
        # VRAM requirements per filter (GB for 1080p frame)
        FILTER_VRAM_REQUIREMENTS = {
            "qtgmc": 0.5,           # QTGMC baseline
            "bm3d_gpu": 1.2,        # BM3DCUDA
            "realesrgan": 2.8,      # RealESRGAN 2x/4x
            "rife": 3.5,            # RIFE interpolation
            "znedi3": 0.3,          # ZNEDI3 (lightweight)
        }
        
        # Only check if GPU features are enabled
        uses_gpu = (
            options.get("bm3d_use_gpu", False) or
            options.get("use_ai_upscaling", False) or
            options.get("ai_interpolation", False)
        )
        
        if not uses_gpu:
            return {'ok': True}  # No GPU features, no VRAM check needed
        
        try:
            from .gpu_accelerator import GPUAccelerator
            
            gpu = GPUAccelerator()
            if not gpu.is_available():
                return {'ok': True}  # GPU not available, skip check
            
            vram = gpu.get_vram_usage()
            available_gb = vram.get('free_gb', 0)
            
            # Get video resolution (use cached info if available)
            width = options.get('width', 1920)
            height = options.get('height', 1080)
            
            # Calculate scale factor relative to 1080p
            scale = (width * height) / (1920 * 1080)
            
            # Estimate VRAM requirement
            required_gb = 0.5  # Base VapourSynth overhead
            
            if options.get("use_qtgmc", True):
                required_gb += FILTER_VRAM_REQUIREMENTS["qtgmc"] * scale
            
            if options.get("bm3d_enabled", False) and options.get("bm3d_use_gpu", False):
                required_gb += FILTER_VRAM_REQUIREMENTS["bm3d_gpu"] * scale
            
            if options.get("use_ai_upscaling", False):
                method = options.get("ai_upscaling_method", "ZNEDI3")
                if "RealESRGAN" in method:
                    required_gb += FILTER_VRAM_REQUIREMENTS["realesrgan"] * scale
                else:  # ZNEDI3
                    required_gb += FILTER_VRAM_REQUIREMENTS["znedi3"] * scale
            
            if options.get("ai_interpolation", False):
                required_gb += FILTER_VRAM_REQUIREMENTS["rife"] * scale
            
            # Check if sufficient VRAM
            if required_gb > available_gb:
                # Generate suggestions
                suggestions = []
                if options.get("ai_interpolation", False):
                    suggestions.append("  • Disable RIFE interpolation (saves ~3.5 GB)")
                if "RealESRGAN" in options.get("ai_upscaling_method", ""):
                    suggestions.append("  • Use ZNEDI3 instead of RealESRGAN (saves ~2.5 GB)")
                if options.get("bm3d_use_gpu", False):
                    suggestions.append("  • Use CPU BM3D instead of GPU (saves ~1.2 GB)")
                if width > 1920 or height > 1080:
                    suggestions.append(f"  • Reduce output resolution ({width}×{height} → 1920×1080)")
                
                return {
                    'ok': False,
                    'required': round(required_gb, 1),
                    'available': round(available_gb, 1),
                    'suggestion': '\n'.join(suggestions) if suggestions else '  • Process in shorter segments'
                }
            
            return {'ok': True}
            
        except Exception as e:
            # GPU check failed, proceed with warning
            return {'ok': True}  # Don't block processing if check fails

    @contextmanager
    def _vspipe_stderr_logger(self, log_callback: Optional[Callable], progress_callback: Optional[Callable] = None, total_frames: int = 0):
        """
        Context manager for vspipe stderr logging thread with frame progress monitoring.
        
        vspipe with -p flag outputs to stderr:
        - Print statements from script (our stage indicators)
        - Frame progress: "Frame 123/252" (with -p flag)
        - Final summary: "Output 252 frames in 194.42 seconds (1.30 fps)"

        Optimization: Ensures thread is properly cleaned up
        """
        import re
        import time
        
        def log_stderr():
            if self.vspipe_process and self.vspipe_process.stderr:
                last_frame = 0
                start_time = time.time()
                last_update_time = start_time
                last_log_time = start_time
                
                # Match vspipe progress format: "Frame 123/252" or "Output 252 frames"
                frame_pattern = re.compile(r'Frame (\d+)/(\d+)')
                output_pattern = re.compile(r'Output (\d+) frames in ([\d.]+) seconds \(([\d.]+) fps\)')
                
                # Read char-by-char to handle \r progress (vspipe doesn't use \n for progress)
                buffer = ""
                while True:
                    char = self.vspipe_process.stderr.read(1)
                    if not char:
                        break
                    
                    if char in ('\r', '\n'):
                        if buffer:
                            line = buffer.strip()
                            buffer = ""
                        else:
                            continue
                    else:
                        buffer += char
                        continue
                    
                    # Parse frame progress from vspipe -p output
                    match = frame_pattern.search(line)
                    if match:
                        current_frame = int(match.group(1))
                        total = int(match.group(2))
                        
                        # Update progress (every 10 frames)
                        if progress_callback and total_frames > 0 and (current_frame - last_frame >= 10 or current_frame == total):
                            elapsed = time.time() - start_time
                            if elapsed > 0 and current_frame > 0:
                                fps = current_frame / elapsed
                                remaining_frames = total - current_frame
                                eta_seconds = remaining_frames / fps if fps > 0 else 0
                                
                                # Format ETA
                                if eta_seconds >= 3600:
                                    eta_str = f"{int(eta_seconds // 3600)}h {int((eta_seconds % 3600) // 60)}m"
                                elif eta_seconds >= 60:
                                    eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                                else:
                                    eta_str = f"{int(eta_seconds)}s"
                                
                                # Calculate progress percentage (vspipe is 0-50% of total)
                                vspipe_progress = (current_frame / total) * 50.0
                                
                                # Call progress_callback with 3 parameters (progress, ETA, FPS)
                                progress_callback(vspipe_progress, f"ETA: {eta_str}", fps)
                                
                                last_frame = current_frame
                                last_update_time = time.time()
                        
                        # Log to console every 2 seconds
                        if log_callback and time.time() - last_log_time >= 2.0:
                            log_callback(f"[vspipe] Processing frame {current_frame}/{total}\n")
                            last_log_time = time.time()
                        continue
                    
                    # Parse final output summary
                    output_match = output_pattern.search(line)
                    if output_match and log_callback:
                        log_callback(f"[vspipe] {line}\n")
                        continue
                    
                    # Log all other messages (including our STAGE indicators from print())
                    if log_callback and line:
                        # Don't log empty lines or repeated progress
                        if not line.startswith('Frame '):
                            log_callback(f"[vspipe] {line}\n")

        thread = threading.Thread(target=log_stderr, daemon=True)
        thread.start()
        try:
            yield thread
        finally:
            # Thread is daemon, will terminate automatically
            pass

    def process_video(
        self,
        input_file: str,
        output_file: str,
        options: dict,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[bool, str]:
        """
        Process video with restoration filters.

        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            options: Processing options dictionary
            progress_callback: Function(percent, eta_str) for progress updates
            log_callback: Function(message) for log messages

        Returns:
            (success: bool, message: str)

        Optimizations:
        - Cached video info lookup
        - Pre-computed AI settings
        - Efficient buffer management
        """
        try:
            # Step 1: Check prerequisites
            if log_callback:
                log_callback("\n=== Checking prerequisites ===\n")
            self.check_prerequisites()

            # Step 2: Analyze input video (with caching)
            if log_callback:
                log_callback("\n=== Analyzing input video ===\n")
                log_callback(f"Input file: {input_file}\n")
            
            # Step 2.5: Check VRAM requirements (GPU features only)
            vram_check = self._check_vram_requirements(options)
            if not vram_check['ok']:
                warning_msg = (
                    f"⚠️ VRAM Warning: Estimated {vram_check['required']:.1f} GB needed, "
                    f"but only {vram_check['available']:.1f} GB available.\n\n"
                    f"Suggestions:\n{vram_check['suggestion']}\n\n"
                    f"Processing may fail or be very slow. Continue anyway?"
                )
                if log_callback:
                    log_callback(f"\n{warning_msg}\n")
                # Note: GUI should show dialog here, we'll just log for now

            width, height, par, frame_count, fps = self._get_cached_video_info(input_file)

            if log_callback:
                log_callback(f"Resolution: {width}x{height}\n")
                log_callback(f"Frame rate: {fps:.2f} fps\n")
                log_callback(f"Estimated frames: {frame_count}\n")

            # Step 3: Auto-detect field order if needed
            if options.get("field_order") == "Auto-Detect":
                if log_callback:
                    log_callback("\nAuto-detecting field order...\n")

                detected_field_order = self.analyzer.detect_field_order(
                    input_file,
                    probe_frames=options.get("idet_probe_frames", 900),
                    prog_dom_ratio=options.get("idet_prog_dom_ratio", 1.5),
                    prog_min=options.get("idet_prog_min", 150),
                    field_dom_ratio=options.get("idet_field_dom_ratio", 1.3),
                    field_min=options.get("idet_field_min", 80),
                    field_fallback_min=options.get("idet_field_fallback_min", 200),
                )

                options["field_order"] = detected_field_order
                if log_callback:
                    log_callback(f"Detected field order: {detected_field_order}\n")

            # Step 4: ProPainter pre-processing (if enabled)
            propainter_input = input_file
            if options.get("ai_inpainting", False):
                if log_callback:
                    log_callback("\n=== ProPainter AI Inpainting ===\n")

                propainter_output = self._run_propainter_preprocessing(
                    input_file, options, log_callback
                )

                if propainter_output:
                    propainter_input = propainter_output
                    if log_callback:
                        log_callback("✅ ProPainter completed, using cleaned video\n")
                else:
                    if log_callback:
                        log_callback(
                            "⚠️  ProPainter failed or not available, using original video\n"
                        )

            # Step 5: Pre-calculate AI settings (optimization: single calculation)
            ai_settings = self._calculate_ai_settings(options, width, height, fps)

            # Store in options for FFmpeg and VapourSynth GPU optimization
            options.update({
                "width": width,  # Input dimensions for GPU tile optimization
                "height": height,
                "output_width": ai_settings["output_width"],
                "output_height": ai_settings["output_height"],
                "output_fps": ai_settings["output_fps"],
            })

            # Step 6: Generate VapourSynth script (lazy initialization)
            if log_callback:
                log_callback("\n=== Generating restoration script ===\n")

            if not self.vs_engine:
                self.vs_engine = VapourSynthEngine(log_callback=log_callback)

            self.vs_engine.create_script(propainter_input, options)

            # Step 7: Get actual frame count from script
            if log_callback:
                log_callback("\nScanning video with VapourSynth...\n")

            total_frames = self.vs_engine.get_total_frames()
            if log_callback:
                log_callback(f"Total frames: {total_frames}\n")

            if total_frames <= 0:
                raise RuntimeError(
                    "Could not determine video length. Check console for details."
                )

            # Step 8: Start VapourSynth pipeline
            if log_callback:
                log_callback("\n=== Starting restoration process ===\n")
                log_callback(f"Output file: {output_file}\n")
                
                # Build processing stages description
                stages = []
                if options.get("deinterlace", True):
                    stages.append("Deinterlacing (QTGMC)")
                if options.get("denoise_enabled", False):
                    stages.append("Denoising (BM3D)")
                if options.get("ai_upscaling", False):
                    method = options.get("ai_upscale_method", "RealESRGAN")
                    stages.append(f"AI Upscaling ({method})")
                
                if stages:
                    stages_str = " → ".join(stages)
                    log_callback(f"\n[Processing Pipeline] {stages_str}\n")
                    log_callback("[Info] Frame processing will take several minutes...\n")

            # Add -p for progress output and -progress for frame-by-frame updates
            vspipe_cmd = ["vspipe", "-p", "-c", "y4m", self.vs_engine.script_file, "-"]

            if ai_settings["uses_ai"] and log_callback:
                log_callback(
                    f"[vspipe] Output format: Y4M ({ai_settings['output_width']}x"
                    f"{ai_settings['output_height']} @ {ai_settings['output_fps']} fps)\n"
                )
            elif log_callback:
                log_callback("[vspipe] Output format: Y4M\n")

            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

            self.vspipe_process = subprocess.Popen(
                vspipe_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=8192,  # Small buffer for line-buffering (vspipe uses \r progress)
                creationflags=cflags,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Monitor vspipe stderr (using context manager for cleanup)
            with self._vspipe_stderr_logger(log_callback, progress_callback, total_frames):
                # Step 9: Encode with FFmpeg
                success = self.encoder.encode(
                    self.vspipe_process,
                    output_file,
                    options,
                    total_frames,
                    progress_callback,
                    log_callback,
                    input_file,
                )

            # Step 10: GFPGAN Face Enhancement (if enabled)
            if success and options.get('face_enhance', False):
                try:
                    if log_callback:
                        log_callback("\n=== Step 10: Face Enhancement (GFPGAN) ===\n")

                    success = self._apply_face_enhancement(
                        output_file,
                        options,
                        progress_callback,
                        log_callback
                    )

                    if success and log_callback:
                        log_callback("[GFPGAN] Face enhancement completed successfully\n")
                except Exception as e:
                    if log_callback:
                        log_callback(f"[WARNING] Face enhancement failed: {e}\n")
                        import traceback
                        log_callback(traceback.format_exc())
                    # Continue with unenhanced video

            # Return appropriate message
            if success:
                msg = "Processing completed successfully"
                if log_callback:
                    log_callback(f"\n✅ {msg}!\n")
            else:
                msg = "Processing failed (see logs)"
                if log_callback:
                    log_callback(f"\n❌ {msg}\n")

            return bool(success), msg

        except Exception as e:
            msg = f"Error: {e}"
            if log_callback:
                log_callback(f"\n❌ {msg}\n")
                import traceback
                log_callback(traceback.format_exc())
            return False, msg

        finally:
            self.cleanup()
            # Always cleanup GPU memory to prevent VRAM leaks
            self._cleanup_gpu_memory()

    def _apply_face_enhancement(
        self,
        video_file: str,
        options: dict,
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Apply GFPGAN face enhancement to encoded video.

        Optimizations:
        - Efficient temp directory tracking
        - Early validation to avoid unnecessary processing
        - Streamlined subprocess calls

        Args:
            video_file: Path to the encoded video file
            options: Processing options (contains face_enhance settings)
            progress_callback: Optional progress callback
            log_callback: Optional log callback

        Returns:
            True if successful, False otherwise
        """
        temp_frames_dir = None
        temp_enhanced_dir = None
        temp_output = None

        try:
            # Import AI components (lazy loading)
            from ai_models.model_manager import ModelManager
            from core.gfpgan_checkpoint_processor import GFPGANCheckpointProcessor
            import hashlib

            # Get model configuration
            face_model_id = options.get('face_model_id', 'gfpgan_v1_3')
            face_weight = options.get('face_weight', 0.5)

            if log_callback:
                log_callback(f"[GFPGAN] Model: {face_model_id}\n")
                log_callback(f"[GFPGAN] Enhancement strength: {face_weight}\n")

            # Initialize Model Manager
            localappdata = os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share'))
            model_root = os.path.join(localappdata, 'Advanced_Tape_Restorer', 'ai_models')

            # Find registry path
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            registry_path = project_root / 'ai_models' / 'models' / 'registry.yaml'

            if log_callback:
                log_callback("[GFPGAN] Initializing model manager...\n")

            manager = ModelManager(str(registry_path), model_root, commercial_mode=True)

            # Ensure GFPGAN model is available
            if log_callback:
                log_callback("[GFPGAN] Ensuring model is downloaded...\n")

            manager.ensure_model_available(face_model_id, auto_download=True)

            # Get model path
            engine_args = manager.prepare_engine_args('gfpgan', face_model_id)
            model_name = engine_args['model_path']
            model_path = os.path.join(model_root, 'gfpgan', model_name)

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"GFPGAN model not found: {model_path}")

            # Estimate disk space requirements before processing
            # Get video properties from the file
            width, height, par, frame_count_estimate, fps_val = self._get_cached_video_info(video_file)
            duration = frame_count_estimate / fps_val if fps_val > 0 else 0
            frame_count_estimate = int(frame_count_estimate) if frame_count_estimate > 0 else 1000
            
            # Estimate PNG file sizes (RGB, PNG compression typically 40% of raw)
            bytes_per_pixel = 3  # RGB
            raw_frame_size = width * height * bytes_per_pixel
            png_compression_ratio = 0.4  # PNG typically compresses to 40% of raw
            estimated_frame_size_mb = (raw_frame_size * png_compression_ratio) / (1024 * 1024)
            
            # Total space = input frames + enhanced frames (2x)
            estimated_total_gb = (estimated_frame_size_mb * frame_count_estimate * 2) / 1024
            
            if log_callback:
                log_callback(f"[GFPGAN] Estimated disk usage: {estimated_total_gb:.2f} GB temporary space\n")
                log_callback(f"[GFPGAN] Frame size: {width}x{height}, ~{estimated_frame_size_mb:.1f} MB per frame\n")
            
            # Check available disk space
            import shutil
            temp_drive = Path(tempfile.gettempdir()).drive or Path(tempfile.gettempdir()).parts[0]
            try:
                disk_usage = shutil.disk_usage(temp_drive)
                available_gb = disk_usage.free / (1024**3)
                
                if log_callback:
                    log_callback(f"[GFPGAN] Available disk space: {available_gb:.2f} GB\n")
                
                # Warn if less than 20% headroom
                required_with_headroom = estimated_total_gb * 1.2
                if available_gb < required_with_headroom:
                    warning = (
                        f"⚠️ LOW DISK SPACE WARNING:\n"
                        f"   Required: ~{estimated_total_gb:.2f} GB\n"
                        f"   Available: {available_gb:.2f} GB\n"
                        f"   Recommended: {required_with_headroom:.2f} GB (with 20% headroom)\n"
                        f"   You may run out of disk space during processing!\n"
                    )
                    if log_callback:
                        log_callback(warning)
            except Exception:
                pass  # Can't check disk space, continue anyway

            # Create temporary directories (use custom path if specified)
            custom_temp_dir = options.get('gfpgan_temp_dir', '')
            if custom_temp_dir and os.path.isdir(custom_temp_dir):
                temp_frames_dir = tempfile.mkdtemp(prefix='gfpgan_frames_', dir=custom_temp_dir)
                temp_enhanced_dir = tempfile.mkdtemp(prefix='gfpgan_enhanced_', dir=custom_temp_dir)
                if log_callback:
                    log_callback(f"[GFPGAN] Using custom temp directory: {custom_temp_dir}\n")
            else:
                temp_frames_dir = tempfile.mkdtemp(prefix='gfpgan_frames_')
                temp_enhanced_dir = tempfile.mkdtemp(prefix='gfpgan_enhanced_')
                if log_callback:
                    log_callback(f"[GFPGAN] Using default temp directory: {tempfile.gettempdir()}\n")
            
            self._temp_files.update([temp_frames_dir, temp_enhanced_dir])

            if log_callback:
                log_callback("[GFPGAN] Extracting frames from video...\n")

            # Extract frames using FFmpeg with fast PNG compression
            # Optimization: compression_level 0 = fastest PNG encoding (still lossless)
            extract_cmd = [
                'ffmpeg', '-y',
                '-threads', '0',  # Use all CPU threads
                '-i', video_file,
                '-compression_level', '0',  # Fastest PNG encoding (3-5x faster, still lossless)
                '-qscale:v', '1',  # PNG maximum quality (lossless)
                os.path.join(temp_frames_dir, 'frame_%06d.png')
            ]
            
            result = subprocess.run(
                extract_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Frame extraction failed: {result.stderr}")

            # Count extracted frames (PNG)
            frame_files = list(Path(temp_frames_dir).glob('*.png'))
            if not frame_files:
                raise RuntimeError("No frames extracted from video")

            if log_callback:
                log_callback(f"[GFPGAN] Extracted {len(frame_files)} frames\n")
                log_callback("[GFPGAN] Enhancing faces...\n")

            # Create unique job ID from video file and settings
            import hashlib
            job_id = f"gfpgan_{hashlib.md5(video_file.encode()).hexdigest()[:12]}"
            
            if log_callback:
                log_callback(f"[GFPGAN] Job ID: {job_id} (for resume support)\n")

            # Initialize checkpoint processor
            checkpoint_processor = GFPGANCheckpointProcessor(
                job_id=job_id,
                input_frames_dir=Path(temp_frames_dir),
                output_frames_dir=Path(temp_enhanced_dir),
                model_path=model_path,
                upscale=1,  # No upscaling, just face enhancement at current resolution
                weight=face_weight,
                checkpoint_interval=50,  # Save checkpoint every 50 frames
                disk_space_buffer_gb=5  # Maintain 5GB free space
            )
            
            # Check if resuming
            checkpoint_status = checkpoint_processor.get_checkpoint_status()
            if checkpoint_status.current_frame > 0:
                if log_callback:
                    log_callback(f"▶️ Resuming from frame {checkpoint_status.current_frame}/{len(frame_files)}\n")
                    log_callback(f"   Progress: {checkpoint_status.progress_percent():.1f}%\n")

            def gfpgan_progress(current, total):
                """Progress callback for GFPGAN processing."""
                if progress_callback:
                    # Calculate percentage for GFPGAN progress
                    pct = int((current / total) * 100)
                    # Use ETA field to show "Face Enhancement: XX%"
                    progress_callback(pct, f"Face Enhancement: {pct}%")
                if log_callback and current % 5 == 0:  # Log every 5 frames
                    log_callback(f"[GFPGAN] Enhanced {current}/{total} frames ({pct}%)\n")
            
            def gfpgan_log(message):
                """Log callback for GFPGAN processing."""
                if log_callback:
                    log_callback(message + "\n")

            # Process with checkpoints
            success = checkpoint_processor.process_with_checkpoints(
                progress_callback=gfpgan_progress,
                log_callback=gfpgan_log
            )
            
            if not success:
                raise RuntimeError("GFPGAN processing failed or was interrupted")

            # Re-encode enhanced frames to video
            if log_callback:
                log_callback("[GFPGAN] Re-encoding enhanced video...\n")

            temp_output = str(Path(video_file).parent / f"temp_enhanced_{Path(video_file).name}")
            self._temp_files.add(temp_output)

            # Get original video properties (fps) for accurate encoding
            import json
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_file]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            fps = '30'  # Default fallback
            if probe_result.returncode == 0:
                try:
                    probe_data = json.loads(probe_result.stdout)
                    for stream in probe_data.get('streams', []):
                        if stream.get('codec_type') == 'video':
                            fps_str = stream.get('r_frame_rate', '30/1')
                            if '/' in fps_str:
                                num, den = fps_str.split('/')
                                fps = str(round(float(num) / float(den), 3))
                            break
                except Exception:
                    pass  # Use default
            
            if log_callback:
                log_callback(f"[GFPGAN] Detected framerate: {fps} fps\n")

            # Use encoder settings from user's Output tab selection
            codec_str = options.get('codec', 'libx264 (H.264, CPU)')
            codec = codec_str.split(' ')[0]  # Extract codec name (e.g., "libx264" from "libx264 (H.264, CPU)")
            
            # Get quality settings from options
            crf = str(options.get('crf', 18))
            preset = options.get('ffmpeg_preset', 'medium')
            
            if log_callback:
                log_callback(f"[GFPGAN] Using encoder: {codec_str}\n")
                log_callback(f"[GFPGAN] Quality: CRF {crf}, Preset: {preset}\n")
            
            # Build encoder options based on codec type
            if 'nvenc' in codec.lower():
                # NVIDIA NVENC
                encoder_opts = ['-preset', preset, '-cq', crf]
            elif 'amf' in codec.lower():
                # AMD AMF
                encoder_opts = ['-quality', preset, '-rc', 'cqp', '-qp_i', crf]
            elif 'qsv' in codec.lower():
                # Intel QuickSync
                encoder_opts = ['-preset', preset, '-global_quality', crf]
            elif 'prores' in codec.lower():
                # ProRes (no CRF/preset)
                encoder_opts = []
            else:
                # CPU encoders (libx264, libx265, etc.)
                encoder_opts = ['-preset', preset, '-crf', crf]
            
            # Get frame count for progress monitoring
            frame_count = len(frame_files)
            
            # Build encoding command (reading PNG enhanced frames)
            # Since upscale=1, frames maintain original resolution - no scaling needed
            encode_cmd = [
                'ffmpeg', '-y',
                '-framerate', fps,
                '-i', os.path.join(temp_enhanced_dir, 'frame_%06d.png'),  # PNG enhanced frames
                '-i', video_file,  # Original for audio
                '-map', '0:v:0',   # Video from frames
                '-map', '1:a?',    # Audio from original (optional)
                '-c:v', codec,
                *encoder_opts,
                '-pix_fmt', 'yuv420p',
                '-c:a', 'copy',    # Copy audio stream
                '-movflags', '+faststart',  # Optimize for streaming
                temp_output
            ]
            
            # DEBUG: Log the actual command
            if log_callback:
                log_callback(f"[DEBUG] FFmpeg re-encode command: {' '.join(encode_cmd)}\n")
                log_callback(f"[DEBUG] Enhanced frames directory: {temp_enhanced_dir}\n")
                log_callback(f"[DEBUG] Frame count: {frame_count}\n")

            # Run with progress monitoring
            process = subprocess.Popen(
                encode_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,  # Line buffered for real-time output
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Monitor encoding progress
            # FFmpeg uses \r to update the same line, not \n for new lines
            # We need to read character-by-character to catch progress updates
            encoded_frames = 0
            stderr_buffer = ""
            
            while process.poll() is None:  # While process is running
                char = process.stderr.read(1) if process.stderr else ""
                if not char:
                    break
                    
                stderr_buffer += char
                
                # Check for carriage return or newline (FFmpeg uses both)
                if char in ['\r', '\n']:
                    line = stderr_buffer.strip()
                    stderr_buffer = ""
                    
                    # Parse frame number from FFmpeg output
                    if 'frame=' in line:
                        try:
                            frame_str = line.split('frame=')[1].split()[0].strip()
                            encoded_frames = int(frame_str)
                            
                            if progress_callback and frame_count > 0:
                                encode_pct = int((encoded_frames / frame_count) * 100)
                                progress_callback(encode_pct, f"Re-encoding: {encode_pct}%")
                            
                            if log_callback and encoded_frames % 50 == 0:
                                log_callback(f"[GFPGAN] Re-encoded {encoded_frames}/{frame_count} frames\n")
                        except (ValueError, IndexError):
                            pass
            
            # Read any remaining output
            remaining = process.stderr.read() if process.stderr else ""
            
            process.wait()
            
            if process.returncode != 0:
                stderr_output = process.stderr.read() if process.stderr else "Unknown error"
                raise RuntimeError(f"Re-encoding failed: {stderr_output}")

            # Replace original with enhanced version
            if log_callback:
                log_callback("[GFPGAN] Replacing original with enhanced video...\n")

            shutil.move(temp_output, video_file)

            return True

        except Exception as e:
            if log_callback:
                log_callback(f"[ERROR] Face enhancement failed: {e}\n")
            raise

        finally:
            # Clean up temporary directories
            for temp_dir in [temp_frames_dir, temp_enhanced_dir]:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass

    def request_stop(self):
        """Request processing to stop."""
        self.stop_requested = True
        self.cleanup()

    def cleanup(self):
        """
        Clean up processes and temporary files.

        Optimization: Efficient process termination with timeout
        """
        # Terminate vspipe with timeout
        if self.vspipe_process and self.vspipe_process.poll() is None:
            try:
                self.vspipe_process.terminate()
                self.vspipe_process.wait(timeout=VSPIPE_TERMINATE_TIMEOUT)
            except subprocess.TimeoutExpired:
                self.vspipe_process.kill()
            except Exception:
                pass

        # Clean up encoder
        if self.encoder:
            self.encoder.cleanup()

        # Clean up script
        if self.vs_engine:
            self.vs_engine.cleanup()

        # Clean up temp files
        self._cleanup_temp_files()

    def _run_propainter_preprocessing(
        self,
        input_file: str,
        options: dict,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> Optional[str]:
        """
        Run ProPainter as pre-processing step.

        Optimizations:
        - Early returns to avoid unnecessary processing
        - Efficient path handling with Path objects
        - Streamlined validation logic

        Args:
            input_file: Original video file
            options: Processing options dict
            log_callback: Logging function

        Returns:
            Path to ProPainter output video, or None if failed
        """
        if not self.propainter.is_available():
            if log_callback:
                log_callback("❌ ProPainter not installed or configured\n")
                log_callback(
                    "   Install ProPainter and set path in Settings > AI Features\n"
                )
            return None

        try:
            # Create temp output file
            temp_dir = Path(tempfile.gettempdir()) / "tape_restorer_propainter"
            temp_dir.mkdir(parents=True, exist_ok=True)

            input_path = Path(input_file)
            temp_output = temp_dir / f"propainter_{input_path.stem}.mp4"
            self._temp_files.add(temp_output)

            # Get ProPainter settings
            inpainting_mode = options.get("inpainting_mode", "Remove Artifacts")

            # Map UI mode to ProPainter mode
            mode_map = {
                "Remove Artifacts": "auto_detect",
                "Object Removal": "object_removal",
                "Restore Damaged Areas": "video_completion",
            }
            propainter_mode = mode_map.get(inpainting_mode, "auto_detect")

            # Get mask path and auto-mask settings
            mask_path = options.get("propainter_mask_path")
            auto_mask = options.get("propainter_auto_mask", False)
            auto_mask_mode = options.get("propainter_auto_mask_mode", "all")
            auto_mask_sensitivity = options.get("propainter_auto_mask_sensitivity", 0.5)

            # Generate auto-mask if enabled and no manual mask provided
            if auto_mask and (not mask_path or not Path(mask_path).exists()):
                if log_callback:
                    log_callback("\n🤖 Auto-generating artifact detection mask...\n")

                mask_dir = temp_dir / f"auto_mask_{input_path.stem}"
                mask_path = str(mask_dir)
                self._temp_files.add(mask_dir)

                success = self.propainter.create_auto_mask(
                    video_path=str(input_file),
                    output_mask_dir=mask_path,
                    detection_mode=auto_mask_mode,
                    sensitivity=auto_mask_sensitivity,
                    log_callback=log_callback,
                )

                if not success:
                    if log_callback:
                        log_callback(
                            "⚠️  Auto-mask generation failed, skipping ProPainter\n"
                        )
                    return None

            # Check if mask is required for this mode
            if propainter_mode in ["object_removal", "video_completion", "auto_detect"]:
                if not mask_path or not Path(mask_path).exists():
                    if log_callback:
                        log_callback(
                            "\nℹ️  ProPainter requires mask files for inpainting\n"
                            "   Mask files identify which areas to fix/remove\n"
                            "\n💡 To use ProPainter:\n"
                            "   Option 1: Enable 'Auto-Generate Mask' in Advanced tab\n"
                            "   Option 2: Manually create mask (white=inpaint, black=keep)\n"
                            "             and specify path in Advanced tab\n"
                            "\n⚠️  Skipping ProPainter - using original video\n"
                        )
                    return None

            # Don't downscale - ProPainter needs masks to match video dimensions exactly
            width = None
            height = None

            if log_callback:
                log_callback(f"Mode: {inpainting_mode}\n")
                if mask_path:
                    log_callback(f"Mask: {mask_path}\n")

            # Get memory preset setting
            memory_preset = options.get("propainter_memory_preset", "auto")

            # Run ProPainter with checkpoint support
            # Enables resume after crashes/disk space issues (10-15 hour processing times)
            if log_callback:
                log_callback("   Using checkpoint system for resumable processing\n")
            
            success = process_propainter_with_checkpoints(
                input_video=str(input_file),
                output_video=str(temp_output),
                mode=propainter_mode,
                mask_path=mask_path,
                width=width,
                height=height,
                use_fp16=True,
                memory_preset=memory_preset,
                log_callback=log_callback,
            )

            if success and temp_output.exists():
                # Validate output video is not empty/corrupt
                file_size = os.path.getsize(temp_output)

                if file_size < MIN_VALID_FILE_SIZE:
                    if log_callback:
                        log_callback(
                            f"⚠️  ProPainter output is too small ({file_size} bytes)\n"
                            "   Output may be empty or corrupt\n"
                            "   Using original video instead\n"
                        )
                    return None

                # Validate with ffprobe
                try:
                    probe_result = subprocess.run(
                        [
                            "ffprobe",
                            "-v", "error",
                            "-count_frames",
                            "-select_streams", "v:0",
                            "-show_entries", "stream=nb_read_frames",
                            "-of", "default=nokey=1:noprint_wrappers=1",
                            str(temp_output),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if probe_result.returncode == 0 and probe_result.stdout.strip():
                        frame_count = int(probe_result.stdout.strip())
                        if frame_count == 0:
                            if log_callback:
                                log_callback(
                                    "⚠️  ProPainter output has 0 frames\n"
                                    "   This usually means ProPainter failed during processing\n"
                                    "   Using original video instead\n"
                                )
                            return None

                        if log_callback:
                            log_callback(
                                f"✓ Validated output: {frame_count} frames, "
                                f"{file_size / 1024 / 1024:.1f} MB\n"
                            )
                except Exception as e:
                    if log_callback:
                        log_callback(f"⚠️  Could not validate output: {e}\n")
                        log_callback("   Proceeding anyway...\n")

                return str(temp_output)
            else:
                if log_callback:
                    log_callback(
                        "\n💡 If you see missing dependencies errors:\n"
                        "   1. Open terminal in ProPainter directory\n"
                        "   2. Activate venv: venv\\Scripts\\activate\n"
                        "   3. Install missing packages:\n"
                        "      pip install av\n"
                        "      (PyAV is required for video I/O)\n"
                    )
                return None

        except Exception as e:
            if log_callback:
                log_callback(f"❌ ProPainter preprocessing error: {e}\n")
            return None

    def _cleanup_temp_files(self):
        """
        Clean up temporary files and directories created during processing.

        Optimization: Uses set for efficient iteration
        """
        for temp_path in self._temp_files:
            try:
                temp_path = Path(temp_path)  # Convert to Path if string
                if temp_path.exists():
                    if temp_path.is_dir():
                        shutil.rmtree(temp_path)
                    else:
                        temp_path.unlink()
            except Exception:
                pass
        self._temp_files.clear()
    
    def _cleanup_gpu_memory(self):
        """
        Clean up GPU memory to prevent VRAM leaks.
        Should be called after each processing session.
        """
        try:
            from .gpu_accelerator import GPUAccelerator
            gpu = GPUAccelerator()
            if gpu.is_available():
                # Log VRAM usage before cleanup
                vram_before = gpu.get_vram_usage()
                print(f"[GPU] VRAM before cleanup: {vram_before.get('used_gb', 0):.2f} GB used, "
                      f"{vram_before.get('free_gb', 0):.2f} GB free")
                
                # Clear cache
                gpu.clear_cache()
                
                # Log VRAM usage after cleanup
                vram_after = gpu.get_vram_usage()
                freed = vram_before.get('used_gb', 0) - vram_after.get('used_gb', 0)
                print(f"[GPU] VRAM after cleanup: {vram_after.get('used_gb', 0):.2f} GB used, "
                      f"{vram_after.get('free_gb', 0):.2f} GB free (freed {freed:.2f} GB)")
        except Exception as e:
            # GPU cleanup is optional, don't fail if unavailable
            import warnings
            warnings.warn(f"GPU memory cleanup warning: {e}")
        
        # Force Python garbage collection
        import gc
        gc.collect()

    def get_video_info(self, input_file: str) -> dict:
        """
        Get comprehensive video information with caching.

        Optimization: Uses cached video_info to avoid redundant ffprobe calls

        Returns:
            dict: Video metadata including codec, resolution, fps, etc.
        """
        width, height, par, frame_count, fps = self._get_cached_video_info(input_file)
        codec_info = self.analyzer.get_codec_info(input_file)

        return {
            "width": width,
            "height": height,
            "par": par,
            "frame_count": frame_count,
            "fps": fps,
            "codec_name": codec_info.get("codec_name"),
            "codec_long_name": codec_info.get("codec_long_name"),
            "pix_fmt": codec_info.get("pix_fmt"),
        }
