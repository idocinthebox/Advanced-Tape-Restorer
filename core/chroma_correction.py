"""
Chroma Phase Correction Module

Hardware-accurate chroma alignment based on professional analog chipset processing.
Implements subpixel U/V plane shifting for composite video color accuracy.

This module replicates the chroma phase correction functionality found in
professional analog video capture chipsets, providing LaserDisc-accurate
color alignment for VHS, Hi8, and other composite video sources.
"""

from __future__ import annotations


def chroma_phase_correct(clip, shift_x_px: float = 0.0, shift_y_px: float = 0.0):
    """
    Apply chroma phase correction by subpixel shifting U/V planes.

    This is a hardware-accurate approach for analog video color alignment:
    - Shifts U and V planes equally (maintains color relationship)
    - Leaves luma (Y) plane untouched
    - Uses subpixel precision for fine adjustments

    Works best on YUV 4:2:2 or 4:2:0 sources (typical analog capture formats).
    Requires VapourSynth core.resize (built-in zimg) support.

    Parameters:
        clip: VapourSynth clip (YUV format required)
        shift_x_px: Horizontal shift in pixels (positive = shift right)
                   Default: 0.0, Typical analog: 0.25px
        shift_y_px: Vertical shift in pixels (positive = shift down)
                   Default: 0.0

    Returns:
        VapourSynth clip with corrected chroma alignment

    Raises:
        ValueError: If clip is not in YUV format

    Example:
        >>> # LaserDisc-accurate correction (hardware default)
        >>> clip = chroma_phase_correct(clip, shift_x_px=0.25)
        >>>
        >>> # Custom correction for specific capture chain
        >>> clip = chroma_phase_correct(clip, shift_x_px=0.5, shift_y_px=-0.1)

    Notes:
        - ATI Theatre chips used 0.25px default for LaserDisc sources
        - VHS may require different values depending on capture hardware
        - Use auto-profiling to detect optimal shift per tape
    """
    import vapoursynth as vs

    core = vs.core

    fmt = clip.format
    if fmt is None or fmt.color_family != vs.YUV:
        raise ValueError("Chroma phase correction requires YUV clip")

    # Split into Y, U, V planes
    y = core.std.ShufflePlanes(clip, planes=0, colorfamily=vs.GRAY)
    u = core.std.ShufflePlanes(clip, planes=1, colorfamily=vs.GRAY)
    v = core.std.ShufflePlanes(clip, planes=2, colorfamily=vs.GRAY)

    # Apply subpixel shift to chroma planes using zimg resize
    # src_left/src_top parameters enable subpixel precision
    # Negative values compensate for the shift direction
    u_shifted = core.resize.Bicubic(
        u, u.width, u.height, src_left=-shift_x_px, src_top=-shift_y_px
    )
    v_shifted = core.resize.Bicubic(
        v, v.width, v.height, src_left=-shift_x_px, src_top=-shift_y_px
    )

    # Recombine planes
    out = core.std.ShufflePlanes(
        [y, u_shifted, v_shifted], planes=[0, 0, 0], colorfamily=vs.YUV
    )

    # Preserve original format if conversion occurred
    if out.format.id != clip.format.id:
        out = core.resize.Bicubic(out, format=clip.format.id)

    return out


def generate_chroma_correction_vpy(
    shift_x_px: float = 0.0, shift_y_px: float = 0.0, apply_before_deinterlace: bool = True
) -> str:
    """
    Generate VapourSynth script snippet for chroma phase correction.

    This function creates the VapourSynth code to be inserted into
    the processing pipeline. Designed for integration with the
    VapourSynthEngine class.

    Parameters:
        shift_x_px: Horizontal chroma shift in pixels
        shift_y_px: Vertical chroma shift in pixels
        apply_before_deinterlace: If True, apply before QTGMC;
                                 if False, apply after QTGMC

    Returns:
        VapourSynth script code as string

    Example:
        >>> code = generate_chroma_correction_vpy(shift_x_px=0.25)
        >>> print(code)
        # Chroma Phase Correction (Hardware-Accurate)
        def chroma_phase_correct(clip, shift_x_px=0.25, shift_y_px=0.0):
            ...
    """
    return f'''
# Chroma Phase Correction (Hardware-Accurate Analog Processing)
def chroma_phase_correct(clip, shift_x_px={shift_x_px}, shift_y_px={shift_y_px}):
    """
    Hardware-accurate chroma alignment based on professional analog chipset processing.
    Replicates subpixel U/V shifting found in broadcast-quality capture hardware.
    """
    fmt = clip.format
    if fmt is None or fmt.color_family != vs.YUV:
        return clip  # Skip if not YUV

    # Split planes
    y = core.std.ShufflePlanes(clip, planes=0, colorfamily=vs.GRAY)
    u = core.std.ShufflePlanes(clip, planes=1, colorfamily=vs.GRAY)
    v = core.std.ShufflePlanes(clip, planes=2, colorfamily=vs.GRAY)

    # Subpixel shift chroma
    u_shifted = core.resize.Bicubic(u, u.width, u.height, src_left=-shift_x_px, src_top=-shift_y_px)
    v_shifted = core.resize.Bicubic(v, v.width, v.height, src_left=-shift_x_px, src_top=-shift_y_px)

    # Recombine
    out = core.std.ShufflePlanes([y, u_shifted, v_shifted], planes=[0, 0, 0], colorfamily=vs.YUV)

    # Preserve format
    if out.format.id != clip.format.id:
        out = core.resize.Bicubic(out, format=clip.format.id)

    return out

clip = chroma_phase_correct(clip, shift_x_px={shift_x_px}, shift_y_px={shift_y_px})
'''


# Hardware presets for common analog sources
CHROMA_PRESETS = {
    "none": {"shift_x_px": 0.0, "shift_y_px": 0.0, "description": "No correction"},
    "laserdisc": {
        "shift_x_px": 0.25,
        "shift_y_px": 0.0,
        "description": "LaserDisc (ATI Theatre default)",
    },
    "vhs_composite": {
        "shift_x_px": 0.5,
        "shift_y_px": 0.0,
        "description": "VHS Composite (typical consumer capture)",
    },
    "svhs": {
        "shift_x_px": 0.15,
        "shift_y_px": 0.0,
        "description": "S-VHS (separate chroma channel)",
    },
    "video8": {
        "shift_x_px": 0.25,
        "shift_y_px": 0.0,
        "description": "Video8 (standard 8mm analog)",
    },
    "hi8": {
        "shift_x_px": 0.2,
        "shift_y_px": 0.0,
        "description": "Hi8 (8mm high band)",
    },
    "betamax": {
        "shift_x_px": 0.3,
        "shift_y_px": 0.0,
        "description": "Betamax (consumer format)",
    },
    "custom": {
        "shift_x_px": 0.0,
        "shift_y_px": 0.0,
        "description": "Custom values (user-specified)",
    },
}


def get_preset(preset_name: str) -> dict:
    """
    Get chroma correction parameters for a hardware preset.

    Parameters:
        preset_name: Preset identifier from CHROMA_PRESETS keys

    Returns:
        Dictionary with shift_x_px, shift_y_px, description

    Example:
        >>> preset = get_preset("laserdisc")
        >>> print(preset["shift_x_px"])
        0.25
    """
    return CHROMA_PRESETS.get(
        preset_name.lower(), CHROMA_PRESETS["custom"]
    ).copy()
