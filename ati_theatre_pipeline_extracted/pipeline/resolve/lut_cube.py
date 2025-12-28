from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class LutParams:
    black_point: float
    white_point: float
    saturation: float  # 1.0 = neutral; >1 boosts

def _apply_levels(x: np.ndarray, black: float, white: float) -> np.ndarray:
    # map [black, white] -> [0,1] with clipping
    y = (x - black) / max(1e-6, (white - black))
    return np.clip(y, 0.0, 1.0)

def _apply_saturation(rgb: np.ndarray, sat: float) -> np.ndarray:
    # simple luma-based sat adjustment (Rec.709-ish weights)
    w = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    l = (rgb * w).sum(axis=-1, keepdims=True)
    return np.clip(l + (rgb - l) * sat, 0.0, 1.0)

def write_cube(path: Path, size: int, params: LutParams, title: str = "preview_lut"):
    """Generate a Resolve-compatible .cube 3D LUT.

    This is intended for *preview* while you tune the pipeline, not final grading.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create grid in Resolve order: B changes fastest, then G, then R.
    vals = np.linspace(0.0, 1.0, size, dtype=np.float32)
    grid = np.array(list((r,g,b) for r in vals for g in vals for b in vals), dtype=np.float32)

    # Levels (same on all channels)
    grid2 = _apply_levels(grid, params.black_point, params.white_point)

    # Saturation
    grid3 = _apply_saturation(grid2, params.saturation)

    with path.open("w", encoding="utf-8") as f:
        f.write(f'TITLE "{title}"\n')
        f.write("LUT_3D_SIZE %d\n" % size)
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n")
        for r,g,b in grid3:
            f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")
