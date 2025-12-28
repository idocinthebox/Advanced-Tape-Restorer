import vapoursynth as vs

try:
    from vsfilm import film
except ImportError:
    film = None

core = vs.core


def apply(
    clip: vs.VideoNode, scale: int = 1, tta: bool = False, **kwargs
) -> vs.VideoNode:
    if film is None:
        raise RuntimeError("vsfilm is not installed.")
    return film(clip, scale=scale, tta=tta, **kwargs)
