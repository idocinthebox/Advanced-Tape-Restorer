"""
ProPainter Setup Wizard - Guides user through external installation
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QFont
import subprocess
import sys
import shutil
from pathlib import Path


class ProPainterSetupDialog(QDialog):
    """Dialog to help users install and configure ProPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ProPainter Setup Assistant")
        self.setMinimumSize(700, 500)
        self.setMaximumSize(900, 700)  # Ensure it fits on screen

        self.propainter_path = None
        self.setup_ui()
        self.check_existing_installation()

    def setup_ui(self):
        """Build the setup wizard UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("ProPainter AI Video Inpainting Setup")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Status
        self.status_label = QLabel("Checking for existing installation...")
        layout.addWidget(self.status_label)

        # Installation info
        info_group = QGroupBox("What is ProPainter?")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "ProPainter is an AI-powered video inpainting tool that can:\n"
            "• Remove scratches, dust, and tape damage\n"
            "• Fill missing or corrupted areas\n"
            "• Remove unwanted objects (date stamps, logos)\n"
            "• Restore heavily degraded footage\n\n"
            "⚠️ ProPainter is a separate tool that must be installed manually.\n"
            "📦 Size: ~3 GB (models + dependencies)\n"
            "⚖️ License: NTU S-Lab License 1.0 - Non-commercial use only\n\n"
            "📄 By installing ProPainter, you agree to:\n"
            "   • Obtain it from the official GitHub repository\n"
            "   • Review and accept the NTU S-Lab License terms\n"
            "   • Use it only for non-commercial purposes\n"
            "   • This application does NOT redistribute ProPainter"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Requirements check
        req_group = QGroupBox("Requirements Check")
        req_layout = QVBoxLayout()

        self.conda_check = QLabel("❓ Conda/Miniconda: Checking...")
        self.git_check = QLabel("❓ Git: Checking...")
        self.gpu_check = QLabel("❓ GPU (8GB+ VRAM): Checking...")

        req_layout.addWidget(self.conda_check)
        req_layout.addWidget(self.git_check)
        req_layout.addWidget(self.gpu_check)
        req_group.setLayout(req_layout)
        layout.addWidget(req_group)

        # Installation path
        path_group = QGroupBox("Installation Location")
        path_layout = QVBoxLayout()

        path_help = QLabel(
            "Select the ProPainter CODE directory (the one containing inference_propainter.py):\n"
            "After git clone, this is usually the NESTED ProPainter folder.\n"
            "Example: C:\\ProPainterInstall\\ProPainter (NOT C:\\ProPainterInstall)"
        )
        path_layout.addWidget(path_help)

        path_input_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(
            "C:/ProPainterInstall/ProPainter (the nested folder with inference_propainter.py)"
        )
        path_input_layout.addWidget(self.path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_path)
        path_input_layout.addWidget(browse_btn)

        path_layout.addLayout(path_input_layout)

        self.path_status = QLabel("")
        path_layout.addWidget(self.path_status)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # Instructions
        instructions_group = QGroupBox("Installation Instructions")
        instructions_layout = QVBoxLayout()

        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setMaximumHeight(200)
        self.instructions_text.setPlainText(self.get_installation_instructions())
        instructions_layout.addWidget(self.instructions_text)

        copy_btn = QPushButton("📋 Copy Commands to Clipboard")
        copy_btn.clicked.connect(self.copy_commands)
        instructions_layout.addWidget(copy_btn)

        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)

        # Quick actions
        actions_layout = QHBoxLayout()

        open_terminal_btn = QPushButton("🖥️ Open Terminal Here")
        open_terminal_btn.clicked.connect(self.open_terminal)
        open_terminal_btn.setToolTip("Opens PowerShell in your selected directory")
        actions_layout.addWidget(open_terminal_btn)

        open_github_btn = QPushButton("🌐 Open GitHub Page")
        open_github_btn.clicked.connect(self.open_github)
        actions_layout.addWidget(open_github_btn)

        layout.addLayout(actions_layout)

        # Bottom buttons
        button_layout = QHBoxLayout()

        test_btn = QPushButton("🧪 Test Installation")
        test_btn.clicked.connect(self.test_installation)
        button_layout.addWidget(test_btn)

        button_layout.addStretch()

        skip_btn = QPushButton("Skip (Install Later)")
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)

        save_btn = QPushButton("Save Path && Close")
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def check_existing_installation(self):
        """Check for existing ProPainter installation."""
        # Check common locations
        common_paths = [
            Path.home() / "ProPainter",
            Path.home() / "Documents" / "ProPainter",
            Path("C:/ProPainter"),
        ]

        for path in common_paths:
            if path.exists() and (path / "inference_propainter.py").exists():
                self.path_edit.setText(str(path))
                self.propainter_path = path
                self.status_label.setText("✅ Found existing ProPainter installation!")
                self.path_status.setText("✅ Valid ProPainter directory")
                break
        else:
            self.status_label.setText(
                "⚠️ ProPainter not found. Manual installation required."
            )

        # Check requirements
        self.check_requirements()

    def check_requirements(self):
        """Check if required tools are installed."""
        # Check conda (optional)
        try:
            result = subprocess.run(
                ["conda", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.conda_check.setText(f"✅ Conda: {result.stdout.strip()}")
            else:
                self.conda_check.setText("⚠️ Conda: Not found (optional, can use venv)")
        except BaseException:
            # Check if we have Python venv as alternative
            try:
                # Use proper Python executable (handle frozen case)
                python_exe = shutil.which('python') or shutil.which('python3')
                if not python_exe and not getattr(sys, 'frozen', False):
                    python_exe = sys.executable
                
                if python_exe:
                    py_result = subprocess.run(
                        [python_exe, "-m", "venv", "--help"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if py_result.returncode == 0:
                        self.conda_check.setText(
                            "✅ Python venv available (conda not needed)"
                        )
                    else:
                        self.conda_check.setText("⚠️ Conda: Not found (can use Python venv)")
                else:
                    self.conda_check.setText(
                        "⚠️ Running from compiled exe - use conda or install Python"
                    )
            except BaseException:
                self.conda_check.setText(
                    "⚠️ Conda: Not installed (can use Python venv instead)"
                )

        # Check git
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.git_check.setText(f"✅ Git: {result.stdout.strip()}")
            else:
                self.git_check.setText("❌ Git: Not found")
        except BaseException:
            self.git_check.setText("❌ Git: Not installed (required for cloning)")

        # Check GPU
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                ),
            )
            if result.returncode == 0:
                vram = result.stdout.strip().split()[0]
                vram_gb = int(vram) / 1024
                if vram_gb >= 8:
                    self.gpu_check.setText(
                        f"✅ GPU: {vram_gb:.1f} GB VRAM (sufficient)"
                    )
                else:
                    self.gpu_check.setText(
                        f"⚠️ GPU: {vram_gb:.1f} GB VRAM (8GB+ recommended)"
                    )
            else:
                self.gpu_check.setText("⚠️ GPU: NVIDIA GPU not detected")
        except BaseException:
            self.gpu_check.setText("⚠️ GPU: Cannot detect (nvidia-smi not available)")

    def browse_path(self):
        """Browse for ProPainter directory."""
        path = QFileDialog.getExistingDirectory(
            self, "Select ProPainter Installation Directory", str(Path.home())
        )

        if path:
            self.path_edit.setText(path)
            self.validate_path(Path(path))

    def validate_path(self, path: Path):
        """Validate the selected path."""
        if not path.exists():
            self.path_status.setText(
                f"📁 Directory doesn't exist yet (will be created during installation)"
            )
            self.propainter_path = None
            return False

        # Check if user selected parent directory instead of nested ProPainter directory
        if (
            not (path / "inference_propainter.py").exists()
            and (path / "ProPainter" / "inference_propainter.py").exists()
        ):
            nested_path = path / "ProPainter"
            self.path_status.setText(
                f"⚠️ Please select the nested ProPainter folder: {nested_path}"
            )
            self.path_edit.setText(str(nested_path))
            # Automatically switch to the correct path
            return self.validate_path(nested_path)

        # Check both possible locations (direct or nested)
        if (path / "inference_propainter.py").exists() or (
            path / "ProPainter" / "inference_propainter.py"
        ).exists():
            weights_dir = path / "weights"
            if weights_dir.exists():
                weights = list(weights_dir.glob("*.pth"))
                if len(weights) >= 3:
                    self.path_status.setText(
                        f"✅ Valid ProPainter installation ({len(weights)} model files found)"
                    )
                    self.propainter_path = path
                    return True
                else:
                    self.path_status.setText(
                        f"⚠️ ProPainter found but models missing (download weights)"
                    )
                    self.propainter_path = path
                    return True
            else:
                self.path_status.setText(
                    "⚠️ ProPainter found but weights folder missing"
                )
                self.propainter_path = path
                return True
        else:
            self.path_status.setText(
                "❌ Not a valid ProPainter directory (inference_propainter.py not found)"
            )
            self.propainter_path = None
            return False

    def get_installation_instructions(self) -> str:
        """Get installation command text."""
        return """Step-by-Step Installation:

