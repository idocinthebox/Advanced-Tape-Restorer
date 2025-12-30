"""
Main Window - Advanced Tape Restorer v4.1
Professional GUI with Theatre Mode integration
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QProgressBar,
    QTextEdit,
    QFrame,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QDialog,
    QLineEdit,
)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPalette, QColor
from pathlib import Path
import os
import shutil
import urllib.request
import tempfile

# Import modular components
from .processing_thread import ProcessingThread
from .settings_manager import SettingsManager, PresetManager
from .ai_model_dialog import AIModelDialog
from .performance_monitor import PerformanceMonitor
from .console_window import ConsoleWindow
from core import VideoAnalyzer
from core.ai_model_manager import model_exists, get_storage_dir

# Import capture functionality
from capture import CaptureDeviceManager, AnalogCaptureEngine, DVCaptureEngine

# Import performance optimization
from core.auto_mode_selector import AutoModeSelector, InferenceMode


class LivePreviewWindow(QDialog):
    """Live preview window for capture monitoring."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Live Preview - Capture")
        self.resize(720, 480)

        layout = QVBoxLayout()

        # Video display label
        self.video_label = QLabel("Preview will appear here when capture starts...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(
            "border: 2px solid gray; background-color: black; color: white;"
        )
        self.video_label.setMinimumSize(640, 480)
        layout.addWidget(self.video_label)

        # Status
        self.preview_status = QLabel("Status: Not Started")
        layout.addWidget(self.preview_status)

        self.setLayout(layout)

        # Preview process
        self.preview_process = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_preview)

    def start_preview(self, device_name: str, resolution: str, framerate: str):
        """Start live preview from capture device."""
        try:
            import subprocess
            import sys

            # Build FFmpeg command for live preview (low latency)
            cmd = [
                "ffplay",
                "-f",
                "dshow",
                "-video_size",
                resolution,
                "-framerate",
                framerate,
                "-i",
                device_name,
                "-vf",
                "scale=640:480",
                "-an",  # No audio for preview
                "-fflags",
                "nobuffer",
                "-flags",
                "low_delay",
                "-framedrop",
            ]

            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.preview_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=cflags,
            )

            self.preview_status.setText("Status: Live Preview Active")
            self.preview_status.setStyleSheet("color: lime;")

        except Exception as e:
            self.preview_status.setText(f"Status: Preview Error - {str(e)}")
            self.preview_status.setStyleSheet("color: red;")

    def stop_preview(self):
        """Stop live preview."""
        if self.preview_process:
            try:
                self.preview_process.terminate()
                self.preview_process.wait(timeout=2)
            except BaseException:
                try:
                    self.preview_process.kill()
                except BaseException:
                    pass
            self.preview_process = None

        self.preview_status.setText("Status: Preview Stopped")
        self.preview_status.setStyleSheet("color: gray;")
        self.video_label.setText("Preview stopped")

    def _update_preview(self):
        """Update preview frame (placeholder for future frame extraction)."""
        # Future: Extract frames from FFmpeg and display

    def closeEvent(self, event):
        """Handle window close."""
        self.stop_preview()
        event.accept()


class CaptureMonitorThread(QThread):
    """Thread to monitor capture progress, dropped frames, and disk space."""

    # Signals for thread-safe GUI updates
    dropped_frames_updated = Signal(int)
    disk_space_updated = Signal(int)  # GB

    def __init__(self, capture_engine, output_folder, output_file):
        super().__init__()
        self.capture_engine = capture_engine
        self.output_folder = output_folder
        self.output_file = output_file
        self.running = True
        self.dropped_frames = 0

    def run(self):
        """Monitor capture process."""
        import time
        import re

        while self.running:
            try:
                # Monitor FFmpeg stderr for dropped frames
                if (
                    hasattr(self.capture_engine, "process")
                    and self.capture_engine.process
                ):
                    # Check if process is still running
                    if self.capture_engine.process.poll() is not None:
                        break

                    # Try to read stderr (non-blocking)
                    if self.capture_engine.process.stderr:
                        try:
                            # Read available stderr
                            import select
                            import sys

                            if sys.platform != "win32":
                                ready, _, _ = select.select(
                                    [self.capture_engine.process.stderr], [], [], 0.1
                                )
                                if ready:
                                    line = self.capture_engine.process.stderr.readline()
                                    if line:
                                        # Parse for dropped frames
                                        # FFmpeg reports: "frame= 1234 fps= 29 drop= 5"
                                        match = re.search(r"drop=\s*(\d+)", line)
                                        if match:
                                            self.dropped_frames = int(match.group(1))
                                            self.dropped_frames_updated.emit(
                                                self.dropped_frames
                                            )
                        except Exception:
                            pass

                # Update disk space every 5 seconds
                try:
                    total, used, free = shutil.disk_usage(self.output_folder)
                    free_gb = free // (2**30)
                    self.disk_space_updated.emit(free_gb)
                except Exception:
                    pass

                time.sleep(1)  # Update every second

            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(1)

    def stop(self):
        """Stop monitoring thread."""
        self.running = False


# Default settings
DEFAULT_SETTINGS = {
    # Input
    "source_filter": "ffms2",
    "field_order": "Auto-Detect",
    # Deinterlacing (QTGMC)
    "deinterlace_preset": "Medium",
    "sharpness": 0.5,
    "faster_processing": False,
    # Denoise
    "bm3d_enabled": False,
    "bm3d_sigma": 2.0,
    "bm3d_use_gpu": False,
    # Advanced
    "temporal_denoise": "None",
    "chroma_denoise": "None",
    "deband_enabled": False,
    "deband_strength": "Medium",
    "stabilization": False,
    "stabilization_mode": "Auto (Detect Best Method)",
    "color_correction": "None",
    "ai_inpainting": False,
    "inpainting_mode": "Remove Artifacts",
    "remove_artifacts": False,
    "artifact_filter": "TComb",
    "fix_chroma_shift": False,
    # Output
    "aspect_ratio_mode": "Keep (Default)",
    "resize_algorithm": "Lanczos",
    "resize_mode": "Letterbox (Pad)",
    "resize_width": 640,
    "resize_height": 480,
    "use_ai_upscaling": False,
    "ai_upscaling_method": "ZNEDI3 (Fast, VapourSynth)",
    "ai_upscale_target": "2x Source Resolution",
    "ai_upscale_custom_width": 1920,
    "ai_upscale_custom_height": 1080,
    "ai_upscale_resize_algo": "Lanczos",
    "codec": "libx264 (H.264, CPU)",
    "audio": "Copy Audio",
    "audio_codec": "AAC",
    "audio_bitrate": "192k",
    "crf": 18,
    "ffmpeg_preset": "medium",
    # Misc
    "debug_logging": False,
    "live_preview_enabled": False,
    "auto_save_presets": True,
    "expert_mode": False,
    # AI model settings
    "ai_model_dir": "",
    "ai_model_min_free_mb": 200,
    "propainter_path": "",  # Path to ProPainter installation
    # UI
    "ui_font_size": 11,
    "ui_theme": "System Default",
    "tooltips_enabled": True,
}


