import vapoursynth as vs

try:
    from vsbasicvsrpp import basicvsrpp

    _HAS_BASICVSRPP = True
except ImportError:
    _HAS_BASICVSRPP = False
    basicvsrpp = None

core = vs.core


def apply(
    clip: vs.VideoNode,
    model: str = "bd",
    scale: int = 2,
    tile_w: int = 0,
    tile_h: int = 0,
    device_index: int = 0,
    length: int = 15,
    cpu_cache: bool = False,
    tile_pad: int = 16,
    **kwargs
) -> vs.VideoNode:
    """
    Apply BasicVSR++ upscaling/deblurring to a clip.

    Model options:
        'reds': Video Super-Resolution (REDS)
        'bi': Video Super-Resolution (Vimeo-90K BI) - upscaling
        'bd': Video Super-Resolution (Vimeo-90K BD) - deblurring (default)
        'dvd': Video Deblurring (DVD)
        'gopro': Video Deblurring (GoPro)
        'denoise': Video Denoising
    """
    if not _HAS_BASICVSRPP:
        raise RuntimeError(
            "vsbasicvsrpp plugin not installed. "
            "Please install it to use BasicVSR++ upscaling."
        )

    # Map model names to model numbers
    model_map = {
        "reds": 0,  # Video Super-Resolution (REDS)
        "bi": 1,  # Video Super-Resolution (Vimeo-90K BI degradation) - upscaling
        "bd": 2,  # Video Super-Resolution (Vimeo-90K BD degradation) - deblurring
        "ntire": 3,  # NTIRE VSR challenge
        "decomp1": 4,  # NTIRE decompress track 1
        "decomp2": 5,  # NTIRE decompress track 2
        "decomp3": 6,  # NTIRE decompress track 3
        "dvd": 7,  # Video Deblurring (DVD)
        "gopro": 8,  # Video Deblurring (GoPro)
        "denoise": 9,  # Video Denoising
    }

    # Get model number (default to 2 = BD model for deblurring)
    model_num = model_map.get(model, 2)

    # Prepare tile size [width, height]
    tile = [tile_w, tile_h] if tile_w > 0 and tile_h > 0 else [0, 0]

    return basicvsrpp(
        clip,
        device_index=device_index,
        model=model_num,
        auto_download=True,  # Auto-download if model file missing
        length=length,
        cpu_cache=cpu_cache,
        tile=tile,
        tile_pad=tile_pad,
    )
