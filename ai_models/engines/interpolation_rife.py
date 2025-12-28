import vapoursynth as vs
from vsrife import rife

core = vs.core


def apply(
    clip: vs.VideoNode,
    model: str = "4.22",
    factor_num: int = 2,
    factor_den: int = 1,
    device_index: int = 0,
    ensemble: bool = False,
    sc: bool = False,
    sc_threshold: float = 0.15,
    **kwargs
) -> vs.VideoNode:
    """
    Apply RIFE frame interpolation to a clip.

    Model versions:
        '4.25': RIFE v4.25 (latest)
        '4.22': RIFE v4.22 (default)
        '4.6': RIFE v4.6
    """
    return rife(
        clip,
        device_index=device_index,
        model=model,
        auto_download=True,
        factor_num=factor_num,
        factor_den=factor_den,
        ensemble=ensemble,
        sc=sc,
        sc_threshold=sc_threshold,
        **kwargs
    )
