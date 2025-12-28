"""
PySide6 activation dialog for serial number entry
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .license_manager import LicenseManager


def show_activation_dialog(license_manager: LicenseManager, tester_id: str) -> bool:
    """
    Show activation dialog and return True if activated.
    
    Args:
        license_manager: LicenseManager instance
        tester_id: Tester identifier
    
    Returns:
        True if activated, False otherwise
    """
    dialog = ActivationDialog(license_manager, tester_id)
    result = dialog.exec()
    
    return result == QDialog.Accepted and dialog.is_activated()


class ActivationDialog(QDialog):
    """Dialog for entering and validating serial number"""
    
    def __init__(self, license_manager: LicenseManager, tester_id: str, parent=None):
        super().__init__(parent)
        
        self.license_manager = license_manager
        self.tester_id = tester_id
        self.activated = False
        
        self.setWindowTitle("Advanced Tape Restorer - Activation")
        self.setMinimumWidth(550)
        self.setMinimumHeight(400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Activate Advanced Tape Restorer v4.1")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info text
        info = QLabel(
            "Please enter your activation code to unlock the full version.\n"
            "Beta testers receive activation codes via email after NDA acceptance."
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Hardware ID group
        hw_group = QGroupBox("Machine Information")
        hw_layout = QVBoxLayout()
        
        hw_label = QLabel(f"Hardware ID: {self.license_manager.get_hardware_id()}")
        hw_label.setStyleSheet("font-family: monospace; color: #666;")
        hw_layout.addWidget(hw_label)
        
        hw_note = QLabel(
            "Note: Activation codes are bound to your hardware ID.\n"
            "Contact support if you need to transfer your license."
        )
        hw_note.setWordWrap(True)
        hw_note.setStyleSheet("font-size: 10px; color: #888;")
        hw_layout.addWidget(hw_note)
        
        hw_group.setLayout(hw_layout)
        layout.addWidget(hw_group)
        
        # Serial number entry
        serial_group = QGroupBox("Activation Code")
        serial_layout = QVBoxLayout()
        
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("ATR-XXXX-XXXX-XXXX-XXXX-XXXX")
        self.serial_input.setFont(QFont("Courier New", 11))
        self.serial_input.setMaxLength(29)  # ATR + 4 groups of 4 chars + 1 group of 8 chars + dashes
        self.serial_input.textChanged.connect(self.format_serial_input)
        serial_layout.addWidget(self.serial_input)
        
        serial_group.setLayout(serial_layout)
        layout.addWidget(serial_group)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Activate")
        self.activate_btn.clicked.connect(self.on_activate)
        self.activate_btn.setDefault(True)
        
        self.trial_btn = QPushButton("Continue Trial (7 days)")
        self.trial_btn.clicked.connect(self.on_trial)
        
        self.cancel_btn = QPushButton("Exit")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.activate_btn)
        button_layout.addWidget(self.trial_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Help link
        help_label = QLabel(
            '<a href="mailto:support@idocinthebox.com">Need help? Contact support</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("color: #0066cc; font-size: 10px;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
    
    def format_serial_input(self, text: str):
        """Auto-format serial number with dashes"""
        # Remove existing dashes and spaces
        clean = text.replace("-", "").replace(" ", "").upper()
        
        # Block cursor position
        cursor_pos = self.serial_input.cursorPosition()
        
        # Format with dashes: ATR-XXXX-XXXX-XXXX-XXXX-XXXX
        if clean.startswith("ATR"):
            clean = clean[3:]  # Remove ATR prefix temporarily
        
        formatted = "ATR"
        for i, char in enumerate(clean[:20]):  # Limit to 20 chars after ATR
            if i % 4 == 0 and i > 0:
                formatted += "-"
            formatted += char
        
        # Update without triggering textChanged again
        self.serial_input.blockSignals(True)
        self.serial_input.setText(formatted)
        self.serial_input.setCursorPosition(min(cursor_pos + 1, len(formatted)))
        self.serial_input.blockSignals(False)
    
    def on_activate(self):
        """Handle activation button click"""
        serial = self.serial_input.text().strip()
        
        if not serial:
            self.status_label.setText("⚠ Please enter an activation code")
            self.status_label.setStyleSheet("padding: 10px; background: #fff3cd; border-radius: 5px; color: #856404;")
            return
        
        # Attempt activation
        success, message = self.license_manager.activate(serial, self.tester_id)
        
        if success:
            self.status_label.setText(f"✓ {message}")
            self.status_label.setStyleSheet("padding: 10px; background: #d4edda; border-radius: 5px; color: #155724;")
            self.activated = True
            
            # Close dialog after brief delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)
        else:
            self.status_label.setText(f"✗ {message}")
            self.status_label.setStyleSheet("padding: 10px; background: #f8d7da; border-radius: 5px; color: #721c24;")
    
    def on_trial(self):
        """Handle trial mode"""
        reply = QMessageBox.question(
            self,
            "Trial Mode",
            "Start 7-day trial?\n\n"
            "You can activate with a serial number at any time.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Generate trial serial (T type, 7 days)
            from .crypto_utils import generate_serial_number
            trial_serial = generate_serial_number(
                "trial",
                self.license_manager.get_hardware_id(),
                self.tester_id,
                expiry_days=7
            )
            
            success, message = self.license_manager.activate(trial_serial, self.tester_id)
            
            if success:
                QMessageBox.information(
                    self,
                    "Trial Activated",
                    "7-day trial activated successfully!\n\n"
                    "You can purchase a full license at:\n"
                    "https://idocinthebox.com/advanced-tape-restorer"
                )
                self.activated = True
                self.accept()
            else:
                QMessageBox.critical(self, "Trial Error", f"Failed to activate trial:\n{message}")
    
    def is_activated(self) -> bool:
        """Check if activation was successful"""
        return self.activated

