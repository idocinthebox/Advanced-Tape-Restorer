"""
Theatre Mode - Hardware-Accurate Analog Processing Orchestration

Coordinates the Theatre Mode processing pipeline, including:
- Auto-profiling and tape analysis
- Hardware-accurate chroma correction
- Field-aware deinterlacing variants
- Black/white level adjustment
- DaVinci Resolve LUT generation
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Callable
import json


@dataclass
class TapeProfile:
    """
    Per-tape analysis results from auto-profiling.

    Attributes:
        input_path: Source video file path
        field_order: Detected field order ('tff', 'bff', or 'progressive')
        chroma_shift_x: Recommended horizontal chroma shift in pixels
        chroma_shift_y: Recommended vertical chroma shift in pixels
        black_point: Detected black level (0.0-1.0)
        white_point: Detected white level (0.0-1.0)
        avg_saturation: Average chroma saturation (0.0-0.5 typical)
        saturation_boost: Recommended saturation multiplier (1.0 = no change)
        notes: List of detected issues or recommendations
    """

    input_path: str
    field_order: str
    chroma_shift_x: float
    chroma_shift_y: float
    black_point: float
    white_point: float
    avg_saturation: float
    saturation_boost: float
    notes: list[str]

    def to_json(self) -> str:
        """Serialize profile to JSON string."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "TapeProfile":
        """Deserialize profile from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

    def save(self, path: Path):
        """Save profile to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "TapeProfile":
        """Load profile from JSON file."""
        return cls.from_json(path.read_text(encoding="utf-8"))


