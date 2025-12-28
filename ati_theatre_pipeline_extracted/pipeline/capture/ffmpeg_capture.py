"""Optional DirectShow ingest helper.

This is here because you asked for 'VapourSynth + QTGMC + ffmpeg', but in practice
most people capture with dedicated tools (VirtualDub2, AMCap, etc.) and then run post.

If you *do* want FFmpeg DirectShow capture, you must:
- have a DirectShow device name
- have stable drivers installed (often not possible for ATI Theatre chips on Win10/11)

Example:
  ffmpeg -f dshow -i video="Your Device":audio="Your Device" ...

This module simply wraps that pattern.
"""

from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from ..utils.subprocesses import run

@dataclass
class CaptureSpec:
    video_device: str
    audio_device: str
    width: int = 720
    height: int = 480
    fps: str = "30000/1001"
    pixel_format: str = "uyvy422"

def capture_dshow(ffmpeg: str, spec: CaptureSpec, out_path: Path, duration_seconds: int | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg,
        "-hide_banner", "-y",
        "-f", "dshow",
        "-video_size", f"{spec.width}x{spec.height}",
        "-framerate", spec.fps,
        "-pixel_format", spec.pixel_format,
        "-i", f"video={spec.video_device}:audio={spec.audio_device}",
        "-c:v", "ffv1",
        "-level", "3",
        "-g", "1",
        "-slicecrc", "1",
        "-c:a", "pcm_s16le",
        str(out_path)
    ]
    if duration_seconds:
        cmd.insert(cmd.index("-i"), "-t")
        cmd.insert(cmd.index("-i"), str(duration_seconds))

    run(cmd)
