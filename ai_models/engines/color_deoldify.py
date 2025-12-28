import vapoursynth as vs

try:
    from vsdeoldify import deoldify
except ImportError:
    deoldify = None

core = vs.core


def apply(
    clip: vs.VideoNode, render_factor: int = 35, model: str = "video", **kwargs
) -> vs.VideoNode:
    if deoldify is None:
        raise RuntimeError("vsdeoldify is not installed.")
    return deoldify(clip, model=model, render_factor=render_factor, **kwargs)
