"""
Processing Thread - Wraps core.VideoProcessor for non-blocking GUI execution
"""

from PySide6.QtCore import QThread, Signal
from core import VideoProcessor
import traceback


class ProcessingThread(QThread):
    """Worker thread that wraps core.VideoProcessor for GUI integration."""

    # Signals emitted to update GUI
    progress_updated = Signal(float)  # Progress percentage (0-100)
    eta_updated = Signal(str)  # Estimated time remaining
    log_updated = Signal(str)  # Log messages
    finished_signal = Signal(bool, str)  # Success, message
    error_occurred = Signal(str)  # Error message

    def __init__(
        self, input_file, output_file, options, propainter_path=None, parent=None
    ):
        super().__init__(parent)
        self.input_file = input_file
        self.output_file = output_file
        self.options = options
        self.propainter_path = propainter_path
        print(f"[DEBUG] ProcessingThread received propainter_path: {propainter_path}")
        self.processor = None
        self._should_stop = False

    def run(self):
        """Execute video processing in background thread."""
        try:
            # Create processor instance with ProPainter path
            self.processor = VideoProcessor(propainter_path=self.propainter_path)

            # Log start
            self.log_updated.emit(f"Starting restoration of: {self.input_file}")
            self.log_updated.emit(f"Output: {self.output_file}")
            self.log_updated.emit("-" * 60)

            # Define callbacks
            def progress_callback(progress, eta_str, fps=0.0):
                """Called by core when progress updates."""
                if self._should_stop:
                    if self.processor:
                        self.processor.request_stop()
                    return
                self.progress_updated.emit(progress)
                self.eta_updated.emit(eta_str)
                
                # Update FPS in performance monitor (access via parent window)
                if hasattr(self.parent(), 'performance_monitor') and fps > 0:
                    self.parent().performance_monitor.set_fps(fps)

            def log_callback(message):
                """Called by core for log messages."""
                self.log_updated.emit(message)

            # Process video using modular core
            success, message = self.processor.process_video(
                input_file=self.input_file,
                output_file=self.output_file,
                options=self.options,
                progress_callback=progress_callback,
                log_callback=log_callback,
            )

            # Emit completion signal
            if self._should_stop:
                self.finished_signal.emit(False, "Processing cancelled by user")
            else:
                self.finished_signal.emit(success, message)

        except Exception as e:
            error_msg = f"Processing error: {str(e)}\n{traceback.format_exc()}"
            self.log_updated.emit(error_msg)
            self.error_occurred.emit(error_msg)
            self.finished_signal.emit(False, str(e))
        
        finally:
            # Always cleanup GPU memory after processing
            try:
                if self.processor:
                    self.processor._cleanup_gpu_memory()
            except Exception:
                pass  # Don't fail on cleanup errors

    def stop(self):
        """Request processing to stop gracefully."""
        self._should_stop = True
        self.log_updated.emit("\nStop requested, cancelling processing...")

        if self.processor:
            # Processor will check _should_stop via progress_callback return value
            pass

    def terminate_processes(self):
        """Force terminate (use with caution)."""
        self.stop()
        # Give it a moment to stop gracefully
        if not self.wait(2000):
            # Force terminate if not stopped
            self.terminate()
            self.wait()
