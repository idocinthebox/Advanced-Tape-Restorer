"""
GUI Module - PySide6 interface for Advanced Tape Restorer v3.0
Optimized with lazy loading for faster startup
"""

__version__ = "3.0.0"


def __getattr__(name):
    """
    Lazy import mechanism for GUI components.
    Components are only loaded when first accessed, improving startup time.
    """
    if name == "MainWindow":
        from .main_window import MainWindow

        return MainWindow
    elif name == "ProcessingThread":
        from .processing_thread import ProcessingThread

        return ProcessingThread
    elif name == "SettingsManager":
        from .settings_manager import SettingsManager

        return SettingsManager
    elif name == "PresetManager":
        from .settings_manager import PresetManager

        return PresetManager
    else:
        raise AttributeError(f"module 'gui' has no attribute '{name}'")
