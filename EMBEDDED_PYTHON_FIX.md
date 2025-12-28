# Embedded Python Fix - December 2025

## Problem
When running the application as a compiled `.exe` (PyInstaller frozen executable) on another computer, it failed with an error about "embedded python". 

The issue was that some parts of the code were using `sys.executable` to try to run Python commands like `pip install` or `python -m venv`. However, when running as a frozen executable, `sys.executable` points to the `.exe` file itself, not a Python interpreter.

## Root Causes

1. **model_installer_dialog.py** - Line 69: Used `sys.executable` for pip install
2. **propainter_setup_dialog.py** - Line 209: Used `sys.executable` for venv check

When these tried to run commands like `"Advanced Tape Restorer.exe" -m pip install`, they would fail because the exe is not Python.

## Solution

### 1. Created Python Utilities Module (`utils/python_utils.py`)
A comprehensive utility module that:
- Detects if running as frozen executable (`is_frozen()`)
- Finds real Python interpreter on the system (`get_python_executable()`)
- Checks if Python commands can be run (`can_run_python_commands()`)
- Provides proper path resolution for frozen/unfrozen states

### 2. Updated Code to Use Utilities
- **model_installer_dialog.py**: Now uses `get_python_executable()` with proper error handling
- **propainter_setup_dialog.py**: Checks for real Python before trying venv commands

### 3. Added Startup Warning (`main.py`)
When running as frozen exe without Python on PATH, the application now shows a clear warning:
```
[WARNING] ═══════════════════════════════════════════════════════════
[WARNING] No Python interpreter found on system PATH
[WARNING] Some features may be limited:
[WARNING]   - Installing Python packages (pip)
[WARNING]   - Creating virtual environments (venv)
[WARNING]   - ProPainter setup wizard
[WARNING]
[WARNING] To enable all features, install Python 3.8+ and add to PATH
[WARNING] ═══════════════════════════════════════════════════════════
```

### 4. Better Error Messages
When package installation fails, users now see:
```
Cannot install packages: No Python interpreter found.
This application is running as a compiled executable.
Please install packages manually or run from Python source.
```

## Files Modified

1. **main.py** - Added `check_python_availability()` function
2. **gui/model_installer_dialog.py** - Updated to use `get_python_executable()`
3. **gui/propainter_setup_dialog.py** - Updated venv detection logic
4. **utils/python_utils.py** - NEW: Comprehensive Python detection utilities
5. **utils/__init__.py** - NEW: Utils package initialization

## Testing Checklist

### Test as Frozen Executable (.exe)

1. **Build the exe**:
   ```batch
   pyinstaller Advanced_Tape_Restorer_v2.spec
   ```

2. **Copy exe to clean computer** (or move to different folder without Python)

3. **Test startup**:
   - Run the exe
   - Check console output for Python availability warning
   - GUI should still launch successfully

4. **Test with Python on PATH**:
   - Install Python 3.8+ on the test computer
   - Add Python to system PATH
   - Run the exe again
   - Should see "[INFO] Python interpreter found: C:\\..."
   - Package installation should work

5. **Test without Python on PATH**:
   - Remove Python from PATH (or use computer without Python)
   - Run the exe
   - Should see warning messages
   - Try to install a model that requires pip
   - Should see clear error message about missing Python

### Test from Source

1. **Run from source**:
   ```batch
   python main.py
   ```
   
2. **No warnings should appear** (Python is obviously available)

3. **Package installation should work normally**

## How It Works

### Detection Flow
```
Application Starts
    ↓
Is sys.frozen == True?
    ↓
NO → Running from source → Use sys.executable (it's Python)
    ↓
YES → Running as .exe → Search for Python on system
    ↓
Check common Python locations:
  - shutil.which('python')
  - shutil.which('python3')
  - shutil.which('py')
  - C:\Python3XX\python.exe
  - C:\Users\...\AppData\Local\Programs\Python\...
    ↓
Found Python? → Use it
    ↓
No Python? → Show warning, disable Python-dependent features
```

### Feature Availability Matrix

| Feature | Running from Source | Frozen exe + Python | Frozen exe - No Python |
|---------|-------------------|---------------------|----------------------|
| GUI Interface | ✅ Yes | ✅ Yes | ✅ Yes |
| Video Processing | ✅ Yes | ✅ Yes | ✅ Yes |
| AI Models (VapourSynth) | ✅ Yes | ✅ Yes | ✅ Yes |
| Package Installation | ✅ Yes | ✅ Yes | ❌ No (clear error) |
| ProPainter Setup | ✅ Yes | ✅ Yes | ⚠️ Limited |
| venv Creation | ✅ Yes | ✅ Yes | ❌ No (clear message) |

## Future Improvements

1. **Bundle Python with exe**: Could use PyInstaller's `--onefile` with embedded Python
2. **Pre-install dependencies**: Include all required packages in the frozen bundle
3. **Download Python**: Add option to download and install Python from within the app
4. **Portable Python**: Include a portable Python distribution with the exe

## User Instructions (For Compiled exe)

If you're running the compiled executable and see Python-related warnings:

### Option 1: Install Python (Recommended)
1. Download Python 3.8 or newer from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart the application
4. All features will be available

### Option 2: Use Pre-configured Package
1. Ensure all Python dependencies are pre-installed on the system
2. The app will work for video processing without Python interpreter access
3. Manual model installation may be required

### Option 3: Run from Source
1. Install Python 3.8+
2. Install requirements: `pip install -r requirements.txt`
3. Run: `python main.py`
4. Full functionality with direct Python access
