"""
Python Utilities - Handle frozen executable detection and Python interpreter location

This module provides utilities to handle the differences between running from
source and running as a PyInstaller frozen executable.
"""

import sys
import shutil
from pathlib import Path


def is_frozen():
    """
    Check if the application is running as a frozen executable.
    
    Returns:
        bool: True if running as PyInstaller exe, False if running from source
    """
    return getattr(sys, 'frozen', False)


def get_python_executable():
    """
    Get the path to a usable Python interpreter.
    
    When running as a PyInstaller frozen executable, sys.executable points to the .exe,
    not a Python interpreter. This function tries to find a real Python interpreter.
    
    Returns:
        str or None: Path to Python executable, or None if running frozen without Python available
    """
    if is_frozen():
        # We're running as an .exe - sys.executable is the .exe, not Python
        # Try to find Python in common locations
        python_candidates = [
            shutil.which('python'),
            shutil.which('python3'),
            shutil.which('py'),  # Windows Python Launcher
        ]
        
        # Add common installation paths (Windows)
        if sys.platform == 'win32':
            for version in ['313', '312', '311', '310', '39', '38']:
                python_candidates.extend([
                    f'C:\\Python{version}\\python.exe',
                    f'C:\\Users\\{Path.home().name}\\AppData\\Local\\Programs\\Python\\Python{version}\\python.exe',
                ])
        
        # Find first valid Python
        for python_path in python_candidates:
            if python_path and Path(python_path).exists():
                # Verify it's actually Python
                try:
                    import subprocess
                    result = subprocess.run(
                        [python_path, '--version'],
                        capture_output=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                    if result.returncode == 0:
                        return python_path
                except Exception:
                    continue
        
        # No Python found
        return None
    else:
        # Running from source - sys.executable is the Python interpreter
        return sys.executable


def can_run_python_commands():
    """
    Check if Python commands (pip, venv, etc.) can be run.
    
    Returns:
        tuple: (bool, str) - (can_run, reason_message)
    """
    python_exe = get_python_executable()
    
    if python_exe is None:
        return (False,
                "No Python interpreter found. This application is running as a compiled executable. "
                "To install packages or use Python features, please install Python 3.8+ on your system.")
    
    return (True, "Python interpreter available")


def get_app_directory():
    """
    Get the application's directory.
    
    Returns:
        Path: Directory where the app is running from (either source dir or exe dir)
    """
    if is_frozen():
        # Running as exe - return exe directory
        return Path(sys.executable).parent
    else:
        # Running from source - return main.py directory
        return Path(__file__).parent.parent


def get_bundled_directory():
    """
    Get the bundled resources directory (for PyInstaller _MEIPASS).
    
    Returns:
        Path: Temporary extraction directory when frozen, source directory otherwise
    """
    if is_frozen() and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent
