"""
Capture Module - Video capture with lazy loading for performance
"""

__version__ = "3.0.0"


def __getattr__(name):
    """Lazy import for capture modules."""
    if name == "CaptureDeviceManager":
        from .device_manager import CaptureDeviceManager

        return CaptureDeviceManager
    elif name == "AnalogCaptureEngine":
        from .analog_capture import AnalogCaptureEngine

        return AnalogCaptureEngine
    elif name == "AnalogCaptureSettings":
        from .analog_capture import AnalogCaptureSettings

        return AnalogCaptureSettings
    elif name == "DVCaptureEngine":
        from .dv_capture import DVCaptureEngine

        return DVCaptureEngine
    else:
        raise AttributeError(f"module 'capture' has no attribute '{name}'")
