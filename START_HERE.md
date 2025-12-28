# 🚨 APP WON'T START? READ THIS FIRST!

## The app is stuck at loading screen and won't close

### ✅ SOLUTION: Use Clean Start Script

**Just double-click this file:**
```
Clean_Start.bat
```

This will automatically:
- ✅ Kill stuck processes
- ✅ Clear cache
- ✅ Restart the app fresh

---

## If that doesn't work:

### Option 1: Emergency Cleanup (PowerShell)
Right-click `Emergency_Cleanup.ps1` → Run with PowerShell

### Option 2: Manual Force Close
1. Open Task Manager (`Ctrl+Shift+Esc`)
2. Find all `python.exe` processes
3. Right-click → End Task (for each one)
4. Run `Clean_Start.bat`

### Option 3: Command Line
```powershell
# Force kill Python
taskkill /F /IM python.exe /T

# Clear cache
cd "C:\Advanced Tape Restorer v4.0"
Remove-Item -Recurse -Force __pycache__, gui\__pycache__, core\__pycache__

# Restart
python main.py
```

---

## What was fixed?

The loading screen hang was caused by capture device detection running on startup. This has been fixed:

- ✅ Device detection no longer runs on startup
- ✅ Devices load automatically when you open the Capture tab
- ✅ App starts much faster
- ✅ No more hanging at splash screen

---

## Quick Start Guide

1. **Close any stuck processes** (Task Manager or Clean_Start.bat)
2. **Run** `Clean_Start.bat` (double-click it)
3. **Close the command prompt** - The app will stay open!
4. **Click** Capture tab if you need capture devices

**Optional:** Run `Create_Desktop_Shortcut.bat` to add a desktop icon for easy access.

---

## Files in this folder:

| File | Purpose |
|------|---------|
| `Clean_Start.bat` | **Normal start** - Launches app, you can close the window |
| `Clean_Start_With_Console.bat` | **Debug mode** - Shows console output, keep window open |
| `Emergency_Cleanup.ps1` | PowerShell script for thorough cleanup |
| `FIX_LOADING_SCREEN.md` | Detailed troubleshooting guide |
| `main.py` | Main application (use Clean_Start.bat instead) |

### Which one to use?

- **`Clean_Start.bat`** - Normal daily use
  - Launches the app in background
  - You can close the command prompt window
  - App stays running independently

- **`Clean_Start_With_Console.bat`** - For troubleshooting
  - Shows console output and errors
  - Keep the window open to see logs
  - Useful for debugging issues

---

## Still having issues?

Check the console output for errors and see `FIX_LOADING_SCREEN.md` for detailed troubleshooting.

**Quick diagnostics:**
```powershell
# Test if Python works
python --version

# Test if FFmpeg works
ffmpeg -version

# Test capture module directly
python capture.py --test-detection
```

---

**✅ The app should now start normally!**

If you still have problems, the console will show what's wrong.
