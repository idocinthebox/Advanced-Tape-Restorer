import vapoursynth as vs

try:
    from vsswinir import swinir

    _HAS_SWINIR = True
except ImportError:
    _HAS_SWINIR = False
    swinir = None

core = vs.core


def apply(
    clip: vs.VideoNode,
    model: str = "real_sr_x4",
    scale: int = 4,
    tile_w: int = 0,
    tile_h: int = 0,
    tile_pad: int = 16,
    device_index: int = None,
    num_streams: int = 1,
    nvfuser: bool = False,
    cuda_graphs: bool = False,
    **kwargs
) -> vs.VideoNode:
    """
    Apply SwinIR upscaling to a clip.

    Model options:
        'lightweight_x2': Lightweight SR x2 (DIV2K)
        'lightweight_x3': Lightweight SR x3 (DIV2K)
        'lightweight_x4': Lightweight SR x4 (DIV2K)
        'real_sr_x4': Real-world SR x4 (BSRGAN/GAN) - default for tape restoration
        'anime_x2': Anime upscaling x2
    """
    if not _HAS_SWINIR:
        raise RuntimeError(
            "vsswinir plugin not installed. "
            "Please install it to use SwinIR upscaling."
        )

    # Map model names to model numbers
    model_map = {
        "lightweight_x2": 0,  # 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2
        "lightweight_x3": 1,  # 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x3
        "lightweight_x4": 2,  # 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4
        "real_sr_x4": 3,  # 003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN (best for real footage)
        "anime_x2": 4,  # 2x_Bubble_AnimeScale_SwinIR_Small_v1
    }

    # Get model number (default to 3 = real SR x4 for tape restoration)
    model_num = model_map.get(model, 3)

    return swinir(
        clip,
        device_index=device_index,
        num_streams=num_streams,
        nvfuser=nvfuser,
        cuda_graphs=cuda_graphs,
        model=model_num,
        tile_w=tile_w,
        tile_h=tile_h,
        tile_pad=tile_pad,
    )
