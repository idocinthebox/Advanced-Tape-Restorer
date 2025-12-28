"""
Capture Device Manager - Detect and manage video capture devices
"""

import subprocess
import sys
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class CaptureDevice:
    """Represents a video capture device."""

    index: int
    name: str
    device_type: str  # 'analog', 'dv', 'hdmi', 'unknown'
    backend: str  # 'directshow', 'dshow', 'avfoundation', etc.
    path: str  # Device path/identifier

    def __str__(self):
        return f"[{self.index}] {self.name} ({self.device_type})"


class CaptureDeviceManager:
    """Detect and manage video capture devices."""

    def __init__(self):
        self.devices: list[CaptureDevice] = []
        self.refresh_devices()

    def refresh_devices(self) -> list[CaptureDevice]:
        """
        Scan for available capture devices.

        Returns:
            List of detected capture devices
        """
        self.devices = []

        if sys.platform == "win32":
            self.devices = self._detect_directshow_devices()
        elif sys.platform == "darwin":
            self.devices = self._detect_avfoundation_devices()
        else:
            self.devices = self._detect_v4l2_devices()

        return self.devices

    def _detect_directshow_devices(self) -> list[CaptureDevice]:
        """Detect DirectShow devices on Windows."""
        devices = []

        try:
            # Use ffmpeg to list DirectShow devices
            cmd = ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"]
            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                cmd, capture_output=True, text=True, creationflags=cflags
            )

            # Parse stderr for device list
            stderr = result.stderr
            video_devices = []

            # Extract video input devices
            in_video_section = False
            for line in stderr.split("\n"):
                if "DirectShow video devices" in line:
                    in_video_section = True
                    continue
                elif "DirectShow audio devices" in line:
                    in_video_section = False
                    break

                if in_video_section:
                    # Match lines like: [dshow @ 000...] "USB Video Device"
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        device_name = match.group(1)
                        video_devices.append(device_name)

            # Create device objects
            for idx, name in enumerate(video_devices):
                device_type = self._identify_device_type(name)
                devices.append(
                    CaptureDevice(
                        index=idx,
                        name=name,
                        device_type=device_type,
                        backend="directshow",
                        path=f'video="{name}"',
                    )
                )

        except Exception as e:
            print(f"Device detection failed: {e}")

        return devices

    def _detect_avfoundation_devices(self) -> list[CaptureDevice]:
        """Detect AVFoundation devices on macOS."""
        # Placeholder for macOS support
        devices = []
        # TODO: Implement AVFoundation device detection
        return devices

    def _detect_v4l2_devices(self) -> list[CaptureDevice]:
        """Detect Video4Linux2 devices on Linux."""
        # Placeholder for Linux support
        devices = []
        # TODO: Implement V4L2 device detection
        return devices

    def _identify_device_type(self, device_name: str) -> str:
        """
        Identify device type based on name.

        Args:
            device_name: Name of the device

        Returns:
            Device type: 'analog', 'dv', 'hdmi', 'unknown'
        """
        name_lower = device_name.lower()

        # DV/Firewire devices
        if any(
            keyword in name_lower for keyword in ["dv", "firewire", "1394", "ieee1394"]
        ):
            return "dv"

        # Analog capture cards
        if any(
            keyword in name_lower
            for keyword in [
                "composite",
                "svideo",
                "s-video",
                "capture card",
                "analog",
                "hauppauge",
                "pinnacle",
                "ati",
                "tv tuner",
                "video capture",
            ]
        ):
            return "analog"

        # HDMI/Digital capture
        if any(
            keyword in name_lower
            for keyword in ["hdmi", "sdi", "blackmagic", "elgato", "avermedia"]
        ):
            return "hdmi"

        # Webcams (probably not useful for tape capture)
        if any(keyword in name_lower for keyword in ["webcam", "camera", "usb video"]):
            return "webcam"

        return "unknown"

    def get_device_by_index(self, index: int) -> Optional[CaptureDevice]:
        """Get device by index."""
        for device in self.devices:
            if device.index == index:
                return device
        return None

    def get_devices_by_type(self, device_type: str) -> list[CaptureDevice]:
        """Get all devices of a specific type."""
        return [d for d in self.devices if d.device_type == device_type]

    def get_analog_devices(self) -> list[CaptureDevice]:
        """Get all analog capture devices."""
        return self.get_devices_by_type("analog")

    def get_dv_devices(self) -> list[CaptureDevice]:
        """Get all DV/Firewire devices."""
        return self.get_devices_by_type("dv")
