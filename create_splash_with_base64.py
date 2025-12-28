"""
Helper script to create splash_screen.py with embedded base64 image
"""

import base64

# Read the image and convert to base64
with open("idocinthebox_creations.jpg", "rb") as f:
    image_data = f.read()
    image_b64 = base64.b64encode(image_data).decode("utf-8")

# Create the splash_screen.py with embedded image
splash_code = (
    '''"""
Splash Screen for Advanced Tape Restorer v3.1
Displays branded loading screen with embedded image (no external files needed)
"""

import base64
from io import BytesIO
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


# Embedded splash image (base64 encoded)
SPLASH_IMAGE_B64 = """'''
    + image_b64
    + '''"""


class SplashScreen(QWidget):
    """Animated splash screen with fade-in and loading animation."""

    def __init__(self, program_name="Advanced Tape Restorer", version="v3.1"):
        super().__init__()

        # --- WINDOW CONFIG ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Base window size (fixed to match splash image)
        self.setFixedSize(900, 500)

        # --- BACKGROUND IMAGE (EMBEDDED) ---
        self.bg_label = QLabel(self)

        # Decode base64 image
        image_data = base64.b64decode(SPLASH_IMAGE_B64)
        pix = QPixmap()
        pix.loadFromData(image_data)

        if pix.isNull():
            print("ERROR: Cannot load embedded splash image")

        scaled_pix = pix.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.bg_label.setPixmap(scaled_pix)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()   # Ensures background stays *behind* all text

        # --- TEXT OVERLAY LAYOUT ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # TITLE
        self.title = QLabel(program_name)
        self.title.setStyleSheet("""
            color: white;
            font-size: 40px;
            font-weight: bold;
            text-shadow: 2px 2px 4px #000000;
        """)
        self.title.setAlignment(Qt.AlignCenter)

        # VERSION
        self.version = QLabel(version)
        self.version.setStyleSheet("""
            color: #DDDDDD;
            font-size: 22px;
            text-shadow: 1px 1px 4px #000;
        """)
        self.version.setAlignment(Qt.AlignCenter)

        # LOADING TEXT (animated)
        self.loading = QLabel("Loading")
        self.loading.setStyleSheet("""
            color: white;
            font-size: 18px;
            text-shadow: 1px 1px 4px #000;
        """)
        self.loading.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(self.title)
        layout.addWidget(self.version)
        layout.addSpacing(50)
        layout.addWidget(self.loading)
        layout.addStretch()

        # --- ANIMATED LOADING DOTS ---
        self.dot_state = 0
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self.animate_loading_text)
        self.dot_timer.start(450)  # dot cycles every 0.45s

        # --- FADE-IN ANIMATION ---
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(1200)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.start()

        # Center the splash screen on screen
        self.center_on_screen()

    def center_on_screen(self):
        """Center the splash screen on the primary screen."""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def animate_loading_text(self):
        """Cycle through loading dots animation."""
        dots = ["", ".", "..", "..."]
        self.dot_state = (self.dot_state + 1) % 4
        self.loading.setText(f"Loading{dots[self.dot_state]}")

    def finish(self):
        """Stop animations and close the splash screen."""
        self.dot_timer.stop()
        self.close()
'''
)

# Write the new splash_screen.py
with open("gui/splash_screen.py", "w", encoding="utf-8") as f:
    f.write(splash_code)

print("Created gui/splash_screen.py with embedded base64 image")
print(f"Image size: {len(image_data)} bytes")
print(f"File size: {len(splash_code)} bytes")
