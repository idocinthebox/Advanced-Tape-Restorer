"""
Advanced Tape Restorer v3.2 - Core Module

Contains the primary logic for video analysis, processing, and encoding.
"""

import re
import tempfile
import json
import shutil
import subprocess
import threading
from pathlib import Path


class VideoAnalyzer:
    """Analyzes video files using ffprobe."""

    def __init__(self):
        """Initializes the VideoAnalyzer."""
        self.ffprobe_path = shutil.which("ffprobe")

    def get_video_info(self, video_path):
        """
        Retrieves video stream information using ffprobe.

        Args:
            video_path (str): The path to the video file.

        Returns:
            dict: A dictionary containing the video information from ffprobe.

        Raises:
            RuntimeError: If ffprobe is not found or if there's an error running it.
            FileNotFoundError: If the video file does not exist.
        """
        if not self.ffprobe_path:
            raise RuntimeError("ffprobe executable not found in system PATH.")

        if not Path(video_path).exists():
            raise FileNotFoundError(f"Input video file not found: {video_path}")

        command = [
            self.ffprobe_path,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]

        result = subprocess.check_output(command, text=True, encoding="utf-8")
        return json.loads(result)


class VapourSynthEngine:
    """Manages the execution of VapourSynth scripts."""

    def __init__(self, script_path):
        """
        Initializes the VapourSynthEngine.

        Args:
            script_path (str): The path to the .vpy VapourSynth script.
        """
        self.script_path = script_path
        self.vspipe_path = shutil.which("vspipe")

    def run(self, output_process):
        """DEPRECATED: Use Popen-based approach for stoppable processes.

        Executes the VapourSynth script and pipes the output.

        Args:
            output_process (subprocess.Popen): The process (e.g., FFmpeg) to pipe the video stream to.

        Raises:
            RuntimeError: If vspipe is not found.
        """
        if not self.vspipe_path:
            raise RuntimeError("vspipe executable not found in system PATH.")

        command = [self.vspipe_path, "--y4m", self.script_path, "-"]

        # The stdout of vspipe is piped to the stdin of the output_process
        subprocess.run(command, stdout=output_process.stdin, check=True)


class FFmpegEncoder:
    """Builds and executes FFmpeg encoding commands."""

    def __init__(self):
        """Initializes the FFmpegEncoder."""
        self.ffmpeg_path = shutil.which("ffmpeg")

    def build_command(self, input_file, output_file, options, pipe_input=False):
        """
        Builds an FFmpeg command list from a dictionary of options.

        Args:
            input_file (str): Path to the input file or '-' for pipe.
            output_file (str): Path to the output file.
            options (dict): A dictionary of encoding options.
            pipe_input (bool): If True, sets the input to '-'.

        Returns:
            list: A list of command-line arguments for FFmpeg.
        """
        if not self.ffmpeg_path:
            raise RuntimeError("ffmpeg executable not found in system PATH.")

        input_path = "-" if pipe_input else str(input_file)

        command = [self.ffmpeg_path, "-i", input_path]

        # --- Codec and Quality ---
        codec_str = options.get("codec", "libx264 (H.264, CPU)")
        codec = codec_str.split(" ")[0]
        command.extend(["-c:v", codec])

        if "crf" in options:
            command.extend(["-crf", str(options["crf"])])

        if "ffmpeg_preset" in options:
            command.extend(["-preset", options["ffmpeg_preset"]])

        # --- Audio ---
        audio_option = options.get("audio", "copy")
        if audio_option.lower() == "no audio":
            command.append("-an")
        else:
            command.extend(["-c:a", audio_option])

        # --- Final Output ---
        command.extend(["-y", str(output_file)])  # -y overwrites output file

        return command


