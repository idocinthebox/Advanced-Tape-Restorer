"""
Gumroad-compatible activation dialog (email + license key)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .license_manager import LicenseManager


class GumroadActivationDialog(QDialog):
    """Dialog for Gumroad email + license key activation"""
    
    def __init__(self, license_manager: LicenseManager, allow_skip: bool = False, parent=None):
        super().__init__(parent)
        
        self.license_manager = license_manager
        self.activated = False
        self.skipped = False  # Track if user chose Community Edition
        self.allow_skip = allow_skip  # Whether to show "Continue Free" button
        
        self.setWindowTitle("Advanced Tape Restorer - Activation")
        self.setMinimumWidth(550)
        self.setMinimumHeight(450)
        
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
        if self.allow_skip:
            info = QLabel(
                "Community Edition is 100% FREE with all features unlocked!\n\n"
                "🎉 Early Adopter Special: Get Pro version at discounted price!\n"
                "Limited time offer for early supporters.\n\n"
                "Or enter your email and license key if you already purchased Pro/Enterprise."
            )
        else:
            info = QLabel(
                "Enter the email and license key from your purchase confirmation."
            )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Email input
        email_group = QGroupBox("Email Address")
        email_layout = QVBoxLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("customer@example.com")
        self.email_input.setFont(QFont("Segoe UI", 10))
        email_layout.addWidget(self.email_input)
        
        email_note = QLabel("Use the email address from your purchase")
        email_note.setStyleSheet("font-size: 10px; color: #666;")
        email_layout.addWidget(email_note)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # License key input
        license_group = QGroupBox("License Key")
        license_layout = QVBoxLayout()
        
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("IDOC-ATR-XXXX-XXXX-XXXX")
        self.license_input.setFont(QFont("Courier New", 11))
        self.license_input.setMaxLength(24)  # IDOC-ATR + 4-4-8
        self.license_input.textChanged.connect(self.format_license_input)
        license_layout.addWidget(self.license_input)
        
        license_note = QLabel("License key from your email confirmation")
        license_note.setStyleSheet("font-size: 10px; color: #666;")
        license_layout.addWidget(license_note)
        
        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("Activate Pro Version")
        self.activate_btn.clicked.connect(self.on_activate)
        self.activate_btn.setDefault(True)
        
        # Trial button (hidden until Pro version ready - code preserved for future use)
        # TODO: Re-enable as "7-Day Pro Trial" when Pro version launches
        # self.trial_btn = QPushButton("Start 7-Day Trial")
        # self.trial_btn.clicked.connect(self.on_trial)
        
        # Community Edition button (only shown if allow_skip=True)
        if self.allow_skip:
            self.community_btn = QPushButton("Continue with Community Edition (Free)")
            self.community_btn.clicked.connect(self.on_community)
            self.community_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            button_layout.addWidget(self.community_btn)
        
        self.cancel_btn = QPushButton("Exit")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.activate_btn)
        # button_layout.addWidget(self.trial_btn)  # Hidden - see above TODO
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Help links
        help_layout = QHBoxLayout()
        
        purchase_label = QLabel(
            '🎁 <a href="https://idocinthebox.com/advanced-tape-restorer">Get Pro - Early Adopter Discount!</a>'
        )
        purchase_label.setOpenExternalLinks(True)
        purchase_label.setAlignment(Qt.AlignLeft)
        purchase_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        support_label = QLabel(
            '<a href="mailto:support@idocinthebox.com">Need Help?</a>'
        )
        support_label.setOpenExternalLinks(True)
        support_label.setAlignment(Qt.AlignRight)
        
        help_layout.addWidget(purchase_label)
        help_layout.addStretch()
        help_layout.addWidget(support_label)
        
        layout.addLayout(help_layout)
        
        self.setLayout(layout)
    
    def format_license_input(self, text: str):
        """Auto-format license key with dashes"""
        # Remove existing dashes and spaces
        clean = text.replace("-", "").replace(" ", "").upper()
        
        # Block cursor position
        cursor_pos = self.license_input.cursorPosition()
        
        # Format with dashes: IDOC-ATR-XXXX-XXXX-XXXX
        if clean.startswith("IDOCATR"):
            clean = clean[7:]  # Remove IDOCATR prefix temporarily
            
            formatted = "IDOC-ATR"
            for i, char in enumerate(clean[:13]):
                if i % 4 == 0 and i > 0:
                    formatted += "-"
                formatted += char
            
            # Update without triggering textChanged again
            self.license_input.blockSignals(True)
            self.license_input.setText(formatted)
            self.license_input.setCursorPosition(min(cursor_pos + 1, len(formatted)))
            self.license_input.blockSignals(False)
        elif clean and not clean.startswith("IDOC"):
            # Auto-add prefix if user starts typing
            formatted = "IDOC-ATR-" + clean[:13]
            self.license_input.blockSignals(True)
            self.license_input.setText(formatted)
            self.license_input.setCursorPosition(len(formatted))
            self.license_input.blockSignals(False)
    
    def on_activate(self):
        """Handle activation button click"""
        email = self.email_input.text().strip()
        license_key = self.license_input.text().strip()
        
        if not email:
            self.status_label.setText("⚠ Please enter your email address")
            self.status_label.setStyleSheet("padding: 10px; background: #fff3cd; border-radius: 5px; color: #856404;")
            return
        
        if not license_key:
            self.status_label.setText("⚠ Please enter your license key")
            self.status_label.setStyleSheet("padding: 10px; background: #fff3cd; border-radius: 5px; color: #856404;")
            return
        
        # Attempt activation
        success, message = self.license_manager.activate_gumroad(email, license_key)
        
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
            "You can activate with a license key at any time.\n\n"
            "Trial requires an email address for identification.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            email = self.email_input.text().strip()
            
            if not email:
                QMessageBox.warning(self, "Email Required", "Please enter an email address for the trial.")
                return
            
            # Generate trial license
            from .crypto_utils import generate_serial_number_gumroad
            trial_key = generate_serial_number_gumroad(email, "trial")
            
            success, message = self.license_manager.activate_gumroad(email, trial_key, is_trial=True)
            
            if success:
                QMessageBox.information(
                    self,
                    "Trial Activated",
                    f"7-day trial activated!\n\n"
                    f"Email: {email}\n\n"
                    "Purchase a full license at:\n"
                    "https://idocinthebox.com/advanced-tape-restorer"
                )
                self.activated = True
                self.accept()
            else:
                QMessageBox.critical(self, "Trial Error", f"Failed to activate trial:\n{message}")
    
    def on_community(self):
        """Handle Community Edition (free) selection"""
        reply = QMessageBox.question(
            self,
            "Continue with Community Edition",
            "You're choosing the Community Edition (100% Free)\n\n"
            "✓ All restoration features unlocked\n"
            "✓ Unlimited resolution (4K, 8K, any size)\n"
            "✓ All AI models available\n"
            "✓ No restrictions\n\n"
            "You can activate a Pro license at any time from Settings.\n\n"
            "Continue with Community Edition?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.skipped = True
            self.accept()  # Close dialog and let app start
    
    def is_activated(self) -> bool:
        """Check if activation was successful"""
        return self.activated


def show_gumroad_activation_dialog(license_manager: LicenseManager, allow_skip: bool = False) -> bool:
    """
    Show Gumroad activation dialog and return True if activated.
    
    Args:
        license_manager: LicenseManager instance
        allow_skip: If True, user can skip and use Community Edition (default: False)
    
    Returns:
        True if activated, False otherwise (includes skipping for Community Edition)
    """
    dialog = GumroadActivationDialog(license_manager, allow_skip=allow_skip)
    result = dialog.exec()
    
    # Return True if activated OR if user chose to skip (Community Edition)
    # The distinction doesn't matter - app will work either way
    return result == QDialog.Accepted or (allow_skip and dialog.skipped)
