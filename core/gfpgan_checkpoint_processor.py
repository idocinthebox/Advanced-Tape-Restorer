"""
GFPGAN Checkpoint Processor - Resumable Face Enhancement
Wraps SmartGFP with checkpoint support for interrupted job recovery

Features:
- Automatic checkpoint saving every N frames
- Resume from last processed frame
- Disk space monitoring during processing
- Frame-level progress tracking
- Compatible with existing SmartGFP optimizations
"""

import time
import hashlib
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

from core.resumable_processor import ResumableProcessor, ProcessingCheckpoint
from ai_models.engines.face_gfpgan import SmartGFPEnhancer
from core.disk_space_manager import check_space_available, format_bytes, get_temp_directory_with_space
import cv2


@dataclass
class GFPGANJobInfo:
    """
    Metadata for a GFPGAN processing job.
    Extends ProcessingCheckpoint with GFPGAN-specific info.
    """
    input_frames_dir: str
    output_frames_dir: str
    model_path: str
    upscale: int
    weight: float
    total_frames: int
    
    def to_dict(self) -> dict:
        return {
            'input_frames_dir': self.input_frames_dir,
            'output_frames_dir': self.output_frames_dir,
            'model_path': self.model_path,
            'upscale': self.upscale,
            'weight': self.weight,
            'total_frames': self.total_frames
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GFPGANJobInfo':
        return cls(**data)


class GFPGANCheckpointProcessor:
    """
    Resumable GFPGAN face enhancement processor.
    
    Wraps SmartGFP with automatic checkpoint saving, allowing jobs to be
    resumed after crashes, disk space exhaustion, or manual cancellation.
    
    AUTOMATIC FRAME MIGRATION:
    If you switch drives mid-processing (e.g., C: to D:), this processor
    automatically migrates already-processed frames to the new location so
    FFmpeg can find all frames in one directory for final video encoding.
    
    Usage:
        processor = GFPGANCheckpointProcessor(
            job_id="video_001_gfpgan",
            input_frames_dir="/path/to/extracted_frames",
            output_frames_dir="/path/to/enhanced_frames",
            model_path="/path/to/GFPGANv1.3.pth",
            checkpoint_interval=50  # Save every 50 frames
        )
        
        processor.process_with_checkpoints(
            progress_callback=lambda cur, total: print(f"{cur}/{total}"),
            log_callback=lambda msg: print(msg)
        )
        
        # Later, to resume:
        processor = GFPGANCheckpointProcessor(
            job_id="video_001_gfpgan",  # Same job_id
            ...
        )
        processor.process_with_checkpoints()  # Automatically resumes
    """
    
    def __init__(
        self,
        job_id: str,
        input_frames_dir: Path,
        output_frames_dir: Path,
        model_path: str,
        upscale: int = 2,
        weight: float = 0.5,
        checkpoint_dir: Optional[Path] = None,
        checkpoint_interval: int = 50,
        disk_space_buffer_gb: int = 5
    ):
        """
        Initialize resumable GFPGAN processor.
        
        Args:
            job_id: Unique identifier for this job (used for checkpoint files)
            input_frames_dir: Directory containing extracted PNG/JPG frames
            output_frames_dir: Directory to save enhanced frames
            model_path: Path to GFPGAN model weights (.pth file)
            upscale: Upscaling factor (1, 2, 4)
            weight: Restoration strength (0.0 to 1.0)
            checkpoint_dir: Directory for checkpoint files (None = use config default)
            checkpoint_interval: Save checkpoint every N frames
            disk_space_buffer_gb: Minimum free disk space to maintain (GB)
        """
        self.job_id = job_id
        self.input_frames_dir = Path(input_frames_dir)
        self.output_frames_dir = Path(output_frames_dir)
        self.model_path = model_path
        self.upscale = upscale
        self.weight = weight
        self.checkpoint_interval = checkpoint_interval
        self.disk_space_buffer_gb = disk_space_buffer_gb
        
        # Create output directory
        self.output_frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Get frame list
        self.frame_files = sorted(self.input_frames_dir.glob("*.png")) + sorted(
            self.input_frames_dir.glob("*.jpg")
        )
        
        if not self.frame_files:
            raise FileNotFoundError(f"No frames found in {self.input_frames_dir}")
        
        # Initialize resumable processor
        self.resumable = ResumableProcessor(
            job_id=job_id,
            input_file=self.input_frames_dir,
            output_file=self.output_frames_dir,
            checkpoint_dir=checkpoint_dir,
            checkpoint_interval=checkpoint_interval
        )
        
        self.resumable.set_total_frames(len(self.frame_files))
        
        # Initialize SmartGFP enhancer (lazy loading - only when processing starts)
        self.enhancer = None
        
        # Track processing state
        self._should_stop = False
        self.stats = {
            'total': len(self.frame_files),
            'processed': 0,
            'skipped_existing': 0,
            'resumed_from': self.resumable.checkpoint.current_frame,
            'migrated_frames': 0
        }
        
        # Store original output directory in checkpoint for migration detection
        self._original_output_dir = None
    
    def _init_enhancer(self):
        """Lazy initialization of SmartGFP enhancer."""
        if self.enhancer is None:
            self.enhancer = SmartGFPEnhancer(
                model_path=self.model_path,
                upscale=self.upscale
            )
    
    def _migrate_existing_frames(self, old_dir: Path, new_dir: Path, log_callback: Optional[Callable] = None) -> int:
        """
        Migrate already-processed frames from old directory to new directory.
        
        This is critical when switching drives mid-processing (e.g., C: to D:).
        All frames must be in one directory for FFmpeg to encode the final video.
        
        Args:
            old_dir: Previous output directory (where frames 0-N exist)
            new_dir: New output directory (where frames N+1 onwards will go)
            log_callback: Optional logging callback
        
        Returns:
            Number of frames migrated
        """
        import shutil
        
        if not old_dir.exists():
            return 0
        
        if log_callback:
            log_callback(f"🔄 Migrating frames from {old_dir} to {new_dir}")
        
        # Get list of already-processed frames
        existing_frames = sorted(old_dir.glob("frame_*.png"))
        
        if not existing_frames:
            return 0
        
        # Create new directory if needed
        new_dir.mkdir(parents=True, exist_ok=True)
        
        migrated = 0
        failed = 0
        
        # Copy each frame to new location
        for frame_file in existing_frames:
            try:
                dest = new_dir / frame_file.name
                
                # Skip if already exists (resume from previous migration)
                if dest.exists():
                    continue
                
                shutil.copy2(frame_file, dest)
                migrated += 1
                
                # Progress update every 100 frames
                if migrated % 100 == 0 and log_callback:
                    log_callback(f"   Migrated {migrated}/{len(existing_frames)} frames...")
                
            except Exception as e:
                if log_callback:
                    log_callback(f"⚠️ Failed to migrate {frame_file.name}: {e}")
                failed += 1
        
        if log_callback:
            if failed > 0:
                log_callback(f"✓ Migrated {migrated} frames ({failed} failed)")
            else:
                log_callback(f"✓ Migrated {migrated} frames successfully")
        
        return migrated
    
    def _detect_and_migrate_frames(self, log_callback: Optional[Callable] = None) -> bool:
        """
        Detect if output directory changed and migrate frames if needed.
        
        Returns:
            True if migration successful or not needed, False on failure
        """
        # Load original output directory from checkpoint metadata
        checkpoint_data = self.resumable.checkpoint.to_dict()
        stored_output = checkpoint_data.get('output_file', '')
        
        if not stored_output:
            # First run, store current output directory
            return True
        
        stored_output_path = Path(stored_output)
        current_output_path = self.output_frames_dir
        
        # Check if output directory changed (drive switch)
        if stored_output_path != current_output_path:
            if log_callback:
                log_callback(f"📍 Output directory changed detected:")
                log_callback(f"   Old: {stored_output_path}")
                log_callback(f"   New: {current_output_path}")
                log_callback(f"   Reason: Likely drive switch for more space")
            
            # Migrate existing frames
            migrated = self._migrate_existing_frames(
                stored_output_path,
                current_output_path,
                log_callback
            )
            
            self.stats['migrated_frames'] = migrated
            
            if migrated > 0:
                if log_callback:
                    log_callback(f"✅ Frame migration complete - all frames now in {current_output_path}")
                return True
            elif stored_output_path.exists() and any(stored_output_path.glob("frame_*.png")):
                # Frames exist but couldn't migrate
                if log_callback:
                    log_callback(f"❌ Frame migration failed - frames remain in {stored_output_path}")
                return False
            else:
                # No frames to migrate (clean resume)
                return True
        
        return True
    
    def _check_disk_space(self, log_callback: Optional[Callable] = None, offer_alternatives: bool = False) -> tuple[bool, Optional[str]]:
        """
        Check if sufficient disk space is available.
        
        Args:
            log_callback: Optional callback for logging
            offer_alternatives: If True, search for alternative drives with enough space
        
        Returns:
            Tuple of (has_space, alternative_path)
            - (True, None) if current path has space
            - (False, None) if no space and no alternatives
            - (False, alt_path) if no space but alternative found
        """
        try:
            from core.disk_space_manager import get_temp_directory_with_space
            
            # Estimate space needed for remaining frames (assume 20MB per enhanced frame)
            remaining_frames = len(self.frame_files) - self.resumable.checkpoint.current_frame
            estimated_size = remaining_frames * 20 * 1024 * 1024  # 20MB per frame
            
            is_available, message = check_space_available(
                estimated_size,
                str(self.output_frames_dir),
                min_free_gb=self.disk_space_buffer_gb
            )
            
            if not is_available:
                if log_callback:
                    log_callback(f"⚠️ {message}")
                
                # Search for alternative drives if requested
                if offer_alternatives:
                    if log_callback:
                        log_callback("🔍 Searching for alternative drives with sufficient space...")
                    
                    alt_path, alt_message = get_temp_directory_with_space(
                        estimated_size,
                        str(self.output_frames_dir)
                    )
                    
                    if alt_path:
                        if log_callback:
                            log_callback(f"✓ Found alternative: {alt_path}")
                            log_callback(alt_message)
                        return False, alt_path
                    else:
                        if log_callback:
                            log_callback("❌ No alternative drives with sufficient space found")
                
                return False, None
            
            return True, None
        
        except Exception as e:
            if log_callback:
                log_callback(f"⚠️ Disk space check failed: {e}")
            return True, None  # Continue if check fails
    
    def request_stop(self):
        """Request graceful stop."""
        self._should_stop = True
    
    def process_with_checkpoints(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        Process frames with automatic checkpoint saving.
        
        Automatically resumes from last checkpoint if job was interrupted.
        
        Args:
            progress_callback: Optional callback(current, total)
            log_callback: Optional callback(message)
        
        Returns:
            True if completed successfully, False if stopped/failed
        """
        # Initialize enhancer
        if log_callback:
            log_callback("[GFPGAN] Initializing face enhancer...")
        
        self._init_enhancer()
        
        # Check disk space before starting (with alternative drive search)
        has_space, alternative_path = self._check_disk_space(log_callback, offer_alternatives=True)
        
        if not has_space:
            if alternative_path:
                if log_callback:
                    log_callback(f"⚠️ Current path has insufficient space")
                    log_callback(f"💡 Alternative available: {alternative_path}")
                    log_callback(f"❌ Please manually configure GFPGAN temp directory to: {alternative_path}")
                    log_callback(f"   Settings → Performance & Cache → GFPGAN Temp Directory")
            else:
                if log_callback:
                    log_callback("❌ Insufficient disk space - processing aborted")
            return False
        
        # Resume message
        start_frame = self.resumable.checkpoint.current_frame
        if start_frame > 0:
            if log_callback:
                log_callback(f"▶️ Resuming from frame {start_frame}/{len(self.frame_files)}")
                log_callback(f"   Progress: {self.resumable.checkpoint.progress_percent():.1f}%")
        else:
            if log_callback:
                log_callback(f"[GFPGAN] Processing {len(self.frame_files)} frames...")
        
        # Process frames with checkpoints
        try:
            for frame_idx in self.resumable.get_frame_range():
                # Check stop request
                if self._should_stop:
                    if log_callback:
                        log_callback("⏹️ Processing stopped by user")
                    self.resumable.checkpoint.status = "paused"
                    self.resumable.save_checkpoint()
                    return False
                
                # Get frame file
                frame_file = self.frame_files[frame_idx]
                output_filename = frame_file.stem + '.png'  # Force PNG output
                output_path = self.output_frames_dir / output_filename
                
                # Skip if already processed (resume optimization)
                if output_path.exists():
                    self.stats['skipped_existing'] += 1
                    self.resumable.mark_frame_complete(frame_idx)
                    continue
                
                # Read frame
                frame = cv2.imread(str(frame_file))
                
                if frame is None:
                    if log_callback:
                        log_callback(f"⚠️ Failed to read {frame_file}, skipping")
                    self.resumable.mark_frame_complete(frame_idx)
                    continue
                
                # Enhance frame
                enhanced = self.enhancer.enhance_frame(frame, weight=self.weight)
                
                # Save enhanced frame
                cv2.imwrite(str(output_path), enhanced)
                
                # Update progress
                self.stats['processed'] += 1
                self.resumable.mark_frame_complete(frame_idx)
                
                # Save checkpoint periodically
                if self.resumable.should_checkpoint():
                    self.resumable.save_checkpoint()
                    
                    # Disk space check every checkpoint interval (with alternative search)
                    has_space, alternative_path = self._check_disk_space(log_callback, offer_alternatives=True)
                    
                    if not has_space:
                        if alternative_path:
                            if log_callback:
                                log_callback("⚠️ Disk space running low on current drive")
                                log_callback(f"✓ Alternative drive found: {alternative_path}")
                                log_callback("")
                                log_callback("📋 TO RESUME WITH MORE SPACE:")
                                log_callback(f"   1. Settings → Performance & Cache → GFPGAN Temp Directory")
                                log_callback(f"   2. Set to: {alternative_path}")
                                log_callback(f"   3. Restart processing (will resume from frame {self.resumable.checkpoint.current_frame})")
                                log_callback("")
                        else:
                            if log_callback:
                                log_callback("❌ Insufficient disk space on all drives")
                        
                        if log_callback:
                            log_callback("⏸️ Processing paused - checkpoint saved")
                        
                        self.resumable.checkpoint.status = "paused"
                        self.resumable.save_checkpoint()
                        return False
                
                # Progress callback
                if progress_callback:
                    progress_callback(frame_idx + 1, len(self.frame_files))
                
                # Periodic status update
                if (frame_idx + 1) % 10 == 0:
                    elapsed = self.resumable.checkpoint.elapsed_time()
                    eta = self.resumable.checkpoint.estimated_remaining()
                    
                    if log_callback:
                        log_callback(
                            f"[GFPGAN] {frame_idx + 1}/{len(self.frame_files)} "
                            f"({self.resumable.checkpoint.progress_percent():.1f}%) "
                            f"ETA: {eta/60:.1f}min"
                        )
            
            # Mark complete
            self.resumable.mark_complete()
            self.resumable.save_checkpoint()
            
            if log_callback:
                total_time = self.resumable.checkpoint.elapsed_time()
                log_callback(f"✅ GFPGAN complete in {total_time/60:.1f} minutes")
                log_callback(f"   Processed: {self.stats['processed']}")
                log_callback(f"   Skipped (already done): {self.stats['skipped_existing']}")
            
            return True
        
        except Exception as e:
            if log_callback:
                log_callback(f"❌ GFPGAN error: {e}")
            
            self.resumable.checkpoint.status = "failed"
            self.resumable.checkpoint.error_message = str(e)
            self.resumable.save_checkpoint()
            
            return False
    
    def get_checkpoint_status(self) -> ProcessingCheckpoint:
        """Get current checkpoint status."""
        return self.resumable.checkpoint
    
    def clear_checkpoint(self):
        """Clear checkpoint file (start fresh)."""
        checkpoint_path = self.resumable._get_checkpoint_path()
        if checkpoint_path.exists():
            checkpoint_path.unlink()


# Example usage
if __name__ == "__main__":
    print("=== GFPGAN Checkpoint Processor Test ===\n")
    
    # Example job
    processor = GFPGANCheckpointProcessor(
        job_id="test_video_gfpgan",
        input_frames_dir=Path("./test_frames"),
        output_frames_dir=Path("./test_enhanced"),
        model_path="GFPGANv1.3.pth",
        checkpoint_interval=10
    )
    
    def progress(current, total):
        print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")
    
    def log(message):
        print(f"[LOG] {message}")
    
    # Process with checkpoints
    success = processor.process_with_checkpoints(
        progress_callback=progress,
        log_callback=log
    )
    
    if success:
        print("\n✅ Processing complete!")
    else:
        print("\n⚠️ Processing interrupted - resume by running again")
        print(f"Checkpoint: {processor.get_checkpoint_status().current_frame} frames completed")
