"""
ProPainter Integration Module - AI Video Inpainting
Handles external ProPainter CLI tool for artifact/damage removal

Performance Optimizations:
- Pre-compiled regex patterns for faster frame/progress parsing
- __slots__ for reduced memory footprint
- Module-level constants for memory presets
- Efficient subprocess handling
"""

import subprocess
import re
import time
from pathlib import Path
from typing import Optional, Callable, Dict

# Pre-compiled regex patterns for faster parsing
_FRAME_REGEX = re.compile(r"\[(\d+)\s+frames?\]", re.IGNORECASE)
_FRAME_REGEX_ALT = re.compile(r"(\d+)\s+(?:video\s+)?frames", re.IGNORECASE)
_PROGRESS_SLASH = re.compile(r"(\d+)/(\d+)")
_PROGRESS_PERCENT = re.compile(r"(\d+)%")
_FRAME_WORD = re.compile(r"frame[:\s]+(\d+)", re.IGNORECASE)

# Keywords for filtering output
_IMPORTANT_KEYWORDS = frozenset(["error", "warning", "completed", "done", "saving"])


class ProPainterEngine:
    """
    Interface to ProPainter for AI video inpainting.
    
    Optimizations: __slots__, module-level regex, efficient subprocess handling
    """
    
    __slots__ = ('propainter_path', 'inference_script', 'gpu_info')

    # Memory presets for different hardware configurations (class constant)
    MEMORY_PRESETS = {
        "auto": {
            "name": "Auto (Detect GPU)",
            "neighbor_length": None,  # Will be set based on GPU
            "ref_stride": None,
            "subvideo_length": None,
            "raft_iter": None,
        },
        "low": {
            "name": "Low (4-8GB VRAM / 8GB RAM)",
            "neighbor_length": 2,
            "ref_stride": 50,
            "subvideo_length": 8,
            "raft_iter": 6,
        },
        "medium": {
            "name": "Medium (8-12GB VRAM / 16GB RAM)",
            "neighbor_length": 4,
            "ref_stride": 40,
            "subvideo_length": 15,
            "raft_iter": 8,
        },
        "high": {
            "name": "High (12-16GB VRAM / 32GB RAM)",
            "neighbor_length": 6,
            "ref_stride": 30,
            "subvideo_length": 25,
            "raft_iter": 10,
        },
        "ultra": {
            "name": "Ultra (24GB+ VRAM / 64GB+ RAM)",
            "neighbor_length": 8,
            "ref_stride": 20,
            "subvideo_length": 40,
            "raft_iter": 12,
        },
    }

    def __init__(self, propainter_path: Optional[str] = None):
        """
        Initialize ProPainter engine.

        Args:
            propainter_path: Path to ProPainter installation directory
                           If None, tries to auto-detect from common locations
        """
        print(f"[DEBUG] ProPainterEngine.__init__ received path: {propainter_path}")
        self.propainter_path = self._find_propainter_path(propainter_path)
        print(f"[DEBUG] ProPainterEngine found path: {self.propainter_path}")
        self.inference_script = None
        self.gpu_info = None

        if self.propainter_path:
            self.inference_script = self.propainter_path / "inference_propainter.py"
            print(f"[DEBUG] ProPainterEngine inference script: {self.inference_script}")
            self.gpu_info = self._detect_gpu()

    def _find_propainter_path(self, custom_path: Optional[str]) -> Optional[Path]:
        """Try to find ProPainter installation. Optimization: Early returns, single check."""
        if custom_path:
            path = Path(custom_path)
            if path.exists():
                return path

        # Check common installation locations
        for base in (Path.home(), Path.home() / "Documents", Path("C:/"), Path("C:/Program Files")):
            path = base / "ProPainter"
            if path.exists() and (path / "inference_propainter.py").exists():
                return path

        return None

    def _find_venv_python(self) -> Optional[str]:
        """Find Python interpreter in ProPainter's virtual environment. Optimization: Tuple iteration."""
        if not self.propainter_path:
            return None

        # Check common venv locations (Windows: Scripts/python.exe, Unix: bin/python)
        for base_dir in (self.propainter_path, self.propainter_path.parent):
            for subpath in (("venv", "Scripts", "python.exe"), ("venv", "bin", "python")):
                venv_python = base_dir.joinpath(*subpath)
                if venv_python.exists():
                    print(f"[DEBUG] Found venv Python: {venv_python}")
                    return str(venv_python)

        print(f"[DEBUG] No venv found, using system Python")
        return None

    def _detect_gpu(self) -> Optional[dict]:
        """Detect GPU and VRAM for auto memory preset selection."""
        try:
            # Try nvidia-smi first
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW
                    if hasattr(subprocess, "CREATE_NO_WINDOW")
                    else 0
                ),
            )

            if result.returncode == 0 and result.stdout.strip():
                line = result.stdout.strip().split("\n")[0]
                parts = line.split(",")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    vram_str = parts[1].strip().split()[0]  # "11264 MiB" -> "11264"
                    vram_gb = int(vram_str) / 1024

                    print(f"[DEBUG] Detected GPU: {name} ({vram_gb:.1f} GB VRAM)")
                    return {"name": name, "vram_gb": vram_gb}
        except Exception as e:
            print(f"[DEBUG] GPU detection failed: {e}")

        return None

    def get_recommended_preset(self) -> str:
        """Get recommended memory preset based on detected GPU."""
        if not self.gpu_info:
            return "low"  # Conservative default if no GPU detected

        vram_gb = self.gpu_info.get("vram_gb", 0)

        if vram_gb >= 20:
            return "ultra"
        elif vram_gb >= 12:
            return "high"
        elif vram_gb >= 8:
            return "medium"
        else:
            return "low"

    def is_available(self) -> bool:
        """Check if ProPainter is installed and ready."""
        print(f"[DEBUG] is_available() check:")
        print(f"  propainter_path: {self.propainter_path}")

        if not self.propainter_path:
            print(f"  ❌ No ProPainter path set")
            return False

        print(f"  inference_script: {self.inference_script}")
        if not self.inference_script or not self.inference_script.exists():
            print(f"  ❌ Inference script not found")
            return False

        # Check for required weights
        weights_dir = self.propainter_path / "weights"
        print(f"  weights_dir: {weights_dir}")
        print(f"  weights_dir.exists(): {weights_dir.exists()}")

        if not weights_dir.exists():
            print(f"  ⚠️ Weights directory not found (will auto-download on first use)")
            # Don't fail - ProPainter can auto-download weights
            return True

        required_weights = [
            "ProPainter.pth",
            "recurrent_flow_completion.pth",
            "raft-things.pth",
        ]
        for weight in required_weights:
            weight_path = weights_dir / weight
            exists = weight_path.exists()
            print(f"  {weight}: {'✓' if exists else '✗'}")
            if not exists:
                print(f"  ⚠️ Weight missing but will auto-download: {weight}")

        # Return True even if weights missing - ProPainter downloads them
        return True

    def process_video(
        self,
        input_video: str,
        output_video: str,
        mode: str = "auto_detect",
        mask_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        use_fp16: bool = True,
        memory_preset: str = "auto",
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Process video with ProPainter.

        Args:
            input_video: Path to input video file
            output_video: Path to save processed video
            mode: Processing mode:
                  - "auto_detect": Automatically detect and remove artifacts
                  - "object_removal": Remove objects (requires mask)
                  - "video_completion": Fill missing areas (requires mask)
            mask_path: Path to mask file/directory (required for object_removal/video_completion)
            width: Output video width (optional, for memory management)
            height: Output video height (optional, for memory management)
            use_fp16: Use half precision to save GPU memory
            log_callback: Function to call with log messages

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            if log_callback:
                log_callback("❌ ProPainter not installed or not configured properly")
            return False

        # Simple warning about memory usage (avoid ctypes during processing)
        if log_callback and memory_preset in ["high", "ultra"]:
            log_callback(
                f"⚠️  Using {memory_preset.upper()} preset - ensure you have sufficient RAM/VRAM\n"
            )
            log_callback(
                f"   If system becomes unresponsive, use LOW or MEDIUM preset instead\n"
            )

        try:
            # Find venv Python (prefer venv over system Python)
            venv_python = self._find_venv_python()
            python_cmd = venv_python if venv_python else "python"

            if log_callback:
                log_callback(f"Using Python: {python_cmd}\n")

            # Build command
            cmd = [
                python_cmd,
                str(self.inference_script),
                "--video",
                input_video,
                "--output",
                output_video,
            ]

            # Add mode-specific parameters
            if mode == "object_removal" or mode == "video_completion":
                if not mask_path:
                    if log_callback:
                        log_callback(f"❌ Mask required for {mode} mode")
                    return False
                cmd.extend(["--mask", mask_path])
            elif mode == "auto_detect":
                # Auto-detect mode also needs masks to identify what to fix
                if not mask_path:
                    if log_callback:
                        log_callback("⚠️  Auto-detect mode requires mask files")
                        log_callback(
                            "   Without masks, ProPainter doesn't know what to fix"
                        )
                    return False
                cmd.extend(["--mask", mask_path])

            # Add optional parameters
            if width:
                cmd.extend(["--width", str(width)])
            if height:
                cmd.extend(["--height", str(height)])
            if use_fp16:
                cmd.append("--fp16")

            # Apply memory preset
            if memory_preset == "auto":
                memory_preset = self.get_recommended_preset()
                if log_callback:
                    log_callback(
                        f"🔍 Auto-detected GPU: {self.gpu_info.get('name', 'Unknown') if self.gpu_info else 'None'}\n"
                    )
                    log_callback(
                        f"📊 Recommended preset: {
                            memory_preset.upper()} ({
                            self.MEMORY_PRESETS[memory_preset]['name']})\n"
                    )

            preset = self.MEMORY_PRESETS.get(memory_preset, self.MEMORY_PRESETS["low"])

            cmd.extend(
                [
                    "--neighbor_length",
                    str(preset["neighbor_length"]),
                    "--ref_stride",
                    str(preset["ref_stride"]),
                    "--subvideo_length",
                    str(preset["subvideo_length"]),
                    "--raft_iter",
                    str(preset["raft_iter"]),
                ]
            )

            if log_callback:
                log_callback(f"⚙️  Memory preset: {preset['name']}\n")
                log_callback(
                    f"   neighbor_length={preset['neighbor_length']}, ref_stride={preset['ref_stride']}, "
                    f"subvideo_length={preset['subvideo_length']}, raft_iter={preset['raft_iter']}\n"
                )

            if log_callback:
                log_callback(f"🎨 Starting ProPainter processing...\n")
                log_callback(f"Command: {' '.join(cmd)}\n")

            # Run ProPainter (imports at module level for speed)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.propainter_path),
                bufsize=1,
            )

            # Track progress
            start_time = time.time()
            total_frames = None
            current_frame = 0
            processing_started = False

            # Stream output with progress tracking (use pre-compiled regex)
            for line in process.stdout:
                line_stripped = line.strip()

                # Detect weight loading
                if "Loading" in line_stripped or "Downloading" in line_stripped:
                    if log_callback:
                        log_callback(f"⬇️  {line_stripped}\n")

                # Detect processing start
                elif (
                    "video frames" in line_stripped.lower()
                    or "total frames" in line_stripped.lower()
                    or "processing:" in line_stripped.lower()
                ):
                    processing_started = True
                    # Extract frame count using pre-compiled regex
                    match = _FRAME_REGEX.search(line_stripped)
                    if not match:
                        match = _FRAME_REGEX_ALT.search(line_stripped)
                    if match:
                        total_frames = int(match.group(1))
                        if log_callback:
                            log_callback(f"📊 Processing {total_frames} frames\n")

                # Track frame progress with pre-compiled regex (optimized parsing)
                elif processing_started:
                    # Pattern 1: "100/252" style (pre-compiled)
                    frame_match = _PROGRESS_SLASH.search(line_stripped)
                    if frame_match:
                        current_frame = int(frame_match.group(1))
                        if not total_frames:
                            total_frames = int(frame_match.group(2))

                    # Pattern 2: Percentage-based progress bar
                    elif total_frames:
                        percent_match = _PROGRESS_PERCENT.search(line_stripped)
                        if percent_match:
                            progress_pct = int(percent_match.group(1))
                            current_frame = int((progress_pct / 100) * total_frames)
                            frame_match = percent_match

                    # Pattern 3: "frame 100" style (pre-compiled)
                    if not frame_match:
                        frame_match = _FRAME_WORD.search(line_stripped)
                        if frame_match:
                            current_frame = int(frame_match.group(1))

                    if frame_match and total_frames and current_frame > 0:
                        progress = (current_frame / total_frames) * 100
                        elapsed = time.time() - start_time
                        fps = current_frame / elapsed if elapsed > 0 else 0

                        # Only show progress every 5% to avoid spam
                        if (
                            current_frame % max(1, total_frames // 20) == 0
                            or current_frame == total_frames
                        ):
                            if total_frames > current_frame:
                                remaining_frames = total_frames - current_frame
                                eta_seconds = remaining_frames / fps if fps > 0 else 0
                                eta_mins = int(eta_seconds / 60)
                                eta_secs = int(eta_seconds % 60)

                                if log_callback:
                                    log_callback(
                                        f"  🎨 ProPainter: {progress:.1f}% ({current_frame}/{total_frames}) | {fps:.2f} fps | ETA: {eta_mins}m {eta_secs}s\n"
                                    )
                            else:
                                if log_callback:
                                    log_callback(
                                        f"  🎨 ProPainter: {progress:.1f}% ({current_frame}/{total_frames}) | {fps:.2f} fps\n"
                                    )

                # Show other important messages (use frozenset for fast lookup)
                elif line_stripped and not line_stripped.startswith("["):
                    lower_line = line_stripped.lower()
                    if any(kw in lower_line for kw in _IMPORTANT_KEYWORDS):
                        if log_callback:
                            log_callback(f"  {line_stripped}\n")

            process.wait()

            if process.returncode == 0:
                elapsed = time.time() - start_time
                if log_callback:
                    log_callback(
                        f"\n✅ ProPainter completed in {elapsed:.1f}s ({elapsed / 60:.1f} minutes)\n"
                    )
                return True
            else:
                if log_callback:
                    log_callback(
                        f"\n❌ ProPainter failed with exit code {process.returncode}\n"
                    )
                return False

        except Exception as e:
            if log_callback:
                log_callback(f"❌ ProPainter error: {e}")
            return False

    def create_auto_mask(
        self,
        video_path: str,
        output_mask_dir: str,
        detection_mode: str = "scratches",
        sensitivity: float = 0.5,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Create automatic mask for artifact detection.

        Detects and masks:
        - Scratches: Vertical/horizontal line artifacts
        - Dropouts: Missing data areas (brightness anomalies)
        - Noise: High-frequency speckles and grain
        - All: Combined detection

        Args:
            video_path: Input video file
            output_mask_dir: Output directory for mask image frames (required by ProPainter)
            detection_mode: "scratches", "dropouts", "noise", or "all"
            sensitivity: Detection sensitivity 0.0-1.0 (higher = more aggressive)
            log_callback: Log function

        Returns:
            True if successful
        """
        try:
            import cv2
            import numpy as np

            if log_callback:
                log_callback(
                    f"🔍 Auto-generating mask ({detection_mode} detection, sensitivity={sensitivity:.1f})..."
                )

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                if log_callback:
                    log_callback("❌ Could not open video file")
                return False

            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Create output directory for mask frames
            mask_dir = Path(output_mask_dir)
            mask_dir.mkdir(parents=True, exist_ok=True)

            if log_callback:
                log_callback(f"Processing {total_frames} frames...")

            frame_idx = 0
            prev_frame = None
            frames_buffer = []  # For temporal analysis

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Initialize combined mask
                combined_mask = np.zeros((height, width), dtype=np.uint8)

                # Detect scratches (vertical/horizontal lines)
                if detection_mode in ["scratches", "all"]:
                    # Sobel edge detection for vertical lines
                    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                    sobelx = np.absolute(sobelx)
                    sobelx = np.uint8(sobelx)

                    # Sobel edge detection for horizontal lines
                    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                    sobely = np.absolute(sobely)
                    sobely = np.uint8(sobely)

                    # Threshold based on sensitivity
                    threshold_val = int(255 * (1.0 - sensitivity))
                    _, scratch_mask_v = cv2.threshold(
                        sobelx, threshold_val, 255, cv2.THRESH_BINARY
                    )
                    _, scratch_mask_h = cv2.threshold(
                        sobely, threshold_val, 255, cv2.THRESH_BINARY
                    )

                    # Combine vertical and horizontal
                    scratch_mask = cv2.bitwise_or(scratch_mask_v, scratch_mask_h)

                    # Morphological operations to connect scratches
                    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
                    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
                    scratch_mask = cv2.morphologyEx(
                        scratch_mask, cv2.MORPH_CLOSE, kernel_v
                    )
                    scratch_mask = cv2.morphologyEx(
                        scratch_mask, cv2.MORPH_CLOSE, kernel_h
                    )

                    combined_mask = cv2.bitwise_or(combined_mask, scratch_mask)

                # Detect dropouts (brightness anomalies)
                if detection_mode in ["dropouts", "all"]:
                    # Find very dark or very bright areas
                    _, dark_mask = cv2.threshold(
                        gray, int(30 * sensitivity), 255, cv2.THRESH_BINARY_INV
                    )
                    _, bright_mask = cv2.threshold(
                        gray, int(255 - 30 * sensitivity), 255, cv2.THRESH_BINARY
                    )

                    dropout_mask = cv2.bitwise_or(dark_mask, bright_mask)

                    # Remove small noise
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                    dropout_mask = cv2.morphologyEx(
                        dropout_mask, cv2.MORPH_OPEN, kernel
                    )
                    dropout_mask = cv2.morphologyEx(
                        dropout_mask, cv2.MORPH_CLOSE, kernel
                    )

                    combined_mask = cv2.bitwise_or(combined_mask, dropout_mask)

                # Detect temporal anomalies (frame differences)
                if detection_mode in ["noise", "all"] and prev_frame is not None:
                    # Frame difference
                    diff = cv2.absdiff(gray, prev_frame)

                    # Threshold based on sensitivity
                    threshold_val = int(50 * sensitivity)
                    _, diff_mask = cv2.threshold(
                        diff, threshold_val, 255, cv2.THRESH_BINARY
                    )

                    # Remove small noise, keep significant anomalies
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_OPEN, kernel)

                    combined_mask = cv2.bitwise_or(combined_mask, diff_mask)

                # Dilate mask slightly to ensure coverage
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                combined_mask = cv2.dilate(combined_mask, kernel, iterations=2)

                # Save mask frame as PNG (ProPainter expects image frames, not video)
                mask_filename = mask_dir / f"{frame_idx:05d}.png"
                cv2.imwrite(str(mask_filename), combined_mask)

                prev_frame = gray.copy()
                frame_idx += 1

                # Progress update every 30 frames
                if frame_idx % 30 == 0 and log_callback:
                    progress = (frame_idx / total_frames) * 100
                    log_callback(
                        f"  Mask generation: {progress:.1f}% ({frame_idx}/{total_frames} frames)"
                    )

            cap.release()

            if log_callback:
                log_callback(f"✅ Auto-mask created: {mask_dir}")
                log_callback(f"   {frame_idx} PNG frames saved")

            return True

        except ImportError:
            if log_callback:
                log_callback("❌ OpenCV not available for auto-masking")
            return False
        except Exception as e:
            if log_callback:
                log_callback(f"❌ Auto-mask error: {e}")
            return False

    def get_installation_guide(self) -> str:
        """Get installation instructions for ProPainter."""
        return """
ProPainter Installation Guide
=============================

1. Clone Repository:
   git clone https://github.com/sczhou/ProPainter.git
   cd ProPainter

2. Create Conda Environment:
   conda create -n propainter python=3.8 -y
   conda activate propainter

3. Install Dependencies:
   pip install -r requirements.txt

4. Download Pretrained Models:
   Models will auto-download on first use, or download manually from:
   https://github.com/sczhou/ProPainter/releases/tag/v0.1.0

   Place in weights/ folder:
   - ProPainter.pth
   - recurrent_flow_completion.pth
   - raft-things.pth

5. Test Installation:
   python inference_propainter.py --video inputs/object_removal/bmx-trees --mask inputs/object_removal/bmx-trees_mask

6. Configure in Application:
   Set ProPainter path in settings to your installation directory.

Requirements:
- CUDA >= 9.2
- PyTorch >= 1.7.1
- GPU with 8GB+ VRAM (16GB recommended for HD)

GPU Memory Requirements:
- 640x480: 10-12 GB
- 720x480: 11-13 GB
- 1280x720: 25-28 GB
- Use --fp16 flag to reduce memory usage by ~30%
"""

    def get_gpu_requirements(
        self, width: int, height: int, use_fp16: bool = True
    ) -> dict:
        """
        Estimate GPU memory requirements for given resolution.

        Args:
            width: Video width
            height: Video height
            use_fp16: Whether using half precision

        Returns:
            Dict with estimated VRAM requirements
        """
        # Rough estimates based on ProPainter documentation
        pixel_count = width * height

        if pixel_count <= 320 * 240:
            vram = 2 if use_fp16 else 3
        elif pixel_count <= 640 * 480:
            vram = 6 if use_fp16 else 10
        elif pixel_count <= 720 * 480:
            vram = 7 if use_fp16 else 11
        elif pixel_count <= 1280 * 720:
            vram = 19 if use_fp16 else 28
        else:
            vram = 25 if use_fp16 else 35

        return {
            "estimated_vram_gb": vram,
            "recommended_vram_gb": vram + 2,
            "use_fp16": use_fp16,
            "resolution": f"{width}x{height}",
        }
