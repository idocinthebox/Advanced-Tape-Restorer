"""
View the splash screen standalone

Usage: python view_splash.py
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.splash_screen import SplashScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create splash screen (stays open until you close it)
    splash = SplashScreen(
        program_name="Advanced Tape Restorer",
        version="v4.1"
    )
    
    splash.show()
    
    print("Splash screen displayed. Close the window to exit.")
    
    sys.exit(app.exec())
