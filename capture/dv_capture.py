"""
DV Capture Engine - Capture from DV/miniDV sources via FireWire
"""

import subprocess
import sys
from typing import Callable, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class DVCaptureSettings:
    """Settings for DV video capture."""

    device_name: str
    format: str = "dv"  # 'dv' or 'hdv'
    codec: str = (
        "copy"  # 'copy' preserves DV stream, or 'huffyuv' for lossless transcode
    )
    duration: Optional[int] = None  # Seconds, None = manual stop


class DVCaptureEngine:
    """Capture engine for DV/miniDV sources via FireWire (IEEE 1394)."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_capturing = False

    def build_capture_command(
        self, settings: DVCaptureSettings, output_file: str
    ) -> list:
        """
        Build FFmpeg capture command for DV sources.

        Args:
            settings: Capture settings
            output_file: Output file path

        Returns:
            FFmpeg command as list
        """
        # DV capture via DirectShow (Windows) or FireWire
        cmd = ["ffmpeg", "-f", "dshow", "-i", settings.device_name]

        # Duration limit
        if settings.duration:
            cmd.extend(["-t", str(settings.duration)])

        # Codec handling
        if settings.codec.lower() == "copy":
            # Stream copy preserves DV format
            cmd.extend(["-c:v", "copy", "-c:a", "copy"])
            # DV output should be .dv or .avi
            if not output_file.lower().endswith((".dv", ".avi")):
                output_file = str(Path(output_file).with_suffix(".avi"))
        else:
            # Transcode to lossless codec
            cmd.extend(
                ["-c:v", settings.codec, "-pix_fmt", "yuv422p", "-c:a", "pcm_s16le"]
            )

        cmd.extend(["-y", output_file])

        return cmd

    def start_capture(
        self,
        settings: DVCaptureSettings,
        output_file: str,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Start DV video capture.

        Args:
            settings: Capture settings
            output_file: Output file path
            log_callback: Function(message) for log messages

        Returns:
            bool: True if capture started successfully
        """
        if self.is_capturing:
            if log_callback:
                log_callback("Capture already in progress\n")
            return False

        try:
            # Ensure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd = self.build_capture_command(settings, output_file)

            if log_callback:
                log_callback(f"Starting DV capture...\n")
                log_callback(f"Device: {settings.device_name}\n")
                log_callback(f"Format: {settings.format}\n")
                log_callback(f"Codec: {settings.codec}\n")
                log_callback(f"Output: {output_file}\n\n")

            # Start capture process
            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=cflags,
            )

            self.is_capturing = True

            if log_callback:
                log_callback("✅ Capture started successfully\n")

            return True

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Failed to start capture: {str(e)}\n")
            return False

    def stop_capture(
        self, log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Stop ongoing DV capture.

        Args:
            log_callback: Function(message) for log messages

        Returns:
            bool: True if stopped successfully
        """
        if not self.is_capturing or not self.process:
            if log_callback:
                log_callback("No capture in progress\n")
            return False

        try:
            if log_callback:
                log_callback("\nStopping DV capture...\n")

            # Send 'q' to FFmpeg to gracefully stop
            if self.process.stdin:
                self.process.stdin.write("q\n")
                self.process.stdin.flush()

            # Wait for process to finish
            self.process.wait(timeout=10)

            self.is_capturing = False

            if log_callback:
                log_callback("✅ Capture stopped successfully\n")

            return True

        except subprocess.TimeoutExpired:
            # Force kill if graceful stop fails
            if self.process:
                self.process.kill()
            self.is_capturing = False
            if log_callback:
                log_callback("⚠ Capture force-stopped\n")
            return True

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Error stopping capture: {str(e)}\n")
            return False

    def get_timecode(self) -> Optional[str]:
        """
        Get current DV timecode from capture stream.

        Returns:
            str: Timecode (HH:MM:SS:FF) or None
        """
        # TODO: Parse DV timecode from stream
        # This requires analyzing the DV stream data
        return None

    def detect_format(self, device_name: str) -> str:
        """
        Auto-detect if source is DV or HDV.

        Args:
            device_name: DV device name

        Returns:
            str: 'dv' or 'hdv'
        """
        # TODO: Probe device to detect format
        # For now, default to DV
        return "dv"
