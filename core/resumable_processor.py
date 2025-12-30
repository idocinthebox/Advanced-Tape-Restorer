"""
Resumable/Incremental Video Processing
Allows processing to be paused and resumed without losing progress

Features:
- Checkpoint saving
- Automatic recovery from crashes
- Progress tracking
- Partial result preservation
- User-configurable checkpoint location
"""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class ProcessingCheckpoint:
    """
    Checkpoint data for resumable processing.
    """

    job_id: str
    input_file: str
    output_file: str
    total_frames: int
    processed_frames: int
    current_frame: int
    start_time: float
    last_update: float
    settings_hash: str
    status: str  # 'running', 'paused', 'completed', 'failed'
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProcessingCheckpoint":
        """Create from dictionary."""
        return cls(**data)

    def progress_percent(self) -> float:
        """Get progress as percentage."""
        if self.total_frames == 0:
            return 0.0
        return (self.processed_frames / self.total_frames) * 100

    def elapsed_time(self) -> float:
        """Get elapsed processing time in seconds."""
        return self.last_update - self.start_time

    def estimated_remaining(self) -> float:
        """Estimate remaining time in seconds."""
        if self.processed_frames == 0:
            return 0.0

        elapsed = self.elapsed_time()
        rate = self.processed_frames / elapsed
        remaining_frames = self.total_frames - self.processed_frames

        return remaining_frames / rate if rate > 0 else 0.0


class ResumableProcessor:
    """
    Manages resumable video processing with checkpoints.

    Usage:
        processor = ResumableProcessor(
            job_id="video_001",
            checkpoint_dir="./checkpoints"
        )

        # Start or resume processing
        for frame_idx in processor.get_frame_range(total_frames=1000):
            result = process_frame(frame_idx)
            processor.mark_frame_complete(frame_idx)

            # Auto-saves checkpoint every 10 frames
            if processor.should_checkpoint():
                processor.save_checkpoint()

        processor.mark_complete()
    """
    
    __slots__ = ('job_id', 'input_file', 'output_file', 'checkpoint_dir', 'checkpoint_interval', 'checkpoint')  # Memory optimization

    def __init__(
        self,
        job_id: str,
        input_file: Path,
        output_file: Path,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_interval: int = 50,
    ):
        """
        Initialize resumable processor.

        Args:
            job_id: Unique identifier for this job
            input_file: Input video path
            output_file: Output video path
            checkpoint_dir: Directory for checkpoint files (None = use config/default)
            checkpoint_interval: Save checkpoint every N frames
        """
        # Load from config if not specified
        if checkpoint_dir is None:
            try:
                from core.config import get_config

                config = get_config()
                checkpoint_dir = config.get_checkpoint_dir()
            except ImportError:
                # Fallback to default
                checkpoint_dir = Path("./checkpoints")

        self.job_id = job_id
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_interval = checkpoint_interval

        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load or create checkpoint
        self.checkpoint = self._load_or_create_checkpoint()

        print(f"Resumable processor initialized: {job_id}")
        if self.checkpoint.processed_frames > 0:
            print(
                f"  Resuming from frame {self.checkpoint.current_frame} "
                f"({self.checkpoint.progress_percent():.1f}%)"
            )

    def _get_checkpoint_path(self) -> Path:
        """Get path to checkpoint file."""
        return self.checkpoint_dir / f"{self.job_id}.checkpoint.json"

    def _load_or_create_checkpoint(self) -> ProcessingCheckpoint:
        """Load existing checkpoint or create new one."""
        checkpoint_path = self._get_checkpoint_path()

        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, "r") as f:
                    data = json.load(f)
                    checkpoint = ProcessingCheckpoint.from_dict(data)

                    # Validate checkpoint
                    if checkpoint.status in ["completed", "failed"]:
                        print(f"⚠ Previous job {checkpoint.status}, starting fresh")
                        return self._create_new_checkpoint()

                    print(f"✓ Loaded checkpoint from {checkpoint_path}")
                    return checkpoint

            except Exception as e:
                print(f"⚠ Failed to load checkpoint: {e}")
                return self._create_new_checkpoint()

        return self._create_new_checkpoint()

    def _create_new_checkpoint(self) -> ProcessingCheckpoint:
        """Create new checkpoint."""
        settings_hash = self._compute_settings_hash()

        return ProcessingCheckpoint(
            job_id=self.job_id,
            input_file=str(self.input_file),
            output_file=str(self.output_file),
            total_frames=0,
            processed_frames=0,
            current_frame=0,
            start_time=time.time(),
            last_update=time.time(),
            settings_hash=settings_hash,
            status="running",
        )

    def _compute_settings_hash(self, settings: Optional[dict] = None) -> str:
        """Compute hash of processing settings to detect changes."""
        if settings is None:
            settings = {}

        # Add file info to settings
        settings["input_file"] = str(self.input_file)
        settings["output_file"] = str(self.output_file)

        settings_str = json.dumps(settings, sort_keys=True)
        return hashlib.md5(settings_str.encode()).hexdigest()

    def set_total_frames(self, total_frames: int):
        """Set total number of frames to process."""
        self.checkpoint.total_frames = total_frames
        self.save_checkpoint()

    def get_frame_range(self, total_frames: Optional[int] = None):
        """
        Get range of frames to process (supports resume).

        Args:
            total_frames: Total frames (if known)

        Yields:
            Frame indices to process
        """
        if total_frames is not None:
            self.set_total_frames(total_frames)

        start_frame = self.checkpoint.current_frame
        end_frame = self.checkpoint.total_frames

        if end_frame == 0:
            raise ValueError("Total frames not set. Call set_total_frames() first.")

        print(f"Processing frames {start_frame} to {end_frame}")

        for frame_idx in range(start_frame, end_frame):
            yield frame_idx

    def mark_frame_complete(self, frame_idx: int):
        """Mark a frame as successfully processed (optimized)."""
        self.checkpoint.current_frame = frame_idx + 1
        self.checkpoint.processed_frames += 1
        self.checkpoint.last_update = time.time()  # Only update timestamp, not full save

    def should_checkpoint(self) -> bool:
        """Check if it's time to save checkpoint."""
        return self.checkpoint.processed_frames % self.checkpoint_interval == 0

    def save_checkpoint(self):
        """Save checkpoint to disk."""
        checkpoint_path = self._get_checkpoint_path()

        try:
            with open(checkpoint_path, "w") as f:
                json.dump(self.checkpoint.to_dict(), f, indent=2)

        except Exception as e:
            print(f"⚠ Failed to save checkpoint: {e}")

    def mark_complete(self):
        """Mark job as completed."""
        self.checkpoint.status = "completed"
        self.checkpoint.processed_frames = self.checkpoint.total_frames
        self.checkpoint.current_frame = self.checkpoint.total_frames
        self.save_checkpoint()

        print(f"✓ Job {self.job_id} completed!")
        print(f"  Total time: {self.checkpoint.elapsed_time():.1f}s")

    def mark_failed(self, error_message: str):
        """Mark job as failed."""
        self.checkpoint.status = "failed"
        self.checkpoint.error_message = error_message
        self.save_checkpoint()

        print(f"✗ Job {self.job_id} failed: {error_message}")

    def pause(self):
        """Pause processing."""
        self.checkpoint.status = "paused"
        self.save_checkpoint()
        print(f"⏸ Job {self.job_id} paused at frame {self.checkpoint.current_frame}")

    def resume(self):
        """Resume processing."""
        if self.checkpoint.status == "paused":
            self.checkpoint.status = "running"
            print(f"▶ Job {self.job_id} resumed")

    def get_progress(self) -> dict:
        """Get current progress information."""
        return {
            "job_id": self.checkpoint.job_id,
            "progress_percent": self.checkpoint.progress_percent(),
            "processed_frames": self.checkpoint.processed_frames,
            "total_frames": self.checkpoint.total_frames,
            "current_frame": self.checkpoint.current_frame,
            "elapsed_time": self.checkpoint.elapsed_time(),
            "estimated_remaining": self.checkpoint.estimated_remaining(),
            "status": self.checkpoint.status,
        }

    def print_progress(self):
        """Print progress information."""
        progress = self.get_progress()

        print(f"\n=== Job {progress['job_id']} ===")
        print(f"Progress: {progress['progress_percent']:.1f}%")
        print(f"Frames: {progress['processed_frames']}/{progress['total_frames']}")
        print(f"Elapsed: {progress['elapsed_time']:.1f}s")
        print(f"Remaining: {progress['estimated_remaining']:.1f}s")
        print(f"Status: {progress['status']}")

    @classmethod
    def cleanup_old_checkpoints(cls, checkpoint_dir: Path, days: int = 7):
        """
        Delete old checkpoint files.

        Args:
            checkpoint_dir: Checkpoint directory
            days: Delete checkpoints older than this many days
        """
        checkpoint_dir = Path(checkpoint_dir)
        if not checkpoint_dir.exists():
            return

        cutoff_time = time.time() - (days * 86400)
        deleted = 0

        for checkpoint_file in checkpoint_dir.glob("*.checkpoint.json"):
            if checkpoint_file.stat().st_mtime < cutoff_time:
                checkpoint_file.unlink()
                deleted += 1

        print(f"✓ Deleted {deleted} old checkpoint(s)")


