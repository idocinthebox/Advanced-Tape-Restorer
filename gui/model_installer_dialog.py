"""
Model Installer Dialog - Guided installation for manual AI models
Helps users install complex AI models that can't be auto-downloaded
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QTextBrowser,
    QProgressBar,
    QGroupBox,
    QMessageBox,
    QFileDialog,
    QCheckBox,
    QLineEdit,
    QApplication,
)
from PySide6.QtCore import Signal, QThread
from PySide6.QtGui import QDesktopServices
from pathlib import Path
import os
import subprocess
import shutil
import sys


def get_python_executable():
    """
    Get the path to a usable Python interpreter.
    
    When running as a PyInstaller frozen executable, sys.executable points to the .exe,
    not a Python interpreter. This function tries to find a real Python interpreter.
    
    Returns:
        str: Path to Python executable, or None if running frozen without Python available
    """
    # Check if we're running as a frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        # We're running as an .exe - sys.executable is the .exe, not Python
        # Try to find Python in common locations
        python_locations = [
            shutil.which('python'),
            shutil.which('python3'),
            'C:\\Python312\\python.exe',
            'C:\\Python311\\python.exe',
            'C:\\Python310\\python.exe',
            'C:\\Python39\\python.exe',
        ]
        
        for python_path in python_locations:
            if python_path and Path(python_path).exists():
                return python_path
        
        # No Python found - can't run pip commands from frozen exe
        return None
    else:
        # Running from source - sys.executable is the Python interpreter
        return sys.executable


class ModelInstallThread(QThread):
    """Background thread for installing model components."""

    progress = Signal(str)  # Status message
    finished = Signal(bool, str)  # success, message

    def __init__(self, model_id, install_type, params):
        super().__init__()
        self.model_id = model_id
        self.install_type = install_type
        self.params = params

    def run(self):
        """Run installation steps."""
        try:
            if self.install_type == "pip_package":
                self._install_pip_package()
            elif self.install_type == "git_clone":
                self._install_git_repo()
            elif self.install_type == "file_copy":
                self._install_file_copy()
            else:
                raise ValueError(f"Unknown install type: {self.install_type}")

            self.finished.emit(True, f"Successfully installed {self.model_id}")

        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}")

    def _install_pip_package(self):
        """Install a pip package."""
        package = self.params.get("package")
        self.progress.emit(f"Installing pip package: {package}")
        self.progress.emit("Running: pip install " + package)

        # Get proper Python executable (handles frozen/unfrozen cases)
        python_exe = get_python_executable()
        if not python_exe:
            raise RuntimeError(
                "Cannot install packages: No Python interpreter found.\n"
                "This application is running as a compiled executable.\n"
                "Please install packages manually or run from Python source."
            )

        result = subprocess.run(
            [python_exe, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Show more details about the error
            error_msg = result.stderr if result.stderr else result.stdout
            self.progress.emit(f"Error output: {error_msg}")
            raise RuntimeError(
                f"pip install failed. Check if you have PyTorch with CUDA installed."
            )

        self.progress.emit("Package installed successfully!")
        self.progress.emit("")
        self.progress.emit("Note: Some plugins require PyTorch with CUDA support.")
        self.progress.emit("If models don't work, install PyTorch CUDA first.")

    def _install_git_repo(self):
        """Clone a git repository."""
        url = self.params.get("url")
        target_dir = self.params.get("target_dir")

        self.progress.emit(f"Cloning repository: {url}")

        result = subprocess.run(
            ["git", "clone", url, target_dir], capture_output=True, text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"git clone failed: {result.stderr}")

        self.progress.emit("Repository cloned successfully")

    def _install_file_copy(self):
        """Copy files from source to destination."""
        source = self.params.get("source")
        dest = self.params.get("dest")

        self.progress.emit(f"Copying files from {source}")

        if os.path.isfile(source):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(source, dest)
        else:
            shutil.copytree(source, dest, dirs_exist_ok=True)

        self.progress.emit("Files copied successfully")


class ModelInstallerDialog(QDialog):
    """
    Guided installer for manual AI models.
    Provides step-by-step instructions and automation where possible.
    """

    installation_complete = Signal(str)  # model_id

    def __init__(self, model_info, model_root, parent=None):
        super().__init__(parent)
        self.model_info = model_info
        self.model_root = model_root
        self.install_thread = None
        self.current_instructions_html = ""  # Store HTML to prevent loss on link click

        self.setWindowTitle(
            f"Install {model_info.get('friendly_name', model_info['id'])}"
        )
        self.setModal(True)

        # Set large size and center on screen
        screen = QApplication.primaryScreen().geometry()
        width = min(1200, int(screen.width() * 0.8))
        height = min(900, int(screen.height() * 0.85))
        self.resize(width, height)

        # Center dialog on screen
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)

        self._build_ui()
        self._load_instructions()

    def _build_ui(self):
        """Build the installer dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            f"<h2>{self.model_info.get('friendly_name', self.model_info['id'])}</h2>"
        )
        layout.addWidget(header)

        # Model info
        info_group = QGroupBox("Model Information")
        info_layout = QVBoxLayout()

        info_text = f"<b>Engine:</b> {self.model_info.get('engine')}<br>"
        info_text += f"<b>License:</b> {self.model_info.get('license')}<br>"

        if self.model_info.get("license_url"):
            info_text += f"<b>License Details:</b> <a href=\"{
                self.model_info['license_url']}\">{
                self.model_info['license_url']}</a><br>"

        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Installation instructions
        inst_group = QGroupBox("Installation Instructions")
        inst_layout = QVBoxLayout()

        # Toolbar with helper buttons
        toolbar_layout = QHBoxLayout()

        self.open_powershell_btn = QPushButton("🖥️ Open PowerShell")
        self.open_powershell_btn.setToolTip(
            "Open PowerShell terminal for running commands"
        )
        self.open_powershell_btn.clicked.connect(self._open_powershell)
        toolbar_layout.addWidget(self.open_powershell_btn)

        self.open_explorer_btn = QPushButton("📁 Open Models Folder")
        self.open_explorer_btn.setToolTip("Open the models directory in File Explorer")
        self.open_explorer_btn.clicked.connect(self._open_models_folder)
        toolbar_layout.addWidget(self.open_explorer_btn)

        toolbar_layout.addStretch()

        inst_layout.addLayout(toolbar_layout)

        self.instructions_text = QTextBrowser()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setOpenExternalLinks(False)  # Handle links manually
        self.instructions_text.setOpenLinks(False)  # Prevent navigation
        self.instructions_text.anchorClicked.connect(self._handle_link_clicked)
        inst_layout.addWidget(self.instructions_text)

        inst_group.setLayout(inst_layout)
        layout.addWidget(inst_group)

        # Installation options
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout()

        # Auto-install checkbox (for supported models)
        self.auto_install_check = QCheckBox(
            "Attempt automatic installation (if supported)"
        )
        self.auto_install_check.setChecked(True)
        options_layout.addWidget(self.auto_install_check)

        # Manual file selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Or select model file manually:"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Browse for model file...")
        file_layout.addWidget(self.file_path_edit, 1)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_btn)
        options_layout.addLayout(file_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress section
        progress_group = QGroupBox("Installation Progress")
        progress_layout = QVBoxLayout()

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(100)
        progress_layout.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.install_btn = QPushButton("Install")
        self.install_btn.clicked.connect(self._start_installation)
        button_layout.addWidget(self.install_btn)

        self.open_folder_btn = QPushButton("Open Model Folder")
        self.open_folder_btn.clicked.connect(self._open_model_folder)
        button_layout.addWidget(self.open_folder_btn)

        button_layout.addStretch()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def _handle_link_clicked(self, url):
        """Handle custom link clicks (URLs, paths, copy actions, commands)."""
        # Store scroll position before handling link
        scrollbar = self.instructions_text.verticalScrollBar()
        scroll_pos = scrollbar.value()

        url_str = url.toString()

        if url_str.startswith("copy:"):
            # Copy path to clipboard
            path = url_str[5:]  # Remove 'copy:' prefix
            clipboard = QApplication.clipboard()
            clipboard.setText(path)
            self._log(f"✓ Copied to clipboard: {path}")
            # Don't show dialog - it causes text to disappear
        elif url_str.startswith("copycmd:"):
            # Copy command to clipboard
            cmd = url_str[8:]  # Remove 'copycmd:' prefix
            clipboard = QApplication.clipboard()
            clipboard.setText(cmd)
            self._log(f"✓ Copied command to clipboard: {cmd}")
            # Don't show dialog - it causes text to disappear
        elif url_str.startswith("open:"):
            # Open directory in file explorer
            path = url_str[5:]  # Remove 'open:' prefix
            path_obj = Path(path)

            # Create directory if it doesn't exist
            if not path_obj.exists():
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    self._log(f"✓ Created directory: {path}")
                except Exception as e:
                    self._log(f"✗ Failed to create directory: {e}")
                    # Restore scroll position and HTML
                    if self.current_instructions_html:
                        self.instructions_text.setHtml(self.current_instructions_html)
                        self.instructions_text.verticalScrollBar().setValue(scroll_pos)
                    return

            # Open in file explorer
            try:
                if os.name == "nt":  # Windows
                    os.startfile(str(path_obj))
                elif os.name == "posix":  # macOS/Linux
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.run([opener, str(path_obj)])
                self._log(f"✓ Opened directory: {path}")
            except Exception as e:
                self._log(f"✗ Failed to open directory: {e}")
        else:
            # Open URL in browser
            QDesktopServices.openUrl(url)
            self._log(f"✓ Opened in browser: {url_str}")

        # Restore HTML and scroll position after handling link
        if self.current_instructions_html:
            self.instructions_text.setHtml(self.current_instructions_html)
            self.instructions_text.verticalScrollBar().setValue(scroll_pos)

    def _make_path_widget(self, path):
        """Create HTML for a path with copy and open buttons."""
        path_str = str(path)
        return (
            f"<div style='background: #ffffff; padding: 10px; margin: 8px 0; border: 2px solid #cccccc; border-radius: 4px;'>"
            f"<code style='color: #000000; background: #f5f5f5; padding: 4px 8px; display: block; margin-bottom: 8px; font-size: 12px;'>{path_str}</code>"
            f"<a href='copy:{path_str}' style='color: #0052cc; text-decoration: none; font-weight: bold; margin-right: 15px;'>📋 Copy Path</a>"
            f"<a href='open:{path_str}' style='color: #0052cc; text-decoration: none; font-weight: bold;'>📁 Open Folder</a>"
            f"</div>"
        )

    def _make_command_widget(self, command, description=""):
        """Create HTML for a command with copy button."""
        desc_html = (
            f"<p style='color: #000000; margin: 0 0 8px 0;'><strong>{description}</strong></p>"
            if description
            else ""
        )
        return (
            f"<div style='background: #ffffff; padding: 12px; margin: 8px 0; border: 2px solid #0052cc; border-radius: 4px;'>"
            f"{desc_html}"
            f"<code style='color: #000000; background: #f0f8ff; padding: 8px; display: block; margin-bottom: 10px; font-size: 13px; border: 1px solid #b3d9ff;'>{command}</code>"
            f"<a href='copycmd:{command}' style='color: #0052cc; font-weight: bold; text-decoration: none; font-size: 14px;'>"
            f"📋 Copy Command</a>"
            f"<p style='color: #333333; font-size: 11px; margin: 8px 0 0 0;'>"
            f"💡 Open PowerShell, paste this command, and press Enter"
            f"</p>"
            f"</div>"
        )

    def _load_instructions(self):
        """Load model-specific installation instructions."""
        self.model_info["id"]
        engine = self.model_info.get("engine", "")
        source_note = self.model_info.get("source", {}).get("note", "")

        instructions = f"<h3>How to Install {self.model_info.get('friendly_name')}</h3>"

        # Engine-specific instructions
        if engine == "basicvsrpp":
            instructions += self._get_basicvsrpp_instructions()
        elif engine == "swinir":
            instructions += self._get_swinir_instructions()
        elif engine == "rife":
            instructions += self._get_rife_instructions()
        elif engine == "gfpgan":
            instructions += self._get_gfpgan_instructions()
        elif engine == "deoldify":
            instructions += self._get_deoldify_instructions()
        elif engine == "svdiffusion":
            instructions += self._get_svdiffusion_instructions()
        elif engine == "amt":
            instructions += self._get_amt_instructions()
        else:
            instructions += f"<p>{source_note}</p>"
            instructions += (
                "<p><b>Installation steps not yet available for this model.</b></p>"
            )
            instructions += (
                "<p>Please contact support or check the project documentation.</p>"
            )

        # Common steps
        instructions += "<hr>"
        instructions += "<h4>After Installation:</h4>"
        instructions += "<ol>"
        instructions += f"<li>Place model files in: <code>{self.model_root}</code></li>"
        instructions += "<li>Click 'Refresh Status' in the Model Manager</li>"
        instructions += "<li>Verify the model shows as 'Installed'</li>"
        instructions += "</ol>"

        # Store HTML before setting it
        self.current_instructions_html = instructions
        self.instructions_text.setHtml(instructions)

    def _get_basicvsrpp_instructions(self):
        """Get BasicVSR++ installation instructions."""

        return f"""
<p><b>BasicVSR++</b> - Video super-resolution with temporal awareness for deblurring and upscaling.</p>

<h4>Step 1: Install PyTorch with CUDA</h4>
<p style="color: #000000;">Required for GPU acceleration (if not already installed):</p>
{self._make_command_widget('pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128', 'Install PyTorch with CUDA 12.8')}

<h4>Step 2: Install VapourSynth Plugin</h4>
{self._make_command_widget('pip install vsbasicvsrpp', 'Install BasicVSR++ plugin')}

<h4>Step 3: Download Model Weights (Automatic)</h4>

<div style="background: #d4f4dd; padding: 12px; margin: 10px 0; border: 2px solid #28a745; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">✓ Fully Automatic Installation</p>
<p style="color: #000000; margin: 5px 0 0 0;">Run this command to download all 11 model files (about 700MB total):</p>
</div>

{self._make_command_widget('python -m vsbasicvsrpp', 'Download all BasicVSR++ models')}

<p style="color: #000000;"><b>What gets downloaded:</b></p>
<ul style="color: #000000;">
    <li><b>BD (Blur Degradation)</b> - Primary model for deblurring old tape footage ✓</li>
    <li><b>BI (Bicubic Interpolation)</b> - For upscaling clean footage</li>
    <li><b>SpyNet</b> - Required dependency for optical flow analysis</li>
    <li><b>Specialized models:</b> DVD deblur, GoPro deblur, denoise, decompress</li>
</ul>

<div style="background: #e7f3ff; padding: 12px; margin: 10px 0; border: 2px solid #0052cc; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">ℹ️ Where do models get stored?</p>
<p style="color: #000000; margin: 5px 0 0 0;">Models are stored in the VapourSynth plugin directory (NOT your application's ai_models folder). This is automatic and managed by the plugin itself.</p>
<p style="color: #555555; margin: 5px 0 0 0; font-size: 11px;">Typical location: <code>Python313\\Lib\\site-packages\\vsbasicvsrpp\\models</code></p>
</div>

<p style="color: #000000;"><b>Verification:</b></p>
<ol style="color: #000000;">
    <li>Wait for all downloads to complete (progress bars will show 100%)</li>
    <li>Models are automatically detected by the plugin</li>
    <li>Click "Refresh Status" in Model Manager → Should show <b>✓ Installed</b></li>
</ol>

<p style="color: #000000;"><b>Requirements:</b> NVIDIA GPU with 2GB+ VRAM, CUDA support</p>
"""

    def _get_swinir_instructions(self):
        """Get SwinIR installation instructions."""

        return f"""
<p><b>SwinIR</b> - Transformer-based image restoration with excellent quality for real-world footage.</p>

<h4>Step 1: Install PyTorch with CUDA</h4>
<p style="color: #000000;">Required for GPU acceleration (if not already installed):</p>
{self._make_command_widget('pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128', 'Install PyTorch with CUDA 12.8')}

<h4>Step 2: Install VapourSynth Plugin</h4>
{self._make_command_widget('pip install vsswinir', 'Install SwinIR plugin')}

<h4>Step 3: Models (Automatic)</h4>

<div style="background: #d4f4dd; padding: 12px; margin: 10px 0; border: 2px solid #28a745; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">✓ Automatic Model Management</p>
<p style="color: #000000; margin: 5px 0 0 0;">SwinIR models are downloaded automatically when first used. You can also pre-download them:</p>
</div>

{self._make_command_widget('python -m vsswinir', 'Pre-download SwinIR models (optional)')}

<p style="color: #000000;"><b>Available models:</b></p>
<ul style="color: #000000;">
    <li><b>Real-world SR x4 (GAN)</b> - Best for old tape restoration ✓</li>
    <li>Lightweight SR x2/x3/x4 - Faster processing</li>
    <li>Anime upscaling x2 - For animation content</li>
</ul>

<div style="background: #e7f3ff; padding: 12px; margin: 10px 0; border: 2px solid #0052cc; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">ℹ️ Where do models get stored?</p>
<p style="color: #000000; margin: 5px 0 0 0;">Models are stored in the VapourSynth plugin directory, NOT your application's ai_models folder. The plugin manages them automatically.</p>
<p style="color: #555555; margin: 5px 0 0 0; font-size: 11px;">Typical location: <code>Python313\\Lib\\site-packages\\vsswinir\\models</code></p>
</div>

<p style="color: #000000;"><b>Verification:</b></p>
<ol style="color: #000000;">
    <li>Models download automatically on first use</li>
    <li>Click "Refresh Status" in Model Manager → Should show <b>✓ Installed</b></li>
</ol>

<p style="color: #000000;"><b>Requirements:</b> NVIDIA GPU with 1.5GB+ VRAM, CUDA support</p>
"""

    def _get_rife_instructions(self):
        """Get RIFE installation instructions."""
        return f"""
<p><b>RIFE</b> (Real-Time Intermediate Flow Estimation) - AI-powered frame interpolation for smooth slow-motion.</p>

<h4>Step 1: Install PyTorch with CUDA</h4>
<p style="color: #000000;">Required for GPU acceleration (if not already installed):</p>
{self._make_command_widget('pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128', 'Install PyTorch with CUDA 12.8')}

<h4>Step 2: Install VapourSynth Plugin</h4>
{self._make_command_widget('pip install vsrife', 'Install RIFE plugin')}

<h4>Step 3: Models (Automatic)</h4>

<div style="background: #d4f4dd; padding: 12px; margin: 10px 0; border: 2px solid #28a745; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">✓ Fully Automatic Installation</p>
<p style="color: #000000; margin: 5px 0 0 0;">RIFE models download automatically on first use. You can also pre-download:</p>
</div>

{self._make_command_widget('python -m vsrife', 'Pre-download RIFE models (optional)')}

<p style="color: #000000;"><b>Available versions:</b></p>
<ul style="color: #000000;">
    <li><b>RIFE v4.22</b> - Default, best quality/speed balance (~25 MB)</li>
    <li>RIFE v4.25 - Latest version</li>
    <li>RIFE v4.6 - Older stable version</li>
</ul>

<div style="background: #e7f3ff; padding: 12px; margin: 10px 0; border: 2px solid #0052cc; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">ℹ️ Where do models get stored?</p>
<p style="color: #000000; margin: 5px 0 0 0;">Models are stored in the VapourSynth plugin directory, NOT your application's ai_models folder. The plugin manages them automatically.</p>
<p style="color: #555555; margin: 5px 0 0 0; font-size: 11px;">Typical location: <code>Python313\\Lib\\site-packages\\vsrife\\models</code></p>
</div>

<p style="color: #000000;"><b>Verification:</b></p>
<ol style="color: #000000;">
    <li>Models download automatically when you first use frame interpolation</li>
    <li>Click "Refresh Status" in Model Manager → Should show <b>✓ Installed</b></li>
</ol>

<p style="color: #000000;"><b>Requirements:</b> NVIDIA GPU with 1GB+ VRAM, CUDA support</p>
"""

    def _get_gfpgan_instructions(self):
        """Get GFPGAN installation instructions."""
        pytorch_cmd = self._make_command_widget(
            "pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128",
            "Install PyTorch with CUDA 12.8 (if not already installed)",
        )
        plugin_cmd = self._make_command_widget(
            "pip install vsgfpgan", "Install GFPGAN plugin"
        )

        return f"""
<p><b>GFPGAN</b> (Generative Facial Prior GAN) for face restoration in old videos.</p>

<h4>Step 1: Install PyTorch with CUDA</h4>
{pytorch_cmd}

<h4>Step 2: Install VapourSynth Plugin</h4>
{plugin_cmd}

<h4>Step 3: Download Model Weights</h4>
<ol style="color: #000000;">
    <li>Direct download: <a href="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth" style="color: #0052cc; font-weight: bold;">GFPGANv1.4.pth</a> (~350 MB)</li>
    <li>Or visit: <a href="https://github.com/TencentARC/GFPGAN/releases" style="color: #0052cc; font-weight: bold;">GFPGAN Releases</a></li>
</ol>

<h4>Step 4: Place Model File</h4>
<p style="color: #000000;">After downloading, click "Browse..." above and select <code style="background: #f5f5f5; padding: 2px 4px;">GFPGANv1.4.pth</code>, then click "Install".</p>
<p style="color: #000000;">Or manually place in: <code style="background: #f5f5f5; padding: 2px 4px;">{self.model_root}/gfpgan/</code></p>

<div style="background: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Use Case:</b> Enhances faces in old family videos and footage.</p>
</div>

<p style="color: #000000;"><b>Requirements:</b></p>
<ul style="color: #000000;">
    <li>PyTorch with CUDA support</li>
    <li>NVIDIA GPU with 4GB+ VRAM</li>
    <li>Best for videos with visible faces</li>
</ul>
"""

    def _get_deoldify_instructions(self):
        """Get DeOldify installation instructions."""
        model_root = Path(self.model_root).resolve()
        target_folder = model_root / "deoldify" / "video"
        target_path = target_folder / "video_model.pth"

        return f"""
<p style="color: #000000;"><b>DeOldify</b> - AI-powered colorization for black & white videos.</p>

<div style="background: #fff3cd; padding: 12px; margin: 10px 0; border: 2px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">⚠️ Manual Installation Required (License Restricted)</p>
<p style="color: #000000; margin: 5px 0 0 0;">DeOldify model weights cannot be redistributed. Follow these steps:</p>
</div>

<h4>Step 1: Download Model File</h4>
<ol style="color: #000000;">
    <li><b>Official Source:</b> <a href="https://github.com/jantic/DeOldify" style="color: #0052cc; font-weight: bold;">DeOldify GitHub Repository</a></li>
    <li>Look in the <code style="background: #f5f5f5; padding: 2px 4px;">models/</code> folder or README for download links</li>
    <li>Download: <code style="background: #f5f5f5; padding: 2px 4px;">video.pth</code> or <code style="background: #f5f5f5; padding: 2px 4px;">video_model.pth</code> (~190 MB)</li>
    <li><b>Alternative:</b> <a href="https://data.deepai.org/deoldify/ColorizeVideo_gen.pth" style="color: #0052cc; font-weight: bold;">ColorizeVideo_gen.pth mirror</a></li>
</ol>

<h4>Step 2: Create Folder Structure</h4>
<p>Create these folders if they don't exist:</p>
{self._make_path_widget(target_folder)}

<h4>Step 3: Copy Model File</h4>
<p>Rename the file to <code>video_model.pth</code> and place it here:</p>
{self._make_path_widget(target_path)}

<p style="color: #000000;"><b>Or use the Browse button:</b></p>
<ol style="color: #000000;">
    <li>Click "Browse..." button above</li>
    <li>Select your downloaded <code style="background: #f5f5f5; padding: 2px 4px;">ColorizeVideo_gen.pth</code> file</li>
    <li>Click "Install" - the app will copy it to the correct location</li>
</ol>

<h4>Step 4: Verify Installation</h4>
<p style="color: #000000;">After placing the file, click "Refresh Status" in the Model Manager.</p>
<p style="color: #000000;">Status should change to: <b>✓ Installed</b></p>

<div style="background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Note:</b> DeOldify plugin requires: <code style="background: #f5f5f5; padding: 2px 4px;">pip install fastai</code> and manual plugin setup.</p>
<p style="color: #000000; margin: 5px 0 0 0;">Visit: <a href="https://github.com/HolyWu/vs-deoldify" style="color: #0052cc; font-weight: bold;">vs-deoldify GitHub</a> for plugin installation.</p>
</div>

<div style="background: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Use Case:</b> Add realistic colors to black & white home movies and historical footage.</p>
</div>

<p style="color: #000000;"><b>Requirements:</b></p>
<ul style="color: #000000;">
    <li>NVIDIA GPU with 4GB+ VRAM</li>
    <li>Processing is slow - recommended for short clips</li>
    <li>Best results on clear, well-lit footage</li>
</ul>
"""

    def _get_svdiffusion_instructions(self):
        """Get Stable Video Diffusion installation instructions."""
        pytorch_cmd = self._make_command_widget(
            "pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128",
            "Install PyTorch with CUDA 12.8",
        )
        libs_cmd = self._make_command_widget(
            "pip install huggingface-hub diffusers transformers accelerate",
            "Install required libraries",
        )
        login_cmd = self._make_command_widget(
            "huggingface-cli login",
            "Login to Hugging Face - follow prompts to paste your token",
        )

        return f"""
<p><b>Stable Video Diffusion</b> - Advanced AI video restoration using diffusion models.</p>

<div style="background: #fff3cd; padding: 12px; margin: 10px 0; border: 2px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">⚠️ Complex Setup - Advanced Users Only</p>
<p style="color: #000000; margin: 5px 0 0 0;">This model requires ~10GB download, 12GB+ VRAM, and is extremely slow. Consider using BasicVSR++ or SwinIR instead for most restoration tasks.</p>
</div>

<h4>Step 1: Install PyTorch with CUDA</h4>
<p style="color: #000000;"><b>For NVIDIA RTX 5070 (Blackwell) - CUDA 12.8:</b></p>
{pytorch_cmd}

<h4>Step 2: Install Required Libraries</h4>
<p style="color: #000000;">This installs Hugging Face ecosystem and diffusion model support:</p>
{libs_cmd}

<h4>Step 3: Setup Hugging Face Authentication</h4>

<div style="background: #e7f3ff; padding: 12px; margin: 10px 0; border: 2px solid #0052cc; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">🔑 Get Your Access Token First:</p>
<ol style="color: #000000; margin: 10px 0 0 20px;">
    <li>Go to <a href="https://huggingface.co/settings/tokens" style="color: #0052cc; font-weight: bold;">huggingface.co/settings/tokens</a></li>
    <li>Click "New token" → Create a token with "Read" permissions</li>
    <li>Copy the token (starts with "hf_...")</li>
    <li>Keep the token page open - you'll paste it in the next step</li>
</ol>
</div>

<p style="color: #000000;"><b>Then login via command line:</b></p>
{login_cmd}

<div style="background: #d4f4dd; padding: 12px; margin: 10px 0; border: 2px solid #28a745; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">What happens after running huggingface-cli login:</p>
<ol style="color: #000000; margin: 10px 0 0 20px;">
    <li>PowerShell will prompt: "Token:" or "Enter your token:"</li>
    <li>Paste your token (right-click or Ctrl+V) - <b>text won't appear as you paste</b></li>
    <li>Press Enter</li>
    <li>You'll see: "Login successful" and "Your token has been saved"</li>
    <li><b>You're now authenticated - proceed to Step 4</b></li>
</ol>
</div>

<h4>Step 4: Model Auto-Download</h4>
<p style="color: #000000;"><b>After authentication, the model downloads automatically when you first use it!</b></p>
<ul style="color: #000000;">
    <li><b>Model ID:</b> <code>stabilityai/stable-video-diffusion-img2vid-xt-1-1</code></li>
    <li><b>Size:</b> ~9.5 GB (downloads to Hugging Face cache, not your app folder)</li>
    <li><b>Cache Location:</b> <code>C:\\Users\\YourName\\.cache\\huggingface\\hub</code></li>
    <li><b>One-time download:</b> Once cached, it won't download again</li>
</ul>

<p style="color: #000000;">Visit model page: <a href="https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt-1-1" style="color: #0052cc; font-weight: bold;">
Stable Video Diffusion on Hugging Face</a></p>

<h4>Step 5: Verification</h4>
<p style="color: #000000;">After completing authentication:</p>
<ol style="color: #000000;">
    <li>Click "Refresh Status" in Model Manager → Should show <b>✓ Installed</b> (checks libraries)</li>
    <li>First use will download the 9.5GB model automatically</li>
    <li>Subsequent uses will load from cache</li>
</ol>

<div style="background: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Use Case:</b> Experimental AI-powered video enhancement using diffusion models for extreme quality restoration on single frames or very short clips.</p>
</div>

<p style="color: #000000;"><b>Requirements:</b></p>
<ul style="color: #000000;">
    <li>NVIDIA GPU with 12GB+ VRAM (16GB recommended)</li>
    <li>Very slow processing - 30+ seconds per frame</li>
    <li>Best for single frame enhancement, not full videos</li>
    <li>Experimental - results highly variable</li>
</ul>

<div style="background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>💡 Recommendation:</b> For most tape restoration, use BasicVSR++ (deblurring) or SwinIR (upscaling) instead. They're faster, require less VRAM, and give more predictable results.</p>
</div>
""".format(
            model_root=self.model_root
        )

    def _get_amt_instructions(self):
        """Get AMT installation instructions."""
        model_root = Path(self.model_root).resolve()
        target_folder = model_root / "amt" / "default"
        target_path = target_folder / "amt_model.ckpt"

        return f"""
<p style="color: #000000;"><b>AMT</b> (Any-to-Many Trajectory) - Advanced frame interpolation.</p>

<div style="background: #fff3cd; padding: 12px; margin: 10px 0; border: 2px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0; font-weight: bold;">⚠️ Manual Installation Required</p>
<p style="color: #000000; margin: 5px 0 0 0;"><b>License:</b> CC BY-NC 4.0 (Non-Commercial Use Only)</p>
<p style="color: #000000; margin: 5px 0 0 0;">This model cannot be auto-downloaded due to license restrictions.</p>
</div>

<h4>Step 1: Download Model File</h4>
<ol style="color: #000000;">
    <li><b>Primary:</b> <a href="https://github.com/MCG-NKU/AMT/releases" style="color: #0052cc; font-weight: bold;">AMT Official Releases</a></li>
    <li><b>Alternative:</b> <a href="https://github.com/lucidrains/AMT" style="color: #0052cc; font-weight: bold;">AMT Alternative Repository</a></li>
    <li>Download checkpoint: <code style="background: #f5f5f5; padding: 2px 4px;">amt-s.pth</code> (~20 MB) or <code style="background: #f5f5f5; padding: 2px 4px;">amt-l.pth</code> (~80 MB)</li>
</ol>

<h4>Step 2: Create Folder Structure</h4>
<p>Create these folders if they don't exist:</p>
{self._make_path_widget(target_folder)}

<h4>Step 3: Copy Model File</h4>
<p style="color: #000000;">Rename the file to <code style="background: #f5f5f5; padding: 2px 4px;">amt_model.ckpt</code> and place it here:</p>
{self._make_path_widget(target_path)}

<p style="color: #000000;"><b>Or use the Browse button:</b></p>
<ol style="color: #000000;">
    <li>Click "Browse..." button above</li>
    <li>Select your downloaded AMT model file</li>
    <li>Click "Install" - the app will copy and rename it correctly</li>
</ol>

<h4>Step 4: Verify Installation</h4>
<p style="color: #000000;">After placing the file, click "Refresh Status" in the Model Manager.</p>
<p style="color: #000000;">Status should change to: <b>✓ Installed</b></p>

<div style="background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>⚠️ License:</b> CC BY-NC 4.0 - Non-Commercial Use Only</p>
<p style="color: #000000; margin: 5px 0 0 0;"><b>Alternative:</b> Use RIFE (already installed, MIT license) for frame interpolation.</p>
</div>

<div style="background: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #2196F3; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Use Case:</b> Advanced frame interpolation for arbitrary frame rate conversion.</p>
<p style="color: #000000; margin: 5px 0 0 0;"><b>Performance:</b> Similar speed to RIFE with improved quality on complex motion.</p>
</div>

<p style="color: #000000;"><b>Requirements:</b></p>
<ul style="color: #000000;">
    <li>NVIDIA GPU with 4GB+ VRAM (6GB+ for large model)</li>
    <li>PyTorch with CUDA support</li>
</ul>

<div style="background: #d4f4dd; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; border-radius: 4px;">
<p style="color: #000000; margin: 0;"><b>Recommendation:</b> Start with amt-s.pth for testing, upgrade to amt-l.pth if quality is insufficient.</p>
</div>
"""

    def _browse_file(self):
        """Browse for model file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model File",
            "",
            "Model Files (*.pth *.pt *.ckpt *.safetensors);;All Files (*.*)",
        )

        if file_path:
            self.file_path_edit.setText(file_path)

    def _open_model_folder(self):
        """Open the model storage folder."""
        engine = self.model_info.get("engine", "")
        folder_path = Path(self.model_root) / engine
        folder_path.mkdir(parents=True, exist_ok=True)

        # Open in file explorer
        if os.name == "nt":  # Windows
            os.startfile(str(folder_path))
        else:
            subprocess.run(["xdg-open", str(folder_path)])

    def _open_powershell(self):
        """Open PowerShell terminal."""
        try:
            if os.name == "nt":  # Windows
                # Open PowerShell in a new window with the model root directory
                import subprocess

                CREATE_NEW_CONSOLE = 0x00000010
                subprocess.Popen(
                    [
                        "powershell.exe",
                        "-NoExit",
                        "-Command",
                        f'cd "{self.model_root}"',
                    ],
                    creationflags=CREATE_NEW_CONSOLE,
                )
                self._log("✓ Opened PowerShell terminal")
            else:
                # For Linux/Mac, open default terminal
                subprocess.Popen(["x-terminal-emulator"], cwd=self.model_root)
                self._log("✓ Opened terminal")
        except Exception as e:
            self._log(f"✗ Failed to open terminal: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open terminal: {e}")

    def _open_models_folder(self):
        """Open the main models directory in file explorer."""
        try:
            models_path = Path(self.model_root)
            models_path.mkdir(parents=True, exist_ok=True)

            if os.name == "nt":  # Windows
                os.startfile(str(models_path))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(models_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(models_path)])

            self._log(f"✓ Opened models folder: {models_path}")
        except Exception as e:
            self._log(f"✗ Failed to open models folder: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open folder: {e}")

    def _start_installation(self):
        """Start the installation process."""
        try:
            print(
                f"[DEBUG] Install button clicked for engine: {self.model_info.get('engine', 'unknown')}"
            )
            engine = self.model_info.get("engine", "")

            # Check if manual file path provided
            manual_file = self.file_path_edit.text().strip()
            if manual_file:
                print(f"[DEBUG] Manual file provided: {manual_file}")
                self._install_manual_file(manual_file)
                return

            # Check if auto-install enabled
            if not self.auto_install_check.isChecked():
                print("[DEBUG] Auto-install not checked, showing info message")
                QMessageBox.information(
                    self,
                    "Manual Installation",
                    "Please follow the instructions above to install the model manually.\n\n"
                    "After installation, click 'Refresh Status' in the Model Manager.",
                )
                return

            # Attempt automatic installation
            print("[DEBUG] Starting automatic installation")
            self._log("Starting automatic installation...")
            self.install_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
        except Exception as e:
            import traceback

            error_msg = (
                f"Error in _start_installation: {str(e)}\n{traceback.format_exc()}"
            )
            print(error_msg)
            self._log(error_msg)
            QMessageBox.critical(self, "Error", f"Installation error: {str(e)}")
            return

        # Determine installation method based on engine
        if engine == "basicvsrpp":
            self._log("Note: vsbasicvsrpp requires PyTorch with CUDA.")
            self._log("If you haven't installed PyTorch CUDA, install it first:")
            self._log(
                "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124"
            )
            self._log("")
            self._install_pip_package("vsbasicvsrpp")
        elif engine == "swinir":
            self._log("Note: vsswinir requires PyTorch with CUDA.")
            self._log("If you haven't installed PyTorch CUDA, install it first:")
            self._log(
                "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124"
            )
            self._log("")
            self._install_pip_package("vsswinir")
        elif engine == "gfpgan":
            self._log("Note: vsgfpgan requires PyTorch with CUDA.")
            self._log("If you haven't installed PyTorch CUDA, install it first:")
            self._log(
                "  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124"
            )
            self._log("")
            self._install_pip_package("vsgfpgan")
        elif engine == "rife":
            self._log("RIFE models are managed automatically by vsrife plugin.")
            self._log("The plugin is already installed with this application.")
            self._log("✓ No installation needed!")
            self.install_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            QMessageBox.information(
                self,
                "Already Installed",
                "RIFE is already installed and ready to use!\n\n"
                "Models download automatically when you use frame interpolation.",
            )
        else:
            self._log(f"Automatic installation not supported for {engine}")
            self.install_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            QMessageBox.information(
                self,
                "Manual Installation Required",
                "Please follow the instructions above for manual installation.",
            )

    def _install_pip_package(self, package):
        """Install a pip package."""
        self._log(f"Attempting to install {package} via pip...")
        self._log(
            "This may take a few minutes depending on your internet connection..."
        )

        self.install_thread = ModelInstallThread(
            self.model_info["id"], "pip_package", {"package": package}
        )
        self.install_thread.progress.connect(self._log)
        self.install_thread.finished.connect(self._on_install_finished)
        self.install_thread.start()

    def _install_manual_file(self, file_path):
        """Install from manually selected file."""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", "Selected file does not exist.")
            return

        # Determine destination
        files = self.model_info.get("files", [])
        if not files:
            QMessageBox.warning(
                self, "Error", "No destination path defined for this model."
            )
            return

        dest_path = Path(self.model_root) / files[0]["path"]
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        self._log(f"Copying file to {dest_path}...")
        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.install_thread = ModelInstallThread(
            self.model_info["id"],
            "file_copy",
            {"source": file_path, "dest": str(dest_path)},
        )
        self.install_thread.progress.connect(self._log)
        self.install_thread.finished.connect(self._on_install_finished)
        self.install_thread.start()

    def _on_install_finished(self, success, message):
        """Handle installation completion."""
        self.install_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self._log(message)

        if success:
            QMessageBox.information(
                self,
                "Success",
                f"{message}\n\nClick 'Refresh Status' in the Model Manager to verify.",
            )
            self.installation_complete.emit(self.model_info["id"])
        else:
            QMessageBox.warning(self, "Installation Failed", message)

    def _log(self, message):
        """Add message to progress log."""
        self.progress_text.append(message)
