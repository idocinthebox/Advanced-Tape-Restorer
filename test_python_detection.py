"""
Test script for Python detection utilities

Run this to test the new Python detection logic without starting the full GUI.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.python_utils import (
    is_frozen,
    get_python_executable,
    can_run_python_commands,
    get_app_directory,
    get_bundled_directory
)


def main():
    print("=" * 70)
    print("Python Detection Test")
    print("=" * 70)
    print()
    
    # Test frozen detection
    frozen = is_frozen()
    print(f"1. Running as frozen executable: {frozen}")
    print(f"   sys.executable: {sys.executable}")
    print()
    
    # Test Python executable location
    python_exe = get_python_executable()
    print(f"2. Python executable found: {python_exe}")
    if python_exe:
        print(f"   ✅ Python available at: {python_exe}")
    else:
        print(f"   ❌ No Python interpreter found")
    print()
    
    # Test if Python commands can run
    can_run, message = can_run_python_commands()
    print(f"3. Can run Python commands: {can_run}")
    print(f"   Message: {message}")
    print()
    
    # Test directory functions
    app_dir = get_app_directory()
    print(f"4. Application directory: {app_dir}")
    print(f"   Exists: {app_dir.exists()}")
    print()
    
    bundled_dir = get_bundled_directory()
    print(f"5. Bundled directory: {bundled_dir}")
    print(f"   Exists: {bundled_dir.exists()}")
    print()
    
    # Test actual Python version if available
    if python_exe:
        print("6. Testing Python executable:")
        import subprocess
        try:
            result = subprocess.run(
                [python_exe, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                print(f"   ✅ {version}")
            else:
                print(f"   ❌ Failed to get version (exit code {result.returncode})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    print()
    
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
