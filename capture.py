"""
Advanced Tape Restorer v4.0 - Capture Module

Contains classes for detecting and managing video capture devices.
Supports real hardware via DirectShow (Windows) and FireWire/DV.
"""

import subprocess
import re
import sys
from typing import List, Dict, Optional


class CaptureDevice:
    """A data class to hold information about a capture device."""

    def __init__(self, name: str, device_type: str, ffmpeg_name: str, 
                 alternative_name: str = None, audio_device: str = None):
        """
        Initializes a CaptureDevice.

        Args:
            name (str): The user-friendly name of the device.
            device_type (str): The type of device, e.g., 'analog' or 'dv'.
            ffmpeg_name (str): The name used by FFmpeg to identify the device.
            alternative_name (str): Alternative device name if detected.
            audio_device (str): Associated audio device name.
        """
        self.name = name
        self.device_type = device_type
        self.ffmpeg_name = ffmpeg_name
        self.alternative_name = alternative_name
        self.audio_device = audio_device
        self.capabilities = {}  # Store device capabilities (inputs, formats, etc.)

    def __str__(self):
        return f"{self.name} ({self.device_type})"


class CaptureDeviceManager:
    """Manages the detection and filtering of video capture devices."""

    def __init__(self):
        """Initializes the CaptureDeviceManager."""
        self.devices = []
        self.audio_devices = []
        self.last_error = None

    def refresh_devices(self, use_mock: bool = False) -> List[CaptureDevice]:
        """
        Scans the system for available capture devices.

        Args:
            use_mock (bool): If True, returns mock devices for testing.

        Returns:
            list: A list of CaptureDevice objects found on the system.
        """
        self.devices = []
        self.audio_devices = []
        self.last_error = None

        if use_mock:
            return self._get_mock_devices()

        try:
            if sys.platform == "win32":
                self._detect_directshow_devices()
            else:
                print("Warning: Device detection only supported on Windows currently")
                return self._get_mock_devices()

            return self.devices

        except Exception as e:
            self.last_error = str(e)
            print(f"Device detection failed: {e}")
            print("Falling back to mock devices for testing")
            return self._get_mock_devices()

    def _get_mock_devices(self) -> List[CaptureDevice]:
        """
        Returns mock devices for testing when no real hardware is available.

        Returns:
            list: A list of mock CaptureDevice objects.
        """
        print("Using mock device detection...")
        self.devices = [
            CaptureDevice(
                name="Elgato Video Capture",
                device_type="analog",
                ffmpeg_name="video=Elgato Video Capture",
                audio_device="audio=Elgato Video Capture"
            ),
            CaptureDevice(
                name="USB Video Device",
                device_type="analog",
                ffmpeg_name="video=USB Video Device",
                audio_device="audio=Microphone (USB Audio Device)"
            ),
            CaptureDevice(
                name="Microsoft DV Camera and VCR",
                device_type="dv",
                ffmpeg_name="video=Microsoft DV Camera and VCR",
                audio_device="audio=Microsoft DV Camera and VCR"
            ),
            CaptureDevice(
                name="Blackmagic WDM Capture",
                device_type="analog",
                ffmpeg_name="video=Blackmagic WDM Capture",
                audio_device="audio=Blackmagic WDM Capture"
            ),
        ]
        return self.devices

    def _detect_directshow_devices(self) -> None:
        """
        Detect DirectShow devices on Windows using FFmpeg.
        Parses output from: ffmpeg -list_devices true -f dshow -i dummy
        """
        try:
            # Run FFmpeg to list DirectShow devices
            cmd = ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"]
            
            # Use CREATE_NO_WINDOW flag on Windows to suppress console
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=creationflags,
                timeout=10
            )

            # FFmpeg outputs device list to stderr
            output = result.stderr

            # Parse video devices
            video_devices = self._parse_dshow_output(output, "video")
            # Parse audio devices
            self.audio_devices = self._parse_dshow_output(output, "audio")

            # Create CaptureDevice objects
            for video_dev in video_devices:
                device_name = video_dev['name']
                alternative_name = video_dev.get('alternative')
                
                # Determine device type (DV devices have "DV" in the name)
                device_type = "dv" if self._is_dv_device(device_name) else "analog"
                
                # Try to find matching audio device
                audio_device = self._find_matching_audio_device(device_name)
                
                # Create FFmpeg device string
                if alternative_name:
                    ffmpeg_name = f'video=@device_pnp_{alternative_name}'
                else:
                    ffmpeg_name = f'video={device_name}'

                device = CaptureDevice(
                    name=device_name,
                    device_type=device_type,
                    ffmpeg_name=ffmpeg_name,
                    alternative_name=alternative_name,
                    audio_device=audio_device
                )
                
                self.devices.append(device)
                print(f"Detected device: {device_name} ({device_type})")

        except subprocess.TimeoutExpired:
            raise Exception("FFmpeg device detection timed out")
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please ensure FFmpeg is installed and in PATH")
        except Exception as e:
            raise Exception(f"Failed to detect DirectShow devices: {str(e)}")

    def _parse_dshow_output(self, output: str, device_type: str) -> List[Dict[str, str]]:
        """
        Parse FFmpeg DirectShow output to extract device names.

        Args:
            output (str): FFmpeg stderr output
            device_type (str): 'video' or 'audio'

        Returns:
            list: List of dictionaries with 'name' and optional 'alternative' keys
        """
        devices = []
        
        # Look for the device type section
        # Example: [dshow @ 0x...] "Elgato Video Capture" (video)
        # Alternative: @device_pnp_\\?\usb#...
        
        lines = output.split('\n')
        in_section = False
        
        for line in lines:
            # Check if we're in the right section
            if f"DirectShow {device_type} devices" in line:
                in_section = True
                continue
            elif "DirectShow audio devices" in line and device_type == "video":
                in_section = False
            elif in_section and '[dshow @' in line:
                # Parse device name
                # Format: [dshow @ 0x...] "Device Name"
                match = re.search(r'"([^"]+)"', line)
                if match:
                    device_name = match.group(1)
                    devices.append({'name': device_name})
                
                # Check for alternative name in next line
                # Format: Alternative name "@device_pnp_\\?\usb#..."
                
        return devices

    def _is_dv_device(self, device_name: str) -> bool:
        """
        Determine if a device is a DV/FireWire device based on its name.

        Args:
            device_name (str): The device name to check

        Returns:
            bool: True if device appears to be DV/FireWire
        """
        dv_keywords = ['dv', 'firewire', 'ieee 1394', '1394', 'camcorder', 'vcr']
        device_lower = device_name.lower()
        
        return any(keyword in device_lower for keyword in dv_keywords)

    def _find_matching_audio_device(self, video_device_name: str) -> Optional[str]:
        """
        Find matching audio device for a video device.

        Args:
            video_device_name (str): Name of the video device

        Returns:
            str or None: FFmpeg audio device string, or None if not found
        """
        # Many capture cards use the same name for audio
        for audio_dev in self.audio_devices:
            audio_name = audio_dev['name']
            if audio_name == video_device_name:
                return f'audio={audio_name}'
            # Check for partial matches (e.g., "USB Video" matches "USB Audio")
            if video_device_name.split()[0] in audio_name:
                return f'audio={audio_name}'
        
        # Default to first audio device if no match found
        if self.audio_devices:
            return f'audio={self.audio_devices[0]["name"]}'
        
        return None

    def get_analog_devices(self) -> List[CaptureDevice]:
        """
        Returns a list of detected devices that are of the 'analog' type.

        Returns:
            list: A list of analog CaptureDevice objects.
        """
        return [device for device in self.devices if device.device_type == "analog"]

    def get_dv_devices(self) -> List[CaptureDevice]:
        """
        Returns a list of detected devices that are of the 'dv' type.

        Returns:
            list: A list of DV CaptureDevice objects.
        """
        return [device for device in self.devices if device.device_type == "dv"]
    
    def get_audio_devices(self) -> List[Dict[str, str]]:
        """
        Returns a list of detected audio devices.

        Returns:
            list: A list of audio device dictionaries.
        """
        return self.audio_devices
    
    def get_device_by_name(self, name: str) -> Optional[CaptureDevice]:
        """
        Find a device by its name.

        Args:
            name (str): The device name to search for

        Returns:
            CaptureDevice or None: The device if found, None otherwise
        """
        for device in self.devices:
            if device.name == name:
                return device
        return None