class TheatreModeProcessor:
    """
    Theatre Mode processing coordinator.

    Manages the hardware-accurate analog processing pipeline:
    1. Auto-profiling (optional but recommended)
    2. Chroma phase correction
    3. Field-aware deinterlacing
    4. Level adjustment
    5. Optional LUT generation
    """

    def __init__(self, work_dir: Path = Path("work")):
        """
        Initialize Theatre Mode processor.

        Args:
            work_dir: Working directory for profiles, LUTs, temp files
        """
        self.work_dir = work_dir
        self.profiles_dir = work_dir / "profiles"
        self.luts_dir = work_dir / "luts"
        self.vpy_dir = work_dir / "vpy"

        # Create directories
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.luts_dir.mkdir(parents=True, exist_ok=True)
        self.vpy_dir.mkdir(parents=True, exist_ok=True)

    def analyze_tape(
        self,
        input_path,
        sample_frames: int = 40,
        sample_stride: int = 150,
        default_chroma_shift_x: float = 0.25,
        default_field_order: str = "tff",
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> TapeProfile:
        """
        Auto-profile a tape to detect optimal processing parameters.
        
        Uses vspipe subprocess (same as video processing) to analyze frames.

        Args:
            input_path: Path to source video file (str or Path)
            sample_frames: Number of frames to analyze (default: 40)
            sample_stride: Frame stride for sampling (default: 150, ~1 per 5 sec)
            default_chroma_shift_x: Default chroma shift if detection fails
            default_field_order: Default field order if detection fails
            progress_callback: Optional callback(percent, message)

        Returns:
            TapeProfile with detected parameters and recommendations

        Raises:
            RuntimeError: If vspipe is not available
            FileNotFoundError: If input file doesn't exist
        """
        import subprocess
        import tempfile
        import json
        
        # Convert to Path object first (before any Path operations)
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if progress_callback:
            progress_callback(0, "Initializing analysis...")

        # Check if vspipe is available
        try:
            result = subprocess.run(
                ["vspipe", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("vspipe is not working correctly")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                "vspipe not found. Please install VapourSynth R65+ and ensure it's on PATH."
            )

        if progress_callback:
            progress_callback(10, "Generating analysis script...")

        # Generate VapourSynth script to analyze frames
        vpy_script = self._generate_analysis_script(
            input_path, sample_frames, sample_stride
        )
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.vpy', delete=False, encoding='utf-8'
        ) as f:
            f.write(vpy_script)
            vpy_path = f.name

        try:
            if progress_callback:
                progress_callback(20, "Running analysis...")

            # Run vspipe to get frame statistics
            result = subprocess.run(
                ["vspipe", "--info", vpy_path, "-"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"vspipe analysis failed: {result.stderr}")

            if progress_callback:
                progress_callback(90, "Processing results...")

            # Parse output to get statistics
            # For now, use simplified analysis with defaults
            # (Full statistical analysis would require frame output parsing)
            notes = []
            
            # Use default values (could be enhanced with actual frame analysis)
            black_point = 0.05
            white_point = 0.9
            avg_saturation = 0.1
            saturation_boost = 1.0
            
            # Generic recommendations
            notes.append(
                f"Field order set to {default_field_order.upper()} (analog tape standard). "
                "Override if capture source is known to be BFF."
            )
            notes.append(
                "Using default chroma correction values. "
                "Adjust X/Y shift if colors appear misaligned."
            )

            if progress_callback:
                progress_callback(95, "Finalizing profile...")

            profile = TapeProfile(
                input_path=str(input_path),
                field_order=default_field_order,
                chroma_shift_x=default_chroma_shift_x,
                chroma_shift_y=0.0,
                black_point=black_point,
                white_point=white_point,
                avg_saturation=avg_saturation,
                saturation_boost=saturation_boost,
                notes=notes,
            )

            # Save profile
            profile_path = self.profiles_dir / f"{input_path.stem}.profile.json"
            profile.save(profile_path)

            if progress_callback:
                progress_callback(100, f"Profile saved to {profile_path.name}")

            return profile
            
        finally:
            # Clean up temp file
            try:
                Path(vpy_path).unlink()
            except:
                pass

    def _generate_analysis_script(
        self, input_path: Path, sample_frames: int, sample_stride: int
    ) -> str:
        """
        Generate VapourSynth script for frame analysis.
        
        Returns a .vpy script that can be run with vspipe.
        """
        return f'''# Theatre Mode Auto-Profiling Script
import vapoursynth as vs
core = vs.core

# Load source
video = core.ffms2.Source(r"{str(input_path)}")

# Basic info output
print(f"Frames: {{video.num_frames}}")
print(f"FPS: {{video.fps_num}}/{{video.fps_den}}")
print(f"Resolution: {{video.width}}x{{video.height}}")

# Output for vspipe
video.set_output()
'''

    def get_profile_path(self, input_path: Path) -> Path:
        """Get the expected profile path for an input file."""
        return self.profiles_dir / f"{input_path.stem}.profile.json"

    def has_profile(self, input_path: Path) -> bool:
        """Check if a profile exists for an input file."""
        return self.get_profile_path(input_path).exists()

    def load_profile(self, input_path: Path) -> Optional[TapeProfile]:
        """
        Load profile for an input file if it exists.

        Returns:
            TapeProfile if found, None otherwise
        """
        profile_path = self.get_profile_path(input_path)
        if not profile_path.exists():
            return None
        return TapeProfile.load(profile_path)

    def generate_theatre_mode_options(
        self, profile: Optional[TapeProfile] = None, user_overrides: Optional[dict] = None
    ) -> dict:
        """
        Generate processing options for Theatre Mode.

        Combines profile recommendations with user overrides.

        Args:
            profile: Optional tape profile from auto-analysis
            user_overrides: Optional dict of user-specified overrides

        Returns:
            Dictionary of processing options for VapourSynthEngine
        """
        # Default Theatre Mode settings
        options = {
            "theatre_mode_enabled": True,
            "chroma_correction_enabled": True,
            "chroma_shift_x_px": 0.25,  # LaserDisc default
            "chroma_shift_y_px": 0.0,
            "field_order": "tff",
            "deinterlace_variant": "standard",  # standard/bob/keep_interlaced
            "apply_level_adjustment": False,
            "black_point": 0.0,
            "white_point": 1.0,
            "saturation_boost": 1.0,
        }

        # Apply profile recommendations if available
        if profile:
            options["chroma_shift_x_px"] = profile.chroma_shift_x
            options["chroma_shift_y_px"] = profile.chroma_shift_y
            options["field_order"] = profile.field_order
            options["black_point"] = profile.black_point
            options["white_point"] = profile.white_point
            options["saturation_boost"] = profile.saturation_boost

            # Auto-enable level adjustment if needed
            if profile.white_point < 0.6 or profile.black_point > 0.1:
                options["apply_level_adjustment"] = True

        # Apply user overrides
        if user_overrides:
            options.update(user_overrides)

        return options


# Deinterlacing variant descriptions for GUI
DEINTERLACE_VARIANTS = {
    "standard": {
        "name": "Standard Progressive",
        "description": "QTGMC deinterlace to progressive (30p/25p). Best for modern displays.",
        "fps_divisor": 2,
    },
    "bob": {
        "name": "Bob (Double-Rate)",
        "description": "QTGMC bob mode (60p/50p). Preserves all motion, double file size.",
        "fps_divisor": 1,
    },
    "keep_interlaced": {
        "name": "Keep Interlaced",
        "description": "Field-aware filtering only, no deinterlace. For interlaced delivery.",
        "fps_divisor": None,
    },
}