# Example usage
if __name__ == "__main__":
    print("=== Resumable Processor Test ===\n")

    # Simulate processing job
    processor = ResumableProcessor(
        job_id="test_video_001",
        input_file=Path("input.mp4"),
        output_file=Path("output.mp4"),
        checkpoint_dir=Path("./test_checkpoints"),
        checkpoint_interval=10,
    )

    # Simulate processing frames
    total_frames = 100

    try:
        for frame_idx in processor.get_frame_range(total_frames=total_frames):
            # Simulate processing
            time.sleep(0.01)

            # Mark complete
            processor.mark_frame_complete(frame_idx)

            # Checkpoint
            if processor.should_checkpoint():
                processor.save_checkpoint()
                print(f"Checkpoint saved at frame {frame_idx}")

            # Simulate interruption at frame 50
            if frame_idx == 50:
                print("\n⚠ Simulating interruption...")
                processor.pause()
                break

        # Resume processing
        print("\n▶ Resuming processing...\n")
        processor.resume()

        for frame_idx in processor.get_frame_range():
            time.sleep(0.01)
            processor.mark_frame_complete(frame_idx)

            if processor.should_checkpoint():
                processor.save_checkpoint()

        # Mark complete
        processor.mark_complete()

    except Exception as e:
        processor.mark_failed(str(e))

    # Print final progress
    processor.print_progress()

    # Cleanup
    ResumableProcessor.cleanup_old_checkpoints(Path("./test_checkpoints"), days=0)

    print("\n✓ Resumable processor test complete")