=== OPTION A: Using Python venv (Recommended - No Conda Required) ===

1. Open PowerShell or Command Prompt

2. Choose installation location:
   We recommend: C:\\ProPainterInstall

3. Clone ProPainter repository:
   cd C:\\ProPainterInstall
   git clone https://github.com/sczhou/ProPainter.git
   cd ProPainter

   IMPORTANT: After git clone, you'll be in C:\\ProPainterInstall\\ProPainter
   This is the directory containing inference_propainter.py
   Verify with: dir (you should see inference_propainter.py)

4. Create Python virtual environment:
   python -m venv venv
   .\\venv\\Scripts\\activate    # Windows
   # source venv/bin/activate   # Linux/Mac

5. Install PyTorch (GPU version):
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

6. Install dependencies:
   If requirements.txt exists:
   pip install -r requirements.txt

   Otherwise install manually:
   pip install opencv-python pillow numpy scipy scikit-image imageio imageio-ffmpeg
   pip install tqdm tensorboard pyyaml einops timm kornia accelerate requests matplotlib

7. Test installation:
   python inference_propainter.py --help

   (If successful, you'll see usage instructions)

=== OPTION B: Using Conda (If you prefer) ===

1-3. Same as above

4. Create conda environment:
   conda create -n propainter python=3.8 -y
   conda activate propainter

5-7. Same as Option A (steps 5-7)

Model weights will auto-download on first run (~500MB).

For detailed instructions, visit:
https://github.com/sczhou/ProPainter
"""

    def copy_commands(self):
        """Copy installation commands to clipboard."""
        # Provide both options, user can choose
        commands = r"""# OPTION A: Using Python venv (No Conda Required)
# Run these commands from your desired installation directory (e.g., C:\ProPainter)
git clone https://github.com/sczhou/ProPainter.git
cd ProPainter
python -m venv venv
.\\venv\\Scripts\\activate
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install opencv-python pillow numpy scipy scikit-image imageio imageio-ffmpeg tqdm tensorboard pyyaml einops timm kornia accelerate requests matplotlib
cd ProPainter
python inference_propainter.py --help

# OPTION B: Using Conda
git clone https://github.com/sczhou/ProPainter.git
cd ProPainter
conda create -n propainter python=3.8 -y
conda activate propainter
pip install opencv-python pillow numpy scipy scikit-image imageio imageio-ffmpeg tqdm tensorboard pyyaml einops timm kornia accelerate requests matplotlib
python inference_propainter.py --help"""

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(commands)

        QMessageBox.information(
            self,
            "Commands Copied",
            "Installation commands copied to clipboard!\n\n"
            "Paste them into your terminal to install ProPainter.",
        )

    def open_terminal(self):
        """Open terminal in the selected directory."""
        path = self.path_edit.text()
        if not path:
            path = str(Path.home())

        if sys.platform == "win32":
            # Open PowerShell
            subprocess.Popen(["powershell", "-NoExit", "-Command", f"cd '{path}'"])
        else:
            # Linux/Mac terminal
            subprocess.Popen(["x-terminal-emulator"], cwd=path)

    def open_github(self):
        """Open ProPainter GitHub page."""
        import webbrowser

        webbrowser.open("https://github.com/sczhou/ProPainter")

    def test_installation(self):
        """Test if ProPainter is properly installed."""
        path = self.path_edit.text()
        if not path:
            QMessageBox.warning(self, "No Path", "Please select a directory first.")
            return

        path = Path(path)

        # Validate path
        if not self.validate_path(path):
            QMessageBox.warning(
                self,
                "Invalid Directory",
                "The selected directory doesn't contain a valid ProPainter installation.\n\n"
                "Make sure inference_propainter.py exists in this directory.",
            )
            return

        # The path should already be validated and point to the correct directory
        # But double-check just in case
        test_path = path
        if not (path / "inference_propainter.py").exists():
            if (path / "ProPainter" / "inference_propainter.py").exists():
                test_path = path / "ProPainter"
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Path",
                    "Could not find inference_propainter.py in the selected directory or its ProPainter subdirectory.",
                )
                return

        # Look for venv in parent directory or current directory
        python_exe = "python"
        venv_locations = [
            path / "venv" / "Scripts" / "python.exe",  # venv in parent
            test_path / "venv" / "Scripts" / "python.exe",  # venv in ProPainter dir
            path.parent / "venv" / "Scripts" / "python.exe",  # venv one level up
        ]

        for venv_python in venv_locations:
            if venv_python.exists():
                python_exe = str(venv_python)
                break

        try:
            # Use longer timeout - first run may download model weights
            result = subprocess.run(
                [python_exe, "inference_propainter.py", "--help"],
                cwd=str(test_path),
                capture_output=True,
                text=True,
                timeout=60,  # Increased from 10s for weight downloads
            )

            if result.returncode == 0:
                QMessageBox.information(
                    self,
                    "✅ Test Passed",
                    "ProPainter installation is working correctly!\n\n"
                    "You can now use AI video inpainting in the Advanced tab.",
                )
                self.propainter_path = path
            else:
                QMessageBox.warning(
                    self,
                    "Test Failed",
                    f"ProPainter test failed.\n\n" f"Error: {result.stderr[:500]}",
                )
        except subprocess.TimeoutExpired:
            QMessageBox.warning(
                self,
                "Test Timeout",
                "Test took too long (>60s).\n\n"
                "This may happen if:\n"
                "• Model weights are being downloaded (first run)\n"
                "• Python environment is slow to start\n\n"
                "Try running processing - it may still work!",
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Test Error", f"Could not test ProPainter:\n{str(e)}"
            )

    def save_and_close(self):
        """Save the path and close dialog."""
        path = self.path_edit.text()

        if path:
            path_obj = Path(path)
            # Validate will auto-correct to nested directory if needed
            if self.validate_path(path_obj):
                # Use the corrected path from the text edit (validate_path updates it)
                self.propainter_path = Path(self.path_edit.text())
                self.accept()
            else:
                reply = QMessageBox.question(
                    self,
                    "Path Not Validated",
                    "The selected path doesn't appear to contain a valid ProPainter installation.\n\n"
                    "Save it anyway? (You can install ProPainter there later)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.propainter_path = path_obj
                    self.accept()
        else:
            self.reject()

    def get_propainter_path(self) -> str:
        """Get the configured ProPainter path."""
        return str(self.propainter_path) if self.propainter_path else ""
