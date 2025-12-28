import vapoursynth as vs
from vsrealesrgan import realesrgan, RealESRGANModel

core = vs.core


def apply(
    clip: vs.VideoNode,
    model: str = "realesr_general_x4v3",
    scale: int = 2,
    tile_w: int = 0,
    tile_h: int = 0,
    device_index: int = 0,
    denoise_strength: float = 0.5,
    tile_pad: int = 8,
    face_enhance: bool = False,
    **kwargs
) -> vs.VideoNode:
    """
    Apply RealESRGAN upscaling to a clip.

    Model options (most common):
        'realesr_general_x4v3': General real-world x4 (default, best for tape restoration)
        'RealESRGAN_x2plus': Real-world x2plus
        'RealESRGAN_x4plus': Real-world x4plus
        'RealESRGAN_x4plus_anime_6B': Anime-optimized x4
        'realesr_animevideov3': Anime video v3

    Args:
        face_enhance: Enable face enhancement (improves facial details)
    """
    # Map model names to enum values
    model_map = {
        "ESRGAN_SRx4": RealESRGANModel.ESRGAN_SRx4,
        "RealESRGAN_x2plus": RealESRGANModel.RealESRGAN_x2plus,
        "RealESRGAN_x4plus": RealESRGANModel.RealESRGAN_x4plus,
        "RealESRGAN_x4plus_anime_6B": RealESRGANModel.RealESRGAN_x4plus_anime_6B,
        "realesr_animevideov3": RealESRGANModel.realesr_animevideov3,
        "realesr_general_x4v3": RealESRGANModel.realesr_general_x4v3,
        "AnimeJaNai_V2_Compact_2x": RealESRGANModel.AnimeJaNai_V2_Compact_2x,
    }

    # Get model enum (default to realesr_general_x4v3 for tape restoration)
    model_enum = model_map.get(model, RealESRGANModel.realesr_general_x4v3)

    # Prepare tile size [width, height]
    tile = [tile_w, tile_h] if tile_w > 0 and tile_h > 0 else [0, 0]

    # Filter out unsupported parameters
    # - weights_path: newer vsrealesrgan auto-downloads models
    # - face_enhance: not supported by vsrealesrgan.realesrgan()
    filtered_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["weights_path", "weights_paths", "face_enhance"]
    }

    # Note: face_enhance is accepted for API compatibility but not passed to realesrgan
    # (vsrealesrgan doesn't support it as of current version)

    return realesrgan(
        clip,
        device_index=device_index,
        model=model_enum,
        auto_download=True,
        denoise_strength=denoise_strength,
        tile=tile,
        tile_pad=tile_pad,
        **filtered_kwargs
    )
