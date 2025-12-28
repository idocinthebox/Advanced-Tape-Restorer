"""
AI Models UI - Model browser and management dialogs

Provides GUI components for:
    - Browsing available AI models from registry
    - Downloading models with progress tracking
    - Viewing model metadata (license, version, size)
    - Managing installed models

Version: 3.0.0
"""

__version__ = "3.0.0"

# Deferred import to avoid PySide6 requirement when not using GUI
__all__ = ["ModelBrowser"]
