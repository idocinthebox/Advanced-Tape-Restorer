from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np

@dataclass
class TapeProfile:
    input_path: str
    field_order: str                 # 'tff' or 'bff'
    chroma_phase_x_px: float
    black_point: float               # 0..1 luma
    white_point: float               # 0..1 luma
    avg_saturation: float            # arbitrary
    notes: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

def _frame_to_plane_np(frame, plane: int) -> np.ndarray:
    import vapoursynth as vs
    fmt = frame.format
    if fmt is None:
        raise ValueError("Frame has no format")
    # For simplicity we assume 8-16bit integer.
    arr = np.asarray(frame[plane])
    # Normalize to 0..1 using bit depth
    depth = fmt.bits_per_sample
    maxv = (1 << depth) - 1
    return arr.astype(np.float32) / float(maxv)

def quick_profile(input_path: Path, sample_frames: int = 40, stride: int = 150, chroma_phase_default_px: float = 0.25, default_field_order: str = "tff"):
    """Sample frames and compute rough luma/chroma stats.

    This is *not* a color-science grade calibration.
    It is meant to automatically pick reasonable 'starting knobs' per tape.
    """
    import vapoursynth as vs
    core = vs.core
    # Use ffms2 for decode; swap to LWLibavSource if you prefer.
    clip = core.ffms2.Source(str(input_path))

    # pick indices
    n = clip.num_frames
    idx = [min(i * stride, n - 1) for i in range(sample_frames)]
    idx = sorted(set(idx))

    lumas = []
    sats = []
    notes = []

    for i in idx:
        f = clip.get_frame(i)
        y = _frame_to_plane_np(f, 0)
        lumas.append(y.mean())

        if f.format.color_family == vs.YUV and f.format.num_planes >= 3:
            u = _frame_to_plane_np(f, 1) - 0.5
            v = _frame_to_plane_np(f, 2) - 0.5
            sat = np.sqrt(u*u + v*v).mean()
            sats.append(float(sat))
        else:
            sats.append(0.0)

    lumas_np = np.array(lumas, dtype=np.float32)
    sats_np = np.array(sats, dtype=np.float32)

    # Estimate black/white points as low/high percentiles of mean luma across samples.
    black = float(np.percentile(lumas_np, 5))
    white = float(np.percentile(lumas_np, 95))

    # crude heuristic: if whites are very low, tape is dull; flag it.
    if white < 0.55:
        notes.append("Low white level across samples; consider gain/levels.")

    # Field order: we cannot reliably auto-detect without comb analysis; keep configurable.
    field_order = default_field_order

    return TapeProfile(
        input_path=str(input_path),
        field_order=field_order,
        chroma_phase_x_px=float(chroma_phase_default_px),
        black_point=black,
        white_point=white,
        avg_saturation=float(sats_np.mean()) if len(sats_np) else 0.0,
        notes=notes,
    )
