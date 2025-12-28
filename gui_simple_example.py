"""
Advanced Tape Restorer v3.0 - SIMPLIFIED GUI EXAMPLE

⚠️ NOTE: This is a REFERENCE IMPLEMENTATION / EXAMPLE GUI created by Gemini Pro.
⚠️ This file is NOT used by the actual application!

The actual GUI used by the application is located at: gui/main_window.py

This simplified GUI demonstrates:
- Basic 3-tab interface (Restoration, Capture, Batch)
- Threading architecture for non-blocking processing
- Progress reporting via signals/slots
- Integration with core.py and capture.py modules

This file is preserved as a reference for understanding the basic structure,
but the full-featured application uses the more complex GUI in the gui/ package.

Created by: Gemini Pro (v3.0 development)
Status: Reference/Example only - NOT ACTIVE
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QProgressBar,
    QTextEdit,
    QFileDialog,
)
from PySide6.QtCore import QThread, Signal, QObject

from core import VideoProcessor
from capture import CaptureDeviceManager


class Worker(QObject):
    """
    A worker object that runs a long task in a separate thread.
    """

    finished = Signal()
    error = Signal(str)
    log = Signal(str)
    progress = Signal(int, int)  # current_frame, total_frames

    def __init__(
        self, processor, input_file, output_file, restoration_options, encoding_options
    ):
        super().__init__()
        self.processor = processor
        self.input_file = input_file
        self.output_file = output_file
        self.restoration_options = restoration_options
        self.encoding_options = encoding_options

    def run(self):
        """Runs the video processing task."""
        try:
            # The callback will emit the progress signal
            def progress_callback(current, total):
                self.progress.emit(current, total)

            self.processor.process_video(
                self.input_file,
                self.output_file,
                self.restoration_options,
                self.encoding_options,
                progress_callback,
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class RestorationTab(QWidget):
    """UI for the main video restoration functionality."""

    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- File Selection ---
        file_group = QGroupBox("1. File Selection")
        file_layout = QFormLayout()
        self.input_file_edit = QLineEdit()
        self.output_file_edit = QLineEdit()
        browse_input_btn = QPushButton("Browse...")
        browse_output_btn = QPushButton("Browse...")
        browse_input_btn.clicked.connect(self.browse_input)
        browse_output_btn.clicked.connect(self.browse_output)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_file_edit)
        input_layout.addWidget(browse_input_btn)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(browse_output_btn)

        file_layout.addRow("Input Video:", input_layout)
        file_layout.addRow("Output Video:", output_layout)
        file_group.setLayout(file_layout)

        # --- Settings ---
        settings_group = QGroupBox("2. Restoration & Encoding Settings")
        settings_layout = QFormLayout()
        self.qtgmc_preset_combo = QComboBox()
        self.qtgmc_preset_combo.addItems(["Slow", "Medium", "Fast", "Placebo"])
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(
            ["H.264 (libx264)", "H.265 (libx265)", "ProRes", "FFV1 (Lossless)"]
        )
        settings_layout.addRow("Deinterlace (QTGMC):", self.qtgmc_preset_combo)
        settings_layout.addRow("Output Codec:", self.codec_combo)
        settings_group.setLayout(settings_layout)

        # --- Processing ---
        process_group = QGroupBox("3. Process")
        process_layout = QVBoxLayout()

        # Button layout
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.start_processing)
        self.stop_button = QPushButton("Stop Processing")
        self.stop_button.clicked.connect(self.request_stop)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        self.progress_bar = QProgressBar()
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        process_layout.addLayout(button_layout)
        process_layout.addWidget(self.progress_bar)
        process_layout.addWidget(self.log_edit)
        process_group.setLayout(process_layout)

        layout.addWidget(file_group)
        layout.addWidget(settings_group)
        layout.addWidget(process_group)
        layout.addStretch()

    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input Video")
        if file_path:
            self.input_file_edit.setText(file_path)

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output Video")
        if file_path:
            self.output_file_edit.setText(file_path)

    def start_processing(self):
        """
        Gathers settings, creates a worker and a thread, and starts processing.
        """
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()

        if not input_file or not output_file:
            self.log_edit.append(
                "<b>ERROR:</b> Please select both an input and an output file."
            )
            return

        # Disable UI elements
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

        # Gather settings from UI
        restoration_options = {"qtgmc_preset": self.qtgmc_preset_combo.currentText()}
        encoding_options = {"codec": self.codec_combo.currentText()}

        # Create thread and worker
        self.thread = QThread()
        self.worker = Worker(
            self.processor,
            input_file,
            output_file,
            restoration_options,
            encoding_options,
        )
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.on_processing_error)
        self.worker.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_processing_finished)

        # Start the thread
        self.thread.start()
        self.log_edit.append(f"<i>Starting processing for: {input_file}</i>")

    def request_stop(self):
        """Requests the processing to stop."""
        self.log_edit.append("<i>Sending stop request...</i>")
        self.processor.request_stop()
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stopping...")

    def update_progress(self, current_frame, total_frames):
        """Updates the progress bar."""
        if total_frames > 0:
            percentage = int((current_frame / total_frames) * 100)
            self.progress_bar.setValue(percentage)

    def on_processing_finished(self):
        if self.processor._stop_requested.is_set():
            self.log_edit.append("<b>Processing was cancelled by the user.</b>")
        else:
            self.log_edit.append("<b>Processing finished successfully!</b>")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop Processing")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(
            100 if not self.processor._stop_requested.is_set() else 0
        )
        self.processor.cleanup()  # Reset the stop flag

    def on_processing_error(self, error_message):
        self.log_edit.append(f"<b>ERROR during processing:</b> {error_message}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop Processing")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)


class CaptureTab(QWidget):
    """UI for the video capture functionality."""

    def __init__(self, capture_manager):
        super().__init__()
        self.capture_manager = capture_manager
        self.init_ui()
        self.refresh_devices()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Device Selection ---
        device_group = QGroupBox("1. Capture Device")
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_devices)
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(refresh_btn)
        device_group.setLayout(device_layout)

        # --- Capture Settings ---
        settings_group = QGroupBox("2. Capture Settings")
        settings_layout = QFormLayout()
        self.capture_codec_combo = QComboBox()
        self.capture_codec_combo.addItems(
            ["FFV1 (Lossless)", "HuffYUV (Lossless)", "Uncompressed"]
        )
        settings_layout.addRow("Capture Codec:", self.capture_codec_combo)
        settings_group.setLayout(settings_layout)

        # --- Controls ---
        controls_group = QGroupBox("3. Controls")
        controls_layout = QHBoxLayout()
        self.start_capture_btn = QPushButton("Start Capture")
        self.stop_capture_btn = QPushButton("Stop Capture")
        self.stop_capture_btn.setEnabled(False)
        controls_layout.addWidget(self.start_capture_btn)
        controls_layout.addWidget(self.stop_capture_btn)
        controls_group.setLayout(controls_layout)

        layout.addWidget(device_group)
        layout.addWidget(settings_group)
        layout.addWidget(controls_group)
        layout.addStretch()

    def refresh_devices(self):
        """Refreshes the list of available capture devices."""
        self.device_combo.clear()
        try:
            devices = self.capture_manager.refresh_devices()
            if not devices:
                self.device_combo.addItem("No capture devices found")
                self.device_combo.setEnabled(False)
            else:
                for device in devices:
                    self.device_combo.addItem(device.name, userData=device)
                self.device_combo.setEnabled(True)
        except Exception as e:
            self.device_combo.addItem(f"Error: {e}")
            self.device_combo.setEnabled(False)


class BatchTab(QWidget):
    """UI for batch processing. (Placeholder)"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QTextEdit(
            "Batch processing interface will be implemented here.\n\n- Add multiple files to a queue.\n- Configure settings for all or individual files.\n- Start the batch and let it run overnight."
        )
        label.setReadOnly(True)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    """The main application window."""

    def __init__(self):
        super().__init__()

        # --- Initialize Backend ---
        self.processor = VideoProcessor()
        self.capture_manager = CaptureDeviceManager()

        # --- Main Window Setup ---
        self.setWindowTitle("Advanced Tape Restorer v3.0")
        self.setGeometry(100, 100, 800, 600)

        # --- Create Tabs ---
        self.tabs = QTabWidget()
        self.restoration_tab = RestorationTab(self.processor)
        self.capture_tab = CaptureTab(self.capture_manager)
        self.batch_tab = BatchTab()

        self.tabs.addTab(self.restoration_tab, "Restoration")
        self.tabs.addTab(self.capture_tab, "Capture")
        self.tabs.addTab(self.batch_tab, "Batch Processing")

        self.setCentralWidget(self.tabs)

        # --- Status Bar ---
        self.statusBar().showMessage(
            "Ready. Please select a video to restore or a device to capture from."
        )

        # --- Check Prerequisites ---
        try:
            self.processor.check_prerequisites()
            self.statusBar().showMessage(
                "Ready. All dependencies (FFmpeg, VapourSynth) found.", 5000
            )
        except RuntimeError as e:
            self.statusBar().showMessage(f"Warning: {e}")
            # In a real app, you'd show a more prominent error dialog here.
            self.restoration_tab.start_button.setEnabled(False)
            self.restoration_tab.log_edit.setText(
                f"ERROR: Could not initialize. Please ensure prerequisites are installed.\n\nDetails: {e}"
            )
