"""
Advanced Tape Restorer v3.1 - Core Processing Module
Modular video restoration engine with lazy loading for performance
"""

__version__ = "3.1.0"


def __getattr__(name):
    """Lazy import for core modules - loads on first access."""
    if name == "VideoProcessor":
        from .processor import VideoProcessor

        return VideoProcessor
    elif name == "VapourSynthEngine":
        from .vapoursynth_engine import VapourSynthEngine

        return VapourSynthEngine
    elif name == "FFmpegEncoder":
        from .ffmpeg_encoder import FFmpegEncoder

        return FFmpegEncoder
    elif name == "VideoAnalyzer":
        from .video_analyzer import VideoAnalyzer

        return VideoAnalyzer
    else:
        raise AttributeError(f"module 'core' has no attribute '{name}'")
