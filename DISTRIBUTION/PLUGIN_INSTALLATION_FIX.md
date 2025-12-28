# VapourSynth Plugin Installation Fix

## Problem
"Total frames: 0" error when processing video = VapourSynth plugins not installed

## Root Cause
**vsrepo.py** is bundled with VapourSynth installer but is NOT a Python package on PyPI.  
It's a standalone script that must be run by full path using Python 3.12.

GitHub repo: https://github.com/vapoursynth/vsrepo

## Solution - Install Plugins Correctly

### Quick Fix (Run These Commands):

**Locate vsrepo.py first:**
```powershell
# User-level install (Install for ME only)
dir "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"

# System-level install (Install for all users)
dir "C:\Program Files\VapourSynth\vsrepo\vsrepo.py"
```

**Install plugins using correct path:**
```powershell
# Replace path with your actual vsrepo.py location

# Update plugin database
py -3.12 "C:\Users\YourName\AppData\Local\Programs\VapourSynth\vsrepo\vsrepo.py" update

# Install essential plugins (vsutil must be installed first - havsfunc dependency)
py -3.12 "C:\Users\YourName\AppData\Local\Programs\VapourSynth\vsrepo\vsrepo.py" install vsutil havsfunc ffms2 mvtools bm3d znedi3

# Verify installation
py -3.12 "C:\Users\YourName\AppData\Local\Programs\VapourSynth\vsrepo\vsrepo.py" installed
```

### Verify Plugins Work:

Run the test script:
```
Setup\Test_VapourSynth_Plugins.bat
```

Or test manually:
```powershell
python -c "import vapoursynth as vs; core = vs.core; print('ffms2:', hasattr(core, 'ffms2'))"
```

Should output: `ffms2: True`

## Critical Plugins

### REQUIRED (app won't work without these):
- **vsutil** - Utility functions (required by havsfunc)
- **ffms2** - Video source filter (reads video files)
- **havsfunc** - Contains QTGMC deinterlacing (depends on vsutil)
- **mvtools** - Motion vector tools (required by QTGMC)

### RECOMMENDED:
- **bm3d** - GPU denoising
- **znedi3** - Fast AI upscaling

## Automated Installer Updated

The fixed installers now:
1. Locate vsrepo.py in VapourSynth installation directory
   - `%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py` (user install)
   - `C:\Program Files\VapourSynth\vsrepo\vsrepo.py` (system install)
2. Use Python 3.12 launcher to run it by full path: `py -3.12 "path\to\vsrepo.py" install ...`

### Test on Fresh Machine:
1. Run: `Setup\Install_Prerequisites_Auto.bat`
2. Restart computer (for PATH changes)
3. Run: `Setup\Test_VapourSynth_Plugins.bat`
4. Launch app and test video processing

## Troubleshooting

### "vsrepo.py not found"
vsrepo.py is bundled with VapourSynth R73 **installer** (not portable version).

**Solution:** Reinstall VapourSynth using the installer:
- Download: https://github.com/vapoursynth/vapoursynth/releases/download/R73/VapourSynth-x64-R73.exe
- Choose "Install for ME only" (matches Python 3.12 user-level install)

### "ffms2: False" after installation
Try reinstalling:
```powershell
# Find your vsrepo.py path first
py -3.12 "path\to\vsrepo.py" update
py -3.12 "path\to\vsrepo.py" install ffms2 --force
```

### Verify vsrepo.py is working:
```powershell
# Replace with your actual path
set VSREPO="%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"

# List available plugins
py -3.12 %VSREPO% available

# List installed plugins
py -3.12 %VSREPO% installed

# Update plugin database
py -3.12 %VSREPO% update
```

## Manual Plugin Installation (if vsrepo.py fails or missing)

If VapourSynth portable version was installed (doesn't include vsrepo.py):

1. Download plugins manually from: https://github.com/vapoursynth/vsrepo-data/tree/master/plugins
2. Extract `.dll` files to:
   - **Windows:** `%APPDATA%\VapourSynth\plugins64\`
3. Download Python scripts (havsfunc) to:
   - **Windows:** `%APPDATA%\VapourSynth\`

**OR** reinstall VapourSynth using the installer (not portable) to get vsrepo.py.

## Test Video Processing

After plugin installation, test with:
1. Launch `Advanced_Tape_Restorer_v3.exe`
2. Load a test video
3. Click "Analyze Video" - should show frame count
4. If still shows "Total frames: 0" - plugins not loaded

Check VapourSynth can find plugins:
```powershell
python -c "import vapoursynth as vs; print([p.namespace for p in vs.core.plugins()])"
```

Should see: `ffms2`, `mv`, `bm3d`, etc.

---

**Date Fixed:** December 21, 2024  
**Issue:** Installer assumed vsrepo was included with VapourSynth (it's not)  
**Solution:** Install vsrepo via pip before using it to install plugins
