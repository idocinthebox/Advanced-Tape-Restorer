from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class VsBuildSpec:
    input_path: Path
    variant: str
    tff: bool
    qtgmc_preset: str
    sharpness: float
    chroma_phase_x_px: float = 0.0
    chroma_phase_y_px: float = 0.0

def build_vpy(spec: VsBuildSpec) -> str:
    # Keep the script self-contained and readable.
    return f'''import vapoursynth as vs
core = vs.core

# Source
src = core.ffms2.Source(r"{spec.input_path.as_posix()}")

# Chroma phase correction (subpixel shift on U/V)
from pipeline.vs.chroma_phase import chroma_phase_correct
c = chroma_phase_correct(src, shift_x_px={spec.chroma_phase_x_px}, shift_y_px={spec.chroma_phase_y_px})

# Variant selection (field-aware options)
from pipeline.vs.variants import apply_variant
out = apply_variant(core, c, variant="{spec.variant}", qtgmc_preset="{spec.qtgmc_preset}", tff={str(spec.tff)}, sharpness={spec.sharpness})

out.set_output()
'''
