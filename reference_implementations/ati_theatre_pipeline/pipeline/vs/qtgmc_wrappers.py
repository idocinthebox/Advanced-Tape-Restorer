from __future__ import annotations

def qtgmc_deinterlace(clip, preset: str = "Slow", tff: bool = True, sharpness: float = 0.2):
    """QTGMC wrapper.

    You must have QTGMC available, typically via havsfunc.QTGMC.

    Notes:
    - 'sharpness' is mapped to QTGMC's Sharpness parameter.
    """
    import havsfunc as haf
    return haf.QTGMC(clip, Preset=preset, TFF=tff, Sharpness=sharpness)
