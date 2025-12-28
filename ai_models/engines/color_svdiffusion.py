import vapoursynth as vs
import subprocess

core = vs.core


def apply(
    clip: vs.VideoNode,
    model_path: str,
    out_path: str = "svd_output.mp4",
    strength: float = 0.35,
    **kwargs
) -> vs.VideoNode:
    temp_in = "svd_input_placeholder.mp4"
    subprocess.run(
        [
            "python",
            "svdiffusion.py",
            "--input",
            temp_in,
            "--output",
            out_path,
            "--model",
            model_path,
            "--strength",
            str(strength),
        ],
        check=True,
    )
    return core.ffms2.Source(out_path)
