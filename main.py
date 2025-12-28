"""
Advanced Tape Restorer v4.1
Professional Video Restoration & Capture Suite with Theatre Mode

Entry point for the application
"""

__version__ = "4.1.0"
__author__ = "AI Agent Team"

# Development bypass for NDA (set to True during development/testing)
# WARNING: Set to False before distributing to testers!
DEV_BYPASS_NDA = True  # Change to False for tester builds

import sys
import atexit
import shutil
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def check_python_availability():
    """
    Check if Python is available when running as frozen executable.
    
    Print a warning if Python interpreter cannot be found, as some features
    will be limited.
    """
    if not getattr(sys, "frozen", False):
        # Running from source - Python is obviously available
        return True
    
    # Running as frozen exe - try to find Python
    import shutil
    python_exe = shutil.which('python') or shutil.which('python3') or shutil.which('py')
    
    if not python_exe:
        print("[WARNING] ═══════════════════════════════════════════════════════")
        print("[WARNING] No Python interpreter found on system PATH")
        print("[WARNING] Some features may be limited:")
        print("[WARNING]   - Installing Python packages (pip)")
        print("[WARNING]   - Creating virtual environments (venv)")
        print("[WARNING]   - ProPainter setup wizard")
        print("[WARNING]")
        print("[WARNING] To enable all features, install Python 3.8+ and add to PATH")
        print("[WARNING] ═══════════════════════════════════════════════════════")
        return False
    else:
        print(f"[INFO] Python interpreter found: {python_exe}")
        return True


def cleanup_pyinstaller_temp():
    """Clean up PyInstaller temporary extraction folders (_MEI folders)."""
    try:
        # PyInstaller extracts to _MEIXXXXXX folders in temp directory
        if getattr(sys, "frozen", False):
            # We're running as compiled EXE
            temp_dir = Path(tempfile.gettempdir())
            current_mei = getattr(sys, "_MEIPASS", None)

            # Clean up old _MEI folders (not the current one)
            for item in temp_dir.glob("_MEI*"):
                if item.is_dir():
                    # Don't delete the currently running MEI folder
                    if current_mei and str(item) == current_mei:
                        continue

                    # Try to delete old MEI folders
                    try:
                        shutil.rmtree(item, ignore_errors=True)
                    except (PermissionError, OSError):
                        # Folder is locked or in use, skip it
                        pass
    except Exception:
        # Don't let cleanup errors affect app startup
        pass


# Register cleanup on exit
atexit.register(cleanup_pyinstaller_temp)

# Clean up old temp folders on startup
cleanup_pyinstaller_temp()

# Check Python availability and warn user if needed
check_python_availability()


def extract_ai_models_for_vapoursynth():
    """
    Extract ai_models package for VapourSynth access when running from PyInstaller exe.

    VapourSynth runs in a separate Python process and needs access to ai_models
    package. When running from exe, we extract it to the exe's directory.
    """
    if not getattr(sys, "frozen", False):
        # Running from source - no extraction needed
        return

    try:
        # Get paths
        exe_dir = Path(sys.executable).parent
        meipass = Path(sys._MEIPASS)

        # Source: ai_models in _MEIPASS (bundled in exe)
        source_ai_models = meipass / "ai_models"

        # Destination: ai_models next to exe
        dest_ai_models = exe_dir / "ai_models"

        # Check if extraction needed (don't re-extract every time)
        if dest_ai_models.exists():
            # Already extracted - skip
            return

        print(f"[PyInstaller] Extracting ai_models for VapourSynth access...")
        print(f"[PyInstaller] Source: {source_ai_models}")
        print(f"[PyInstaller] Destination: {dest_ai_models}")

        # Copy the entire ai_models directory
        if source_ai_models.exists():
            shutil.copytree(source_ai_models, dest_ai_models)
            print(f"[PyInstaller] ai_models extracted successfully!")
        else:
            print(f"[WARNING] ai_models not found in exe bundle at {source_ai_models}")

    except Exception as e:
        # Don't crash app if extraction fails
        print(f"[WARNING] Failed to extract ai_models: {e}")
        print("[WARNING] AI upscaling via VapourSynth may not work")


# Extract ai_models for VapourSynth when running from exe
extract_ai_models_for_vapoursynth()


def main_cli():
    """Command-line test mode."""
    print("=" * 60)
    print(f"Advanced Tape Restorer v{__version__} - Test Mode")
    print("=" * 60)
    print()
    print("Running module tests...")
    print()

    from test_modules import main as test_main

    return test_main()


