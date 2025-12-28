"""
AI Engines - Modular wrappers for VapourSynth AI plugins

Each engine provides a standardized `apply(clip, **kwargs)` interface
for consistent usage across the application.

Available Engines:
    Upscaling:
        - upscaling_realesrgan: RealESRGAN 2x/4x upscaling
        - upscaling_basicvsrpp: BasicVSR++ video super-resolution
        - upscaling_swinir: SwinIR transformer-based upscaling

    Interpolation:
        - interpolation_rife: RIFE frame interpolation
        - interpolation_amt: AMT adaptive motion interpolation

    Colorization:
        - color_deoldify: DeOldify B&W colorization
        - color_svdiffusion: Stable Diffusion colorization

    Face Enhancement:
        - face_gfpgan: GFPGAN face restoration

    Forensic:
        - forensic_videocleaner: Video artifact cleaning

Usage:
    from ai_models.engines.upscaling_realesrgan import apply as realesrgan_apply

    result_clip = realesrgan_apply(
        clip,
        model="RealESRGAN_x2plus",
        scale=2,
        tile_w=0,
        tile_h=0,
        fp16=True,
        weights_path="/path/to/model.pth"
    )
"""

__version__ = "3.0.0"

__all__ = []
