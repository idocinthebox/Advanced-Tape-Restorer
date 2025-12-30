"""
Checkpoint Resume Dialog - Detect and resume interrupted jobs on startup
"""

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt


class CheckpointResumeDialog(QDialog):
    """
    Dialog to show incomplete checkpoints and allow user to resume or discard them.
    """
    
    def __init__(self, checkpoint_dir: Path, parent=None):
        super().__init__(parent)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.selected_job = None
        self.action = None  # 'resume' or 'discard'
        
        self.setWindowTitle("Resume Interrupted Jobs")
        self.setModal(True)
        self.resize(600, 400)
        
        self._init_ui()
        self._load_checkpoints()
    
    def _init_ui(self):
        """Initialize UI layout."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(
            "Found interrupted processing jobs.\n"
            "You can resume from where they stopped or discard them."
        )
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Checkpoint list
        self.checkpoint_list = QListWidget()
        self.checkpoint_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.checkpoint_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.resume_button = QPushButton("▶️ Resume Selected")
        self.resume_button.clicked.connect(self._on_resume)
        self.resume_button.setEnabled(False)
        button_layout.addWidget(self.resume_button)
        
        self.discard_button = QPushButton("🗑️ Discard Selected")
        self.discard_button.clicked.connect(self._on_discard)
        self.discard_button.setEnabled(False)
        button_layout.addWidget(self.discard_button)
        
        self.discard_all_button = QPushButton("🗑️ Discard All")
        self.discard_all_button.clicked.connect(self._on_discard_all)
        button_layout.addWidget(self.discard_all_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.checkpoint_list.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _load_checkpoints(self):
        """Load checkpoint files from directory."""
        if not self.checkpoint_dir.exists():
            return
        
        checkpoint_files = list(self.checkpoint_dir.glob("*.checkpoint.json"))
        
        for checkpoint_file in checkpoint_files:
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                # Only show paused or running jobs (not completed/failed)
                status = data.get('status', 'unknown')
                if status in ['paused', 'running']:
                    # Create list item
                    job_id = data.get('job_id', 'Unknown')
                    progress = data.get('processed_frames', 0)
                    total = data.get('total_frames', 0)
                    progress_pct = (progress / total * 100) if total > 0 else 0
                    
                    input_file = Path(data.get('input_file', 'Unknown')).name
                    
                    item_text = (
                        f"{job_id[:20]}...\n"
                        f"  Progress: {progress}/{total} frames ({progress_pct:.1f}%)\n"
                        f"  Input: {input_file}\n"
                        f"  Status: {status.upper()}"
                    )
                    
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'checkpoint_file': str(checkpoint_file),
                        'job_id': job_id,
                        'data': data
                    })
                    
                    self.checkpoint_list.addItem(item)
            
            except Exception as e:
                print(f"Failed to load checkpoint {checkpoint_file}: {e}")
        
        if self.checkpoint_list.count() == 0:
            self.checkpoint_list.addItem("No interrupted jobs found")
            self.resume_button.setEnabled(False)
            self.discard_button.setEnabled(False)
            self.discard_all_button.setEnabled(False)
    
    def _on_selection_changed(self):
        """Enable/disable buttons based on selection."""
        has_selection = len(self.checkpoint_list.selectedItems()) > 0
        self.resume_button.setEnabled(has_selection)
        self.discard_button.setEnabled(has_selection)
    
    def _on_resume(self):
        """Resume selected job."""
        selected_items = self.checkpoint_list.selectedItems()
        if not selected_items:
            return
        
        item_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        self.selected_job = item_data
        self.action = 'resume'
        self.accept()
    
    def _on_discard(self):
        """Discard selected job."""
        selected_items = self.checkpoint_list.selectedItems()
        if not selected_items:
            return
        
        item_data = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not item_data:
            return
        
        # Confirm discard
        reply = QMessageBox.question(
            self,
            "Confirm Discard",
            "Are you sure you want to discard this checkpoint?\n"
            "You will lose all progress and have to start over.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete checkpoint file
            checkpoint_file = Path(item_data['checkpoint_file'])
            try:
                checkpoint_file.unlink()
                # Remove from list
                row = self.checkpoint_list.row(selected_items[0])
                self.checkpoint_list.takeItem(row)
                
                QMessageBox.information(
                    self,
                    "Checkpoint Discarded",
                    "The checkpoint has been deleted."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete checkpoint: {e}"
                )
    
    def _on_discard_all(self):
        """Discard all checkpoints."""
        if self.checkpoint_list.count() == 0:
            return
        
        # Confirm discard all
        reply = QMessageBox.question(
            self,
            "Confirm Discard All",
            f"Are you sure you want to discard ALL {self.checkpoint_list.count()} checkpoints?\n"
            "You will lose all progress on all interrupted jobs.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete all checkpoint files
            deleted = 0
            failed = 0
            
            for i in range(self.checkpoint_list.count()):
                item = self.checkpoint_list.item(i)
                item_data = item.data(Qt.ItemDataRole.UserRole)
                
                if item_data:
                    checkpoint_file = Path(item_data['checkpoint_file'])
                    try:
                        checkpoint_file.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {checkpoint_file}: {e}")
                        failed += 1
            
            # Clear list
            self.checkpoint_list.clear()
            
            QMessageBox.information(
                self,
                "Checkpoints Discarded",
                f"Deleted {deleted} checkpoint(s).\n"
                + (f"Failed to delete {failed} file(s)." if failed > 0 else "")
            )
    
    def get_result(self):
        """
        Get the user's action.
        
        Returns:
            Tuple of (action, job_data) where action is 'resume' or 'discard',
            or (None, None) if dialog was closed.
        """
        return self.action, self.selected_job


# Test/example usage
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Get checkpoint directory
    localappdata = Path.home() / "AppData" / "Local" / "Advanced_Tape_Restorer" / "checkpoints"
    
    dialog = CheckpointResumeDialog(localappdata)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        action, job_data = dialog.get_result()
        print(f"Action: {action}")
        print(f"Job: {job_data}")
    else:
        print("Dialog closed")
    
    sys.exit(0)