class MainWindow(QMainWindow):
    """Main application window for Advanced Tape Restorer v4.1"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Advanced Tape Restorer v4.1 - Professional Video Restoration with Theatre Mode"
        )

        # Set larger initial size
        self.resize(1400, 900)

        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        window_geo = self.frameGeometry()
        center_point = screen.center()
        window_geo.moveCenter(center_point)
        self.move(window_geo.topLeft())

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.preset_manager = PresetManager()
        
        # Initialize auto mode selector for AI inference
        self.auto_mode_selector = AutoModeSelector()
        
        # Initialize capture device manager
        self.capture_device_manager = CaptureDeviceManager()
        self.capture_devices = []
        self.audio_devices = []

        # Load settings or use defaults
        settings = self.settings_manager.load_settings()
        for key, default_value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = default_value
        self.settings_manager.save_settings(settings)

        # State
        self.input_file = ""
        self.output_file = ""
        self.processing_thread = None
        self.batch_jobs = []
        self.batch_processing = False
        self.current_batch_index = 0
        self.capture_output_folder = ""
        self.capture_thread = None
        self.capture_monitor_thread = None
        self.live_preview_window = None
        self.capture_devices_loaded = False  # Track if devices have been loaded
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.metrics_updated.connect(self._update_performance_labels)
        self.performance_monitor.start_monitoring(processing=False)
        
        # Console window (floating)
        self.console_window = None

        # Build UI
        self._build_ui()
        # Apply UI font size, theme, and tooltips from settings
        try:
            self.apply_ui_font_size()
            self.apply_ui_theme()
            self.apply_tooltips()
        except Exception:
            pass
        self._setup_menu_bar()

        self.console_log("Advanced Tape Restorer v4.1 - Ready")
        self.console_log("Using modular architecture with core and capture modules")
        self.console_log("-" * 60)

        # Load capture output folder from settings
        self.capture_output_folder = settings.get("capture_output_folder", "")
        if self.capture_output_folder:
            self.capture_output_label.setText(self.capture_output_folder)

        # Initialize capture devices after UI is complete
        # Temporarily disabled to prevent startup hang - will auto-refresh on first use
        # self.refresh_capture_devices()

        # Update Output tab resize state based on AI upscaling
        try:
            self._update_output_resize_state()
        except Exception as e:
            self.console_log(f"Failed to update output resize state: {e}")

        # Ensure AI models are present on first-run or when needed
        try:
            self.check_ai_models_on_startup()
        except Exception as e:
            self.console_log(f"AI model check failed: {e}")
        # Ensure AI models are present on first-run or when needed
        try:
            self.check_ai_models_on_startup()
        except Exception as e:
            self.console_log(f"AI model check failed: {e}")
        
        # Check for incomplete checkpoints on startup (after UI is ready)
        QTimer.singleShot(1000, self._check_for_incomplete_checkpoints)
        
        # Initialize output mode state (show/hide codec options)
        try:
            self._on_output_mode_changed(self.output_mode_combo.currentText())
        except Exception as e:
            self.console_log(f"Failed to initialize output mode state: {e}")

    def _build_ui(self):
        """Build the main user interface."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # File selection section (fixed)
        file_section = self._build_file_section()
        main_layout.addWidget(file_section, 0)

        # Tab widget for settings (expandable)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_capture_tab(), "Capture")
        self.tabs.addTab(self._build_input_tab(), "Input")
        self.tabs.addTab(self._build_restoration_tab(), "Restoration")
        self.tabs.addTab(self._build_advanced_tab(), "Advanced")
        self.tabs.addTab(self._build_ai_tools_tab(), "AI Tools")
        self.tabs.addTab(self._build_output_tab(), "Output")
        
        # Connect tab change event to auto-refresh capture devices
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        from PySide6.QtWidgets import QSizePolicy

        self.tabs.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.tabs, 1)

        # Control buttons (fixed)
        control_section = self._build_control_section()
        main_layout.addWidget(control_section, 0)

        # Bottom status row (AI model dir + console toggle)
        bottom_status = self._build_bottom_status()
        main_layout.addWidget(bottom_status, 0)
        
        # Create status bar for performance monitoring
        self._build_status_bar()

    def _build_file_section(self) -> QFrame:
        """Build input/output file selection section."""
        frame = QFrame()
        layout = QVBoxLayout()

        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input File:"))
        self.input_line_edit = QLineEdit()
        self.input_line_edit.setPlaceholderText("Type or paste file path, or click Browse...")
        self.input_line_edit.setToolTip(
            "Enter input video file path manually or click Browse to select\n"
            "Supports: AVI, MP4, MKV, MTS, M2TS, TS, MOV, etc."
        )
        self.input_line_edit.textChanged.connect(self._on_input_path_changed)
        input_layout.addWidget(self.input_line_edit, 1)
        browse_input_btn = QPushButton("Browse...")
        browse_input_btn.clicked.connect(self.select_input)
        browse_input_btn.setToolTip(
            "Select video file to restore (AVI, MP4, MKV, etc.)"
        )
        input_layout.addWidget(browse_input_btn)
        layout.addLayout(input_layout)

        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.output_line_edit = QLineEdit()
        self.output_line_edit.setPlaceholderText("Type or paste output path, or click Browse...")
        self.output_line_edit.setToolTip(
            "Enter output video file path manually or click Browse to select\n"
            "Supports: MP4, MKV, MOV, AVI, etc."
        )
        self.output_line_edit.textChanged.connect(self._on_output_path_changed)
        output_layout.addWidget(self.output_line_edit, 1)
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.clicked.connect(self.select_output)
        browse_output_btn.setToolTip("Choose output file location and name")
        output_layout.addWidget(browse_output_btn)
        layout.addLayout(output_layout)

        frame.setLayout(layout)
        return frame

    def _build_capture_tab(self) -> QWidget:
        """Build NEW capture tab for analog/DV capture."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Capture device selection
        device_group = QGroupBox("Capture Device")
        device_layout = QGridLayout()

        device_layout.addWidget(QLabel("Device Type:"), 0, 0)
        self.capture_device_type = QComboBox()
        self.capture_device_type.addItems(["Analog (VHS/Hi8)", "DV/miniDV (FireWire)"])
        self.capture_device_type.setToolTip(
            "Analog: VHS/Hi8/Betamax via capture card | DV: FireWire camcorders"
        )
        device_layout.addWidget(self.capture_device_type, 0, 1)

        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_capture_devices)
        refresh_btn.setToolTip("Scan for connected capture devices")
        device_layout.addWidget(refresh_btn, 0, 2)

        device_layout.addWidget(QLabel("Video Device:"), 1, 0)
        self.video_device_combo = QComboBox()
        self.video_device_combo.setToolTip("Select video capture device or camera")
        device_layout.addWidget(self.video_device_combo, 1, 1, 1, 2)

        device_layout.addWidget(QLabel("Audio Device:"), 2, 0)
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.setToolTip("Select audio capture device or line-in")
        device_layout.addWidget(self.audio_device_combo, 2, 1, 1, 2)

        device_layout.addWidget(QLabel("Video Input:"), 3, 0)
        self.video_input_combo = QComboBox()
        self.video_input_combo.addItems(
            [
                "Auto (Default)",
                "Composite (RCA)",
                "S-Video (Y/C)",
                "Component (YPbPr)",
                "HDMI/Digital",
            ]
        )
        self.video_input_combo.setCurrentIndex(0)  # Auto by default
        self.video_input_combo.setToolTip(
            "Select video input source on capture card:\n\n"
            "• Auto: Use device default (no crossbar override)\n"
            "• Composite: RCA yellow connector (standard VHS)\n"
            "• S-Video: Y/C connector (better quality, S-VHS)\n"
            "• Component: YPbPr connectors (highest quality analog)\n"
            "• HDMI/Digital: Digital input (if supported)\n\n"
            "Note: Not all capture cards support input switching.\n"
            "If capture fails, try 'Auto' setting."
        )
        device_layout.addWidget(self.video_input_combo, 3, 1, 1, 2)

        device_layout.addWidget(QLabel("Audio Input:"), 4, 0)
        self.audio_input_combo = QComboBox()
        self.audio_input_combo.addItems(
            ["Auto (Default)", "Line In", "Microphone", "CD Audio", "Video Audio"]
        )
        self.audio_input_combo.setCurrentIndex(0)  # Auto by default
        self.audio_input_combo.setToolTip(
            "Select audio input source on capture card:\n\n"
            "• Auto: Use device default (recommended)\n"
            "• Line In: External audio input (RCA red/white)\n"
            "• Microphone: Mic input (rarely used for tape capture)\n"
            "• CD Audio: CD audio (legacy)\n"
            "• Video Audio: Audio from video input (usually auto-selected)\n\n"
            "Most cards auto-select audio matching video input.\n"
            "Use 'Auto' unless you need separate audio source."
        )
        device_layout.addWidget(self.audio_input_combo, 4, 1, 1, 2)

        device_group.setLayout(device_layout)
        layout.addWidget(device_group)

        # Capture Presets
        preset_group = QGroupBox("Capture Presets")
        preset_layout = QHBoxLayout()

        preset_layout.addWidget(QLabel("Preset:"))
        self.capture_preset_combo = QComboBox()
        self.capture_preset_combo.addItems(
            [
                "Custom",
                "VHS NTSC (Composite)",
                "VHS PAL (Composite)",
                "S-VHS NTSC (S-Video)",
                "S-VHS PAL (S-Video)",
                "DV NTSC (FireWire)",
                "DV PAL (FireWire)",
                "Component NTSC (YPbPr)",
                "Component PAL (YPbPr)",
            ]
        )
        self.capture_preset_combo.currentTextChanged.connect(self._apply_capture_preset)
        self.capture_preset_combo.setToolTip(
            "Quick-load common capture configurations:\n\n"
            "• Custom: Manual configuration\n"
            "• VHS NTSC/PAL: Standard VHS via composite\n"
            "• S-VHS: Higher quality via S-Video\n"
            "• DV: Digital tape via FireWire\n"
            "• Component: Highest quality analog\n\n"
            "Selecting a preset auto-configures all settings below."
        )
        preset_layout.addWidget(self.capture_preset_combo, 1)

        self.save_preset_btn = QPushButton("Save as Preset")
        self.save_preset_btn.clicked.connect(self._save_custom_capture_preset)
        self.save_preset_btn.setToolTip("Save current settings as custom preset")
        preset_layout.addWidget(self.save_preset_btn)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Capture settings
        settings_group = QGroupBox("Capture Settings")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("Codec:"), 0, 0)
        self.capture_codec = QComboBox()
        self.capture_codec.addItems(
            ["HuffYUV (Lossless)", "FFV1 (Lossless)", "Lagarith"]
        )
        self.capture_codec.setToolTip(
            "Lossless codec for capture (HuffYUV: fast, FFV1: best compression)"
        )
        settings_layout.addWidget(self.capture_codec, 0, 1)

        settings_layout.addWidget(QLabel("Resolution:"), 0, 2)
        self.capture_resolution = QComboBox()
        self.capture_resolution.addItems(
            ["720x480 (NTSC)", "720x576 (PAL)", "640x480", "Custom"]
        )
        self.capture_resolution.setToolTip(
            "Capture resolution (use native tape resolution for best quality)"
        )
        settings_layout.addWidget(self.capture_resolution, 0, 3)

        settings_layout.addWidget(QLabel("Frame Rate:"), 1, 0)
        self.capture_framerate = QComboBox()
        self.capture_framerate.addItems(
            ["29.97 fps (NTSC)", "25 fps (PAL)", "23.976 fps", "30 fps"]
        )
        self.capture_framerate.setToolTip(
            "NTSC: 29.97 fps (USA/Japan) | PAL: 25 fps (Europe/Australia)"
        )
        settings_layout.addWidget(self.capture_framerate, 1, 1)

        settings_layout.addWidget(QLabel("Output Folder:"), 2, 0)
        self.capture_output_label = QLabel("Not set")
        self.capture_output_label.setStyleSheet("border: 1px solid gray; padding: 3px;")
        settings_layout.addWidget(self.capture_output_label, 2, 1, 1, 2)
        browse_capture_btn = QPushButton("Browse...")
        browse_capture_btn.clicked.connect(self.select_capture_output)
        browse_capture_btn.setToolTip("Select folder to save captured video files")
        settings_layout.addWidget(browse_capture_btn, 2, 3)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Capture controls
        controls_layout = QHBoxLayout()
        self.start_capture_btn = QPushButton("Start Capture")
        self.start_capture_btn.clicked.connect(self.start_capture)
        self.start_capture_btn.setStyleSheet(
            "background-color: green; color: white; font-weight: bold;"
        )
        controls_layout.addWidget(self.start_capture_btn)

        self.stop_capture_btn = QPushButton("Stop Capture")
        self.stop_capture_btn.clicked.connect(self.stop_capture)
        self.stop_capture_btn.setEnabled(False)
        self.stop_capture_btn.setStyleSheet(
            "background-color: red; color: white; font-weight: bold;"
        )
        controls_layout.addWidget(self.stop_capture_btn)

        layout.addLayout(controls_layout)

        # Advanced options
        advanced_layout = QHBoxLayout()

        self.auto_process_capture = QCheckBox("Auto-restore after capture")
        self.auto_process_capture.setToolTip(
            "Automatically process captured video with restoration filters"
        )
        advanced_layout.addWidget(self.auto_process_capture)

        self.live_preview_check = QCheckBox("Enable Live Preview")
        self.live_preview_check.setChecked(False)
        self.live_preview_check.setToolTip(
            "Show live video preview during capture\n\n"
            "WARNING: May reduce capture performance on slower systems.\n"
            "Disable if experiencing dropped frames."
        )
        advanced_layout.addWidget(self.live_preview_check)

        advanced_layout.addStretch()
        layout.addLayout(advanced_layout)

        # Disk space and status
        status_layout = QHBoxLayout()

        self.disk_space_label = QLabel("Disk Space: N/A")
        self.disk_space_label.setStyleSheet(
            "border: 1px solid gray; padding: 5px; background-color: #2a2a2a;"
        )
        status_layout.addWidget(self.disk_space_label)

        self.capture_status_label = QLabel("Status: Ready")
        self.capture_status_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        status_layout.addWidget(self.capture_status_label, 1)

        layout.addLayout(status_layout)

        # Dropped frame counter
        self.dropped_frames_label = QLabel("Dropped Frames: 0")
        self.dropped_frames_label.setStyleSheet(
            "border: 1px solid gray; padding: 5px; background-color: #1a3d1a;"
        )
        layout.addWidget(self.dropped_frames_label)

        layout.addStretch()
        widget.setLayout(layout)

        # Device list will be initialized after UI complete

        return widget

    def _build_input_tab(self) -> QWidget:
        """Build input settings tab."""
        widget = QWidget()
        layout = QGridLayout()
        row = 0

        # Source filter
        layout.addWidget(QLabel("Source Filter:"), row, 0)
        self.source_filter_combo = QComboBox()
        self.source_filter_combo.addItems(
            [
                "Auto (Best for Source)",
                "BestSource (Best - Most Reliable)",
                "FFMS2 (Fast Indexing)",
                "LSMASH (Alternative)"
            ]
        )
        # Map old settings to new format
        old_filter = self.settings_manager.get("source_filter", "Auto")
        if old_filter == "ffms2":
            self.source_filter_combo.setCurrentText("FFMS2 (Fast Indexing)")
        elif old_filter == "lsmas":
            self.source_filter_combo.setCurrentText("LSMASH (Alternative)")
        elif old_filter == "bestsource":
            self.source_filter_combo.setCurrentText("BestSource (Best - Most Reliable)")
        else:
            self.source_filter_combo.setCurrentText("Auto (Best for Source)")
        self.source_filter_combo.setToolTip(
            "VapourSynth source filter (video decoder):\n\n"
            "Auto: BestSource for tapes → FFMS2 for digital (recommended)\n\n"
            "BestSource: Most accurate FPS/audio sync, best for tape sources\n"
            "  • Correctly handles interlaced/telecine flags\n"
            "  • Superior audio sync reliability\n"
            "  • Slower initial indexing (one-time cost)\n\n"
            "FFMS2: Fast indexing, good compatibility\n"
            "  • Faster first load\n"
            "  • May have audio sync issues on some sources\n\n"
            "LSMASH: Alternative for seeking-heavy workflows"
        )
        layout.addWidget(self.source_filter_combo, row, 1)
        row += 1

        # Field order
        layout.addWidget(QLabel("Field Order:"), row, 0)
        self.field_order_combo = QComboBox()
        self.field_order_combo.addItems(
            [
                "Auto-Detect",
                "Top Field First (TFF)",
                "Bottom Field First (BFF)",
                "Progressive",
            ]
        )
        self.field_order_combo.setCurrentText(
            self.settings_manager.get("field_order", "Auto-Detect")
        )
        self.field_order_combo.setToolTip(
            "Field order for deinterlacing:\n"
            "Auto-Detect: Analyze with FFmpeg idet (recommended)\n"
            "TFF: Top field first (most NTSC)\n"
            "BFF: Bottom field first (some PAL)\n"
            "Progressive: No deinterlacing needed"
        )
        layout.addWidget(self.field_order_combo, row, 1)

        detect_btn = QPushButton("Detect Now")
        detect_btn.clicked.connect(self.detect_field_order)
        detect_btn.setToolTip("Run field order detection on current input file")
        layout.addWidget(detect_btn, row, 2)
        row += 1

        layout.addItem(
            QSpacerItem(
                0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            row,
            0,
        )
        widget.setLayout(layout)
        return widget

    def _build_restoration_tab(self) -> QWidget:
        """Build main restoration filters tab."""
        widget = QWidget()
        layout = QGridLayout()
        row = 0

        # Theatre Mode - Hardware-Accurate Analog Processing
        theatre_group = QGroupBox("Theatre Mode - Hardware-Accurate Analog Processing (NEW)")
        theatre_layout = QGridLayout()
        
        self.theatre_mode_check = QCheckBox("Enable Theatre Mode")
        self.theatre_mode_check.setChecked(self.settings_manager.get("theatre_mode_enabled", False))
        self.theatre_mode_check.setToolTip(
            "Theatre Mode: Hardware-accurate analog processing\n"
            "Replicates professional broadcast chipset algorithms\n"
            "Best for: VHS, LaserDisc, Hi8, Betamax tapes"
        )
        self.theatre_mode_check.stateChanged.connect(self._on_theatre_mode_toggled)
        theatre_layout.addWidget(self.theatre_mode_check, 0, 0, 1, 4)
        
        # Chroma Correction subsection
        theatre_layout.addWidget(QLabel("Chroma Correction:"), 1, 0)
        
        self.chroma_correction_check = QCheckBox("Enable")
        self.chroma_correction_check.setChecked(self.settings_manager.get("chroma_correction_enabled", False))
        self.chroma_correction_check.setToolTip(
            "Fix chroma phase misalignment in analog captures\n"
            "Corrects red/blue fringing and color shifts"
        )
        theatre_layout.addWidget(self.chroma_correction_check, 1, 1)
        
        theatre_layout.addWidget(QLabel("Preset:"), 1, 2)
        self.chroma_preset_combo = QComboBox()
        self.chroma_preset_combo.addItems([
            "LaserDisc (0.25px)",
            "VHS Composite (0.5px)",
            "S-VHS (0.15px)",
            "Video8 (0.25px)",
            "Hi8 (0.2px)",
            "Betamax (0.3px)",
            "Custom"
        ])
        # Map saved preset to display name
        preset_map = {
            "laserdisc": "LaserDisc (0.25px)",
            "vhs_composite": "VHS Composite (0.5px)",
            "svhs": "S-VHS (0.15px)",
            "video8": "Video8 (0.25px)",
            "hi8": "Hi8 (0.2px)",
            "betamax": "Betamax (0.3px)",
            "custom": "Custom"
        }
        saved_preset = self.settings_manager.get("chroma_preset", "laserdisc")
        self.chroma_preset_combo.setCurrentText(preset_map.get(saved_preset, "LaserDisc (0.25px)"))
        self.chroma_preset_combo.setToolTip(
            "Hardware-accurate chroma shift presets:\n"
            "LaserDisc: Professional analog disc (0.25px)\n"
            "VHS Composite: Consumer VHS (0.5px)\n"
            "S-VHS: High-quality VHS (0.15px)\n"
            "Hi8: 8mm high-band (0.2px)\n"
            "Betamax: Beta format (0.3px)"
        )
        self.chroma_preset_combo.currentTextChanged.connect(self._on_chroma_preset_changed)
        theatre_layout.addWidget(self.chroma_preset_combo, 1, 3)
        
        # Custom chroma shift controls
        theatre_layout.addWidget(QLabel("X Shift (px):"), 2, 0)
        self.chroma_shift_x_spin = QDoubleSpinBox()
        self.chroma_shift_x_spin.setRange(-2.0, 2.0)
        self.chroma_shift_x_spin.setSingleStep(0.05)
        self.chroma_shift_x_spin.setDecimals(2)
        self.chroma_shift_x_spin.setValue(float(self.settings_manager.get("chroma_shift_x_px", 0.25)))
        self.chroma_shift_x_spin.setToolTip("Horizontal chroma shift in pixels (-2.0 to +2.0)")
        theatre_layout.addWidget(self.chroma_shift_x_spin, 2, 1)
        
        theatre_layout.addWidget(QLabel("Y Shift (px):"), 2, 2)
        self.chroma_shift_y_spin = QDoubleSpinBox()
        self.chroma_shift_y_spin.setRange(-2.0, 2.0)
        self.chroma_shift_y_spin.setSingleStep(0.05)
        self.chroma_shift_y_spin.setDecimals(2)
        self.chroma_shift_y_spin.setValue(float(self.settings_manager.get("chroma_shift_y_px", 0.0)))
        self.chroma_shift_y_spin.setToolTip("Vertical chroma shift in pixels (-2.0 to +2.0)")
        theatre_layout.addWidget(self.chroma_shift_y_spin, 2, 3)
        
        # Deinterlace Variant
        theatre_layout.addWidget(QLabel("Deinterlace Variant:"), 3, 0)
        self.deinterlace_variant_combo = QComboBox()
        self.deinterlace_variant_combo.addItems([
            "Standard (Progressive)",
            "Bob (Double-Rate)",
            "Keep Interlaced"
        ])
        # Map saved variant to display name
        variant_map = {
            "standard": "Standard (Progressive)",
            "bob": "Bob (Double-Rate)",
            "keep_interlaced": "Keep Interlaced"
        }
        saved_variant = self.settings_manager.get("deinterlace_variant", "standard")
        self.deinterlace_variant_combo.setCurrentText(variant_map.get(saved_variant, "Standard (Progressive)"))
        self.deinterlace_variant_combo.setToolTip(
            "Deinterlacing mode for Theatre Mode:\n"
            "Standard: 60i → 30p progressive (default)\n"
            "Bob: 60i → 60p double-rate (preserves motion)\n"
            "Keep Interlaced: No deinterlacing (archival)"
        )
        theatre_layout.addWidget(self.deinterlace_variant_combo, 3, 1, 1, 3)
        
        # Auto-Profiling button
        self.analyze_tape_btn = QPushButton("Analyze Tape (Auto-Profile)")
        self.analyze_tape_btn.setToolTip(
            "Automatically detect optimal settings for this tape:\n"
            "• Field order detection\n"
            "• Black/white point analysis\n"
            "• Chroma shift estimation\n"
            "• Saturation level detection"
        )
        self.analyze_tape_btn.clicked.connect(self._on_analyze_tape)
        theatre_layout.addWidget(self.analyze_tape_btn, 4, 0, 1, 2)
        
        # Level Adjustment subsection
        self.level_adjustment_check = QCheckBox("Apply Level Adjustment")
        self.level_adjustment_check.setChecked(self.settings_manager.get("apply_level_adjustment", False))
        self.level_adjustment_check.setToolTip(
            "Adjust black/white points and saturation\n"
            "Useful for faded tapes or crushed blacks"
        )
        theatre_layout.addWidget(self.level_adjustment_check, 4, 2, 1, 2)
        
        theatre_layout.addWidget(QLabel("Black Point:"), 5, 0)
        self.black_point_spin = QDoubleSpinBox()
        self.black_point_spin.setRange(0.0, 0.5)
        self.black_point_spin.setSingleStep(0.01)
        self.black_point_spin.setDecimals(2)
        self.black_point_spin.setValue(float(self.settings_manager.get("black_point", 0.0)))
        self.black_point_spin.setToolTip("Black level (0.0 = no change, 0.1 = lift shadows)")
        theatre_layout.addWidget(self.black_point_spin, 5, 1)
        
        theatre_layout.addWidget(QLabel("White Point:"), 5, 2)
        self.white_point_spin = QDoubleSpinBox()
        self.white_point_spin.setRange(0.5, 1.0)
        self.white_point_spin.setSingleStep(0.01)
        self.white_point_spin.setDecimals(2)
        self.white_point_spin.setValue(float(self.settings_manager.get("white_point", 1.0)))
        self.white_point_spin.setToolTip("White level (1.0 = no change, 0.85 = compress highlights)")
        theatre_layout.addWidget(self.white_point_spin, 5, 3)
        
        theatre_layout.addWidget(QLabel("Saturation Boost:"), 6, 0)
        self.saturation_boost_spin = QDoubleSpinBox()
        self.saturation_boost_spin.setRange(0.5, 2.0)
        self.saturation_boost_spin.setSingleStep(0.1)
        self.saturation_boost_spin.setDecimals(1)
        self.saturation_boost_spin.setValue(float(self.settings_manager.get("saturation_boost", 1.0)))
        self.saturation_boost_spin.setToolTip("Saturation multiplier (1.0 = no change, 1.2 = boost faded colors)")
        theatre_layout.addWidget(self.saturation_boost_spin, 6, 1, 1, 3)
        
        theatre_group.setLayout(theatre_layout)
        layout.addWidget(theatre_group, row, 0, 1, 4)
        row += 1
        
        # Enable/disable Theatre Mode controls initially
        self._on_theatre_mode_toggled(self.theatre_mode_check.checkState())

        # QTGMC deinterlacing (core restoration filter)
        deinterlace_group = QGroupBox("QTGMC Deinterlacing (Primary Restoration)")
        deinterlace_layout = QGridLayout()

        deinterlace_layout.addWidget(QLabel("Preset:"), 0, 0)
        self.qtgmc_preset = QComboBox()
        self.qtgmc_preset.addItems(
            [
                "Draft",
                "Ultra Fast",
                "Super Fast",
                "Very Fast",
                "Faster",
                "Fast",
                "Medium",
                "Slow",
                "Slower",
                "Very Slow",
                "Placebo",
            ]
        )
        self.qtgmc_preset.setCurrentText(
            self.settings_manager.get("deinterlace_preset", "Medium")
        )
        self.qtgmc_preset.setToolTip(
            "QTGMC quality preset:\n"
            "Draft-Fast: Quick preview\n"
            "Medium: Balanced (recommended)\n"
            "Slow-Placebo: Maximum quality, very slow"
        )
        deinterlace_layout.addWidget(self.qtgmc_preset, 0, 1)

        deinterlace_layout.addWidget(QLabel("Sharpness:"), 0, 2)
        self.sharpness_spin = QDoubleSpinBox()
        self.sharpness_spin.setRange(0.0, 1.0)
        self.sharpness_spin.setSingleStep(0.1)
        self.sharpness_spin.setDecimals(1)
        self.sharpness_spin.setValue(float(self.settings_manager.get("sharpness", 0.5)))
        self.sharpness_spin.setToolTip(
            "Sharpness enhancement (0.0 = soft, 1.0 = sharp)"
        )
        deinterlace_layout.addWidget(self.sharpness_spin, 0, 3)

        self.faster_processing_check = QCheckBox("Faster Processing (Lower Quality)")
        self.faster_processing_check.setChecked(
            self.settings_manager.get("faster_processing", False)
        )
        self.faster_processing_check.setToolTip(
            "Enable FasterTaps for quicker processing"
        )
        deinterlace_layout.addWidget(self.faster_processing_check, 1, 0, 1, 2)

        deinterlace_group.setLayout(deinterlace_layout)
        layout.addWidget(deinterlace_group, row, 0, 1, 4)
        row += 1

        # BM3D Denoise
        denoise_group = QGroupBox("BM3D Denoise (Optional)")
        denoise_layout = QGridLayout()

        self.bm3d_check = QCheckBox("Enable BM3D Denoise")
        self.bm3d_check.setChecked(self.settings_manager.get("bm3d_enabled", False))
        self.bm3d_check.setToolTip("Advanced denoising for noisy VHS/analog footage")
        denoise_layout.addWidget(self.bm3d_check, 0, 0)

        denoise_layout.addWidget(QLabel("Strength:"), 0, 1)

        # Beginner mode: preset dropdown
        self.bm3d_strength = QComboBox()
        self.bm3d_strength.addItems(
            ["None", "Light (Fast)", "Medium (Slow)", "Strong (Very Slow)"]
        )
        current_sigma = float(self.settings_manager.get("bm3d_sigma", 2.0))
        # Map sigma to preset names
        if current_sigma <= 1.5:
            self.bm3d_strength.setCurrentText("None")
        elif current_sigma <= 3.5:
            self.bm3d_strength.setCurrentText("Light (Fast)")
        elif current_sigma <= 6.5:
            self.bm3d_strength.setCurrentText("Medium (Slow)")
        else:
            self.bm3d_strength.setCurrentText("Strong (Very Slow)")
        self.bm3d_strength.setToolTip(
            "Denoise strength:\n"
            "Light (Fast): Quick preview (sigma ~3)\n"
            "Medium (Slow): Balanced (sigma ~5)\n"
            "Strong (Very Slow): Heavy noise (sigma ~8)"
        )
        denoise_layout.addWidget(self.bm3d_strength, 0, 2)

        # Expert mode: numeric spinbox
        self.bm3d_sigma = QDoubleSpinBox()
        self.bm3d_sigma.setRange(0.0, 10.0)
        self.bm3d_sigma.setSingleStep(0.5)
        self.bm3d_sigma.setDecimals(1)
        self.bm3d_sigma.setValue(current_sigma)
        self.bm3d_sigma.setToolTip("Denoise sigma (0.0-10.0, higher = stronger)")
        denoise_layout.addWidget(self.bm3d_sigma, 0, 2)
        self.bm3d_sigma.hide()  # Hidden by default

        self.bm3d_gpu_check = QCheckBox("Use GPU (CUDA)")
        self.bm3d_gpu_check.setChecked(self.settings_manager.get("bm3d_use_gpu", False))
        self.bm3d_gpu_check.setToolTip(
            "Enable GPU acceleration (requires CUDA-capable GPU)"
        )
        denoise_layout.addWidget(self.bm3d_gpu_check, 0, 3)

        denoise_group.setLayout(denoise_layout)
        layout.addWidget(denoise_group, row, 0, 1, 4)
        row += 1

        # VHS artifact removal
        self.artifact_removal_check = QCheckBox(
            "Remove VHS Artifacts (Dot Crawl/Rainbow)"
        )
        self.artifact_removal_check.setChecked(
            self.settings_manager.get("remove_artifacts", False)
        )
        self.artifact_removal_check.setToolTip(
            "Remove composite video artifacts (dot crawl, rainbow)"
        )
        layout.addWidget(self.artifact_removal_check, row, 0, 1, 2)

        layout.addWidget(QLabel("Filter:"), row, 2)
        self.artifact_filter_combo = QComboBox()
        self.artifact_filter_combo.addItems(["TComb", "Bifrost"])
        self.artifact_filter_combo.setCurrentText(
            self.settings_manager.get("artifact_filter", "TComb")
        )
        self.artifact_filter_combo.setToolTip("TComb: Classic | Bifrost: Modern")
        layout.addWidget(self.artifact_filter_combo, row, 3)
        row += 1

        self.chroma_shift_check = QCheckBox("Fix VHS Chroma Shift (Slow)")
        self.chroma_shift_check.setChecked(
            self.settings_manager.get("fix_chroma_shift", False)
        )
        self.chroma_shift_check.setToolTip(
            "Corrects color misalignment (red/blue fringing)"
        )
        layout.addWidget(self.chroma_shift_check, row, 0, 1, 4)
        row += 1

        layout.addItem(
            QSpacerItem(
                0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            row,
            0,
        )
        widget.setLayout(layout)
        return widget

    def _build_advanced_tab(self) -> QWidget:
        """Build advanced filters tab."""
        widget = QWidget()
        layout = QGridLayout()
        row = 0

        # Temporal denoise
        layout.addWidget(QLabel("Temporal Denoise:"), row, 0)
        self.temporal_denoise_combo = QComboBox()
        self.temporal_denoise_combo.addItems(["None", "Light", "Medium", "Strong"])
        self.temporal_denoise_combo.setCurrentText(
            self.settings_manager.get("temporal_denoise", "None")
        )
        self.temporal_denoise_combo.setToolTip(
            "Reduce temporal noise across frames (None = off, Strong = aggressive)"
        )
        layout.addWidget(self.temporal_denoise_combo, row, 1)

        # Expert mode numeric controls (hidden by default)
        self.temporal_denoise_label_expert = QLabel("Temporal Strength:")
        layout.addWidget(self.temporal_denoise_label_expert, row, 0)
        self.temporal_denoise_label_expert.hide()

        self.temporal_denoise_spin = QDoubleSpinBox()
        self.temporal_denoise_spin.setRange(0.0, 10.0)
        self.temporal_denoise_spin.setSingleStep(0.5)
        self.temporal_denoise_spin.setDecimals(1)
        self.temporal_denoise_spin.setValue(3.0)
        self.temporal_denoise_spin.setToolTip(
            "Temporal denoise strength (0=off, 10=max)"
        )
        layout.addWidget(self.temporal_denoise_spin, row, 1)
        self.temporal_denoise_spin.hide()

        # Chroma denoise
        layout.addWidget(QLabel("Chroma Denoise:"), row, 2)
        self.chroma_denoise_combo = QComboBox()
        self.chroma_denoise_combo.addItems(["None", "Light", "Medium", "Strong"])
        self.chroma_denoise_combo.setToolTip(
            "Reduce color noise/chroma artifacts (helps with VHS rainbow patterns)"
        )

        # Expert mode numeric controls
        self.deband_label_expert = QLabel("Deband Range:")
        layout.addWidget(self.deband_label_expert, row, 1)
        self.deband_label_expert.hide()

        self.deband_range_spin = QSpinBox()
        self.deband_range_spin.setRange(5, 30)
        self.deband_range_spin.setValue(15)
        self.deband_range_spin.setToolTip("Debanding range (5-30, higher = stronger)")
        layout.addWidget(self.deband_range_spin, row, 2)
        self.deband_range_spin.hide()

        self.chroma_denoise_combo.setCurrentText(
            self.settings_manager.get("chroma_denoise", "None")
        )
        layout.addWidget(self.chroma_denoise_combo, row, 3)

        # Expert mode numeric controls
        self.chroma_denoise_label_expert = QLabel("Chroma Strength:")
        layout.addWidget(self.chroma_denoise_label_expert, row, 2)
        self.chroma_denoise_label_expert.hide()

        self.chroma_denoise_spin = QDoubleSpinBox()
        self.chroma_denoise_spin.setRange(0.0, 10.0)
        self.chroma_denoise_spin.setSingleStep(0.5)
        self.chroma_denoise_spin.setDecimals(1)
        self.chroma_denoise_spin.setValue(3.0)
        self.chroma_denoise_spin.setToolTip("Chroma denoise strength (0=off, 10=max)")
        layout.addWidget(self.chroma_denoise_spin, row, 3)
        self.chroma_denoise_spin.hide()

        row += 1

        # Debanding
        self.deband_check = QCheckBox("Enable Debanding")
        self.deband_check.setChecked(self.settings_manager.get("deband_enabled", False))
        self.deband_check.setToolTip(
            "Remove color banding artifacts from heavily compressed sources"
        )
        layout.addWidget(self.deband_check, row, 0)

        layout.addWidget(QLabel("Deband Strength:"), row, 1)
        self.deband_strength_combo = QComboBox()
        self.deband_strength_combo.addItems(["Light", "Medium", "Strong"])
        self.deband_strength_combo.setCurrentText(
            self.settings_manager.get("deband_strength", "Medium")
        )
        self.deband_strength_combo.setToolTip(
            "Light: Subtle | Medium: Balanced | Strong: Aggressive (may blur)"
        )
        layout.addWidget(self.deband_strength_combo, row, 2)
        row += 1

        # Stabilization
        self.stabilization_check = QCheckBox("Enable Video Stabilization")
        self.stabilization_check.setChecked(
            self.settings_manager.get("stabilization", False)
        )
        self.stabilization_check.setToolTip(
            "Reduce camera shake and handheld jitter using motion compensation\n"
            "• Auto: Analyzes and picks best method (MVTools)\n"
            "• General: Overall shake reduction (translation + zoom)\n"
            "• Horizontal/Vertical: Linear panning/tilting correction\n"
            "• Roll: Rotational camera movement correction\n"
            "• Aggressive: Multi-pass for very shaky footage"
        )
        layout.addWidget(self.stabilization_check, row, 0, 1, 2)

        # Stabilization mode
        layout.addWidget(QLabel("Stabilization Mode:"), row, 2)
        self.stabilization_mode_combo = QComboBox()
        self.stabilization_mode_combo.addItems(
            [
                "Auto (Detect Best Method)",
                "General Shake (MVTools)",
                "Horizontal/Vertical (SubShaker)",
                "Roll Correction (Depan)",
                "Aggressive (Multi-Pass)",
            ]
        )
        self.stabilization_mode_combo.setCurrentText(
            self.settings_manager.get("stabilization_mode", "Auto (Detect Best Method)")
        )
        self.stabilization_mode_combo.setToolTip(
            "Auto: Analyzes motion and picks best method\n"
            "General: MVTools for overall shake reduction\n"
            "Horizontal/Vertical: SubShaker for linear movement\n"
            "Roll: Depan for rotational correction\n"
            "Aggressive: Multi-pass for very shaky footage"
        )
        layout.addWidget(self.stabilization_mode_combo, row, 3)
        row += 1

        # Color correction
        layout.addWidget(QLabel("Color Correction:"), row, 2)
        self.color_correction_combo = QComboBox()
        self.color_correction_combo.addItems(
            [
                "None",
                "Auto White Balance",
                "Restore Faded Colors",
                "Increase Saturation",
                "Decrease Saturation",
            ]
        )
        self.color_correction_combo.setCurrentText(
            self.settings_manager.get("color_correction", "None")
        )
        self.color_correction_combo.setToolTip(
            "Adjust color and white balance: Auto WB | Restore faded | Adjust saturation"
        )
        layout.addWidget(self.color_correction_combo, row, 3)
        row += 1

        layout.addItem(
            QSpacerItem(
                0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            row,
            0,
        )
        widget.setLayout(layout)
        return widget

    def _build_ai_tools_tab(self) -> QWidget:
        """Build AI Tools tab with all AI-powered features."""
        from PySide6.QtWidgets import QScrollArea

        # Create scroll area for overflow content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Create content widget
        widget = QWidget()
        layout = QVBoxLayout()

        # AI Upscaling Group
        upscaling_group = QGroupBox("AI Upscaling")
        upscaling_layout = QGridLayout()
        upscaling_row = 0

        self.ai_upscaling_check = QCheckBox("Enable AI Upscaling")
        self.ai_upscaling_check.setChecked(
            self.settings_manager.get("use_ai_upscaling", False)
        )
        self.ai_upscaling_check.setToolTip(
            "AI super-resolution for upscaling (GPU recommended)"
        )
        self.ai_upscaling_check.stateChanged.connect(self._on_ai_upscaling_toggled)
        upscaling_layout.addWidget(self.ai_upscaling_check, upscaling_row, 0, 1, 2)
        upscaling_row += 1

        upscaling_layout.addWidget(QLabel("Method:"), upscaling_row, 0)
        self.ai_upscaling_method_combo = QComboBox()
        self.ai_upscaling_method_combo.addItems(
            [
                "ZNEDI3 (Fast, VapourSynth)",
                "RealESRGAN (Best Quality, CUDA)",
                "BasicVSR++ (Video-Aware, CUDA)",
                "SwinIR (Transformer-Based, CUDA)",
            ]
        )
        current_method = self.settings_manager.get(
            "ai_upscaling_method", "ZNEDI3 (Fast, VapourSynth)"
        )
        self.ai_upscaling_method_combo.setCurrentText(current_method)
        self.ai_upscaling_method_combo.setToolTip(
            "AI Upscaling Methods:\n\n"
            "• ZNEDI3: Fast, good quality (OpenCL GPU)\n"
            "  → Best for: Quick previews, older GPUs\n\n"
            "• RealESRGAN: Photo-optimized, frame-by-frame (CUDA GPU)\n"
            "  → Best for: Maximum spatial detail\n"
            "  → Note: May flicker without temporal smoothing\n\n"
            "• BasicVSR++: Video-specific with native temporal awareness (v3.0 NEW)\n"
            "  → Best for: Tape restoration, archival footage\n"
            "  → Built-in temporal stability (no flickering)\n"
            "  → Recommended for most users!\n\n"
            "• SwinIR: Transformer-based, excellent quality (v3.0 NEW)\n"
            "  → Best for: High-quality upscaling with good detail"
        )
        self.ai_upscaling_method_combo.currentTextChanged.connect(
            lambda text: self.settings_manager.save("ai_upscaling_method", text)
        )
        self.ai_upscaling_method_combo.currentTextChanged.connect(
            self._on_upscaling_method_changed
        )
        upscaling_layout.addWidget(self.ai_upscaling_method_combo, upscaling_row, 1)
        upscaling_row += 1

        upscaling_layout.addWidget(QLabel("Target Resolution:"), upscaling_row, 0)
        self.ai_upscale_target_combo = QComboBox()
        self.ai_upscale_target_combo.addItems(
            [
                "Source Resolution (No change)",
                "2x Source Resolution",
                "3x Source Resolution",
                "4x Source Resolution",
                "1080p (1920×1080 FHD)",
                "1440p (2560×1440 QHD)",
                "2160p (3840×2160 4K UHD)",
                "4320p (7680×4320 8K UHD)",
                "DCI 2K (2048×1080)",
                "DCI 4K (4096×2160)",
                "Custom...",
            ]
        )
        current_target = self.settings_manager.get(
            "ai_upscale_target", "2x Source Resolution"
        )
        self.ai_upscale_target_combo.setCurrentText(current_target)
        self.ai_upscale_target_combo.setToolTip(
            "All methods support any target resolution via post-resize:\n"
            "• AI upscales at native scale (RealESRGAN 4x, BasicVSR++ 2x, SwinIR 2x/3x/4x, ZNEDI3 2x)\n"
            "• Then resizes to your target resolution using high-quality Lanczos or your chosen method\n\n"
            "Source multipliers (2x, 3x, 4x): Auto-calculate from input video\n"
            "Standard resolutions (1080p, 4K, 8K): Fixed output dimensions\n"
            "Custom: Specify exact width × height"
        )
        self.ai_upscale_target_combo.currentTextChanged.connect(
            self._on_ai_target_changed
        )
        upscaling_layout.addWidget(self.ai_upscale_target_combo, upscaling_row, 1)
        upscaling_row += 1

        upscaling_layout.addWidget(QLabel("Final Resize Algorithm:"), upscaling_row, 0)
        self.ai_upscale_resize_algo_combo = QComboBox()
        self.ai_upscale_resize_algo_combo.addItems(
            ["Lanczos", "Bicubic", "Spline36", "Point"]
        )
        current_resize_algo = self.settings_manager.get(
            "ai_upscale_resize_algo", "Lanczos"
        )
        self.ai_upscale_resize_algo_combo.setCurrentText(current_resize_algo)
        self.ai_upscale_resize_algo_combo.setToolTip(
            "Algorithm used for final resize after AI upscaling:\n"
            "• Lanczos: Sharp, best quality (recommended)\n"
            "• Bicubic: Smooth, good quality\n"
            "• Spline36: Sharp edges, detailed\n"
            "• Point: Nearest neighbor, pixelated (fast)"
        )
        self.ai_upscale_resize_algo_combo.currentTextChanged.connect(
            lambda text: self.settings_manager.save("ai_upscale_resize_algo", text)
        )
        upscaling_layout.addWidget(self.ai_upscale_resize_algo_combo, upscaling_row, 1)
        upscaling_row += 1

        # Temporal smoothing checkbox (reduce AI flickering)
        self.temporal_smoothing_check = QCheckBox(
            "Temporal Smoothing (Reduce AI Flickering)"
        )
        self.temporal_smoothing_check.setChecked(
            self.settings_manager.get("use_temporal_smoothing", True)  # Default ON
        )
        self.temporal_smoothing_check.setToolTip(
            "Apply temporal smoothing after AI upscaling to reduce frame-to-frame flickering.\n\n"
            "Benefits:\n"
            "• Eliminates 'shimmer' and texture wobble in static scenes\n"
            "• Stabilizes color consistency across frames\n"
            "• Removes 'AI breathing' artifacts (pulsing)\n"
            "• Professional, stable output quality\n\n"
            "Performance: ~3-5% slower (minimal impact)\n"
            "Highly recommended for tape restoration!"
        )
        self.temporal_smoothing_check.stateChanged.connect(
            lambda state: self.settings_manager.save(
                "use_temporal_smoothing", state == Qt.CheckState.Checked.value
            )
        )
        upscaling_layout.addWidget(
            self.temporal_smoothing_check, upscaling_row, 0, 1, 2
        )
        upscaling_row += 1

        # Temporal smoothing strength (only shown when temporal smoothing is enabled)
        upscaling_layout.addWidget(QLabel("  Strength:"), upscaling_row, 0)
        self.temporal_strength_combo = QComboBox()
        self.temporal_strength_combo.addItems(["Light", "Medium", "Strong"])
        current_strength = self.settings_manager.get("temporal_strength", "Medium")
        self.temporal_strength_combo.setCurrentText(current_strength)
        self.temporal_strength_combo.setToolTip(
            "Temporal smoothing strength:\n"
            "• Light: Minimal smoothing, preserves most detail (for clean sources)\n"
            "• Medium: Balanced smoothing (recommended for tape restoration)\n"
            "• Strong: Aggressive smoothing (for very flickery AI output)"
        )
        self.temporal_strength_combo.currentTextChanged.connect(
            lambda text: self.settings_manager.save("temporal_strength", text)
        )
        upscaling_layout.addWidget(self.temporal_strength_combo, upscaling_row, 1)
        upscaling_row += 1

        # Face Enhancement checkbox (GFPGAN post-processing)
        self.ai_face_enhance_check = QCheckBox(
            "Enable AI Face Enhancement (GFPGAN)"
        )
        self.ai_face_enhance_check.setChecked(
            self.settings_manager.get("face_enhance", False)
        )
        self.ai_face_enhance_check.setToolTip(
            "Enable GFPGAN face restoration as a post-processing step.\n\n"
            "Uses GFPGAN (GAN Prior Embedded Network) to restore and enhance faces in degraded video.\n"
            "Works independently of the upscaling method - applied after all other processing.\n\n"
            "Requirements:\n"
            "• PyTorch with CUDA (GPU acceleration required)\n"
            "• Python 3.13 compatible (use Disty0's forks)\n"
            "• ~30ms per frame on RTX GPU (CUDA only, no NPU support)\n\n"
            "Installation:\n"
            "pip install git+https://github.com/Disty0/BasicSR.git\n"
            "pip install git+https://github.com/Disty0/GFPGAN.git facexlib\n\n"
            "Recommended for: Family videos, interviews, portraits with visible faces\n"
            "Note: May increase processing time significantly"
        )
        self.ai_face_enhance_check.stateChanged.connect(
            lambda state: self.settings_manager.save(
                "face_enhance", state == Qt.CheckState.Checked.value
            )
        )
        upscaling_layout.addWidget(self.ai_face_enhance_check, upscaling_row, 0, 1, 2)
        upscaling_row += 1

        # Show current GFPGAN temp directory setting (read-only display)
        gfpgan_info_layout = QHBoxLayout()
        gfpgan_info_layout.addWidget(QLabel("Current temp directory:"))
        self.gfpgan_temp_path_label = QLabel(
            self.settings_manager.get("gfpgan_temp_dir", "Default (System Temp)")
        )
        self.gfpgan_temp_path_label.setStyleSheet("color: gray; font-style: italic;")
        self.gfpgan_temp_path_label.setToolTip("Configure in Settings tab → Performance & Cache")
        gfpgan_info_layout.addWidget(self.gfpgan_temp_path_label)
        gfpgan_info_layout.addStretch()
        upscaling_layout.addLayout(gfpgan_info_layout, upscaling_row, 0, 1, 2)
        upscaling_row += 1
        
        # Note about configuring in Settings
        gfpgan_note_label = QLabel("💡 <i>Configure GFPGAN temp directory in <b>Settings tab → Performance & Cache</b></i>")
        gfpgan_note_label.setStyleSheet("color: #888; font-size: 10px;")
        upscaling_layout.addWidget(gfpgan_note_label, upscaling_row, 0, 1, 2)
        upscaling_row += 1

        upscaling_group.setLayout(upscaling_layout)
        layout.addWidget(upscaling_group)

        # ProPainter Inpainting Group
        propainter_group = QGroupBox("ProPainter - AI Video Inpainting")
        propainter_layout = QGridLayout()
        pp_row = 0

        self.ai_inpainting_check = QCheckBox("Enable ProPainter ⚠️")
        self.ai_inpainting_check.setChecked(
            self.settings_manager.get("ai_inpainting", False)
        )
        self.ai_inpainting_check.setToolTip(
            "⚠️ RESOURCE INTENSIVE: Requires 6GB+ RAM available, GPU recommended\n"
            "Remove scratches, artifacts, tape damage using AI (very slow)\n"
            "Use LOW preset first to test system stability"
        )
        propainter_layout.addWidget(self.ai_inpainting_check, pp_row, 0, 1, 2)
        pp_row += 1

        # Show current ProPainter temp directory setting (read-only display)
        propainter_info_layout = QHBoxLayout()
        propainter_info_layout.addWidget(QLabel("Current temp directory:"))
        self.propainter_temp_path_label = QLabel(
            self.settings_manager.get("propainter_temp_dir", "Default (System Temp)")
        )
        self.propainter_temp_path_label.setStyleSheet("color: gray; font-style: italic;")
        self.propainter_temp_path_label.setToolTip("Configure in Settings tab → Performance & Cache")
        propainter_info_layout.addWidget(self.propainter_temp_path_label)
        propainter_info_layout.addStretch()
        propainter_layout.addLayout(propainter_info_layout, pp_row, 0, 1, 2)
        pp_row += 1
        
        # Note about configuring in Settings
        propainter_note_label = QLabel("💡 <i>Configure ProPainter temp directory in <b>Settings tab → Performance & Cache</b></i>")
        propainter_note_label.setStyleSheet("color: #888; font-size: 10px;")
        propainter_layout.addWidget(propainter_note_label, pp_row, 0, 1, 2)
        pp_row += 1

        propainter_layout.addWidget(QLabel("Mode:"), pp_row, 2)
        self.inpainting_mode_combo = QComboBox()
        self.inpainting_mode_combo.addItems(
            ["Remove Artifacts", "Object Removal", "Restore Damaged Areas"]
        )
        self.inpainting_mode_combo.setCurrentText(
            self.settings_manager.get("inpainting_mode", "Remove Artifacts")
        )
        self.inpainting_mode_combo.setToolTip(
            "Artifacts: Auto-detect damage | Object: Manual mask | Restore: Heavy damage"
        )
        propainter_layout.addWidget(self.inpainting_mode_combo, pp_row, 3)
        pp_row += 1

        # Auto-mask generation
        self.propainter_auto_mask_check = QCheckBox("Auto-Generate Mask")
        self.propainter_auto_mask_check.setChecked(
            self.settings_manager.get("propainter_auto_mask", False)
        )
        self.propainter_auto_mask_check.setToolTip(
            "Automatically detect and mask artifacts (scratches, dropouts, noise)"
        )
        propainter_layout.addWidget(self.propainter_auto_mask_check, pp_row, 0, 1, 2)

        propainter_layout.addWidget(QLabel("Detection Mode:"), pp_row, 2)
        self.propainter_auto_mask_mode_combo = QComboBox()
        self.propainter_auto_mask_mode_combo.addItems(
            ["All Artifacts", "Scratches Only", "Dropouts Only", "Noise Only"]
        )
        mode_map = {
            "all": "All Artifacts",
            "scratches": "Scratches Only",
            "dropouts": "Dropouts Only",
            "noise": "Noise Only",
        }
        current_mode = self.settings_manager.get("propainter_auto_mask_mode", "all")
        self.propainter_auto_mask_mode_combo.setCurrentText(
            mode_map.get(current_mode, "All Artifacts")
        )
        self.propainter_auto_mask_mode_combo.setToolTip(
            "What types of artifacts to detect and mask"
        )
        propainter_layout.addWidget(self.propainter_auto_mask_mode_combo, pp_row, 3)
        pp_row += 1

        propainter_layout.addWidget(QLabel("Sensitivity:"), pp_row, 0)
        self.propainter_auto_mask_sensitivity_spin = QDoubleSpinBox()
        self.propainter_auto_mask_sensitivity_spin.setRange(0.1, 1.0)
        self.propainter_auto_mask_sensitivity_spin.setSingleStep(0.1)
        self.propainter_auto_mask_sensitivity_spin.setValue(
            self.settings_manager.get("propainter_auto_mask_sensitivity", 0.5)
        )
        self.propainter_auto_mask_sensitivity_spin.setToolTip(
            "Higher = more aggressive detection (0.1-1.0)"
        )
        propainter_layout.addWidget(
            self.propainter_auto_mask_sensitivity_spin, pp_row, 1
        )

        propainter_layout.addWidget(QLabel("Memory Preset:"), pp_row, 2)
        self.propainter_memory_preset_combo = QComboBox()
        self.propainter_memory_preset_combo.addItems(
            [
                "Auto (Detect GPU)",
                "Low (4-8GB VRAM)",
                "Medium (8-12GB VRAM)",
                "High (12-16GB VRAM)",
                "Ultra (24GB+ VRAM)",
            ]
        )
        preset_map = {
            "auto": "Auto (Detect GPU)",
            "low": "Low (4-8GB VRAM)",
            "medium": "Medium (8-12GB VRAM)",
            "high": "High (12-16GB VRAM)",
            "ultra": "Ultra (24GB+ VRAM)",
        }
        current_preset = self.settings_manager.get("propainter_memory_preset", "auto")
        self.propainter_memory_preset_combo.setCurrentText(
            preset_map.get(current_preset, "Auto (Detect GPU)")
        )
        self.propainter_memory_preset_combo.setToolTip(
            "Memory usage preset:\n"
            "• Auto: Detects GPU and picks best preset\n"
            "• Low: Slowest but works on any hardware\n"
            "• Medium/High: Balanced speed/memory\n"
            "• Ultra: Fastest, requires powerful GPU"
        )
        propainter_layout.addWidget(self.propainter_memory_preset_combo, pp_row, 3)
        pp_row += 1

        # Manual mask file
        propainter_layout.addWidget(QLabel("Manual Mask (Optional):"), pp_row, 0)
        self.propainter_mask_edit = QLineEdit()
        self.propainter_mask_edit.setText(
            self.settings_manager.get("propainter_mask_path", "")
        )
        self.propainter_mask_edit.setPlaceholderText(
            "Auto-mask or browse for manual mask"
        )
        self.propainter_mask_edit.setToolTip(
            "White pixels = areas to inpaint/fix, Black pixels = keep original"
        )
        propainter_layout.addWidget(self.propainter_mask_edit, pp_row, 1, 1, 2)

        self.propainter_mask_btn = QPushButton("Browse...")
        self.propainter_mask_btn.clicked.connect(self._browse_propainter_mask)
        self.propainter_mask_btn.setToolTip(
            "Select a mask image (white = areas to restore, black = keep original)"
        )
        propainter_layout.addWidget(self.propainter_mask_btn, pp_row, 3)
        pp_row += 1

        propainter_group.setLayout(propainter_layout)
        layout.addWidget(propainter_group)

        # Frame Interpolation (RIFE) Group
        interpolation_group = QGroupBox("RIFE - AI Frame Interpolation")
        interpolation_layout = QGridLayout()
        interp_row = 0

        self.ai_interpolation_check = QCheckBox("Enable Frame Interpolation")
        self.ai_interpolation_check.setChecked(
            self.settings_manager.get("ai_interpolation", False)
        )
        self.ai_interpolation_check.setToolTip(
            "AI-based frame interpolation to increase framerate (requires GPU)"
        )
        interpolation_layout.addWidget(self.ai_interpolation_check, interp_row, 0, 1, 2)

        interpolation_layout.addWidget(QLabel("Target Framerate:"), interp_row, 2)
        self.interpolation_factor_combo = QComboBox()
        self.interpolation_factor_combo.addItems(
            ["2x (30fps→60fps)", "3x (30fps→90fps)", "4x (30fps→120fps)"]
        )
        self.interpolation_factor_combo.setCurrentText(
            self.settings_manager.get("interpolation_factor", "2x (30fps→60fps)")
        )
        self.interpolation_factor_combo.setToolTip(
            "Higher values = smoother motion but slower processing"
        )
        interpolation_layout.addWidget(self.interpolation_factor_combo, interp_row, 3)
        interp_row += 1

        interpolation_group.setLayout(interpolation_layout)
        layout.addWidget(interpolation_group)

        # Colorization (DeOldify) Group
        colorization_group = QGroupBox("DeOldify - AI Colorization")
        color_layout = QGridLayout()
        color_row = 0

        self.ai_colorization_check = QCheckBox("Enable Colorization")
        self.ai_colorization_check.setChecked(
            self.settings_manager.get("ai_colorization", False)
        )
        self.ai_colorization_check.setToolTip(
            "AI-based colorization for black & white footage"
        )
        color_layout.addWidget(self.ai_colorization_check, color_row, 0, 1, 2)

        color_layout.addWidget(QLabel("Artistic Factor:"), color_row, 2)
        self.deoldify_artistic_spin = QSpinBox()
        self.deoldify_artistic_spin.setRange(0, 40)
        self.deoldify_artistic_spin.setValue(
            self.settings_manager.get("deoldify_artistic", 35)
        )
        self.deoldify_artistic_spin.setToolTip(
            "0 = realistic, 40 = vibrant colors (35 recommended)"
        )
        color_layout.addWidget(self.deoldify_artistic_spin, color_row, 3)
        color_row += 1

        color_layout.addWidget(QLabel("Model Type:"), color_row, 0)
        self.deoldify_model_combo = QComboBox()
        self.deoldify_model_combo.addItems(
            ["Video Model (Stable)", "Artistic Model (Vivid)"]
        )
        self.deoldify_model_combo.setCurrentText(
            self.settings_manager.get("deoldify_model", "Video Model (Stable)")
        )
        self.deoldify_model_combo.setToolTip(
            "Video: Temporal consistency | Artistic: More vibrant colors"
        )
        color_layout.addWidget(self.deoldify_model_combo, color_row, 1, 1, 3)
        color_row += 1

        colorization_group.setLayout(color_layout)
        layout.addWidget(colorization_group)

        layout.addStretch()
        widget.setLayout(layout)

        # Wrap in scroll area to handle overflow
        scroll_area.setWidget(widget)
        return scroll_area

    def _build_output_tab(self) -> QWidget:
        """Build output encoding options tab."""
        widget = QWidget()
        layout = QGridLayout()
        row = 0

        # Aspect ratio / resize
        layout.addWidget(QLabel("Aspect Ratio Mode:"), row, 0)
        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(
            ["Keep (Default)", "Correct to Square Pixels", "Manual Resize"]
        )
        self.aspect_ratio_combo.setCurrentText(
            self.settings_manager.get("aspect_ratio_mode", "Keep (Default)")
        )
        self.aspect_ratio_combo.setToolTip(
            "Keep: Preserve source aspect ratio\n"
            "Square Pixels: Fix 4:3 anamorphic (DV footage)\n"
            "Manual: Custom resolution\n\n"
            "⚠️ When AI Upscaling is enabled, use 'AI Tools' tab for resolution control"
        )
        layout.addWidget(self.aspect_ratio_combo, row, 1)

        layout.addWidget(QLabel("Resize Algorithm:"), row, 2)
        self.resize_algo_combo = QComboBox()
        self.resize_algo_combo.addItems(["Bicubic", "Lanczos", "Spline36", "Point"])
        self.resize_algo_combo.setCurrentText(
            self.settings_manager.get("resize_algorithm", "Lanczos")
        )
        self.resize_algo_combo.setToolTip(
            "Lanczos: Sharp, best quality | Bicubic: Smooth | Spline36: Detailed | Point: Fast, pixelated"
        )
        layout.addWidget(self.resize_algo_combo, row, 3)
        row += 1

        # AI Upscaling status info
        self.ai_resize_info_label = QLabel("")
        self.ai_resize_info_label.setStyleSheet(
            "color: #0052cc; font-weight: bold; padding: 5px;"
        )
        self.ai_resize_info_label.setWordWrap(True)
        layout.addWidget(self.ai_resize_info_label, row, 0, 1, 4)
        row += 1

        layout.addWidget(QLabel("Resize Mode:"), row, 0)
        self.resize_mode_combo = QComboBox()
        self.resize_mode_combo.addItems(["Letterbox (Pad)", "Crop to Fill", "Stretch"])
        self.resize_mode_combo.setCurrentText(
            self.settings_manager.get("resize_mode", "Letterbox (Pad)")
        )
        self.resize_mode_combo.setToolTip(
            "Letterbox: Add black bars | Crop: Cut edges | Stretch: Distort"
        )
        layout.addWidget(self.resize_mode_combo, row, 1)

        layout.addWidget(QLabel("Width:"), row, 2)
        self.resize_width_spin = QSpinBox()
        self.resize_width_spin.setRange(64, 4096)
        self.resize_width_spin.setSingleStep(2)
        self.resize_width_spin.setValue(
            int(self.settings_manager.get("resize_width", 640))
        )
        self.resize_width_spin.setToolTip(
            "Target width in pixels (must be even number)"
        )
        layout.addWidget(self.resize_width_spin, row, 3)
        row += 1

        layout.addWidget(QLabel("Height:"), row, 2)
        self.resize_height_spin = QSpinBox()
        self.resize_height_spin.setRange(64, 4096)
        self.resize_height_spin.setSingleStep(2)
        self.resize_height_spin.setValue(
            int(self.settings_manager.get("resize_height", 480))
        )
        self.resize_height_spin.setToolTip(
            "Target height in pixels (must be even number)"
        )
        layout.addWidget(self.resize_height_spin, row, 3)
        row += 1

        # Output Mode (Video or Frame Sequence)
        layout.addWidget(QLabel("Output Mode:"), row, 0)
        self.output_mode_combo = QComboBox()
        self.output_mode_combo.addItems(["Video File", "Frame Sequence"])
        self.output_mode_combo.setCurrentText(
            self.settings_manager.get("output_mode", "Video File")
        )
        self.output_mode_combo.setToolTip(
            "Video File: Standard video encoding\n"
            "Frame Sequence: Output individual frames (PNG, TIFF, etc.)"
        )
        self.output_mode_combo.currentTextChanged.connect(self._on_output_mode_changed)
        layout.addWidget(self.output_mode_combo, row, 1)
        
        layout.addWidget(QLabel("Frame Format:"), row, 2)
        self.frame_format_combo = QComboBox()
        self.frame_format_combo.addItems([
            "PNG (Lossless)",
            "TIFF 16-bit",
            "JPEG (Quality 95)",
            "DPX (Cinema)"
        ])
        self.frame_format_combo.setCurrentText(
            self.settings_manager.get("frame_format", "PNG (Lossless)")
        )
        self.frame_format_combo.setToolTip(
            "PNG: Lossless, good compression\n"
            "TIFF: Professional archival, 16-bit\n"
            "JPEG: Lossy, small files\n"
            "DPX: Cinema standard, 10-bit"
        )
        layout.addWidget(self.frame_format_combo, row, 3)
        row += 1
        
        # Codec (only for video mode)
        layout.addWidget(QLabel("Codec:"), row, 0)
        self.codec_combo = QComboBox()
        codecs = [
            "libx264 (H.264, CPU)",
            "libx265 (H.265, CPU)",
            "h264_nvenc (NVIDIA H.264)",
            "hevc_nvenc (NVIDIA H.265)",
            "libsvtav1 (AV1)",
            "ProRes 4444 XQ",
            "ProRes 4444",
            "ProRes 422 (HQ)",
            "ProRes 422",
            "ProRes 422 (LT)",
            "ProRes 422 (Proxy)",
            "DNxHD",
            "FFV1 (Lossless)",
        ]
        self.codec_combo.addItems(codecs)
        self.codec_combo.setCurrentText(
            self.settings_manager.get("codec", "libx264 (H.264, CPU)")
        )
        self.codec_combo.setToolTip(
            "H.264: Universal compatibility | H.265: Better compression | ProRes: Professional editing"
        )
        layout.addWidget(self.codec_combo, row, 1)

        # Audio
        layout.addWidget(QLabel("Audio:"), row, 2)
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Copy Audio", "Re-encode Audio", "No Audio"])
        self.audio_combo.setCurrentText(
            self.settings_manager.get("audio", "Copy Audio")
        )
        self.audio_combo.setToolTip(
            "Copy: No quality loss | Re-encode: Convert format | No Audio: Remove audio track"
        )
        layout.addWidget(self.audio_combo, row, 3)
        row += 1

        # Audio codec/bitrate
        layout.addWidget(QLabel("Audio Codec:"), row, 0)
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(["AAC", "AC3", "PCM (lossless)"])
        self.audio_codec_combo.setCurrentText(
            self.settings_manager.get("audio_codec", "AAC")
        )
        self.audio_codec_combo.setToolTip(
            "AAC: Best quality/size | AC3: DVD/Blu-ray standard | PCM: Uncompressed"
        )
        layout.addWidget(self.audio_codec_combo, row, 1)

        layout.addWidget(QLabel("Audio Bitrate:"), row, 2)
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["128k", "192k", "256k", "320k", "Lossless"])
        self.audio_bitrate_combo.setCurrentText(
            self.settings_manager.get("audio_bitrate", "192k")
        )
        self.audio_bitrate_combo.setToolTip(
            "Higher = better quality (192k recommended for most content)"
        )
        layout.addWidget(self.audio_bitrate_combo, row, 3)
        row += 1

        # Quality (CRF)
        layout.addWidget(QLabel("Quality (CRF):"), row, 0)
        self.crf_spinbox = QSpinBox()
        self.crf_spinbox.setRange(0, 51)
        self.crf_spinbox.setValue(int(self.settings_manager.get("crf", 18)))
        self.crf_spinbox.setToolTip(
            "Lower = better quality (15-20 archival, 21-28 recommended)"
        )
        layout.addWidget(self.crf_spinbox, row, 1)

        # Preset
        layout.addWidget(QLabel("Encoder Preset:"), row, 2)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ]
        )
        self.preset_combo.setCurrentText(
            self.settings_manager.get("ffmpeg_preset", "medium")
        )
        self.preset_combo.setToolTip(
            "Fast: Quick encoding | Medium: Balanced | Slow: Best compression (longer encode)"
        )
        layout.addWidget(self.preset_combo, row, 3)
        row += 1

        # AI Inference Mode section
        inference_label = QLabel("AI Inference Mode:")
        inference_label.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px;")
        layout.addWidget(inference_label, row, 0, 1, 4)
        row += 1

        # Auto mode checkbox
        self.auto_inference_check = QCheckBox("Auto-detect optimal mode (Recommended)")
        self.auto_inference_check.setChecked(
            self.settings_manager.get("auto_inference_mode", True)
        )
        self.auto_inference_check.setToolTip(
            "Automatically selects the best inference mode based on your GPU VRAM.\n\n"
            "Benefits:\n"
            "• Prevents out-of-memory errors on low-VRAM GPUs\n"
            "• Maximizes quality when VRAM allows\n"
            "• Optimizes for battery life on laptops\n\n"
            "Uncheck to manually select a specific mode."
        )
        self.auto_inference_check.stateChanged.connect(self._on_auto_inference_changed)
        layout.addWidget(self.auto_inference_check, row, 0, 1, 4)
        row += 1

        # Current recommendation label
        self.inference_recommendation_label = QLabel("")
        self.inference_recommendation_label.setStyleSheet(
            "color: #0052cc; padding: 5px; font-style: italic;"
        )
        self.inference_recommendation_label.setWordWrap(True)
        layout.addWidget(self.inference_recommendation_label, row, 0, 1, 4)
        row += 1

        # Manual mode selector
        layout.addWidget(QLabel("Manual Mode:"), row, 0)
        self.inference_mode_combo = QComboBox()
        self.inference_mode_combo.addItems([
            "PyTorch FP32 - Best Quality (6GB+ VRAM)",
            "PyTorch FP16 - Excellent Quality (3GB+ VRAM)",
            "ONNX FP16 - Great Quality, Low VRAM (2GB+)",
            "ONNX INT8 - Good Quality, Very Low VRAM (1GB+)",
            "CPU Only - Slow but Always Works"
        ])
        
        # Load saved mode or detect
        saved_mode = self.settings_manager.get("manual_inference_mode", "pytorch_fp32")
        mode_map = {
            "pytorch_fp32": 0,
            "pytorch_fp16": 1,
            "onnx_fp16": 2,
            "onnx_int8": 3,
            "cpu_only": 4
        }
        self.inference_mode_combo.setCurrentIndex(mode_map.get(saved_mode, 0))
        self.inference_mode_combo.setEnabled(not self.auto_inference_check.isChecked())
        self.inference_mode_combo.setToolTip(
            "PyTorch FP32: Full precision, best quality (requires 6GB+ VRAM)\n"
            "PyTorch FP16: Half precision, 2x faster, 50% less VRAM\n"
            "ONNX FP16: Optimized, works on AMD/Intel/NPU, 50% less VRAM\n"
            "ONNX INT8: Quantized, works on 2GB GPUs (some quality loss)\n"
            "CPU Only: Fallback for systems without GPU"
        )
        self.inference_mode_combo.currentIndexChanged.connect(self._on_manual_inference_changed)
        layout.addWidget(self.inference_mode_combo, row, 1, 1, 3)
        row += 1

        # Show mode details button
        details_btn = QPushButton("ℹ️ Compare Modes")
        details_btn.setToolTip("Show detailed comparison of all inference modes")
        details_btn.clicked.connect(self._show_inference_mode_details)
        layout.addWidget(details_btn, row, 0, 1, 2)
        
        # GPU info label
        self.gpu_info_label = QLabel("")
        self.gpu_info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.gpu_info_label, row, 2, 1, 2)
        row += 1

        # Update inference recommendation on startup
        self._update_inference_recommendation()

        layout.addItem(
            QSpacerItem(
                0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            row,
            0,
        )
        widget.setLayout(layout)
        return widget

    def _build_control_section(self) -> QFrame:
        """Build processing control buttons."""
        frame = QFrame()
        layout = QHBoxLayout()

        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setMinimumHeight(40)
        self.start_button.setToolTip("Begin video restoration with current settings")
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setToolTip("Cancel current processing job")
        layout.addWidget(self.stop_button)

        # Progress bar with GPU metrics
        progress_layout = QVBoxLayout()

        # Top row: Progress % + GPU metrics (GPU-specific, shown during processing)
        progress_info_top = QHBoxLayout()
        self.progress_label = QLabel("0.0%")
        progress_info_top.addWidget(self.progress_label)
        progress_info_top.addStretch()
        
        self.gpu_usage_label = QLabel("")
        self.gpu_vram_label = QLabel("")
        progress_info_top.addWidget(self.gpu_usage_label)
        progress_info_top.addWidget(self.gpu_vram_label)
        
        # Middle row: Progress bar
        self.progressbar = QProgressBar()
        self.progressbar.setValue(0)
        
        # Pipeline status (shows current processing stages)
        self.pipeline_label = QLabel("")
        self.pipeline_label.setStyleSheet("color: #888; font-style: italic;")
        self.pipeline_label.setAlignment(Qt.AlignCenter)
        
        # Bottom row: Frame count + fps + ETA
        progress_info_bottom = QHBoxLayout()
        self.frame_count_label = QLabel("")
        progress_info_bottom.addWidget(self.frame_count_label)
        progress_info_bottom.addStretch()
        self.fps_label = QLabel("")
        progress_info_bottom.addWidget(self.fps_label)
        self.eta_label = QLabel("ETA: --:--:--")
        progress_info_bottom.addWidget(self.eta_label)

        progress_layout.addLayout(progress_info_top)
        progress_layout.addWidget(self.progressbar)
        progress_layout.addWidget(self.pipeline_label)
        progress_layout.addLayout(progress_info_bottom)

        layout.addLayout(progress_layout, 1)
        frame.setLayout(layout)
        return frame

    def _build_status_bar(self):
        """Build status bar with performance metrics."""
        status_bar = self.statusBar()
        
        # Left side: System metrics
        self.status_cpu_label = QLabel("🖥️ CPU: --")
        self.status_ram_label = QLabel("💾 RAM: --")
        self.status_threads_label = QLabel("⚙️ Threads: --")
        
        status_bar.addWidget(self.status_cpu_label)
        status_bar.addWidget(QLabel(" | "))
        status_bar.addWidget(self.status_ram_label)
        status_bar.addWidget(QLabel(" | "))
        status_bar.addWidget(self.status_threads_label)
        
        # Right side: CUDA status
        self.status_cuda_label = QLabel("CUDA: --")
        status_bar.addPermanentWidget(self.status_cuda_label)

    def _build_bottom_status(self) -> QFrame:
        """Build bottom status area above the console: AI model directory and console toggle."""
        frame = QFrame()
        layout = QHBoxLayout()

        # AI model directory label
        self.ai_model_dir_label = QLabel("")
        self.ai_model_dir_label.setStyleSheet("border: 1px solid gray; padding: 4px;")
        layout.addWidget(self.ai_model_dir_label, 1)

        change_btn = QPushButton("🤖 AI Models...")
        change_btn.setToolTip(
            "Open AI Model Manager to download models, change directory, setup ProPainter"
        )
        change_btn.clicked.connect(self.show_ai_model_manager)
        layout.addWidget(change_btn)

        # Console window toggle
        self.console_toggle_btn = QPushButton("📋 Show Console Window")
        self.console_toggle_btn.clicked.connect(self.toggle_console_window)
        self.console_toggle_btn.setToolTip("Open console output in separate window")
        layout.addWidget(self.console_toggle_btn)

        frame.setLayout(layout)

        # Initialize label value
        self.update_ai_model_label()

        return frame

    def update_ai_model_label(self):
        """Update the AI model directory label from settings or default."""
        settings = self.settings_manager.load_settings()
        ai_dir = settings.get("ai_model_dir")
        if not ai_dir:
            try:
                ai_dir = str(get_storage_dir())
            except Exception:
                ai_dir = "(unknown)"
        self.ai_model_dir_label.setText(f"AI Model Dir: {ai_dir}")

    def apply_ui_font_size(self):
        """Apply UI font size from settings to the QApplication."""
        try:
            settings = self.settings_manager.load_settings()
            size = int(settings.get("ui_font_size", 11))
            font = QFont()
            font.setPointSize(size)
            app = QApplication.instance()
            if app is not None and hasattr(app, "setFont"):
                app.setFont(font)
                # Also adjust console's fixed font if present
                try:
                    self.console_text.setFont(font)
                except Exception:
                    pass
        except Exception:
            pass

    def apply_ui_theme(self):
        """Apply UI theme from settings (Dark Mode, Light Mode, or System Default)."""
        try:
            settings = self.settings_manager.load_settings()
            theme = settings.get("ui_theme", "System Default")
            app = QApplication.instance()
            if app is None:
                return

            if theme == "Dark Mode":
                # Apply dark palette
                palette = QPalette()
                palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
                palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
                palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
                palette.setColor(
                    QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
                )
                app.setPalette(palette)
                app.setStyle("Fusion")
                # Fix QComboBox dropdown visibility in dark mode
                app.setStyleSheet("""
                    QComboBox QAbstractItemView {
                        background-color: #353535;
                        color: #FFFFFF;
                        selection-background-color: #2A82DA;
                        selection-color: #FFFFFF;
                        border: 1px solid #555555;
                    }
                """)
                self.console_log("🌙 Dark Mode enabled")
            elif theme == "Light Mode":
                # Apply light palette (bright, clean colors)
                palette = QPalette()
                palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
                palette.setColor(
                    QPalette.ColorRole.AlternateBase, QColor(245, 245, 245)
                )
                palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
                palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
                palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
                palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
                palette.setColor(
                    QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
                )
                app.setPalette(palette)
                app.setStyle("Fusion")
                # Fix QComboBox dropdown visibility in light mode
                app.setStyleSheet("""
                    QComboBox QAbstractItemView {
                        background-color: #FFFFFF;
                        color: #000000;
                        selection-background-color: #0078D7;
                        selection-color: #FFFFFF;
                        border: 1px solid #CCCCCC;
                    }
                """)
                self.console_log("☀️ Light Mode enabled")
            else:  # System Default
                # Reset to system default - use native Windows style
                app.setStyle("windowsvista")
                app.setPalette(app.style().standardPalette())
                app.setStyleSheet("")  # Clear any custom stylesheets
                self.console_log("💻 System Default theme enabled")
        except Exception as e:
            self.console_log(f"Theme apply error: {e}")

    def apply_tooltips(self):
        """Enable or disable tooltips across all widgets."""
        try:
            settings = self.settings_manager.load_settings()
            enabled = settings.get("tooltips_enabled", True)

            # Get all widgets in the application
            all_widgets = self.findChildren(QWidget)

            for widget in all_widgets:
                # Store original tooltip if not already stored
                if not hasattr(widget, "_original_tooltip"):
                    widget._original_tooltip = widget.toolTip()

                # Enable or disable tooltip
                if enabled:
                    if (
                        hasattr(widget, "_original_tooltip")
                        and widget._original_tooltip
                    ):
                        widget.setToolTip(widget._original_tooltip)
                else:
                    widget.setToolTip("")

            status = "enabled" if enabled else "disabled"
            self.console_log(f"💬 Tooltips {status}")
        except Exception as e:
            self.console_log(f"Tooltip apply error: {e}")

    def toggle_console(self, hidden: bool):
        """Show or hide the console text area."""
        if hidden:
            try:
                self.console_frame.hide()
            except Exception:
                self.console_text.hide()
            self.console_toggle_btn.setText("Show Console")
        else:
            try:
                self.console_frame.show()
            except Exception:
                self.console_text.show()
            self.console_toggle_btn.setText("Hide Console")
        # Make sure layout recalculates and remaining widgets expand
        try:
            layout = self.centralWidget().layout()
            if layout:
                layout.activate()
            self.centralWidget().updateGeometry()
            self.centralWidget().adjustSize()
        except Exception:
            pass

    def _setup_menu_bar(self):
        """Build application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Select Input...", self.select_input)
        file_menu.addAction("Select Output...", self.select_output)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Batch menu
        batch_menu = menubar.addMenu("Batch")
        batch_menu.addAction("Add Current to Queue", self.add_to_batch)
        batch_menu.addAction("Start Batch Processing", self.start_batch_processing)

        # Presets menu
        presets_menu = menubar.addMenu("Presets")
        presets_menu.addAction("Save Current Settings...", self.save_preset)
        presets_menu.addAction("Load Preset...", self.load_preset)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Detect Field Order", self.detect_field_order)
        tools_menu.addSeparator()

        # Expert mode toggle
        self.expert_mode_action = tools_menu.addAction("Expert Mode (Numeric Values)")
        self.expert_mode_action.setCheckable(True)
        self.expert_mode_action.setChecked(
            self.settings_manager.get("expert_mode", False)
        )
        self.expert_mode_action.toggled.connect(self._toggle_expert_mode)
        tools_menu.addSeparator()

        # AI Model Manager (v3.0)
        tools_menu.addAction(
            "🤖 Manage AI Models (v3.0)...", self.show_ai_model_manager
        )
        tools_menu.addSeparator()
        tools_menu.addAction("Settings...", self.show_settings_dialog)
        tools_menu.addSeparator()

        tools_menu.addAction("Clear Console", lambda: self.console_text.clear())

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)

    # File selection methods
    def select_input(self):
        """Select input video file via dialog."""
        # Use current input as starting directory if valid
        start_dir = ""
        if self.input_file and os.path.isfile(self.input_file):
            start_dir = str(Path(self.input_file).parent)
        
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Video",
            start_dir,
            filter="Video Files (*.mkv *.mp4 *.avi *.mts *.m2ts *.ts *.mov);;All Files (*.*)",
        )
        if file:
            # Normalize to Windows backslashes
            file = file.replace('/', '\\')
            self.input_file = file
            self.input_line_edit.setText(file)
            self.console_log(f"Input file: {file}")

            # Auto-suggest output
            if not self.output_file:
                path = Path(file)
                output = path.parent / f"{path.stem}_restored.mp4"
                output_str = str(output).replace('/', '\\')
                self.output_file = output_str
                self.output_line_edit.setText(output_str)

    def select_output(self):
        """Select output video file or directory via dialog."""
        # Check if frame sequence mode
        is_frame_sequence = (self.output_mode_combo.currentText() == "Frame Sequence")
        
        # Use current output as starting directory if valid
        start_dir = ""
        if self.output_file:
            output_path = Path(self.output_file)
            if output_path.parent.exists():
                start_dir = str(output_path.parent)
        elif self.input_file and os.path.isfile(self.input_file):
            start_dir = str(Path(self.input_file).parent)
        
        if is_frame_sequence:
            # Select directory for frame sequence
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory for Frame Sequence",
                start_dir
            )
            if directory:
                # Normalize to Windows backslashes
                directory = directory.replace('/', '\\')
                
                # Get format extension
                frame_format = self.frame_format_combo.currentText()
                ext = {
                    "PNG (Lossless)": "png",
                    "TIFF 16-bit": "tif",
                    "JPEG (Quality 95)": "jpg",
                    "DPX (Cinema)": "dpx"
                }.get(frame_format, "png")
                
                # Build frame pattern
                output_pattern = f"{directory}\\frame_%06d.{ext}"
                self.output_file = output_pattern
                self.output_line_edit.setText(output_pattern)
                self.console_log(f"Output frame sequence: {output_pattern}")
        else:
            # Select single video file
            file, _ = QFileDialog.getSaveFileName(
                self,
                "Select Output Video",
                start_dir,
                filter="Video Files (*.mp4 *.mkv *.mov);;All Files (*.*)",
            )
            if file:
                # Normalize to Windows backslashes
                file = file.replace('/', '\\')
                self.output_file = file
                self.output_line_edit.setText(file)
                self.console_log(f"Output file: {file}")
    
    def _on_output_mode_changed(self, mode: str):
        """Handle output mode change (Video/Frame Sequence)."""
        is_video = (mode == "Video File")
        
        # Show/hide codec and audio options
        self.codec_combo.setEnabled(is_video)
        self.audio_combo.setEnabled(is_video)
        self.audio_codec_combo.setEnabled(is_video)
        self.audio_bitrate_combo.setEnabled(is_video)
        self.crf_spin.setEnabled(is_video)
        self.ffmpeg_preset_combo.setEnabled(is_video)
        
        # Show/hide frame format
        self.frame_format_combo.setEnabled(not is_video)
        
        # Update output file browse button tooltip
        if is_video:
            tooltip = "Choose output file location and name"
        else:
            tooltip = "Choose output directory for frame sequence"
        
        # Find and update browse button tooltip
        for child in self.findChildren(QPushButton):
            if child.text() == "Browse..." and "output" in child.toolTip().lower():
                child.setToolTip(tooltip)
                break
    
    def _on_input_path_changed(self, text: str):
        """Handle manual input path changes with validation."""
        text = text.strip()
        if text:
            # Remove quotes if user pasted path with quotes
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            
            # Normalize path separators to Windows backslashes
            text = text.replace('/', '\\')
            
            # Update internal state
            self.input_file = text
            
            # Visual feedback: change color based on validity
            if os.path.isfile(text):
                self.input_line_edit.setStyleSheet("QLineEdit { background-color: #e8f5e9; color: #1b5e20; }")
            else:
                self.input_line_edit.setStyleSheet("QLineEdit { background-color: #fff3e0; color: #e65100; }")
        else:
            self.input_file = ""
            self.input_line_edit.setStyleSheet("")
    
    def _on_output_path_changed(self, text: str):
        """Handle manual output path changes with validation."""
        text = text.strip()
        if text:
            # Remove quotes if user pasted path with quotes
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            
            # Normalize path separators to Windows backslashes
            text = text.replace('/', '\\')
            
            # Update internal state
            self.output_file = text
            
            # Visual feedback: check if parent directory exists
            output_path = Path(text)
            if output_path.parent.exists():
                self.output_line_edit.setStyleSheet("QLineEdit { background-color: #e8f5e9; color: #1b5e20; }")
            else:
                self.output_line_edit.setStyleSheet("QLineEdit { background-color: #fff3e0; color: #e65100; }")
        else:
            self.output_file = ""
            self.output_line_edit.setStyleSheet("")

    def get_current_options(self) -> dict:
        """Get current GUI settings as dictionary."""
        expert_mode = self.settings_manager.get("expert_mode", False)

        return {
            "source_filter": self.source_filter_combo.currentText().split()[0].lower(),
            "field_order": self.field_order_combo.currentText(),
            # Theatre Mode settings
            "theatre_mode_enabled": self.theatre_mode_check.isChecked(),
            "chroma_correction_enabled": self.chroma_correction_check.isChecked(),
            "chroma_preset": {
                "LaserDisc (0.25px)": "laserdisc",
                "VHS Composite (0.5px)": "vhs_composite",
                "S-VHS (0.15px)": "svhs",
                "Hi8 (0.2px)": "hi8",
                "Betamax (0.3px)": "betamax",
                "Custom": "custom"
            }.get(self.chroma_preset_combo.currentText(), "laserdisc"),
            "chroma_shift_x_px": self.chroma_shift_x_spin.value(),
            "chroma_shift_y_px": self.chroma_shift_y_spin.value(),
            "deinterlace_variant": {
                "Standard (Progressive)": "standard",
                "Bob (Double-Rate)": "bob",
                "Keep Interlaced": "keep_interlaced"
            }.get(self.deinterlace_variant_combo.currentText(), "standard"),
            "apply_level_adjustment": self.level_adjustment_check.isChecked(),
            "black_point": self.black_point_spin.value(),
            "white_point": self.white_point_spin.value(),
            "saturation_boost": self.saturation_boost_spin.value(),
            "deinterlace_preset": self.qtgmc_preset.currentText(),
            "sharpness": self.sharpness_spin.value(),
            "faster_processing": self.faster_processing_check.isChecked(),
            "bm3d_enabled": self.bm3d_check.isChecked(),
            "bm3d_sigma": self._get_bm3d_sigma(),
            "bm3d_use_gpu": self.bm3d_gpu_check.isChecked(),
            "temporal_denoise": (
                str(self.temporal_denoise_spin.value())
                if expert_mode and self.temporal_denoise_spin.isVisible()
                else self.temporal_denoise_combo.currentText()
            ),
            "chroma_denoise": (
                str(self.chroma_denoise_spin.value())
                if expert_mode and self.chroma_denoise_spin.isVisible()
                else self.chroma_denoise_combo.currentText()
            ),
            "deband_enabled": self.deband_check.isChecked(),
            "deband_strength": self.deband_strength_combo.currentText(),
            "deband_range": (
                self.deband_range_spin.value()
                if expert_mode and self.deband_range_spin.isVisible()
                else None
            ),
            "stabilization": self.stabilization_check.isChecked(),
            "stabilization_mode": self.stabilization_mode_combo.currentText(),
            "color_correction": self.color_correction_combo.currentText(),
            "ai_interpolation": self.ai_interpolation_check.isChecked(),
            "interpolation_factor": self.interpolation_factor_combo.currentText(),
            # GFPGAN face restoration options removed
            "ai_inpainting": self.ai_inpainting_check.isChecked(),
            "inpainting_mode": self.inpainting_mode_combo.currentText(),
            "propainter_auto_mask": self.propainter_auto_mask_check.isChecked(),
            "propainter_auto_mask_mode": {
                "All Artifacts": "all",
                "Scratches Only": "scratches",
                "Dropouts Only": "dropouts",
                "Noise Only": "noise",
            }.get(self.propainter_auto_mask_mode_combo.currentText(), "all"),
            "propainter_auto_mask_sensitivity": self.propainter_auto_mask_sensitivity_spin.value(),
            "propainter_mask_path": self.propainter_mask_edit.text(),
            "propainter_memory_preset": {
                "Auto (Detect GPU)": "auto",
                "Low (4-8GB VRAM)": "low",
                "Medium (8-12GB VRAM)": "medium",
                "High (12-16GB VRAM)": "high",
                "Ultra (24GB+ VRAM)": "ultra",
            }.get(self.propainter_memory_preset_combo.currentText(), "auto"),
            "remove_artifacts": self.artifact_removal_check.isChecked(),
            "artifact_filter": self.artifact_filter_combo.currentText(),
            "fix_chroma_shift": self.chroma_shift_check.isChecked(),
            "aspect_ratio_mode": self.aspect_ratio_combo.currentText(),
            "resize_algorithm": self.resize_algo_combo.currentText(),
            "output_mode": self.output_mode_combo.currentText(),
            "frame_format": self.frame_format_combo.currentText(),
            "resize_mode": self.resize_mode_combo.currentText(),
            "resize_width": self.resize_width_spin.value(),
            "resize_height": self.resize_height_spin.value(),
            "use_ai_upscaling": self.ai_upscaling_check.isChecked(),
            "ai_upscaling_method": self.ai_upscaling_method_combo.currentText(),
            "face_enhance": self.ai_face_enhance_check.isChecked(),
            "gfpgan_temp_dir": self.settings_manager.get("gfpgan_temp_dir", ""),
            "propainter_temp_dir": self.settings_manager.get("propainter_temp_dir", ""),
            "use_temporal_smoothing": self.temporal_smoothing_check.isChecked(),
            "temporal_strength": self.temporal_strength_combo.currentText(),
            "codec": self.codec_combo.currentText(),
            "audio": self.audio_combo.currentText(),
            "audio_codec": self.audio_codec_combo.currentText(),
            "audio_bitrate": self.audio_bitrate_combo.currentText(),
            "crf": self.crf_spinbox.value(),
            "ffmpeg_preset": self.preset_combo.currentText(),
        }

    # Processing control
    def start_processing(self):
        """Start video processing."""
        if not self.input_file:
            QMessageBox.warning(self, "No Input", "Please select an input file!")
            return

        if not self.output_file:
            QMessageBox.warning(self, "No Output", "Please select an output file!")
            return

        # Get current options
        options = self.get_current_options()
        
        # Check disk space if GFPGAN face enhancement is enabled
        if options.get("face_enhance", False):
            if not self._check_disk_space_for_gfpgan(options):
                self.console_log("❌ Processing aborted due to insufficient disk space")
                return

        # Note: RealESRGAN and RIFE auto-download their models via VapourSynth plugins
        # (vsrealesrgan and vsrife have auto_download=True built-in)
        # No manual model checking needed

        # Check if ProPainter is enabled but not configured
        if options.get("ai_inpainting", False):
            propainter_path = self.settings_manager.get("propainter_path", "")

            if not propainter_path or not Path(propainter_path).exists():
                reply = QMessageBox.question(
                    self,
                    "ProPainter Not Configured",
                    "AI Video Inpainting is enabled but ProPainter is not installed or configured.\n\n"
                    "Would you like to set it up now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.show_propainter_setup()
                    return  # Don't start processing yet
                else:
                    # Disable ProPainter for this run
                    options["ai_inpainting"] = False
                    self.console_log("⚠️ ProPainter disabled for this run")

        # Create processing thread
        # Reload settings to get latest ProPainter path (in case it was just configured)
        current_settings = self.settings_manager.load_settings()
        propainter_path = current_settings.get("propainter_path", "")

        self.console_log(
            f"[DEBUG] Loaded settings, propainter_path = '{propainter_path}'"
        )

        if propainter_path:
            self.console_log(f"Using ProPainter path: {propainter_path}")
        else:
            self.console_log("[DEBUG] No ProPainter path in settings")

        self.processing_thread = ProcessingThread(
            self.input_file,
            self.output_file,
            options,
            propainter_path=propainter_path if propainter_path else None,
            parent=self,
        )

        # Connect signals
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.eta_updated.connect(self.update_eta)
        self.processing_thread.log_updated.connect(self.console_log)
        self.processing_thread.finished_signal.connect(self.on_processing_finished)

        # Start processing
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.processing_thread.start()
        self.console_log("Processing started...")
        
        # Update pipeline label
        stages = []
        if options.get("deinterlace", True):
            stages.append("Deinterlacing")
        if options.get("denoise_enabled", False):
            stages.append("Denoising")
        if options.get("ai_upscaling", False):
            method = options.get("ai_upscale_method", "RealESRGAN").split(" ")[0]  # Extract first word
            stages.append(f"AI {method}")
        
        if stages:
            pipeline_text = " → ".join(stages) + " → Encoding"
        else:
            pipeline_text = "Encoding"
        
        self.pipeline_label.setText(f"Pipeline: {pipeline_text}")
        
        # Switch performance monitoring to processing mode (500ms updates)
        self.performance_monitor.start_monitoring(processing=True)

    def stop_processing(self):
        """Stop video processing."""
        if self.processing_thread and self.processing_thread.isRunning():
            self.console_log("Stopping processing...")
            self.processing_thread.stop()
            self.stop_button.setEnabled(False)

    def update_progress(self, progress: float):
        """Update progress bar."""
        self.progressbar.setValue(int(progress))
        self.progress_label.setText(f"{progress:.1f}%")

    def update_eta(self, eta_str: str):
        """Update ETA label."""
        self.eta_label.setText(f"ETA: {eta_str}")

    def on_processing_finished(self, success: bool, message: str):
        """Handle processing completion."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Switch performance monitoring back to idle mode (2s updates)
        self.performance_monitor.start_monitoring(processing=False)
        
        # Clear GPU metrics from progress area
        self.gpu_usage_label.setText("")
        self.gpu_vram_label.setText("")
        self.fps_label.setText("")
        self.frame_count_label.setText("")
        self.pipeline_label.setText("")  # Clear pipeline status

        if success:
            self.console_log("Processing completed successfully!")
            QMessageBox.information(self, "Success", message)
        else:
            self.console_log(f"Processing failed: {message}")
            QMessageBox.critical(self, "Error", message)

    def console_log(self, message: str):
        """Append message to console (floating window if open, otherwise buffer)."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        
        # Send to console window if open
        if self.console_window and self.console_window.isVisible():
            self.console_window.append_message(formatted)
        # Otherwise, buffer messages for when window opens
        else:
            if not hasattr(self, '_console_buffer'):
                self._console_buffer = []
            self._console_buffer.append(formatted)
            # Keep buffer size manageable
            if len(self._console_buffer) > 1000:
                self._console_buffer = self._console_buffer[-1000:]
    
    def toggle_console_window(self):
        """Open or close the floating console window."""
        if self.console_window is None or not self.console_window.isVisible():
            # Create and show console window
            self.console_window = ConsoleWindow(self)
            self.console_window.closed.connect(self._on_console_window_closed)
            
            # Flush buffered messages
            if hasattr(self, '_console_buffer'):
                for msg in self._console_buffer:
                    self.console_window.append_message(msg)
                self._console_buffer.clear()
            
            self.console_window.show()
            self.console_toggle_btn.setText("📋 Hide Console Window")
        else:
            # Close console window
            self.console_window.close()
    
    def _on_console_window_closed(self):
        """Handle console window being closed."""
        self.console_toggle_btn.setText("📋 Show Console Window")
    
    def _update_performance_labels(self, metrics: dict):
        """Update all performance labels from metrics dict."""
        # Status bar (always visible)
        self.status_cpu_label.setText(self.performance_monitor.get_cpu_label())
        self.status_ram_label.setText(self.performance_monitor.get_ram_label())
        self.status_threads_label.setText(self.performance_monitor.get_threads_label())
        self.status_cuda_label.setText(self.performance_monitor.get_cuda_status())
        
        # Enhanced progress area (GPU metrics, only when processing)
        if self.processing_thread and self.processing_thread.isRunning():
            gpu_label_text = self.performance_monitor.get_gpu_label()
            vram_label_text = self.performance_monitor.get_vram_label()
            fps_label_text = self.performance_monitor.get_fps_label()
            
            self.gpu_usage_label.setText(gpu_label_text)
            self.gpu_vram_label.setText(vram_label_text)
            self.fps_label.setText(fps_label_text)
        else:
            # Clear GPU metrics when not processing
            self.gpu_usage_label.setText("")
            self.gpu_vram_label.setText("")
            self.fps_label.setText("")

    def _get_bm3d_sigma(self) -> float:
        """Get BM3D sigma value (from preset or direct numeric)."""
        expert_mode = self.settings_manager.get("expert_mode", False)

        if expert_mode and self.bm3d_sigma.isVisible():
            return self.bm3d_sigma.value()
        else:
            strength = self.bm3d_strength.currentText()
            sigma_map = {
                "None": 0.0,
                "Light (Fast)": 3.0,
                "Medium (Slow)": 5.0,
                "Strong (Very Slow)": 8.0,
            }
            return sigma_map.get(strength, 5.0)

    # --- AI model download helpers ---

    def check_ai_models_on_startup(self):
        """Check for AI models required by saved settings and prompt to download if missing."""
        settings = self.settings_manager.load_settings()
        needed = []
        if settings.get("ai_interpolation", False):
            needed.append("rife")
        if settings.get("use_ai_upscaling", False):
            needed.append("realesrgan")
        if not needed:
            return

        missing = [m for m in needed if not model_exists(m)]
        if not missing:
            return

        reply = QMessageBox.question(
            self,
            "Download AI Models?",
            f"This installation is missing AI model files required for: {', '.join(missing)}.\n\nDownload now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.start_download_thread(missing)

    def start_download_thread(self, models: list):
        """Start a `ModelDownloadThread` (Qt) to download models and show a QProgressDialog."""
        from .model_download_thread import ModelDownloadThread
        from PySide6.QtWidgets import QProgressDialog

        # Pre-flight: determine target dir and possibly prompt for alternative if low space
        settings = self.settings_manager.load_settings()
        target_dir = Path(settings.get("ai_model_dir") or get_storage_dir())
        try:
            total, used, free = shutil.disk_usage(str(target_dir))
        except Exception:
            try:
                sd = get_storage_dir()
                total, used, free = shutil.disk_usage(str(sd))
                target_dir = sd
            except Exception:
                pass

        # Best-effort estimate of remote sizes (HEAD requests); collect per-model sizes
        per_model_sizes = {}
        estimated_bytes = 0
        try:
            registry = __import__(
                "core.ai_model_manager", fromlist=["MODEL_REGISTRY"]
            ).MODEL_REGISTRY
        except Exception:
            registry = {}

        for m in models:
            size = None
            try:
                url = registry.get(m, {}).get("url")
                if url:
                    req = urllib.request.Request(url, method="HEAD")
                    with urllib.request.urlopen(req, timeout=8) as r:
                        s = r.getheader("Content-Length")
                        if s:
                            size = int(s)
            except Exception:
                size = None
            per_model_sizes[m] = size
            if size:
                estimated_bytes += size

        # Reusable validation: require at least configured min MB OR estimated download size
        min_mb = int(settings.get("ai_model_min_free_mb", 200))
        min_bytes = min_mb * (2**20)

        def _validate_space_and_prompt(dir_path: Path) -> tuple[bool, Path]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                total2, used2, free2 = shutil.disk_usage(str(dir_path))
            except Exception:
                free2 = None

            required = max(min_bytes, estimated_bytes or 0)

            if free2 is None:
                # cannot determine free space; ask user whether to continue or choose another
                resp = QMessageBox.question(
                    self,
                    "Cannot Determine Free Space",
                    f"Cannot determine free space for {dir_path}.\n\nProceed with this folder?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if resp == QMessageBox.StandardButton.Yes:
                    return True, dir_path
                return False, dir_path

            if free2 >= required:
                return True, dir_path

            # Not enough free space: prompt user to choose different folder or continue anyway
            msg = (
                f"Selected folder {dir_path} has only {free2 // (2**20)} MB free.\n"
                f"Estimated required: {max(required // (2**20), min_mb)} MB.\n\n"
                "Choose a different folder or continue anyway."
            )
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Insufficient Free Space")
            dlg.setText(msg)
            choose_btn = dlg.addButton(
                "Choose Different Folder", QMessageBox.ButtonRole.AcceptRole
            )
            continue_btn = dlg.addButton(
                "Continue Anyway", QMessageBox.ButtonRole.DestructiveRole
            )
            dlg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            dlg.exec()

            clicked = dlg.clickedButton()
            if clicked == choose_btn:
                alt = QFileDialog.getExistingDirectory(
                    self, "Select Folder to Store AI Models", str(dir_path)
                )
                if not alt:
                    return False, dir_path
                # validate writability
                try:
                    td = Path(alt)
                    td.mkdir(parents=True, exist_ok=True)
                    tmpf = tempfile.NamedTemporaryFile(dir=str(td), delete=True)
                    tmpf.write(b"test")
                    tmpf.flush()
                    tmpf.close()
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Directory Not Writable",
                        f"Cannot write to the selected folder:\n{alt}\n\n{e}",
                    )
                    return False, dir_path

                # Save to settings and update label
                settings["ai_model_dir"] = alt
                self.settings_manager.save_settings(settings)
                self.update_ai_model_label()
                return _validate_space_and_prompt(Path(alt))
            elif clicked == continue_btn:
                return True, dir_path
            else:
                return False, dir_path

        ok, new_target = _validate_space_and_prompt(target_dir)
        if not ok:
            self.console_log(
                "Model download cancelled by user due to insufficient space."
            )
            return
        target_dir = new_target

        # Show estimated download size confirmation
        def _format_bytes(n: int) -> str:
            if n <= 0:
                return "Unknown"
            if n < 1024:
                return f"{n} B"
            kb = n / 1024
            if kb < 1024:
                return f"{kb:.1f} KB"
            mb = kb / 1024
            if mb < 1024:
                return f"{mb:.1f} MB"
            gb = mb / 1024
            return f"{gb:.2f} GB"

        est = estimated_bytes
        est_text = _format_bytes(est) if est else "Unknown"

        # Build per-model text
        per_model_lines = []
        for m in models:
            s = per_model_sizes.get(m)
            per_model_lines.append(f"{m}: {_format_bytes(s) if s else 'Unknown'}")
        models_text = "\n".join(per_model_lines)

        settings_confirm = settings.get("confirm_model_download", True)
        if settings_confirm:
            # Use a QMessageBox with a checkbox to remember the choice; show per-model sizes
            msg = QMessageBox(self)
            msg.setWindowTitle("Confirm Download")
            msg.setText(
                f"You are about to download:\n{models_text}\n\nEstimated total size: {est_text}\n\nProceed?"
            )
            msg.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            cb = QCheckBox("Remember my choice and don't ask again")
            msg.setCheckBox(cb)

            # Add a small help button explaining why sizes may be Unknown
            help_btn = msg.addButton("Why Unknown?", QMessageBox.ButtonRole.HelpRole)

            # Run dialog in a loop to handle Help button presses without closing
            while True:
                ret = msg.exec()
                clicked = msg.clickedButton()
                if clicked == help_btn:
                    QMessageBox.information(
                        self,
                        "Why sizes may be unknown",
                        "Some model hosts (Google Drive, redirects, or CDN endpoints) do not provide a reliable Content-Length header,\n"
                        "so the downloader cannot determine file size ahead of time. In those cases the dialog shows 'Unknown'.\n\n"
                        "If you prefer, you can download models manually and place them in the AI model folder.",
                    )
                    # continue loop to re-show the confirmation
                    continue
                break

            if ret != QMessageBox.StandardButton.Yes:
                self.console_log("Model download cancelled by user.")
                return
            if cb.isChecked():
                settings["confirm_model_download"] = False
                self.settings_manager.save_settings(settings)
        else:
            # User chose to skip confirmation previously
            self.console_log(
                f"Auto-confirming download for: {', '.join(models)} (user preference)"
            )

        # Create and configure Qt thread
        thread = ModelDownloadThread(models, parent=self)

        dlg = QProgressDialog("Downloading AI models...", "Cancel", 0, 100, self)
        dlg.setWindowTitle("Downloading Models")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(200)
        dlg.setAutoClose(False)

        def on_model_started(model_name: str):
            dlg.setLabelText(f"Preparing download: {model_name}")
            dlg.setValue(0)

        def on_progress(model_name: str, downloaded: int, total: int):
            if total and total > 0:
                pct = int(downloaded * 100 / total)
                dlg.setValue(pct)
                dlg.setLabelText(f"Downloading {model_name}: {pct}%")
            else:
                dlg.setValue(0)
                dlg.setLabelText(
                    f"Downloading {model_name}: {downloaded // 1024 // 1024} MiB"
                )
            # Mirror to console
            self.console_log(
                f"{model_name}: {downloaded} / {total if total > 0 else 'unknown'} bytes"
            )

        def on_error(msg: str):
            QMessageBox.critical(self, "Download Error", msg)

        def on_finished(success: bool, message: str):
            if success:
                QMessageBox.information(self, "Download Complete", message)
            else:
                if message.lower().startswith("cancel"):
                    QMessageBox.information(
                        self, "Download Cancelled", "Download was cancelled."
                    )
                else:
                    QMessageBox.critical(self, "Download Failed", message)

        thread.model_started.connect(on_model_started)
        thread.progress.connect(on_progress)
        thread.error.connect(on_error)
        thread.finished_signal.connect(on_finished)

        def on_cancel():
            thread.request_cancel()

        dlg.canceled.connect(on_cancel)

        thread.start()
        dlg.exec()
        # ensure thread stops if still running
        if thread.isRunning():
            thread.request_cancel()
            thread.wait(2000)

    def _on_ai_upscaling_toggled(self):
        """Handle AI upscaling checkbox state change."""
        enabled = self.ai_upscaling_check.isChecked()
        self.settings_manager.set("use_ai_upscaling", enabled)
        self.settings_manager.save_settings(self.settings_manager._settings)
        self.console_log(f"AI Upscaling: {'Enabled' if enabled else 'Disabled'}")

        # Update Output tab UI state
        self._update_output_resize_state()

    def _update_output_resize_state(self):
        """Update Output tab resize controls based on AI upscaling state."""
        ai_enabled = self.ai_upscaling_check.isChecked()

        if ai_enabled:
            # Show info message and disable manual resize controls
            target = self.ai_upscale_target_combo.currentText()
            info_text = f"ℹ️ AI Upscaling is enabled → Resolution controlled by 'AI Tools' tab (Target: {target})"
            self.ai_resize_info_label.setText(info_text)
            self.ai_resize_info_label.setVisible(True)

            # Disable manual resize controls (but keep aspect ratio correction available)
            self.resize_width_spin.setEnabled(False)
            self.resize_height_spin.setEnabled(False)
            self.resize_mode_combo.setEnabled(False)

            # Prevent Manual Resize mode when AI is active
            if self.aspect_ratio_combo.currentText() == "Manual Resize":
                self.aspect_ratio_combo.setCurrentText("Keep (Default)")
        else:
            # Hide info message and enable manual resize controls
            self.ai_resize_info_label.setVisible(False)
            self.resize_width_spin.setEnabled(True)
            self.resize_height_spin.setEnabled(True)
            self.resize_mode_combo.setEnabled(True)

    def _on_ai_target_changed(self, text: str):
        """Handle AI upscale target resolution change."""
        # Save the setting
        self.settings_manager.save("ai_upscale_target", text)

        # Update the info label in Output tab (only if AI upscaling is enabled)
        if self.ai_upscaling_check.isChecked():
            self._update_output_resize_state()

        if text == "Custom...":

            # Show custom resolution dialog
            from PySide6.QtWidgets import (
                QDialog,
                QVBoxLayout,
                QHBoxLayout,
                QLabel,
                QSpinBox,
                QDialogButtonBox,
            )

            dialog = QDialog(self)
            dialog.setWindowTitle("Custom AI Upscale Resolution")
            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("Enter target resolution for AI upscaling:"))

            # Width
            width_layout = QHBoxLayout()
            width_layout.addWidget(QLabel("Width:"))
            width_spin = QSpinBox()
            width_spin.setRange(64, 7680)
            width_spin.setSingleStep(2)
            width_spin.setValue(
                self.settings_manager.get("ai_upscale_custom_width", 1920)
            )
            width_layout.addWidget(width_spin)
            layout.addLayout(width_layout)

            # Height
            height_layout = QHBoxLayout()
            height_layout.addWidget(QLabel("Height:"))
            height_spin = QSpinBox()
            height_spin.setRange(64, 4320)
            height_spin.setSingleStep(2)
            height_spin.setValue(
                self.settings_manager.get("ai_upscale_custom_height", 1080)
            )
            height_layout.addWidget(height_spin)
            layout.addLayout(height_layout)

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Save custom resolution
                self.settings_manager.save(
                    "ai_upscale_custom_width", width_spin.value()
                )
                self.settings_manager.save(
                    "ai_upscale_custom_height", height_spin.value()
                )
                self.settings_manager.save(
                    "ai_upscale_target",
                    f"Custom ({width_spin.value()}×{height_spin.value()})",
                )

                # Update dropdown to show custom resolution
                current_index = self.ai_upscale_target_combo.currentIndex()
                if (
                    current_index == self.ai_upscale_target_combo.count() - 1
                ):  # "Custom..." is last
                    # Insert custom resolution before "Custom..."
                    custom_text = f"Custom ({width_spin.value()}×{height_spin.value()})"
                    self.ai_upscale_target_combo.insertItem(current_index, custom_text)
                    self.ai_upscale_target_combo.setCurrentIndex(current_index)

                self.console_log(
                    f"AI upscale target set to: {width_spin.value()}×{height_spin.value()}"
                )
            else:
                # User cancelled - revert to previous selection
                prev_target = self.settings_manager.get(
                    "ai_upscale_target", "2x Source Resolution"
                )
                self.ai_upscale_target_combo.setCurrentText(prev_target)

    def _on_upscaling_method_changed(self, text: str):
        """Handle AI upscaling method change."""
        # GFPGAN face enhancement now works independently as post-processing
        # so we no longer need to disable it based on upscaling method
        pass

    def _toggle_expert_mode(self, enabled: bool):
        """Toggle between beginner (presets) and expert (numeric) mode."""
        self.console_log(f"Expert mode: {'Enabled' if enabled else 'Disabled'}")

        # Save preference
        settings = self.settings_manager.load_settings()
        settings["expert_mode"] = enabled
        self.settings_manager.save_settings(settings)

        # Toggle visibility of controls
        # BM3D denoise
        if enabled:
            self.bm3d_strength.hide()
            self.bm3d_sigma.show()
        else:
            self.bm3d_sigma.hide()
            self.bm3d_strength.show()

        # Temporal denoise
        if enabled:
            self.temporal_denoise_combo.hide()
            self.temporal_denoise_label_expert.show()
            self.temporal_denoise_spin.show()
        else:
            self.temporal_denoise_spin.hide()
            self.temporal_denoise_label_expert.hide()
            self.temporal_denoise_combo.show()

        # Chroma denoise
        if enabled:
            self.chroma_denoise_combo.hide()
            self.chroma_denoise_label_expert.show()
            self.chroma_denoise_spin.show()
        else:
            self.chroma_denoise_spin.hide()
            self.chroma_denoise_label_expert.hide()
            self.chroma_denoise_combo.show()

        # Debanding
        if enabled:
            self.deband_strength_combo.hide()
            self.deband_label_expert.show()
            self.deband_range_spin.show()
        else:
            self.deband_range_spin.hide()
            self.deband_label_expert.hide()
            self.deband_strength_combo.show()

        # Show message
        if enabled:
            QMessageBox.information(
                self,
                "Expert Mode Enabled",
                "Expert mode is now active!\n\n"
                "Restoration and Advanced tabs now show numeric controls:\n"
                "• BM3D: Direct sigma value (0.0-10.0)\n"
                "• Temporal Denoise: Numeric strength (0.0-10.0)\n"
                "• Chroma Denoise: Numeric strength (0.0-10.0)\n"
                "• Debanding: Range value (5-30)\n\n"
                "Use these for fine-tuned control over restoration filters.",
            )
        else:
            QMessageBox.information(
                self,
                "Beginner Mode",
                "Beginner mode is now active.\n\n"
                "Using simple preset options:\n"
                "• Light, Medium, Strong\n"
                "• Easy to understand and use\n\n"
                "Perfect for quick restoration without technical knowledge.",
            )

    # Capture methods (placeholders)
    def refresh_capture_devices(self):
        """Refresh capture device list."""
        self.console_log("Refreshing capture devices...")
        try:
            from capture import CaptureDeviceManager

            manager = CaptureDeviceManager()
            devices = manager.refresh_devices()

            self.video_device_combo.clear()
            self.audio_device_combo.clear()

            for device in devices:
                # CaptureDevice is a dataclass, use dot notation
                self.video_device_combo.addItem(device.name)
                # Note: Audio device detection not yet implemented in manager

            self.console_log(f"Found {len(devices)} capture devices")
        except Exception as e:
            self.console_log(f"Device detection error: {e}")

    def select_capture_output(self):
        """Select capture output folder."""
        # Start from current folder or default to user's Videos folder
        start_dir = (
            self.capture_output_folder
            if self.capture_output_folder
            else str(Path.home() / "Videos")
        )

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Capture Output Folder",
            start_dir,
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder:
            self.capture_output_folder = folder
            self.capture_output_label.setText(folder)
            self.console_log(f"Capture output folder: {folder}")

            # Save to settings
            settings = self.settings_manager.load_settings()
            settings["capture_output_folder"] = folder
            self.settings_manager.save_settings(settings)

            # Show disk space info
            try:
                import shutil

                total, used, free = shutil.disk_usage(folder)
                free_gb = free // (2**30)
                self.console_log(f"Available space: {free_gb} GB")

                # Update disk space label
                if free_gb < 50:
                    self.disk_space_label.setStyleSheet(
                        "border: 1px solid gray; padding: 5px; background-color: #4a2a2a; color: #ff8888;"
                    )
                    self.disk_space_label.setText(f"Disk Space: {free_gb} GB (LOW!)")
                elif free_gb < 100:
                    self.disk_space_label.setStyleSheet(
                        "border: 1px solid gray; padding: 5px; background-color: #4a3a2a; color: #ffaa88;"
                    )
                    self.disk_space_label.setText(f"Disk Space: {free_gb} GB")
                else:
                    self.disk_space_label.setStyleSheet(
                        "border: 1px solid gray; padding: 5px; background-color: #2a2a2a;"
                    )
                    self.disk_space_label.setText(f"Disk Space: {free_gb} GB")
            except Exception:
                pass

    def refresh_capture_devices(self):
        """Refresh and populate capture device lists."""
        self.console_log("Refreshing capture devices...")
        
        try:
            # Try to detect real hardware first
            self.capture_devices = self.capture_device_manager.refresh_devices(use_mock=False)
            self.audio_devices = self.capture_device_manager.get_audio_devices()
            
            if not self.capture_devices:
                # No real hardware found, use mock devices
                self.console_log("No capture hardware detected. Using mock devices for testing.")
                self.capture_devices = self.capture_device_manager.refresh_devices(use_mock=True)
            else:
                self.console_log(f"✓ Detected {len(self.capture_devices)} capture device(s)")
            
            # Clear and populate video device combo
            self.video_device_combo.clear()
            for device in self.capture_devices:
                self.video_device_combo.addItem(device.name, device)
            
            # Clear and populate audio device combo
            self.audio_device_combo.clear()
            self.audio_device_combo.addItem("Auto (Match Video Device)", None)
            for audio_dev in self.audio_devices:
                self.audio_device_combo.addItem(audio_dev['name'], audio_dev)
            
            if self.capture_devices:
                self.console_log("Device list updated successfully")
            
        except Exception as e:
            self.console_log(f"⚠ Device detection error: {str(e)}")
            self.console_log("Using mock devices as fallback")
            # Use mock devices as fallback
            try:
                self.capture_devices = self.capture_device_manager.refresh_devices(use_mock=True)
                self.video_device_combo.clear()
                for device in self.capture_devices:
                    self.video_device_combo.addItem(device.name, device)
            except Exception as e2:
                self.console_log(f"✗ Failed to load mock devices: {str(e2)}")
                QMessageBox.critical(
                    self,
                    "Device Detection Failed",
                    f"Failed to detect or load capture devices:\n{str(e)}\n\nPlease check:\n"
                    "• FFmpeg is installed and in PATH\n"
                    "• Capture hardware is connected\n"
                    "• Device drivers are installed"
                )

    def _on_tab_changed(self, index: int):
        """Handle tab change - auto-refresh capture devices when Capture tab is opened."""
        # Check if Capture tab (index 0) was selected and devices not loaded yet
        if index == 0 and not self.capture_devices_loaded:
            self.console_log("Capture tab opened - refreshing devices...")
            try:
                self.refresh_capture_devices()
                self.capture_devices_loaded = True
            except Exception as e:
                self.console_log(f"⚠ Could not load capture devices: {e}")

    def _apply_capture_preset(self, preset_name: str):
        """Apply capture preset configuration."""
        if preset_name == "Custom":
            return  # Do nothing for custom

        # Define presets
        presets = {
            "VHS NTSC (Composite)": {
                "codec": 0,  # HuffYUV
                "resolution": 0,  # 720x480
                "framerate": 0,  # 29.97
                "video_input": 1,  # Composite
                "audio_input": 0,  # Auto
            },
            "VHS PAL (Composite)": {
                "codec": 0,  # HuffYUV
                "resolution": 1,  # 720x576
                "framerate": 1,  # 25 fps
                "video_input": 1,  # Composite
                "audio_input": 0,  # Auto
            },
            "S-VHS NTSC (S-Video)": {
                "codec": 0,  # HuffYUV
                "resolution": 0,  # 720x480
                "framerate": 0,  # 29.97
                "video_input": 2,  # S-Video
                "audio_input": 0,  # Auto
            },
            "S-VHS PAL (S-Video)": {
                "codec": 0,  # HuffYUV
                "resolution": 1,  # 720x576
                "framerate": 1,  # 25 fps
                "video_input": 2,  # S-Video
                "audio_input": 0,  # Auto
            },
            "DV NTSC (FireWire)": {
                "codec": 0,  # HuffYUV (or use copy for DV)
                "resolution": 0,  # 720x480
                "framerate": 0,  # 29.97
                "video_input": 0,  # Auto
                "audio_input": 0,  # Auto
            },
            "DV PAL (FireWire)": {
                "codec": 0,  # HuffYUV
                "resolution": 1,  # 720x576
                "framerate": 1,  # 25 fps
                "video_input": 0,  # Auto
                "audio_input": 0,  # Auto
            },
            "Component NTSC (YPbPr)": {
                "codec": 0,  # HuffYUV
                "resolution": 0,  # 720x480
                "framerate": 0,  # 29.97
                "video_input": 3,  # Component
                "audio_input": 0,  # Auto
            },
            "Component PAL (YPbPr)": {
                "codec": 0,  # HuffYUV
                "resolution": 1,  # 720x576
                "framerate": 1,  # 25 fps
                "video_input": 3,  # Component
                "audio_input": 0,  # Auto
            },
        }

        preset = presets.get(preset_name)
        if not preset:
            return

        # Block signals temporarily to avoid triggering preset change
        self.capture_preset_combo.blockSignals(True)

        # Apply preset settings
        self.capture_codec.setCurrentIndex(preset["codec"])
        self.capture_resolution.setCurrentIndex(preset["resolution"])
        self.capture_framerate.setCurrentIndex(preset["framerate"])
        self.video_input_combo.setCurrentIndex(preset["video_input"])
        self.audio_input_combo.setCurrentIndex(preset["audio_input"])

        # Re-enable signals
        self.capture_preset_combo.blockSignals(False)

        self.console_log(f"Applied capture preset: {preset_name}")

    def _save_custom_capture_preset(self):
        """Save current capture settings as custom preset."""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(
            self, "Save Capture Preset", "Enter preset name:", text="My Custom Preset"
        )

        if not ok or not name:
            return

        # Get current settings
        preset_data = {
            "codec": self.capture_codec.currentIndex(),
            "resolution": self.capture_resolution.currentIndex(),
            "framerate": self.capture_framerate.currentIndex(),
            "video_input": self.video_input_combo.currentIndex(),
            "audio_input": self.audio_input_combo.currentIndex(),
        }

        # Load existing custom presets from settings
        settings = self.settings_manager.load_settings()
        custom_presets = settings.get("capture_custom_presets", {})
        custom_presets[name] = preset_data
        settings["capture_custom_presets"] = custom_presets
        self.settings_manager.save_settings(settings)

        # Add to dropdown if not already there
        if self.capture_preset_combo.findText(name) == -1:
            self.capture_preset_combo.addItem(name)

        # Select the saved preset
        self.capture_preset_combo.setCurrentText(name)

        self.console_log(f"Saved capture preset: {name}")
        QMessageBox.information(
            self, "Preset Saved", f"Capture preset '{name}' saved successfully!"
        )

    def _browse_propainter_mask(self):
        """Browse for ProPainter mask file or folder."""
        # Ask user if they want file or folder
        reply = QMessageBox.question(
            self,
            "Select Mask Type",
            "Do you have a single mask video file?\n\n"
            "Yes = Select mask video file\n"
            "No = Select folder containing mask image frames",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Select mask video file
            file, _ = QFileDialog.getOpenFileName(
                self,
                "Select Mask Video File",
                "",
                "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)",
            )
            if file:
                self.propainter_mask_edit.setText(file)
                self.console_log(f"Mask file selected: {file}")
        else:
            # Select folder with mask frames
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Folder with Mask Frames",
                "",
                QFileDialog.Option.ShowDirsOnly,
            )
            if folder:
                self.propainter_mask_edit.setText(folder)
                self.console_log(f"Mask folder selected: {folder}")

    def _update_dropped_frames(self, count: int):
        """Update dropped frames display (slot for monitor thread signal)."""
        if count == 0:
            self.dropped_frames_label.setText("Dropped Frames: 0")
            self.dropped_frames_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #1a3d1a;"
            )
        elif count < 10:
            self.dropped_frames_label.setText(f"Dropped Frames: {count} (OK)")
            self.dropped_frames_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #3d3d1a; color: yellow;"
            )
        else:
            self.dropped_frames_label.setText(f"Dropped Frames: {count} (WARNING!)")
            self.dropped_frames_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #4a2a2a; color: #ff8888;"
            )

    def _update_disk_space_monitor(self, free_gb: int):
        """Update disk space display during capture (slot for monitor thread signal)."""
        if free_gb < 50:
            self.disk_space_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #4a2a2a; color: #ff8888;"
            )
            self.disk_space_label.setText(f"Disk Space: {free_gb} GB (LOW!)")
        elif free_gb < 100:
            self.disk_space_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #4a3a2a; color: #ffaa88;"
            )
            self.disk_space_label.setText(f"Disk Space: {free_gb} GB")
        else:
            self.disk_space_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px; background-color: #2a2a2a;"
            )
            self.disk_space_label.setText(f"Disk Space: {free_gb} GB")

    def start_capture(self):
        """Start video capture."""
        # Validate settings
        if not self.capture_output_folder:
            QMessageBox.warning(
                self,
                "No Output Folder",
                "Please select a capture output folder first!\n\n"
                "Use the Browse button to choose where captured files will be saved.",
            )
            return

        video_device = self.video_device_combo.currentText()
        if not video_device or video_device == "No devices found":
            QMessageBox.warning(
                self,
                "No Device Selected",
                "Please select a video capture device!\n\n"
                "Click 'Refresh Devices' to scan for connected capture hardware.",
            )
            return

        # Generate output filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        codec = (
            self.capture_codec.currentText().split()[0].lower()
        )  # Extract codec name

        # Determine file extension based on codec
        extension_map = {"huffyuv": ".avi", "ffv1": ".mkv", "lagarith": ".avi"}
        extension = extension_map.get(codec, ".avi")

        output_file = (
            Path(self.capture_output_folder) / f"capture_{timestamp}{extension}"
        )

        # Get input sources for confirmation dialog
        video_input_display = self.video_input_combo.currentText()
        audio_input_display = self.audio_input_combo.currentText()

        # Confirm start
        reply = QMessageBox.question(
            self,
            "Start Capture?",
            f"Ready to capture from:\n{video_device}\n\n"
            f"Video Input: {video_input_display}\n"
            f"Audio Input: {audio_input_display}\n"
            f"Output file:\n{output_file}\n\n"
            f"Format: {codec.upper()}{extension}\n"
            f"Resolution: {self.capture_resolution.currentText()}\n"
            f"Frame rate: {self.capture_framerate.currentText()}\n\n"
            "Click 'Stop Capture' when finished.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Start capture
        try:
            from capture import AnalogCaptureEngine, AnalogCaptureSettings

            # Build settings
            resolution = self.capture_resolution.currentText().split()[
                0
            ]  # Extract resolution
            framerate = self.capture_framerate.currentText().split()[0]  # Extract fps
            audio_device = self.audio_device_combo.currentText()

            # Get video input selection
            video_input_text = self.video_input_combo.currentText()
            video_input_pin = None
            if video_input_text != "Auto (Default)":
                # Map selection to pin number
                video_input_map = {
                    "Composite (RCA)": 0,
                    "S-Video (Y/C)": 1,
                    "Component (YPbPr)": 2,
                    "HDMI/Digital": 4,
                }
                video_input_pin = video_input_map.get(video_input_text)

            # Get audio input selection
            audio_input_text = self.audio_input_combo.currentText()
            audio_input_pin = None
            if audio_input_text != "Auto (Default)":
                # Map selection to pin number
                audio_input_map = {
                    "Line In": 0,
                    "Microphone": 1,
                    "CD Audio": 2,
                    "Video Audio": 3,
                }
                audio_input_pin = audio_input_map.get(audio_input_text)

            settings = AnalogCaptureSettings(
                device_name=f"video={video_device}",
                resolution=resolution,
                framerate=framerate,
                codec=codec,
                audio_device=(
                    audio_device
                    if audio_device and audio_device != "No devices found"
                    else None
                ),
                video_input_pin=video_input_pin,  # Crossbar video input selection
                audio_input_pin=audio_input_pin,  # Crossbar audio input selection
            )

            # Create capture engine
            engine = AnalogCaptureEngine()
            success = engine.start_capture(
                settings, str(output_file), log_callback=self.console_log
            )

            if success:
                self.capture_thread = engine
                self.start_capture_btn.setEnabled(False)
                self.stop_capture_btn.setEnabled(True)
                self.capture_status_label.setText(
                    f"Status: CAPTURING to {output_file.name}"
                )
                self.capture_status_label.setStyleSheet(
                    "border: 1px solid green; padding: 5px; background-color: #1a3d1a; color: lime;"
                )

                # Store output file for auto-processing
                self._last_captured_file = str(output_file)

                # Start capture monitoring thread
                self.capture_monitor_thread = CaptureMonitorThread(
                    engine.process, self.capture_output_folder
                )
                self.capture_monitor_thread.dropped_frames_updated.connect(
                    self._update_dropped_frames
                )
                self.capture_monitor_thread.disk_space_updated.connect(
                    self._update_disk_space_monitor
                )
                self.capture_monitor_thread.start()
                self.console_log(
                    "Capture monitoring started (dropped frames + disk space)"
                )

                # Start live preview if enabled
                if self.live_preview_check.isChecked():
                    try:
                        self.live_preview_window = LivePreviewWindow(self)
                        self.live_preview_window.start_preview(
                            f"video={video_device}", resolution, framerate
                        )
                        self.live_preview_window.show()
                        self.console_log("Live preview window opened")
                    except Exception as preview_error:
                        self.console_log(
                            f"Warning: Could not start live preview: {preview_error}"
                        )
                        # Non-fatal error, continue capture
            else:
                QMessageBox.critical(
                    self,
                    "Capture Failed",
                    "Failed to start capture. Check console for details.",
                )

        except Exception as e:
            self.console_log(f"Capture error: {e}")
            import traceback

            self.console_log(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Capture error: {str(e)}")

    def stop_capture(self):
        """Stop video capture."""
        if not self.capture_thread:
            return

        try:
            self.capture_thread.stop_capture(log_callback=self.console_log)

            self.start_capture_btn.setEnabled(True)
            self.stop_capture_btn.setEnabled(False)
            self.capture_status_label.setText("Status: Capture stopped")
            self.capture_status_label.setStyleSheet(
                "border: 1px solid gray; padding: 5px;"
            )

            # Stop capture monitor thread
            if self.capture_monitor_thread:
                self.capture_monitor_thread.stop()
                self.capture_monitor_thread.wait()
                self.capture_monitor_thread = None
                self.console_log("Capture monitoring stopped")

            # Close live preview window
            if self.live_preview_window:
                self.live_preview_window.stop_preview()
                self.live_preview_window.close()
                self.live_preview_window = None
                self.console_log("Live preview closed")

            # Ask if user wants to process the captured file
            if (
                hasattr(self, "_last_captured_file")
                and self.auto_process_capture.isChecked()
            ):
                reply = QMessageBox.question(
                    self,
                    "Process Captured Video?",
                    f"Capture complete!\n\n"
                    f"File: {Path(self._last_captured_file).name}\n\n"
                    "Would you like to process this video now with restoration filters?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Load captured file as input
                    self.input_file = self._last_captured_file
                    self.input_label.setText(Path(self._last_captured_file).name)

                    # Auto-suggest output
                    output_path = Path(self._last_captured_file)
                    output = output_path.parent / f"{output_path.stem}_restored.mp4"
                    self.output_file = str(output)
                    self.output_label.setText(output.name)

                    # Switch to Input tab
                    self.tabs.setCurrentIndex(1)  # Input tab
                    self.console_log(
                        f"\nReady to process captured file: {self._last_captured_file}"
                    )

            self.capture_thread = None

        except Exception as e:
            self.console_log(f"Stop capture error: {e}")

    # Detection
    def detect_field_order(self):
        """Detect field order of current input."""
        if not self.input_file:
            QMessageBox.warning(self, "No Input", "Please select an input file first!")
            return

        self.console_log("Detecting field order...")
        try:
            analyzer = VideoAnalyzer()
            field_order = analyzer.detect_field_order(self.input_file)
            self.field_order_combo.setCurrentText(field_order)
            self.console_log(f"Detected: {field_order}")
            QMessageBox.information(
                self, "Detection Complete", f"Field Order: {field_order}"
            )
        except Exception as e:
            self.console_log(f"Detection error: {e}")
            QMessageBox.warning(self, "Detection Failed", str(e))

    # Theatre Mode handlers
    def _on_theatre_mode_toggled(self, state):
        """Enable/disable Theatre Mode controls based on checkbox state."""
        enabled = (state == Qt.CheckState.Checked.value)
        
        # Enable/disable all Theatre Mode controls
        self.chroma_correction_check.setEnabled(enabled)
        self.chroma_preset_combo.setEnabled(enabled)
        self.chroma_shift_x_spin.setEnabled(enabled)
        self.chroma_shift_y_spin.setEnabled(enabled)
        self.deinterlace_variant_combo.setEnabled(enabled)
        self.analyze_tape_btn.setEnabled(enabled)
        self.level_adjustment_check.setEnabled(enabled)
        self.black_point_spin.setEnabled(enabled)
        self.white_point_spin.setEnabled(enabled)
        self.saturation_boost_spin.setEnabled(enabled)
        
        # QTGMC controls remain active - both modes use same deinterlacing quality settings
        # Theatre Mode flow: Chroma Correction → QTGMC → Level Adjustment
        # Standard Mode flow: QTGMC only
        
        if enabled:
            self.console_log("✅ Theatre Mode ENABLED - Hardware-accurate analog processing")
            self.console_log("   Flow: Chroma Correction → QTGMC → Level Adjustment")
            self.console_log("   (Using QTGMC quality settings from 'Deinterlacing' section below)")
        else:
            self.console_log("❌ Theatre Mode DISABLED - Standard v3.3 processing")
            self.console_log("   Flow: QTGMC only")
    
    def _on_chroma_preset_changed(self, text: str):
        """Update chroma shift values when preset changes."""
        # Map display names to preset keys
        preset_key_map = {
            "LaserDisc (0.25px)": "laserdisc",
            "VHS Composite (0.5px)": "vhs_composite",
            "S-VHS (0.15px)": "svhs",
            "Hi8 (0.2px)": "hi8",
            "Betamax (0.3px)": "betamax",
            "Custom": "custom"
        }
        
        preset_key = preset_key_map.get(text, "laserdisc")
        
        if preset_key != "custom":
            # Load preset values from chroma_correction module
            try:
                from core.chroma_correction import get_preset
                preset_values = get_preset(preset_key)
                self.chroma_shift_x_spin.setValue(preset_values.get("shift_x_px", 0.25))
                self.chroma_shift_y_spin.setValue(preset_values.get("shift_y_px", 0.0))
                self.console_log(f"✓ Loaded {text} chroma preset")
            except Exception as e:
                self.console_log(f"⚠ Failed to load preset: {e}")
    
    def _on_analyze_tape(self):
        """Run Theatre Mode auto-profiling on current input."""
        if not self.input_file:
            QMessageBox.warning(self, "No Input", "Please select an input file first!")
            return
        
        self.console_log("Analyzing tape (Theatre Mode auto-profiling)...")
        self.analyze_tape_btn.setEnabled(False)
        self.analyze_tape_btn.setText("Analyzing...")
        
        try:
            from core.theatre_mode import TheatreModeProcessor
            from PySide6.QtWidgets import QProgressDialog
            
            # Show progress dialog
            progress = QProgressDialog("Analyzing tape...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(10)
            QApplication.processEvents()
            
            self.console_log(f"Starting analysis of: {self.input_file}")
            
            # Define progress callback
            def update_progress(pct, msg):
                progress.setValue(int(pct))
                progress.setLabelText(msg)
                QApplication.processEvents()
            
            # Run analysis (uses vspipe like normal processing)
            processor = TheatreModeProcessor()
            profile = processor.analyze_tape(
                self.input_file,
                progress_callback=update_progress
            )
            
            progress.setValue(100)
            self.console_log("Analysis complete, processing results...")
            
            if profile:
                # Apply detected settings
                self.chroma_shift_x_spin.setValue(float(profile.chroma_shift_x))
                self.chroma_shift_y_spin.setValue(float(profile.chroma_shift_y))
                self.black_point_spin.setValue(float(profile.black_point))
                self.white_point_spin.setValue(float(profile.white_point))
                self.saturation_boost_spin.setValue(float(profile.saturation_boost))
                
                # Update field order if detected
                if profile.field_order and str(profile.field_order) != "Unknown":
                    self.field_order_combo.setCurrentText(str(profile.field_order))
                
                # Set preset to Custom
                self.chroma_preset_combo.setCurrentText("Custom")
                
                # Show results
                notes = profile.notes if hasattr(profile, 'notes') and profile.notes else []
                if isinstance(notes, str):
                    notes = [notes]
                notes_text = "\n• ".join(str(n) for n in notes) if notes else "No specific recommendations"
                
                result_msg = (
                    "Theatre Mode Auto-Profiling Complete!\n\n"
                    "Detected Settings:\n"
                    f"• Field Order: {str(profile.field_order)}\n"
                    f"• Chroma Shift X: {float(profile.chroma_shift_x):.2f}px\n"
                    f"• Chroma Shift Y: {float(profile.chroma_shift_y):.2f}px\n"
                    f"• Black Point: {float(profile.black_point):.2f}\n"
                    f"• White Point: {float(profile.white_point):.2f}\n"
                    f"• Saturation Boost: {float(profile.saturation_boost):.1f}x\n\n"
                    "Recommendations:\n"
                    f"• {notes_text}\n\n"
                    "Settings have been applied to the UI."
                )
                
                QMessageBox.information(self, "Analysis Complete", result_msg)
                self.console_log("✓ Theatre Mode auto-profiling complete")
            else:
                self.console_log("✗ Analysis returned None")
                QMessageBox.warning(self, "Analysis Failed", "Could not analyze tape. Check console for details.")
                
        except RuntimeError as e:
            # vspipe not found or failed
            self.console_log(f"✗ Analysis error: {e}")
            msg = (
                f"Auto-profiling failed: {str(e)}\n\n"
                "Options:\n"
                "1. Use manual Theatre Mode settings (presets work great!)\n"
                "2. Ensure VapourSynth is installed and vspipe.exe is on PATH\n\n"
                "Note: Theatre Mode processing still works - only auto-profiling needs vspipe."
            )
            QMessageBox.warning(self, "Analysis Failed", msg)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.console_log(f"✗ Analysis error: {e}")
            self.console_log(f"Traceback: {error_details}")
            QMessageBox.warning(self, "Analysis Failed", f"Error: {str(e)}\n\nCheck console for details.")
        finally:
            self.analyze_tape_btn.setEnabled(True)
            self.analyze_tape_btn.setText("Analyze Tape (Auto-Profile)")

    # ProPainter setup
    def show_propainter_setup(self):
        """Show ProPainter setup wizard."""
        from gui.propainter_setup_dialog import ProPainterSetupDialog

        dialog = ProPainterSetupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = dialog.get_propainter_path()
            if path:
                # Save to settings
                settings = self.settings_manager.load_settings()
                settings["propainter_path"] = str(path)
                self.settings_manager.save_settings(settings)
                # Reload to update cache
                self.settings_manager.load_settings()

                self.console_log(f"✅ ProPainter path configured: {path}")
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    f"ProPainter path saved!\n\n"
                    f"You can now use AI Video Inpainting in the Advanced tab.",
                )

    # Removed show_ai_model_storage() - now handled by AI Model Manager dialog

    def show_settings_dialog(self):
        """Show settings dialog with UI and performance options."""
        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QDialogButtonBox,
            QLabel,
            QSpinBox,
            QLineEdit,
            QPushButton,
            QFileDialog,
            QGroupBox,
            QDoubleSpinBox,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)

        settings = self.settings_manager.load_settings()

        # UI Settings Group
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout()

        current_font = int(settings.get("ui_font_size", 11))
        ui_layout.addWidget(QLabel("UI font size (points):"))
        font_spin = QSpinBox()
        font_spin.setRange(8, 32)
        font_spin.setValue(current_font)
        ui_layout.addWidget(font_spin)

        ui_layout.addWidget(QLabel("UI theme:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["System Default", "Dark Mode", "Light Mode"])
        current_theme = settings.get("ui_theme", "System Default")
        theme_combo.setCurrentText(current_theme)
        theme_combo.setToolTip(
            "System Default: Use OS theme | Dark Mode: Dark UI | Light Mode: Light UI"
        )
        ui_layout.addWidget(theme_combo)

        tooltips_check = QCheckBox("Enable Tooltips")
        tooltips_check.setChecked(settings.get("tooltips_enabled", True))
        tooltips_check.setToolTip("Show helpful tooltips when hovering over controls")
        ui_layout.addWidget(tooltips_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        # AI Model Settings Group
        ai_group = QGroupBox("AI Models")
        ai_layout = QVBoxLayout()

        current_min = int(settings.get("ai_model_min_free_mb", 200))
        ai_layout.addWidget(QLabel("Minimum free space for AI models (MB):"))
        spin = QSpinBox()
        spin.setRange(50, 102400)
        spin.setValue(current_min)
        ai_layout.addWidget(spin)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Performance/Cache Settings Group
        try:
            from core.config import get_config

            cache_config = get_config()

            perf_group = QGroupBox("Performance & Cache")
            perf_layout = QVBoxLayout()

            # Cache directory
            perf_layout.addWidget(QLabel("Cache directory:"))
            cache_dir_layout = QHBoxLayout()
            cache_dir_edit = QLineEdit(str(cache_config.get_cache_dir()))
            cache_dir_edit.setToolTip(
                "Directory for storing processed frame cache (speeds up re-processing)"
            )
            cache_dir_layout.addWidget(cache_dir_edit)

            cache_browse_btn = QPushButton("Browse...")

            def browse_cache_dir():
                dir_path = QFileDialog.getExistingDirectory(
                    dialog, "Select Cache Directory", cache_dir_edit.text()
                )
                if dir_path:
                    cache_dir_edit.setText(dir_path)

            cache_browse_btn.clicked.connect(browse_cache_dir)
            cache_dir_layout.addWidget(cache_browse_btn)
            perf_layout.addLayout(cache_dir_layout)

            # Cache max size
            perf_layout.addWidget(QLabel("Cache max size (GB):"))
            cache_size_spin = QDoubleSpinBox()
            cache_size_spin.setRange(1.0, 1000.0)
            cache_size_spin.setValue(cache_config.get_cache_max_size_gb())
            cache_size_spin.setToolTip(
                "Maximum disk space to use for cache (old files auto-deleted)"
            )
            perf_layout.addWidget(cache_size_spin)

            # Checkpoint directory
            perf_layout.addWidget(QLabel("Checkpoint directory:"))
            checkpoint_dir_layout = QHBoxLayout()
            checkpoint_dir_edit = QLineEdit(str(cache_config.get_checkpoint_dir()))
            checkpoint_dir_edit.setToolTip(
                "Directory for storing processing checkpoints (enables resume)"
            )
            checkpoint_dir_layout.addWidget(checkpoint_dir_edit)

            checkpoint_browse_btn = QPushButton("Browse...")

            def browse_checkpoint_dir():
                dir_path = QFileDialog.getExistingDirectory(
                    dialog, "Select Checkpoint Directory", checkpoint_dir_edit.text()
                )
                if dir_path:
                    checkpoint_dir_edit.setText(dir_path)

            checkpoint_browse_btn.clicked.connect(browse_checkpoint_dir)
            checkpoint_dir_layout.addWidget(checkpoint_browse_btn)
            perf_layout.addLayout(checkpoint_dir_layout)

            # GFPGAN Temp Directory
            perf_layout.addWidget(QLabel("\nGFPGAN Temp directory:"))
            gfpgan_temp_layout = QHBoxLayout()
            current_gfpgan_temp = self.settings_manager.get("gfpgan_temp_dir", "")
            gfpgan_temp_edit = QLineEdit(current_gfpgan_temp if current_gfpgan_temp else "Default (System Temp)")
            gfpgan_temp_edit.setToolTip(
                "Custom directory for GFPGAN temporary frame extraction.\n"
                "GFPGAN extracts all frames to disk before processing.\n"
                "For an 18-minute HD video, this can be 60-100GB!\n\n"
                "Select a drive with sufficient free space (D:\\, E:\\, etc.)\n"
                "Leave empty to use system temp directory."
            )
            gfpgan_temp_layout.addWidget(gfpgan_temp_edit)

            gfpgan_browse_btn = QPushButton("Browse...")

            def browse_gfpgan_temp():
                dir_path = QFileDialog.getExistingDirectory(
                    dialog, "Select GFPGAN Temp Directory", 
                    gfpgan_temp_edit.text() if gfpgan_temp_edit.text() != "Default (System Temp)" else ""
                )
                if dir_path:
                    gfpgan_temp_edit.setText(dir_path)
                    self.settings_manager.save("gfpgan_temp_dir", dir_path)
                    self.gfpgan_temp_path_label.setText(dir_path)
                    self.gfpgan_temp_path_label.setStyleSheet("color: black;")
                    self.console_log(f"GFPGAN temp directory set to: {dir_path}")

            gfpgan_browse_btn.clicked.connect(browse_gfpgan_temp)
            gfpgan_temp_layout.addWidget(gfpgan_browse_btn)
            
            gfpgan_clear_btn = QPushButton("Clear")
            def clear_gfpgan_temp():
                gfpgan_temp_edit.setText("Default (System Temp)")
                self.settings_manager.save("gfpgan_temp_dir", "")
                self.gfpgan_temp_path_label.setText("Default (System Temp)")
                self.gfpgan_temp_path_label.setStyleSheet("color: gray; font-style: italic;")
                self.console_log("GFPGAN temp directory reset to default")
            
            gfpgan_clear_btn.clicked.connect(clear_gfpgan_temp)
            gfpgan_temp_layout.addWidget(gfpgan_clear_btn)
            perf_layout.addLayout(gfpgan_temp_layout)

            # ProPainter Temp Directory
            perf_layout.addWidget(QLabel("\nProPainter Temp directory:"))
            propainter_temp_layout = QHBoxLayout()
            current_propainter_temp = self.settings_manager.get("propainter_temp_dir", "")
            propainter_temp_edit = QLineEdit(current_propainter_temp if current_propainter_temp else "Default (System Temp)")
            propainter_temp_edit.setToolTip(
                "Custom directory for ProPainter temporary processing files.\n"
                "ProPainter generates large intermediate files during processing.\n"
                "For a 1-hour video, this can be 30-100GB!\n\n"
                "Select a drive with sufficient free space (D:\\, E:\\, etc.)\n"
                "Leave empty to use system temp directory."
            )
            propainter_temp_layout.addWidget(propainter_temp_edit)

            propainter_browse_btn = QPushButton("Browse...")

            def browse_propainter_temp():
                dir_path = QFileDialog.getExistingDirectory(
                    dialog, "Select ProPainter Temp Directory", 
                    propainter_temp_edit.text() if propainter_temp_edit.text() != "Default (System Temp)" else ""
                )
                if dir_path:
                    propainter_temp_edit.setText(dir_path)
                    self.settings_manager.save("propainter_temp_dir", dir_path)
                    self.propainter_temp_path_label.setText(dir_path)
                    self.propainter_temp_path_label.setStyleSheet("color: black;")
                    self.console_log(f"ProPainter temp directory set to: {dir_path}")

            propainter_browse_btn.clicked.connect(browse_propainter_temp)
            propainter_temp_layout.addWidget(propainter_browse_btn)
            
            propainter_clear_btn = QPushButton("Clear")
            def clear_propainter_temp():
                propainter_temp_edit.setText("Default (System Temp)")
                self.settings_manager.save("propainter_temp_dir", "")
                self.propainter_temp_path_label.setText("Default (System Temp)")
                self.propainter_temp_path_label.setStyleSheet("color: gray; font-style: italic;")
                self.console_log("ProPainter temp directory reset to default")
            
            propainter_clear_btn.clicked.connect(clear_propainter_temp)
            propainter_temp_layout.addWidget(propainter_clear_btn)
            perf_layout.addLayout(propainter_temp_layout)

            perf_group.setLayout(perf_layout)
            layout.addWidget(perf_group)

        except ImportError:
            # Cache config not available
            cache_config = None
            cache_dir_edit = None
            cache_size_spin = None
            checkpoint_dir_edit = None

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save UI settings
            settings["ai_model_min_free_mb"] = int(spin.value())
            settings["ui_font_size"] = int(font_spin.value())
            settings["ui_theme"] = theme_combo.currentText()
            settings["tooltips_enabled"] = tooltips_check.isChecked()
            self.settings_manager.save_settings(settings)

            # Save cache settings
            if cache_config is not None:
                cache_config.set_cache_dir(cache_dir_edit.text(), silent=True)
                cache_config.set_cache_max_size_gb(cache_size_spin.value())
                cache_config.set_checkpoint_dir(checkpoint_dir_edit.text(), silent=True)

            # Apply UI changes immediately
            try:
                self.apply_ui_font_size()
                self.apply_ui_theme()
                self.apply_tooltips()
            except Exception:
                pass

            QMessageBox.information(
                self,
                "Saved",
                "Settings saved successfully!\n\n"
                f"UI: {font_spin.value()}pt font, {theme_combo.currentText()} theme\n"
                f"AI: {spin.value()} MB min free space\n"
                + (
                    f"Cache: {cache_dir_edit.text()} ({cache_size_spin.value():.1f} GB max)"
                    if cache_config
                    else ""
                ),
            )

    def show_ai_model_manager(self):
        """Show the AI Model Manager dialog (v3.0)."""
        try:
            dialog = AIModelDialog(self)
            result = dialog.exec()

            # If model directory changed, update settings
            if result == QDialog.DialogCode.Accepted:
                new_model_root = dialog.get_model_root()
                settings = self.settings_manager.load_settings()
                settings["ai_model_dir"] = new_model_root
                self.settings_manager.save_settings(settings)
                self.console_log(f"AI model directory set to: {new_model_root}")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to open AI Model Manager:\n{e}"
            )
            self.console_log(f"AI Model Manager error: {e}")

    # Removed show_model_downloader() - now handled by AI Model Manager dialog

    # Batch processing (placeholders)
    def add_to_batch(self):
        """Add current job to batch queue."""
        self.console_log("Batch queue feature coming soon...")

    def start_batch_processing(self):
        """Start batch queue processing."""
        self.console_log("Batch processing feature coming soon...")

    # Presets
    def save_preset(self):
        """Save current settings as preset."""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Save Preset", "Preset Name:")
        if ok and name:
            options = self.get_current_options()
            self.preset_manager.add_preset(name, options)
            self.console_log(f"Preset '{name}' saved")

    def load_preset(self):
        """Load preset."""
        names = self.preset_manager.get_preset_names()
        if not names:
            QMessageBox.information(self, "No Presets", "No saved presets found!")
            return

        # Show selection dialog (simplified)
        self.console_log("Preset loading feature coming soon...")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Advanced Tape Restorer v3.1",
            "<h3>Advanced Tape Restorer v3.1</h3>"
            "<p>Professional Video Restoration & Capture Suite</p>"
            "<p><b>Core Technologies:</b></p>"
            "<ul>"
            "<li>Python 3.13 (PSF License)</li>"
            "<li>PySide6/Qt6 (LGPL v3) - GUI Framework</li>"
            "<li>VapourSynth (LGPL v2.1+) - Video Processing</li>"
            "<li>FFmpeg (LGPL v2.1+) - Video Encoding</li>"
            "<li>DirectShow (Windows API) - Capture</li>"
            "</ul>"
            "<p><b>Video Processing Plugins:</b></p>"
            "<ul>"
            "<li>QTGMC (GPL v3) - Deinterlacing</li>"
            "<li>BM3D (MIT) - Noise Reduction</li>"
            "<li>RIFE (MIT) - AI Frame Interpolation</li>"
            "<li>RealESRGAN (BSD 3-Clause) - AI Upscaling</li>"
            "<li>f3kdb (GPL v3) - Debanding</li>"
            "<li>FFMS2, L-SMASH-Works (MIT) - Source Filters</li>"
            "</ul>"
            "<p><b>AI Features (Optional):</b></p>"
            "<ul>"
            "<li>ProPainter (NTU S-Lab License - Non-Commercial) - AI Inpainting</li>"
            "</ul>"
            "<p><b>Note on model size estimation:</b> Some model hosts (for example, Google Drive, certain redirects, or CDN endpoints) do not provide a reliable Content-Length header. When that happens the application cannot estimate file sizes ahead of download and will display 'Unknown' in the download confirmation. You can always download models manually and place them in the AI model folder; see `docs/AI_FEATURES_COMPLETE.md` for details and canonical URLs.</p>"
            "<p><b>GPL/LGPL Compliance:</b></p>"
            "<p>This application complies with all open-source licenses. GPL-licensed plugins "
            "are installed separately by users and called as external processes. LGPL components "
            "are dynamically linked or used as external executables. No GPL code is bundled in "
            "this executable.</p>"
            "<p><b>Commercial Distribution:</b></p>"
            "<p>This software may be legally distributed commercially. See THIRD_PARTY_LICENSES.md "
            "for complete license compliance information and acknowledgments.</p>"
            "<p style='margin-top: 10px;'><i>Thank you to all open-source developers who make "
            "projects like this possible! 🙏</i></p>"
            "<p style='margin-top: 10px; font-size: small;'>Version 2.0 | November 2025</p>",
        )
    
    def _on_auto_inference_changed(self, state):
        """Handle auto inference mode checkbox change."""
        is_auto = state == Qt.CheckState.Checked.value
        self.settings_manager.save("auto_inference_mode", is_auto)
        self.inference_mode_combo.setEnabled(not is_auto)
        self._update_inference_recommendation()
    
    def _on_manual_inference_changed(self, index):
        """Handle manual inference mode selection."""
        mode_map = {
            0: "pytorch_fp32",
            1: "pytorch_fp16",
            2: "onnx_fp16",
            3: "onnx_int8",
            4: "cpu_only"
        }
        mode_value = mode_map.get(index, "pytorch_fp32")
        self.settings_manager.save("manual_inference_mode", mode_value)
        
        # Update auto mode selector override
        mode_enum_map = {
            "pytorch_fp32": InferenceMode.PYTORCH_FP32,
            "pytorch_fp16": InferenceMode.PYTORCH_FP16,
            "onnx_fp16": InferenceMode.ONNX_FP16,
            "onnx_int8": InferenceMode.ONNX_INT8,
            "cpu_only": InferenceMode.CPU_ONLY
        }
        self.auto_mode_selector.set_manual_override(mode_enum_map.get(mode_value))
        self._update_inference_recommendation()
    
    def _update_inference_recommendation(self):
        """Update the inference mode recommendation label."""
        try:
            if self.auto_inference_check.isChecked():
                # Get auto-detected mode
                result = self.auto_mode_selector.detect_best_mode(
                    target_model="realesrgan",  # Use common model for general recommendation
                    force_auto=True
                )
                
                self.inference_recommendation_label.setText(
                    f"✓ Auto Mode: {result.explanation}"
                )
                
                # Show warning if needed
                if result.override_warning:
                    self.inference_recommendation_label.setText(
                        f"⚠️ {result.override_warning}"
                    )
                    self.inference_recommendation_label.setStyleSheet(
                        "color: #FF6B35; padding: 5px; font-style: italic;"
                    )
                else:
                    self.inference_recommendation_label.setStyleSheet(
                        "color: #0052cc; padding: 5px; font-style: italic;"
                    )
                
                # Update GPU info
                gpu_manager = self.auto_mode_selector.multi_gpu
                best_gpu = gpu_manager.get_best_ai_gpu()
                if best_gpu:
                    self.gpu_info_label.setText(
                        f"🎮 {best_gpu.name} ({best_gpu.memory_available}MB VRAM available)"
                    )
                else:
                    self.gpu_info_label.setText("⚠️ No GPU detected")
            else:
                # Manual mode selected
                mode_index = self.inference_mode_combo.currentIndex()
                mode_names = [
                    InferenceMode.PYTORCH_FP32,
                    InferenceMode.PYTORCH_FP16,
                    InferenceMode.ONNX_FP16,
                    InferenceMode.ONNX_INT8,
                    InferenceMode.CPU_ONLY
                ]
                selected_mode = mode_names[mode_index]
                
                info = self.auto_mode_selector.get_mode_info(selected_mode)
                self.inference_recommendation_label.setText(
                    f"Manual: {info.get('description', 'Custom mode selected')}"
                )
                self.inference_recommendation_label.setStyleSheet(
                    "color: #666; padding: 5px; font-style: italic;"
                )
        except Exception as e:
            self.inference_recommendation_label.setText(f"Error detecting mode: {e}")
            self.inference_recommendation_label.setStyleSheet("color: red;")
    
    def _show_inference_mode_details(self):
        """Show detailed comparison dialog for inference modes."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Inference Mode Comparison")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h3>AI Inference Mode Comparison</h3>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Table with mode details
        text = QTextEdit()
        text.setReadOnly(True)
        
        html = "<table border='1' cellpadding='8' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr style='background-color: #f0f0f0;'>"
        html += "<th>Mode</th><th>Quality</th><th>Speed</th><th>VRAM Usage</th><th>Compatibility</th>"
        html += "</tr>"
        
        modes = [
            InferenceMode.PYTORCH_FP32,
            InferenceMode.PYTORCH_FP16,
            InferenceMode.ONNX_FP16,
            InferenceMode.ONNX_INT8,
            InferenceMode.CPU_ONLY
        ]
        
        for mode in modes:
            info = self.auto_mode_selector.get_mode_info(mode)
            html += f"<tr>"
            html += f"<td><b>{mode.value.upper().replace('_', ' ')}</b></td>"
            html += f"<td>{info.get('quality', 'N/A')}</td>"
            html += f"<td>{info.get('speed', 'N/A')}</td>"
            html += f"<td>{info.get('vram_usage', 'N/A')}</td>"
            html += f"<td>{info.get('compatibility', 'N/A')}</td>"
            html += f"</tr>"
            html += f"<tr><td colspan='5' style='font-size: 11px; padding-left: 20px;'>{info.get('description', '')}</td></tr>"
        
        html += "</table>"
        
        # Add recommendations
        html += "<br><h4>Recommendations:</h4>"
        html += "<ul>"
        html += "<li><b>8GB+ VRAM:</b> PyTorch FP32 for best quality</li>"
        html += "<li><b>6-8GB VRAM:</b> PyTorch FP16 or ONNX FP16 for great quality + speed</li>"
        html += "<li><b>4-6GB VRAM:</b> ONNX FP16 to prevent OOM errors</li>"
        html += "<li><b>2-4GB VRAM:</b> ONNX INT8 (quality loss acceptable for stability)</li>"
        html += "<li><b>Integrated/No GPU:</b> CPU Only (slow but functional)</li>"
        html += "</ul>"
        
        text.setHtml(html)
        layout.addWidget(text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    def _check_disk_space_for_gfpgan(self, options):
        """Check if sufficient disk space is available for GFPGAN frame extraction."""
        try:
            from core.disk_space_manager import (
                estimate_frame_extraction_size,
                check_space_available,
                get_temp_directory_with_space,
                format_bytes
            )
            
            # Estimate required space
            estimated_bytes = estimate_frame_extraction_size(self.input_file)
            
            # Check custom temp dir or system temp
            temp_dir = options.get("gfpgan_temp_dir") or None
            
            available, msg = check_space_available(estimated_bytes, temp_dir)
            
            if not available:
                # Show error and try to find alternative
                alt_dir, alt_msg = get_temp_directory_with_space(estimated_bytes, temp_dir)
                
                if alt_dir:
                    reply = QMessageBox.question(
                        self,
                        "Disk Space Warning",
                        f"{msg}\n\nAlternative location found:\n{alt_msg}\n\n"
                        f"Use alternative location?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # Update temp directory setting
                        self.settings_manager.set("gfpgan_temp_dir", str(alt_dir))
                        self.gfpgan_temp_dir_edit.setText(str(alt_dir))
                        self.console_log(f"✓ Using alternative temp directory: {alt_dir}")
                    else:
                        # User declined - abort processing
                        return False
                else:
                    QMessageBox.critical(
                        self,
                        "Insufficient Disk Space",
                        f"{msg}\n\n{alt_msg}\n\n"
                        f"Processing cannot continue."
                    )
                    return False
            
            elif "Warning" in msg:
                # Show warning but allow continuing
                reply = QMessageBox.question(
                    self,
                    "Low Disk Space Warning",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return False
            
            else:
                # Sufficient space - log it
                self.console_log(f"✓ Disk space check passed - {format_bytes(estimated_bytes)} required")
            
            return True
            
        except Exception as e:
            self.console_log(f"⚠ Disk space check failed: {e}")
            # Don't block processing on check failure
            return True

    def _browse_gfpgan_temp_dir(self):
        """Browse for custom GFPGAN temporary directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select GFPGAN Temporary Folder",
            self.settings_manager.get("gfpgan_temp_dir", ""),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.gfpgan_temp_path_label.setText(folder)
            self.gfpgan_temp_path_label.setStyleSheet("color: black;")
            self.settings_manager.save("gfpgan_temp_dir", folder)
            self.console_log(f"GFPGAN temp directory set to: {folder}")
    
    def _clear_gfpgan_temp_dir(self):
        """Clear custom GFPGAN temp directory and use default."""
        self.gfpgan_temp_path_label.setText("Default (System Temp)")
        self.gfpgan_temp_path_label.setStyleSheet("color: gray; font-style: italic;")
        self.settings_manager.save("gfpgan_temp_dir", "")
        self.console_log("GFPGAN temp directory reset to default")
    
    def _check_for_incomplete_checkpoints(self):
        """Check for incomplete GFPGAN checkpoints on startup and offer to resume."""
        try:
            from gui.checkpoint_resume_dialog import CheckpointResumeDialog
            
            # Get checkpoint directory
            localappdata = os.getenv('LOCALAPPDATA', os.path.expanduser('~/.local/share'))
            checkpoint_dir = Path(localappdata) / 'Advanced_Tape_Restorer' / 'checkpoints'
            
            if not checkpoint_dir.exists():
                return
            
            # Check if there are any checkpoints
            checkpoint_files = list(checkpoint_dir.glob("*.checkpoint.json"))
            if not checkpoint_files:
                return
            
            # Check if any are incomplete (paused/running)
            has_incomplete = False
            for checkpoint_file in checkpoint_files:
                try:
                    import json
                    with open(checkpoint_file, 'r') as f:
                        data = json.load(f)
                    
                    status = data.get('status', '')
                    if status in ['paused', 'running']:
                        has_incomplete = True
                        break
                except Exception:
                    continue
            
            if not has_incomplete:
                return
            
            # Show dialog
            self.console_log("Found interrupted jobs - showing resume dialog...")
            
            dialog = CheckpointResumeDialog(checkpoint_dir, parent=self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                action, job_data = dialog.get_result()
                
                if action == 'resume' and job_data:
                    self.console_log(f"▶️ Resume requested for job: {job_data['job_id']}")
                    self.console_log("   Load the original video file and click Start Processing")
                    self.console_log("   The job will automatically resume from where it stopped")
                    
                    QMessageBox.information(
                        self,
                        "Resume Job",
                        f"To resume job '{job_data['job_id']}':\n\n"
                        f"1. Load the original video file\n"
                        f"2. Enable GFPGAN in AI Tools tab\n"
                        f"3. Click Start Processing\n\n"
                        f"The job will automatically resume from frame {job_data['data']['current_frame']}"
                    )
        
        except Exception as e:
            self.console_log(f"⚠ Checkpoint check failed: {e}")
            # Don't block startup on checkpoint check failure