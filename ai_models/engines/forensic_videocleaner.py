import vapoursynth as vs
import subprocess

core = vs.core


def apply(
    clip: vs.VideoNode,
    input_path: str,
    output_path: str,
    videocleaner_exe: str = r"C:\\VideoCleaner\\VideoCleaner.exe",
    script: str = None,
    **kwargs
) -> vs.VideoNode:
    args = [videocleaner_exe, input_path, output_path]
    if script:
        args += ["--script", script]
    subprocess.run(args, check=True)
    return core.ffms2.Source(output_path)
