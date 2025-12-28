import os
import vapoursynth as vs
import subprocess

NC_ENV = "ALLOW_NONCOMMERCIAL_ENGINES"


def apply(
    clip: vs.VideoNode,
    model_path: str,
    config_path: str = "",
    out_temp: str = "amt_temp_output.mp4",
    **kwargs
) -> vs.VideoNode:
    if os.getenv(NC_ENV) != "1":
        raise RuntimeError(
            "AMT is licensed under CC BY-NC 4.0 and is disabled "
            "in commercial builds. Set ALLOW_NONCOMMERCIAL_ENGINES=1 "
            "to enable."
        )

    subprocess.run(
        [
            "python",
            "amt_interpolate.py",
            "--input",
            "INPUT_PLACEHOLDER",
            "--config",
            config_path,
            "--model",
            model_path,
            "--output",
            out_temp,
        ],
        check=True,
    )

    core = vs.core
    return core.ffms2.Source(out_temp)
