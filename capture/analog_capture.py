"""
Analog Capture Engine - Capture from analog sources (VHS, Hi8, etc.)
"""

import subprocess
import sys
from typing import Callable, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AnalogCaptureSettings:
    """Settings for analog video capture."""

    device_name: str
    resolution: str = "720x480"  # NTSC default
    framerate: str = "29.97"
    codec: str = "huffyuv"  # Lossless codec
    pixel_format: str = "yuv422p"
    audio_device: Optional[str] = None
    audio_channels: int = 2
    duration: Optional[int] = None  # Seconds, None = manual stop
    # Crossbar settings (input source selection)
    video_input_pin: Optional[int] = None  # 0=Composite, 1=S-Video, 2=Component, etc.
    audio_input_pin: Optional[int] = None  # Audio input pin (usually matches video)


class AnalogCaptureEngine:
    """Capture engine for analog video sources."""

    # Standard crossbar input mappings (DirectShow)
    VIDEO_INPUTS = {
        "composite": 0,
        "s-video": 1,
        "svideo": 1,
        "component": 2,
        "tuner": 3,
        "hdmi": 4,
    }

    # Human-readable input names for GUI
    INPUT_NAMES = {
        0: "Composite (RCA)",
        1: "S-Video (Y/C)",
        2: "Component (YPbPr)",
        3: "TV Tuner",
        4: "HDMI/Digital",
    }

    CODEC_PRESETS = {
        "huffyuv": {"codec": "huffyuv", "pix_fmt": "yuv422p", "extension": ".avi"},
        "lagarith": {"codec": "lagarith", "pix_fmt": "yuv422p", "extension": ".avi"},
        "ffv1": {
            "codec": "ffv1",
            "level": "3",
            "pix_fmt": "yuv422p",
            "extension": ".mkv",
        },
        "utvideo": {"codec": "utvideo", "pix_fmt": "yuv422p", "extension": ".avi"},
    }

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_capturing = False

    def build_capture_command(
        self, settings: AnalogCaptureSettings, output_file: str
    ) -> list:
        """
        Build FFmpeg capture command for analog sources.

        Args:
            settings: Capture settings
            output_file: Output file path

        Returns:
            FFmpeg command as list
        """
        codec_config = self.CODEC_PRESETS.get(
            settings.codec.lower(), self.CODEC_PRESETS["huffyuv"]
        )

        cmd = [
            "ffmpeg",
            "-f",
            "dshow",
            "-video_size",
            settings.resolution,
            "-framerate",
            settings.framerate,
            "-pixel_format",
            settings.pixel_format,
        ]

        # Add crossbar input selection if specified
        if settings.video_input_pin is not None:
            cmd.extend(
                ["-crossbar_video_input_pin_number", str(settings.video_input_pin)]
            )

        if settings.audio_input_pin is not None:
            cmd.extend(
                ["-crossbar_audio_input_pin_number", str(settings.audio_input_pin)]
            )

        cmd.extend(["-i", settings.device_name])

        # Add audio if specified
        if settings.audio_device:
            cmd.extend(
                [
                    "-f",
                    "dshow",
                    "-i",
                    f"audio={settings.audio_device}",
                    "-ac",
                    str(settings.audio_channels),
                ]
            )

        # Duration limit
        if settings.duration:
            cmd.extend(["-t", str(settings.duration)])

        # Video codec
        cmd.extend(["-c:v", codec_config["codec"], "-pix_fmt", codec_config["pix_fmt"]])

        # FFV1-specific options
        if codec_config["codec"] == "ffv1":
            cmd.extend(["-level", codec_config["level"]])

        # Audio codec (if present)
        if settings.audio_device:
            cmd.extend(["-c:a", "pcm_s16le"])

        cmd.extend(["-y", output_file])

        return cmd

    def start_capture(
        self,
        settings: AnalogCaptureSettings,
        output_file: str,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Start analog video capture.

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
                log_callback(f"Starting analog capture...\n")
                log_callback(f"Device: {settings.device_name}\n")
                log_callback(f"Resolution: {settings.resolution}\n")
                log_callback(f"Codec: {settings.codec}\n")
                log_callback(f"Output: {output_file}\n\n")

            # Start capture process
            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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
        Stop ongoing capture.

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
                log_callback("\nStopping capture...\n")

            # Send 'q' to FFmpeg to gracefully stop
            if self.process.stdin:
                self.process.stdin.write("q")
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

    def get_capture_stats(self) -> Optional[dict]:
        """
        Get current capture statistics.

        Returns:
            dict: Capture stats (frames, duration, filesize) or None
        """
        if not self.is_capturing or not self.process:
            return None

        # TODO: Parse FFmpeg stderr for progress stats
        # This would require monitoring stderr in a separate thread
        return {"status": "capturing", "frames": 0, "duration": 0.0}

    def get_available_inputs(self) -> dict[int, str]:
        """
        Get list of commonly available video inputs for analog capture cards.

        Returns:
            dict: Mapping of input pin numbers to human-readable names

        Note:
            DirectShow doesn't provide a standard way to enumerate crossbar inputs
            via FFmpeg. This returns the standard input layout for most capture cards.

            Most analog capture cards support:
            - Pin 0: Composite (RCA yellow connector)
            - Pin 1: S-Video (Y/C connector)

            Professional cards may also have:
            - Pin 2: Component (YPbPr)
            - Pin 3: TV Tuner
            - Pin 4: HDMI/Digital input
        """
        return self.INPUT_NAMES.copy()

    def get_common_inputs(self) -> dict[int, str]:
        """
        Get common input options for typical consumer capture cards.

        Returns:
            dict: Most common inputs (Composite and S-Video)
        """
        return {0: "Composite (RCA)", 1: "S-Video (Y/C)"}

    @staticmethod
    def get_input_pin_by_name(input_name: str) -> Optional[int]:
        """
        Get input pin number from input name.

        Args:
            input_name: Input name (e.g., 'composite', 's-video', 'svideo')

        Returns:
            int: Pin number or None if not found
        """
        name_lower = input_name.lower().strip()
        return AnalogCaptureEngine.VIDEO_INPUTS.get(name_lower)

    @staticmethod
    def get_input_name(pin_number: int) -> str:
        """
        Get human-readable name for input pin number.

        Args:
            pin_number: Input pin number

        Returns:
            str: Human-readable input name or 'Unknown Input'
        """
        return AnalogCaptureEngine.INPUT_NAMES.get(pin_number, f"Input {pin_number}")