def main_gui():
    """Launch graphical interface with splash screen."""
    import os
    import platform
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import QTimer

    # Initialize Qt app first (needed for dialogs)
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced Tape Restorer")
    app.setOrganizationName("Tape Restoration Tools")

    # Get tester ID early (used for both NDA and licensing)
    tester_id = os.getenv("ATR_TESTER_ID") or platform.node() or "UNKNOWN"

    # ========== LICENSE ACTIVATION (OPTIONAL) ==========
    # Community Edition is FREE - no activation required
    # Pro/Enterprise users can activate for additional features
    license_info = None
    try:
        from licensing import LicenseManager, show_gumroad_activation_dialog
        from pathlib import Path
        
        # Initialize license manager
        license_mgr = LicenseManager()
        
        # Check if activated
        if not license_mgr.is_activated():
            # Show OPTIONAL activation dialog with "Continue as Community" option
            # User can skip and use Community Edition for free
            activated = show_gumroad_activation_dialog(license_mgr, allow_skip=True)
            # NOTE: activated can be False (user chose Community Edition) - this is OK!
        
        # Get license info (None if using Community Edition)
        license_info = license_mgr.get_license_info()
        if license_info and license_info.days_remaining():
            days = license_info.days_remaining()
            if days <= 7:
                QMessageBox.warning(
                    None,
                    "License Expiring Soon",
                    f"Your {license_info.license_type.value} license expires in {days} days.\n\n"
                    "Please renew your license to continue using the software.\n"
                    "Visit: https://idocinthebox.com/advanced-tape-restorer"
                )
    
    except ImportError as e:
        QMessageBox.critical(
            None,
            "Licensing System Error",
            f"Licensing module not found:\n{e}\n\nPlease ensure licensing folder is present."
        )
        return 1
    except Exception as e:
        QMessageBox.critical(
            None,
            "Licensing System Error",
            f"Error during license check:\n{e}\n\nApplication cannot start."
        )
        return 1
    # ========== END LICENSE ACTIVATION ==========

    # ========== NDA ENFORCEMENT ==========
    if not DEV_BYPASS_NDA:
        try:
            from NDA.nda_enforcement import config as nda_config
            from NDA.nda_enforcement.config import get_default_config
            from NDA.nda_enforcement.hooks import on_app_start
            from NDA.nda_enforcement.pyside6_clickwrap import run_nda_clickwrap

            # Get NDA configuration (uses new simplified config system)
            cfg = get_default_config()
            
            # Construct path to NDA PDF using filename from config
            NDA_PDF_PATH = Path(__file__).parent / "NDA" / nda_config.nda_filename

            # Ensure NDA file exists
            if not NDA_PDF_PATH.exists():
                QMessageBox.critical(
                    None,
                    "NDA Missing",
                    f"NDA document not found at:\n{NDA_PDF_PATH}\n\n"
                    f"Expected: {nda_config.nda_filename}\n\n"
                    "Application cannot start."
                )
                return 1

            # Check if NDA acceptance exists
            allowed, msg = on_app_start(cfg, tester_id)
            if not allowed:
                # Show NDA acceptance dialog
                ok = run_nda_clickwrap(cfg, tester_id, nda_pdf_path=NDA_PDF_PATH)
                if not ok:
                    # User declined NDA
                    QMessageBox.warning(
                        None,
                        "NDA Required",
                        "You must accept the Beta NDA to use this software.\n\nApplication will now exit."
                    )
                    return 1

        except ImportError as e:
            QMessageBox.critical(
                None,
                "NDA System Error",
                f"NDA enforcement module not found:\n{e}\n\nPlease ensure NDA folder is present."
            )
            return 1
        except Exception as e:
            QMessageBox.critical(
                None,
                "NDA System Error",
                f"Error during NDA enforcement:\n{e}\n\nApplication cannot start."
            )
            return 1
    # ========== END NDA ENFORCEMENT ==========

    # NOTE: This imports from gui/ package (gui/main_window.py), NOT gui_simple_example.py
    # The gui/__init__.py file redirects to gui.main_window.MainWindow
    from gui import MainWindow
    from gui.splash_screen import SplashScreen

    # Show splash screen IMMEDIATELY
    splash = SplashScreen(
        program_name="Advanced Tape Restorer", version=f"v{__version__}"
    )
    splash.show()

    # Force immediate display of splash screen
    app.processEvents()

    # Deferred initialization of main window (allows splash to display first)
    window = None

    def load_main_window():
        """Load main window after splash is visible."""
        nonlocal window
        # This may take time with AI model initialization
        window = MainWindow()

        # Show main window and close splash after minimum display time
        def show_main_window():
            if window:
                splash.finish()
                window.show()

        # Keep splash visible for at least 2.5 seconds total
        QTimer.singleShot(2500, show_main_window)

    # Start loading main window after 100ms (lets splash render first)
    QTimer.singleShot(100, load_main_window)

    return app.exec()


def main():
    """Main entry point - launch GUI or test mode."""
    # Check for --test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        return main_cli()

    # Try to launch GUI, fall back to test mode if unavailable
    try:
        return main_gui()
    except ImportError as e:
        print(f"GUI not available: {e}")
        print("Falling back to test mode...")
        print()
        return main_cli()


if __name__ == "__main__":
    sys.exit(main())
