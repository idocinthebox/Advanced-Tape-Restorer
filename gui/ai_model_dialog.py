"""
AI Model Manager Dialog - Advanced Tape Restorer v3.0
User interface for managing AI models (download, view status, configure)
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QTextEdit,
    QMessageBox,
    QHeaderView,
    QGroupBox,
    QCheckBox,
    QLineEdit,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QColor
from pathlib import Path
import os

from ai_models.model_manager import ModelManager
from .model_installer_dialog import ModelInstallerDialog
from .propainter_setup_dialog import ProPainterSetupDialog


class ModelDownloadThread(QThread):
    """Background thread for downloading models."""

    progress = Signal(str, float)  # model_id, progress (0-100)
    finished = Signal(str, bool, str)  # model_id, success, message
    log_message = Signal(str)

    def __init__(self, model_manager, model_id, hf_token=None):
        super().__init__()
        self.model_manager = model_manager
        self.model_id = model_id
        self.hf_token = hf_token

    def run(self):
        """Download model in background."""
        try:
            self.log_message.emit(f"Starting download of {self.model_id}...")

            # Progress callback
            def progress_callback(current, total):
                if total > 0:
                    percent = (current / total) * 100
                    self.progress.emit(self.model_id, percent)

            # ensure_model_available returns ModelEntry on success or raises exception
            result = self.model_manager.ensure_model_available(
                self.model_id,
                auto_download=True,
                progress_callback=progress_callback,
                hf_token=self.hf_token,
            )

            if result:
                self.finished.emit(
                    self.model_id, True, f"Successfully downloaded {self.model_id}"
                )
            else:
                self.finished.emit(
                    self.model_id, False, f"Failed to download {self.model_id}"
                )

        except Exception as e:
            import traceback

            error_msg = (
                f"Error downloading {self.model_id}: {str(e)}\n{traceback.format_exc()}"
            )
            self.log_message.emit(error_msg)
            self.finished.emit(self.model_id, False, str(e))


class AIModelDialog(QDialog):
    """Dialog for managing AI models."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Model Manager - Advanced Tape Restorer v3.0")
        self.setModal(True)
        self.resize(900, 600)

        # Initialize model manager
        self.registry_path = Path("ai_models/models/registry.yaml")

        # Get model root from settings or use default
        default_model_root = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "Advanced_Tape_Restorer",
            "ai_models",
        )
        self.model_root = default_model_root

        try:
            self.model_manager = ModelManager(
                str(self.registry_path), self.model_root, commercial_mode=True
            )
            self.models = [
                self._model_entry_to_dict(m) for m in self.model_manager.list_models()
            ]
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to initialize model manager: {e}\n\nRegistry path: {self.registry_path}",
            )
            self.models = []
            self.model_manager = None

        self.download_threads = {}

        self._build_ui()
        self._populate_table()

    def _model_entry_to_dict(self, entry):
        """Convert ModelEntry dataclass to dict for easier access."""
        return {
            "id": entry.id,
            "engine": entry.engine,
            "friendly_name": entry.friendly_name,
            "version": entry.version,
            "license": entry.license,
            "license_url": entry.license_url,
            "non_commercial": entry.non_commercial,
            "default_for_engine": entry.default_for_engine,
            "source": entry.source,
            "files": [{"path": f.path, "sha256": f.sha256} for f in entry.files],
            "engine_args": entry.engine_args,
        }

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)

        # Info section
        info_group = QGroupBox("Model Storage Configuration")
        info_layout = QVBoxLayout()

        # Model directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Model Directory:"))
        self.model_dir_label = QLabel(self.model_root)
        self.model_dir_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        dir_layout.addWidget(self.model_dir_label, 1)
        change_dir_btn = QPushButton("Change...")
        change_dir_btn.clicked.connect(self._change_model_directory)
        dir_layout.addWidget(change_dir_btn)
        info_layout.addLayout(dir_layout)

        # Commercial mode checkbox
        self.commercial_checkbox = QCheckBox("Commercial Mode (show all models)")
        self.commercial_checkbox.setChecked(True)
        self.commercial_checkbox.stateChanged.connect(self._on_commercial_mode_changed)
        info_layout.addWidget(self.commercial_checkbox)

        # HuggingFace authentication
        hf_layout = QHBoxLayout()
        hf_layout.addWidget(QLabel("HuggingFace Token:"))
        self.hf_token_input = QLineEdit()
        self.hf_token_input.setPlaceholderText(
            "Optional: Enter HF token for restricted models"
        )
        self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        hf_layout.addWidget(self.hf_token_input, 1)
        hf_help_btn = QPushButton("?")
        hf_help_btn.setMaximumWidth(30)
        hf_help_btn.clicked.connect(self._show_hf_help)
        hf_layout.addWidget(hf_help_btn)
        info_layout.addLayout(hf_layout)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Models table
        table_group = QGroupBox("Available AI Models")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Model Name", "Engine", "Version", "License", "Status", "Actions"]
        )

        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Model Name
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Engine
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # Version
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )  # License
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Status
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )  # Actions

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Model details
        details_group = QGroupBox("Model Details")
        details_layout = QVBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(120)
        details_layout.addWidget(self.details_text)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Log output
        log_group = QGroupBox("Download Log")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Status")
        self.refresh_btn.clicked.connect(self._populate_table)
        button_layout.addWidget(self.refresh_btn)

        # ProPainter setup button
        propainter_btn = QPushButton("🎨 Setup ProPainter...")
        propainter_btn.setToolTip("Configure ProPainter AI Inpainting installation")
        propainter_btn.clicked.connect(self._show_propainter_setup)
        button_layout.addWidget(propainter_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _show_hf_help(self):
        """Show HuggingFace token help dialog."""
        QMessageBox.information(
            self,
            "HuggingFace Token Help",
            "<h3>Why do I need a HuggingFace token?</h3>"
            "<p>Some models are hosted on HuggingFace with authentication requirements. "
            "You'll need a free HuggingFace account and access token to download them.</p>"
            "<h4>How to get a token:</h4>"
            "<ol>"
            "<li>Visit <a href='https://huggingface.co/join'>https://huggingface.co/join</a> to create a free account</li>"
            "<li>Go to <a href='https://huggingface.co/settings/tokens'>https://huggingface.co/settings/tokens</a></li>"
            "<li>Click 'New token' and create a token with 'read' permissions</li>"
            "<li>Copy the token and paste it in the field above</li>"
            "</ol>"
            "<p><b>Note:</b> Your token is stored locally and only used for downloading models.</p>",
        )

    def _change_model_directory(self):
        """Allow user to change model storage directory."""
        new_dir = QFileDialog.getExistingDirectory(
            self, "Select Model Storage Directory", self.model_root
        )

        if new_dir:
            self.model_root = new_dir
            self.model_dir_label.setText(new_dir)

            # Reinitialize model manager
            try:
                self.model_manager = ModelManager(
                    str(self.registry_path),
                    self.model_root,
                    commercial_mode=self.commercial_checkbox.isChecked(),
                )
                self._populate_table()
                self._log("Model directory changed to: " + new_dir)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to change directory: {e}")

    def _on_commercial_mode_changed(self):
        """Handle commercial mode checkbox change."""
        if self.model_manager:
            self.model_manager.commercial_mode = self.commercial_checkbox.isChecked()
            self._populate_table()

    def _populate_table(self):
        """Populate the models table."""
        if not self.model_manager:
            return

        self.table.setRowCount(0)

        # Get all models
        try:
            self.models = [
                self._model_entry_to_dict(m) for m in self.model_manager.list_models()
            ]
        except Exception as e:
            self._log(f"Error listing models: {e}")
            return

        # Filter by commercial mode
        if not self.commercial_checkbox.isChecked():
            self.models = [m for m in self.models if not m.get("non_commercial", False)]

        # Populate table
        for row, model in enumerate(self.models):
            self.table.insertRow(row)

            # Model name
            name_item = QTableWidgetItem(model.get("friendly_name", model["id"]))
            name_item.setData(Qt.ItemDataRole.UserRole, model["id"])
            self.table.setItem(row, 0, name_item)

            # Engine
            engine_item = QTableWidgetItem(model.get("engine", "unknown"))
            self.table.setItem(row, 1, engine_item)

            # Version
            version_item = QTableWidgetItem(str(model.get("version", "N/A")))
            self.table.setItem(row, 2, version_item)

            # License
            license_item = QTableWidgetItem(model.get("license", "Unknown"))
            if model.get("non_commercial", False):
                license_item.setForeground(
                    QColor(255, 140, 0)
                )  # Orange for non-commercial
            self.table.setItem(row, 3, license_item)

            # Status
            is_installed = self._check_model_installed(model["id"])
            status_item = QTableWidgetItem(
                "✓ Installed" if is_installed else "Not installed"
            )
            if is_installed:
                status_item.setForeground(QColor(0, 150, 0))  # Green
            else:
                status_item.setForeground(QColor(150, 0, 0))  # Red
            self.table.setItem(row, 4, status_item)

            # Actions button
            source_type = model.get("source", {}).get("type", "")
            source_url = model.get("source", {}).get("url")

            if not is_installed:
                # Automatic download types: huggingface, github_release, direct
                if (
                    source_type in ("huggingface", "github_release", "direct")
                    and source_url
                ):
                    download_btn = QPushButton("Download")
                    download_btn.clicked.connect(
                        lambda checked, m=model["id"]: self._download_model(m)
                    )
                    self.table.setCellWidget(row, 5, download_btn)
                # External applications
                elif source_type == "external_app":
                    info_item = QTableWidgetItem("External")
                    info_item.setForeground(QColor(100, 100, 100))
                    info_item.setToolTip(
                        "This is an external application - install separately"
                    )
                    self.table.setItem(row, 5, info_item)
                # Manual or github_repo (requires manual setup)
                else:
                    install_btn = QPushButton("Install...")
                    install_btn.clicked.connect(
                        lambda checked, m=model["id"]: self._show_installer(m)
                    )
                    self.table.setCellWidget(row, 5, install_btn)
            else:
                installed_item = QTableWidgetItem("—")
                self.table.setItem(row, 5, installed_item)

    def _check_model_installed(self, model_id: str) -> bool:
        """Check if a model is installed."""
        if not self.model_manager:
            return False

        try:
            model_entry = self.model_manager.get_model(model_id)
            if not model_entry:
                return False

            # For models with no files (plugin-only), check if the plugin is installed
            if not model_entry.files:
                return self._check_plugin_installed(model_entry.engine)

            # Check if all files exist
            for file_info in model_entry.files:
                file_path = Path(self.model_root) / file_info.path
                if not file_path.exists():
                    return False

            return True
        except Exception:
            return False

    def _check_plugin_installed(self, engine: str) -> bool:
        """Check if a VapourSynth plugin or external tool is installed."""
        plugin_map = {
            "basicvsrpp": "vsbasicvsrpp",
            "swinir": "vsswinir",
            "gfpgan": "vsgfpgan",
            "rife": "vsrife",
            "svdiffusion": "diffusers",  # SVD uses diffusers library
            # Note: film, dain, deoldify, amt don't have pip packages
            # They require manual installation from GitHub
        }

        plugin_name = plugin_map.get(engine)
        if not plugin_name:
            return False

        try:
            __import__(plugin_name)
            return True
        except ImportError:
            return False

    def _on_selection_changed(self):
        """Handle table selection change to show model details."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.details_text.clear()
            return

        # Get model ID from first column
        row = selected_items[0].row()
        item = self.table.item(row, 0)
        if not item:
            return
        model_id = item.data(Qt.ItemDataRole.UserRole)

        # Find model info
        model = next((m for m in self.models if m["id"] == model_id), None)
        if not model:
            return

        # Build details text
        details = f"<b>Model ID:</b> {model['id']}<br>"
        details += f"<b>Friendly Name:</b> {model.get('friendly_name', 'N/A')}<br>"
        details += f"<b>Engine:</b> {model.get('engine', 'N/A')}<br>"
        details += f"<b>Version:</b> {model.get('version', 'N/A')}<br>"
        details += f"<b>License:</b> {model.get('license', 'N/A')}"

        if model.get("license_url"):
            details += f" (<a href=\"{model['license_url']}\">details</a>)"

        details += "<br>"

        if model.get("non_commercial", False):
            details += "<b style='color: orange;'>⚠ Non-Commercial Use Only</b><br>"

        # Source info
        source = model.get("source", {})
        if source.get("type") == "external_app":
            details += f"<b>Type:</b> External Application<br>"
            if source.get("url"):
                details += f"<b>Website:</b> <a href=\"{source['url']}\">{source['url']}</a><br>"
        elif source.get("type") == "manual":
            details += f"<b>Type:</b> Manual Download Required<br>"
            if source.get("note"):
                details += f"<b>Note:</b> {source.get('note')}<br>"
        elif source.get("url"):
            details += f"<b>Source:</b> {source.get('type', 'unknown')}<br>"

        # Engine args
        if model.get("engine_args"):
            details += f"<b>Engine Args:</b> {str(model['engine_args'])}<br>"

        # Files
        if model.get("files"):
            details += f"<b>Files:</b><br>"
            for file_info in model["files"]:
                file_path = Path(self.model_root) / file_info["path"]
                exists = "✓" if file_path.exists() else "✗"
                details += f"  {exists} {file_info['path']}<br>"

        self.details_text.setHtml(details)

    def _download_model(self, model_id: str):
        """Download a model."""
        if not self.model_manager:
            return

        # Check if already downloading
        if model_id in self.download_threads:
            QMessageBox.information(
                self, "Info", f"Model {model_id} is already being downloaded."
            )
            return

        # Disable download button for this model
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item_model_id = item.data(Qt.ItemDataRole.UserRole)
                if item_model_id == model_id:
                    widget = self.table.cellWidget(row, 5)
                    if widget and isinstance(widget, QPushButton):
                        widget.setEnabled(False)
                        widget.setText("Downloading...")
                    break

        # Create and start download thread
        hf_token = (
            self.hf_token_input.text().strip()
            if hasattr(self, "hf_token_input")
            else None
        )
        thread = ModelDownloadThread(self.model_manager, model_id, hf_token)
        thread.progress.connect(self._on_download_progress)
        thread.finished.connect(self._on_download_finished)
        thread.log_message.connect(self._log)

        self.download_threads[model_id] = thread
        thread.start()

        self._log(f"Started download: {model_id}")

    def _on_download_progress(self, model_id: str, progress: float):
        """Handle download progress update."""
        # Update button text with progress
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item_model_id = item.data(Qt.ItemDataRole.UserRole)
                if item_model_id == model_id:
                    widget = self.table.cellWidget(row, 5)
                    if widget and isinstance(widget, QPushButton):
                        widget.setText(f"Downloading {progress:.0f}%")
                    break

    def _on_download_finished(self, model_id: str, success: bool, message: str):
        """Handle download completion."""
        try:
            self._log(message)

            # Remove from download threads
            if model_id in self.download_threads:
                thread = self.download_threads[model_id]
                thread.wait()  # Wait for thread to fully finish
                del self.download_threads[model_id]

            # Show message
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Download Failed", message)

            # Refresh table
            self._populate_table()
        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self._log(
                f"Error in download completion handler: {str(e)}\n{error_details}"
            )
            QMessageBox.critical(
                self, "Error", f"Error handling download completion: {str(e)}"
            )

    def _show_installer(self, model_id: str):
        """Show the model installer dialog."""
        # Find model info
        model = next((m for m in self.models if m["id"] == model_id), None)
        if not model:
            return

        # Create and show installer dialog
        installer = ModelInstallerDialog(model, self.model_root, self)
        installer.installation_complete.connect(
            lambda mid: self._on_installation_complete(mid)
        )
        installer.exec()

    def _on_installation_complete(self, model_id: str):
        """Handle installation completion."""
        self._log(f"Installation completed for {model_id}")
        # Refresh the table to update status
        self._populate_table()

    def _log(self, message: str):
        """Add message to log."""
        self.log_text.append(message)

    def get_model_root(self) -> str:
        """Get the current model root directory."""
        return self.model_root

    def _show_propainter_setup(self):
        """Show ProPainter setup wizard."""
        try:
            dialog = ProPainterSetupDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                path = dialog.get_propainter_path()
                if path:
                    # Save to settings via parent window
                    parent = self.parent()
                    if parent and hasattr(parent, "settings_manager"):
                        settings = parent.settings_manager.load_settings()
                        settings["propainter_path"] = str(path)
                        parent.settings_manager.save_settings(settings)
                        parent.settings_manager.load_settings()  # Reload cache

                        if hasattr(parent, "console_log"):
                            parent.console_log(f"✅ ProPainter path configured: {path}")

                        self.log_text.append(f"✅ ProPainter configured: {path}")
                        QMessageBox.information(
                            self,
                            "Configuration Saved",
                            f"ProPainter path saved!\n\n"
                            f"You can now use AI Video Inpainting in the AI Tools tab.",
                        )
                    else:
                        self.log_text.append(
                            f"⚠️ ProPainter path: {path} (settings not accessible)"
                        )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to open ProPainter setup dialog:\n{e}"
            )
            self.log_text.append(f"❌ ProPainter setup error: {e}")

    def closeEvent(self, event):
        """Handle dialog close event - wait for downloads to finish."""
        if self.download_threads:
            reply = QMessageBox.question(
                self,
                "Downloads in Progress",
                f"{len(self.download_threads)} download(s) still in progress.\nWait for completion before closing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            else:
                # Force stop all download threads
                for thread in self.download_threads.values():
                    thread.terminate()
                    thread.wait(1000)

        event.accept()
