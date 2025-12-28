import vapoursynth as vs

try:
    from vsdain import dain
except ImportError:
    dain = None

core = vs.core


def apply(
    clip: vs.VideoNode, factor: float = 2.0, model: str = "default", **kwargs
) -> vs.VideoNode:
    if dain is None:
        raise RuntimeError("vsdain is not installed.")
    return dain(clip, factor=factor, model=model, **kwargs)
