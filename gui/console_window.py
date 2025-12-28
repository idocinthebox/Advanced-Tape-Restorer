"""
Console Window - Detachable console output window
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class ConsoleWindow(QDialog):
    """Separate floating window for console output."""
    
    closed = Signal()  # Emitted when window is closed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Tape Restorer - Console")
        self.resize(900, 400)
        
        # Make it a normal window (not modal)
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout()
        
        # Console text area
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas, monospace; font-size: 10pt;"
        )
        layout.addWidget(self.console_text)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Console")
        clear_btn.clicked.connect(self.clear_console)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close Window")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def append_message(self, message: str):
        """Append message to console."""
        self.console_text.append(message)
    
    def clear_console(self):
        """Clear console text."""
        self.console_text.clear()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.closed.emit()
        event.accept()
