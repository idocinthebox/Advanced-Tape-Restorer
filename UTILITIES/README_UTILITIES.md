# Advanced Tape Restorer v4.0 - Utilities

This folder contains optional troubleshooting and debugging utilities.

## Normal Usage

**Users should NOT need these utilities for regular use.**

Simply double-click `Advanced_Tape_Restorer_v4.0.exe` to launch the application.

---

## Utilities

### Force_Cache_Cleanup.bat
**When to use:** App hanging at loading screen, weird behavior, or after crashes

**What it does:**
1. Stops all running instances
2. Clears Python `__pycache__` folders
3. Removes PyInstaller temp folders (`_MEI*`)
4. Deletes VapourSynth temp scripts

**How to use:**
```
Double-click Force_Cache_Cleanup.bat
Wait for cleanup to complete
Launch the app normally
```

---

### Launch_With_Console.bat
**When to use:** Debugging issues, seeing error messages, reporting bugs

**What it does:**
- Rebuilds the EXE with console output enabled
- Launches the debug version with visible console window
- Shows all log messages and errors

**How to use:**
```
Double-click Launch_With_Console.bat
App launches with console window
Check console for error messages
```

**Note:** Requires PyInstaller and source code to rebuild

---

### Emergency_Cleanup.ps1
**When to use:** Severe corruption, multiple cache issues

**What it does:**
- PowerShell version of Force_Cache_Cleanup
- More thorough cleanup
- Handles locked files

**How to use:**
```powershell
Right-click Emergency_Cleanup.ps1
Select "Run with PowerShell"
```

---

## Support

If these utilities don't resolve your issue, check:
1. `TROUBLESHOOTING.md` in the DOCUMENTATION folder
2. GitHub Issues: [Your GitHub URL]
3. Project Wiki: [Your Wiki URL]
