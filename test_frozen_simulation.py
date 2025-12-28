"""
Test script to simulate running as frozen executable (without Python)

This helps test the error handling when Python is not available.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def simulate_frozen_without_python():
    """Simulate running as frozen executable without Python on PATH."""
    
    # Temporarily set sys.frozen to simulate PyInstaller
    sys.frozen = True
    sys.executable = "C:\\Program Files\\Advanced Tape Restorer\\Advanced_Tape_Restorer.exe"
    
    # Temporarily hide Python from search
    import shutil
    original_which = shutil.which
    
    def fake_which(cmd, *args, **kwargs):
        """Return None for python/python3/py to simulate no Python on PATH."""
        if cmd in ['python', 'python3', 'py']:
            return None
        return original_which(cmd, *args, **kwargs)
    
    shutil.which = fake_which
    
    # Now test the utilities
    from utils.python_utils import (
        is_frozen,
        get_python_executable,
        can_run_python_commands,
    )
    
    print("=" * 70)
    print("Simulated Frozen Executable Test (No Python)")
    print("=" * 70)
    print()
    
    print(f"1. Running as frozen executable: {is_frozen()}")
    print(f"   sys.executable: {sys.executable}")
    print()
    
    python_exe = get_python_executable()
    print(f"2. Python executable found: {python_exe}")
    if python_exe:
        print(f"   ✅ Python available at: {python_exe}")
    else:
        print(f"   ❌ No Python interpreter found (EXPECTED BEHAVIOR)")
    print()
    
    can_run, message = can_run_python_commands()
    print(f"3. Can run Python commands: {can_run}")
    print(f"   Message: {message}")
    print()
    
    # Test what happens when trying to install a package
    print("4. Simulating package installation attempt:")
    try:
        from gui.model_installer_dialog import get_python_executable as get_py
        py = get_py()
        if py:
            print(f"   ✅ Would use: {py}")
        else:
            print(f"   ❌ No Python - installation would fail with clear error message")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Restore original functions
    shutil.which = original_which
    del sys.frozen
    
    print("=" * 70)
    print("Simulation Complete")
    print("This is what users see when running .exe without Python installed")
    print("=" * 70)


if __name__ == "__main__":
    simulate_frozen_without_python()
