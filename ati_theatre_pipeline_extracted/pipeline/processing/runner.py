from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

from ..utils.subprocesses import run
from ..vs.script_builder import VsBuildSpec, build_vpy

@dataclass
class ProcessRequest:
    input_path: Path
    out_path: Path
    variant: str
    tff: bool
    qtgmc_preset: str
    sharpness: float
    chroma_phase_x_px: float
    chroma_phase_y_px: float

def process_with_vspipe_and_ffmpeg(vspipe: str, ffmpeg: str, req: ProcessRequest, temp_dir: Path) -> Path:
    temp_dir.mkdir(parents=True, exist_ok=True)
    vpy_path = temp_dir / (req.input_path.stem + f".{req.variant}.vpy")

    vpy = build_vpy(VsBuildSpec(
        input_path=req.input_path,
        variant=req.variant,
        tff=req.tff,
        qtgmc_preset=req.qtgmc_preset,
        sharpness=req.sharpness,
        chroma_phase_x_px=req.chroma_phase_x_px,
        chroma_phase_y_px=req.chroma_phase_y_px,
    ))
    vpy_path.write_text(vpy, encoding="utf-8")

    req.out_path.parent.mkdir(parents=True, exist_ok=True)

    # vspipe -> y4m -> ffmpeg encode
    cmd = [
        vspipe, str(vpy_path), "-", "--y4m",
        "|", ffmpeg, "-hide_banner", "-y",
        "-i", "-",
        "-c:v", "ffv1",
        "-level", "3",
        "-g", "1",
        "-slicecrc", "1",
        "-c:a", "copy",
        str(req.out_path)
    ]

    # Windows shell piping: run through cmd.exe
    if "|" in cmd:
        shell_cmd = " ".join(cmd)
        run(["cmd.exe", "/c", shell_cmd])
    else:
        run(cmd)

    return req.out_path