class AnalogCaptureEngine:
    """
    Handles the logic for capturing from an analog (DirectShow) device.
    Builds FFmpeg commands for real-time capture.
    """

    def __init__(self, device: CaptureDevice, settings: Dict):
        """
        Initialize the analog capture engine.

        Args:
            device (CaptureDevice): The capture device to use
            settings (dict): Capture settings (codec, resolution, framerate, etc.)
        """
        self.device = device
        self.settings = settings
        self.process = None
        self.output_file = None
        print(f"AnalogCaptureEngine initialized for '{self.device.name}'")

    def build_capture_command(self, output_file: str) -> List[str]:
        """
        Build the FFmpeg command for analog capture.

        Args:
            output_file (str): Path to output file

        Returns:
            list: FFmpeg command as list of strings
        """
        self.output_file = output_file
        
        cmd = ["ffmpeg", "-hide_banner"]
        
        # Input format (DirectShow on Windows)
        cmd.extend(["-f", "dshow"])
        
        # Video settings
        resolution = self.settings.get("resolution", "720x480")
        framerate = self.settings.get("framerate", "29.97")
        pixel_format = self.settings.get("pixel_format", "uyvy422")
        
        cmd.extend(["-video_size", resolution])
        cmd.extend(["-framerate", framerate])
        cmd.extend(["-pixel_format", pixel_format])
        
        # Video input source (crossbar pin selection)
        video_input = self.settings.get("video_input", "Auto")
        if video_input and video_input != "Auto (Default)":
            # Map input types to DirectShow crossbar pins
            crossbar_map = {
                "Composite (RCA)": "1",  # PhysConn_Video_Composite
                "S-Video (Y/C)": "2",     # PhysConn_Video_SVideo
                "Component (YPbPr)": "3", # PhysConn_Video_RGB
                "HDMI/Digital": "0"       # PhysConn_Video_SerialDigital
            }
            pin = crossbar_map.get(video_input)
            if pin:
                cmd.extend(["-crossbar_video_input_pin_number", pin])
        
        # Audio input source
        audio_input = self.settings.get("audio_input", "Auto")
        if audio_input and audio_input != "Auto (Default)":
            # Map audio input types
            audio_crossbar_map = {
                "Line In": "1",      # PhysConn_Audio_Line
                "Microphone": "3",   # PhysConn_Audio_Microphone
                "CD Audio": "4",     # PhysConn_Audio_CD
                "Video Audio": "2"   # PhysConn_Audio_AESDigital
            }
            pin = audio_crossbar_map.get(audio_input)
            if pin:
                cmd.extend(["-crossbar_audio_input_pin_number", pin])
        
        # Device input (video + audio)
        if self.device.audio_device:
            input_str = f"{self.device.ffmpeg_name}:{self.device.audio_device}"
        else:
            input_str = self.device.ffmpeg_name
        cmd.extend(["-i", input_str])
        
        # Codec settings
        codec = self.settings.get("codec", "huffyuv")
        codec_map = {
            "HuffYUV (Lossless)": "huffyuv",
            "FFV1 (Lossless)": "ffv1",
            "Lagarith": "lagarith",
            "UT Video": "utvideo"
        }
        video_codec = codec_map.get(codec, "huffyuv")
        cmd.extend(["-c:v", video_codec])
        
        # Audio codec (PCM for lossless)
        cmd.extend(["-c:a", "pcm_s16le"])
        cmd.extend(["-ar", "48000"])  # 48 kHz sample rate
        
        # Output file
        cmd.append(output_file)
        
        return cmd

    def start_capture(self, output_file: str, log_callback=None) -> bool:
        """
        Start capturing video.

        Args:
            output_file (str): Path to save captured file
            log_callback: Optional callback for logging

        Returns:
            bool: True if capture started successfully
        """
        try:
            cmd = self.build_capture_command(output_file)
            
            if log_callback:
                log_callback(f"Starting capture: {' '.join(cmd)}")
            
            # Use CREATE_NO_WINDOW on Windows
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
            
            if log_callback:
                log_callback(f"Capture started successfully (PID: {self.process.pid})")
            
            return True
            
        except Exception as e:
            if log_callback:
                log_callback(f"Failed to start capture: {str(e)}")
            return False

    def stop_capture(self, log_callback=None) -> bool:
        """
        Stop ongoing capture.

        Args:
            log_callback: Optional callback for logging

        Returns:
            bool: True if stopped successfully
        """
        if not self.process:
            return False
        
        try:
            if log_callback:
                log_callback("Stopping capture...")
            
            # Send 'q' to FFmpeg stdin to gracefully stop
            if self.process.poll() is None:
                try:
                    self.process.communicate(input=b'q', timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.terminate()
                    self.process.wait(timeout=2)
            
            if log_callback:
                log_callback("Capture stopped")
            
            return True
            
        except Exception as e:
            if log_callback:
                log_callback(f"Error stopping capture: {str(e)}")
            try:
                self.process.kill()
            except:
                pass
            return False

    def is_running(self) -> bool:
        """
        Check if capture is currently running.

        Returns:
            bool: True if capture process is active
        """
        return self.process is not None and self.process.poll() is None

    def get_dropped_frames(self) -> int:
        """
        Get the number of dropped frames during capture.
        Parses FFmpeg stderr output.

        Returns:
            int: Number of dropped frames (0 if cannot determine)
        """
        # This would require parsing FFmpeg's stderr output in real-time
        # For now, return 0 (placeholder)
        # TODO: Implement real-time stderr parsing in a monitoring thread
        return 0


class DVCaptureEngine:
    """
    Handles the logic for capturing from a DV (FireWire/IEEE 1394) device.
    Supports both DV and HDV formats.
    """

    def __init__(self, device: CaptureDevice, settings: Dict):
        """
        Initialize the DV capture engine.

        Args:
            device (CaptureDevice): The DV/FireWire device to use
            settings (dict): Capture settings
        """
        self.device = device
        self.settings = settings
        self.process = None
        self.output_file = None
        print(f"DVCaptureEngine initialized for '{self.device.name}'")

    def build_capture_command(self, output_file: str) -> List[str]:
        """
        Build the FFmpeg command for DV/FireWire capture.

        Args:
            output_file (str): Path to output file

        Returns:
            list: FFmpeg command as list of strings
        """
        self.output_file = output_file
        
        cmd = ["ffmpeg", "-hide_banner"]
        
        # Input format (DirectShow for DV on Windows)
        cmd.extend(["-f", "dshow"])
        
        # DV-specific settings
        framerate = self.settings.get("framerate", "29.97")
        cmd.extend(["-framerate", framerate])
        
        # Device input
        if self.device.audio_device:
            input_str = f"{self.device.ffmpeg_name}:{self.device.audio_device}"
        else:
            input_str = self.device.ffmpeg_name
        cmd.extend(["-i", input_str])
        
        # For DV, we can copy the stream directly (lossless)
        codec = self.settings.get("codec", "copy")
        
        if codec == "copy" or "DV" in codec:
            # Copy DV stream directly (fastest, lossless)
            cmd.extend(["-c:v", "copy"])
            cmd.extend(["-c:a", "copy"])
        else:
            # Re-encode if user selected a different codec
            codec_map = {
                "HuffYUV (Lossless)": "huffyuv",
                "FFV1 (Lossless)": "ffv1",
                "Lagarith": "lagarith"
            }
            video_codec = codec_map.get(codec, "copy")
            cmd.extend(["-c:v", video_codec])
            cmd.extend(["-c:a", "pcm_s16le"])
        
        # Output file (AVI container for DV)
        if not output_file.lower().endswith('.avi'):
            output_file = output_file.rsplit('.', 1)[0] + '.avi'
        
        cmd.append(output_file)
        
        return cmd

    def start_capture(self, output_file: str, log_callback=None) -> bool:
        """
        Start capturing DV video.

        Args:
            output_file (str): Path to save captured file
            log_callback: Optional callback for logging

        Returns:
            bool: True if capture started successfully
        """
        try:
            cmd = self.build_capture_command(output_file)
            
            if log_callback:
                log_callback(f"Starting DV capture: {' '.join(cmd)}")
            
            # Use CREATE_NO_WINDOW on Windows
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
            
            if log_callback:
                log_callback(f"DV capture started (PID: {self.process.pid})")
                log_callback("Tip: DV capture uses stream copy for lossless quality")
            
            return True
            
        except Exception as e:
            if log_callback:
                log_callback(f"Failed to start DV capture: {str(e)}")
            return False

    def stop_capture(self, log_callback=None) -> bool:
        """
        Stop ongoing DV capture.

        Args:
            log_callback: Optional callback for logging

        Returns:
            bool: True if stopped successfully
        """
        if not self.process:
            return False
        
        try:
            if log_callback:
                log_callback("Stopping DV capture...")
            
            # Send 'q' to FFmpeg stdin to gracefully stop
            if self.process.poll() is None:
                try:
                    self.process.communicate(input=b'q', timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.terminate()
                    self.process.wait(timeout=2)
            
            if log_callback:
                log_callback("DV capture stopped")
            
            return True
            
        except Exception as e:
            if log_callback:
                log_callback(f"Error stopping DV capture: {str(e)}")
            try:
                self.process.kill()
            except:
                pass
            return False

    def is_running(self) -> bool:
        """
        Check if DV capture is currently running.

        Returns:
            bool: True if capture process is active
        """
        return self.process is not None and self.process.poll() is None

    def detect_dv_format(self) -> str:
        """
        Detect if the DV source is standard DV or HDV.

        Returns:
            str: 'DV' or 'HDV' or 'Unknown'
        """
        # This would require probing the device stream
        # For now, assume standard DV
        # TODO: Implement format detection by probing stream
        return "DV"

    def extract_timecode(self) -> Optional[str]:
        """
        Extract DV timecode from the stream.

        Returns:
            str or None: Timecode string if available
        """
        # DV tapes have embedded timecode
        # This would require parsing the DV stream
        # TODO: Implement timecode extraction
        return None


# ============================================================================
# Utility Functions
# ============================================================================

def list_all_devices(use_mock: bool = False) -> Dict[str, List[CaptureDevice]]:
    """
    Quick utility to list all available capture devices.

    Args:
        use_mock (bool): If True, returns mock devices

    Returns:
        dict: Dictionary with 'all', 'analog', and 'dv' device lists
    """
    manager = CaptureDeviceManager()
    manager.refresh_devices(use_mock=use_mock)
    
    return {
        'all': manager.devices,
        'analog': manager.get_analog_devices(),
        'dv': manager.get_dv_devices(),
        'audio': manager.audio_devices
    }


def test_device_detection():
    """
    Test function to verify device detection is working.
    Prints all detected devices to console.
    """
    print("=" * 70)
    print("Advanced Tape Restorer - Capture Device Detection Test")
    print("=" * 70)
    print()
    
    try:
        print("Attempting to detect real hardware...")
        devices = list_all_devices(use_mock=False)
        
        print(f"\n✓ Detection successful!")
        print(f"  Total devices: {len(devices['all'])}")
        print(f"  Analog devices: {len(devices['analog'])}")
        print(f"  DV/FireWire devices: {len(devices['dv'])}")
        print(f"  Audio devices: {len(devices['audio'])}")
        
        if devices['all']:
            print("\nVideo Devices:")
            print("-" * 70)
            for i, device in enumerate(devices['all'], 1):
                print(f"{i}. {device.name}")
                print(f"   Type: {device.device_type}")
                print(f"   FFmpeg: {device.ffmpeg_name}")
                if device.audio_device:
                    print(f"   Audio: {device.audio_device}")
                print()
        
        if devices['audio']:
            print("Audio Devices:")
            print("-" * 70)
            for i, audio_dev in enumerate(devices['audio'], 1):
                print(f"{i}. {audio_dev['name']}")
            print()
        
        if not devices['all']:
            print("\n⚠ No capture devices detected.")
            print("  This could mean:")
            print("  - No capture hardware is connected")
            print("  - Drivers are not installed")
            print("  - FFmpeg cannot access DirectShow devices")
            print("\n  The application will use mock devices for testing.")
        
    except Exception as e:
        print(f"\n✗ Device detection failed: {str(e)}")
        print("\nFalling back to mock devices...")
        devices = list_all_devices(use_mock=True)
        print(f"\nMock devices loaded: {len(devices['all'])} devices")
    
    print("\n" + "=" * 70)
    return devices


# ============================================================================
# CLI Test Interface
# ============================================================================

if __name__ == "__main__":
    """
    Command-line test interface for capture module.
    Run: python capture.py
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Tape Restorer - Capture Module Test")
    parser.add_argument("--test-detection", action="store_true", 
                       help="Test device detection")
    parser.add_argument("--mock", action="store_true",
                       help="Use mock devices instead of real hardware")
    parser.add_argument("--list-devices", action="store_true",
                       help="List all available capture devices")
    
    args = parser.parse_args()
    
    if args.test_detection or not any(vars(args).values()):
        # Default action: test detection
        test_device_detection()
    
    elif args.list_devices:
        devices = list_all_devices(use_mock=args.mock)
        print("\n=== Video Devices ===")
        for device in devices['all']:
            print(f"- {device}")
        
        print("\n=== Audio Devices ===")
        for audio in devices['audio']:
            print(f"- {audio['name']}")

