# How to Fix the Stuck Loading Screen

## Problem
The app hangs at the loading screen and won't close.

## Quick Fix

### Option 1: Use the Clean Start Script (Recommended)
1. Close VS Code or any terminal windows showing the error
2. Double-click `Clean_Start.bat` in the project folder
3. The script will automatically:
   - Kill stuck Python processes
   - Clear cache files
   - Launch the app fresh

### Option 2: Manual Fix
1. **Force close the app:**
   - Press `Ctrl+C` in the terminal where it's running
   - Or open Task Manager (Ctrl+Shift+Esc)
   - End all `python.exe` processes

2. **Clear Python cache:**
   ```powershell
   cd "C:\Advanced Tape Restorer v4.0"
   Remove-Item -Recurse -Force __pycache__, gui\__pycache__, core\__pycache__ -ErrorAction SilentlyContinue
   ```

3. **Restart the app:**
   ```powershell
   python main.py
   ```

## What Was Fixed

The issue was caused by the app trying to detect capture devices on startup, which was causing a hang. I've fixed it by:

1. **Disabled startup device detection** - Devices no longer load during app startup
2. **Added lazy loading** - Devices now load automatically when you click the Capture tab for the first time
3. **Added "Refresh Devices" button** - You can manually refresh at any time

## Using Capture Devices Now

When you open the app:
1. Go to the **Capture** tab
2. Devices will automatically load (first time only)
3. Or click **"Refresh Devices"** button to scan again

## If It Still Hangs

If the app still hangs:
1. Check console output for errors
2. Try starting without capture support:
   ```powershell
   # Temporarily rename capture.py to skip import
   Rename-Item capture.py capture.py.bak
   python main.py
   # Rename it back later
   Rename-Item capture.py.bak capture.py
   ```

3. Check FFmpeg is installed:
   ```powershell
   ffmpeg -version
   ```

## Clean Start Script Details

The `Clean_Start.bat` file does:
1. Kills any stuck Python processes
2. Removes all `__pycache__` folders
3. Deletes all `.pyc` bytecode files
4. Launches the app with a clean slate

**Use this anytime the app won't start properly!**

---

**Status:** ✅ FIXED - App should now start normally
