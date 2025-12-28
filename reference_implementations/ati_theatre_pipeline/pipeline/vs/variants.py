from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

VariantName = Literal["deinterlace_qtgmc", "keep_interlaced_fieldaware", "bob_qtgmc"]

@dataclass
class Variant:
    name: VariantName
    description: str

VARIANTS = [
    Variant("deinterlace_qtgmc", "Standard: QTGMC -> progressive output (best for most deliverables)."),
    Variant("bob_qtgmc", "Bob: QTGMC with FPSDivisor=1 (double-rate motion for special cases)."),
    Variant("keep_interlaced_fieldaware", "Keep interlaced: field-aware filters only; no deinterlace (for interlaced delivery)."),
]

def apply_variant(core, clip, variant: VariantName, qtgmc_preset: str, tff: bool, sharpness: float):
    import vapoursynth as vs
    import havsfunc as haf

    if variant == "deinterlace_qtgmc":
        return haf.QTGMC(clip, Preset=qtgmc_preset, TFF=tff, Sharpness=sharpness, FPSDivisor=2)
    if variant == "bob_qtgmc":
        return haf.QTGMC(clip, Preset=qtgmc_preset, TFF=tff, Sharpness=sharpness, FPSDivisor=1)
    if variant == "keep_interlaced_fieldaware":
        # Example: mild cleanup while staying interlaced.
        # You can add interlaced-safe denoisers here.
        return clip

    raise ValueError(f"Unknown variant: {variant}")
