from __future__ import annotations

def chroma_phase_correct(clip, shift_x_px: float = 0.0, shift_y_px: float = 0.0):
    """Chroma phase correction by subpixel shifting U/V planes.

    This is a pragmatic approach for 'LaserDisc-accurate' style tweaks:
    - shift U and V equally
    - leave luma untouched

    Works best on YUV 4:2:2 or 4:2:0 sources.
    Requires core.resize (built-in zimg) support.

    Parameters:
      shift_x_px: positive shifts chroma right
      shift_y_px: positive shifts chroma down
    """
    import vapoursynth as vs
    core = vs.core

    fmt = clip.format
    if fmt is None or fmt.color_family != vs.YUV:
        raise ValueError("Expected a YUV clip")

    y = core.std.ShufflePlanes(clip, planes=0, colorfamily=vs.GRAY)
    u = core.std.ShufflePlanes(clip, planes=1, colorfamily=vs.GRAY)
    v = core.std.ShufflePlanes(clip, planes=2, colorfamily=vs.GRAY)

    # zimg resize allows subpixel shift via src_left/src_top
    # (note: this is not the *only* correct way to do chroma alignment, but it's robust and simple)
    u2 = core.resize.Bicubic(u, u.width, u.height, src_left=-shift_x_px, src_top=-shift_y_px)
    v2 = core.resize.Bicubic(v, v.width, v.height, src_left=-shift_x_px, src_top=-shift_y_px)

    out = core.std.ShufflePlanes([y, u2, v2], planes=[0, 0, 0], colorfamily=vs.YUV)

    # preserve original format if possible
    if out.format.id != clip.format.id:
        out = core.resize.Bicubic(out, format=clip.format.id)
    return out