class VideoProcessor:
    """Orchestrates the video restoration process."""

    def __init__(self):
        """Initializes the VideoProcessor."""
        self.analyzer = VideoAnalyzer()
        self.encoder = FFmpegEncoder()
        self._stop_requested = threading.Event()
        self.active_processes = []

    def check_prerequisites(self):
        """
        Checks if all required command-line tools are available.

        Raises:
            RuntimeError: If a required tool (ffmpeg, ffprobe, vspipe) is not found.
        """
        tools = ["ffmpeg", "ffprobe", "vspipe"]
        missing = [tool for tool in tools if not shutil.which(tool)]
        if missing:
            raise RuntimeError(f"Missing required tools in PATH: {', '.join(missing)}")

    def get_video_info(self, video_path):
        """
        Gets video information by delegating to the VideoAnalyzer.

        Args:
            video_path (str): The path to the video file.

        Returns:
            dict: A dictionary containing video information.
        """
        return self.analyzer.get_video_info(video_path)

    def _read_ffmpeg_progress(self, process, total_frames, callback):
        """Reads and parses ffmpeg's stderr for progress updates."""
        # FFmpeg progress line format: frame=  123 fps= 25.0 q=28.0 size=...
        frame_regex = re.compile(r"frame=\s*(\d+)")
        fps_regex = re.compile(r"fps=\s*([\d\.]+)")

        while process.poll() is None:
            line = process.stderr.readline()
            if not line:
                break

            frame_match = frame_regex.search(line)
            if frame_match:
                current_frame = int(frame_match.group(1))
                fps = 0.0
                
                # Try to extract FPS from the same line
                fps_match = fps_regex.search(line)
                if fps_match:
                    try:
                        fps = float(fps_match.group(1))
                    except ValueError:
                        fps = 0.0
                
                if callback:
                    callback(current_frame, total_frames, fps)

    def process_video(
        self,
        input_file,
        output_file,
        restoration_options,
        encoding_options,
        progress_callback=None,
    ):
        """
        Generates a VapourSynth script and runs the vspipe -> ffmpeg pipeline.
        This process is designed to be cancellable.
        """
        self.cleanup()  # Ensure stop flag is clear before starting
        print(f"Processing '{input_file}' to '{output_file}'...")

        # Get total frames for progress calculation
        try:
            video_info = self.get_video_info(input_file)
            total_frames = int(video_info["streams"][0].get("nb_frames", 0))
            if total_frames == 0:
                # Fallback for streams where nb_frames is not available
                print(
                    "Warning: nb_frames not found, progress bar will be indeterminate."
                )
        except Exception as e:
            print(f"Warning: Could not get total frames. {e}")
            total_frames = 0

        # 1. Generate a VapourSynth script (for this example, a dummy script)
        script_content = f"""
import vapoursynth as vs
core = vs.get_core()
video = core.ffms2.Source(source='{input_file}')
# Add actual filters based on restoration_options here
video.set_output()
"""
        script_path = Path(tempfile.gettempdir()) / "temp_restoration_script.vpy"
        script_path.write_text(script_content, encoding="utf-8")

        # 2. Build FFmpeg command and start the encoder process
        ffmpeg_cmd = self.encoder.build_command(
            input_file, output_file, encoding_options, pipe_input=True
        )
        # Add '-progress pipe:2' to send progress to stderr, which we capture
        ffmpeg_proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.active_processes.append(ffmpeg_proc)

        # 3. Start the VapourSynth process, piping its output to FFmpeg
        vspipe_cmd = [shutil.which("vspipe"), "--y4m", str(script_path), "-"]
        vspipe_proc = subprocess.Popen(vspipe_cmd, stdout=ffmpeg_proc.stdin)
        self.active_processes.append(vspipe_proc)

        # 4. Start a thread to read progress from ffmpeg's stderr
        if progress_callback and total_frames > 0:
            progress_thread = threading.Thread(
                target=self._read_ffmpeg_progress,
                args=(ffmpeg_proc, total_frames, progress_callback),
            )
            progress_thread.start()

        # 4. Monitor the process and check for stop requests
        while ffmpeg_proc.poll() is None:
            if self._stop_requested.is_set():
                print("Stop requested, terminating subprocesses...")
                # Terminate processes in reverse order
                vspipe_proc.terminate()
                ffmpeg_proc.terminate()
                # Wait for them to close to prevent zombie processes
                vspipe_proc.wait(timeout=5)
                ffmpeg_proc.wait(timeout=5)
                print("Subprocesses terminated.")
                break

            # Wait for a short duration to avoid busy-waiting
            try:
                ffmpeg_proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                continue

        self.active_processes.clear()
        if "progress_thread" in locals() and progress_thread.is_alive():
            progress_thread.join()

    def request_stop(self):
        """Sets a flag to gracefully stop any ongoing processing."""
        self._stop_requested.set()
        print("Stop request received.")
        # In a real app, you might also kill self.active_processes here
        # if they don't respond to the flag quickly.

    def cleanup(self):
        """Cleans up temporary files and resets state."""
        self._stop_requested.clear()
        print("Cleanup complete.")
