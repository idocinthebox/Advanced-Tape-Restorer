# RealESRGAN Dependency Workflow - CLARIFICATION

## Your Question: Do I need to run AI installers first?

**SHORT ANSWER: NO - You do NOT need to run `Install_PyTorch_CUDA.bat` for RealESRGAN to work!**

---

## The Confusion Explained

There are **TWO completely separate ways** to use AI models in Advanced Tape Restorer:

### Method 1: VapourSynth Plugins (What We Actually Use) ✅
**This is how the app ACTUALLY works:**
- RealESRGAN runs via `vsrealesrgan` plugin (VapourSynth)
- RIFE runs via `vsrife` plugin (VapourSynth)
- These plugins have **built-in PyTorch** (bundled inside the plugin DLLs)
- Models are **auto-downloaded** by the plugins themselves
- **NO PYTHON REQUIRED** - runs in separate vspipe process
- **NO PYTORCH INSTALLATION NEEDED** by the user

### Method 2: Standalone Python Tools (What We DON'T Use) ❌
**This is what `Install_PyTorch_CUDA.bat` installs:**
- Standalone PyTorch for **external** tools only
- ProPainter (external app, not VapourSynth)
- GFPGAN (can run standalone)
- Custom Python scripts
- **NOT used by the main app's restoration features**

---

## What You ACTUALLY Need to Install

### REQUIRED for RealESRGAN to work:

#### 1. FFmpeg
```powershell
# Check if installed:
ffmpeg -version
```
**Purpose:** Video encoding/decoding

#### 2. VapourSynth R73 (Installer version, NOT portable)
```powershell
# Check if installed:
vspipe --version
```
**Purpose:** Video processing framework

#### 3. VapourSynth Plugins (via vsrepo)
```powershell
# Locate vsrepo.py:
dir "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"

# Install plugins using Python 3.12:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" update
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install vsutil havsfunc ffms2 mvtools znedi3 bm3d
```

**Critical plugins:**
- `vsutil` - Required by havsfunc
- `havsfunc` - Contains QTGMC deinterlacing
- `ffms2` - Video source filter
- `mvtools` - Motion compensation
- `znedi3` - Fast AI upscaling
- `bm3d` - GPU denoising (optional but recommended)

#### 4. For RealESRGAN specifically (optional, auto-downloads):
```powershell
# This is optional - vsrealesrgan auto-downloads models
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan
```

**The `vsrealesrgan` plugin will auto-download RealESRGAN models on first use!**

---

## The Correct Installation Workflow

### Step 1: Install Prerequisites
```powershell
# From DISTRIBUTION\Setup\ folder:
.\Install_Prerequisites_Auto.bat
```
This installs:
- Python 3.12 (for vsrepo.py only)
- VapourSynth R73
- FFmpeg

### Step 2: Install VapourSynth Plugins
```powershell
# From DISTRIBUTION\Setup\ folder:
.\Install_VapourSynth_Plugins.bat
```
This installs:
- vsutil, havsfunc, ffms2, mvtools, znedi3, bm3d

### Step 3: (OPTIONAL) Install RealESRGAN Plugin
```powershell
# Only if you want RealESRGAN upscaling:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan

# Or let it auto-download on first use (happens automatically)
```

### Step 4: (OPTIONAL) Install PyTorch for External Tools
```powershell
# ONLY if you want ProPainter or standalone tools:
.\Install_PyTorch_CUDA.bat
```
**NOT NEEDED for the app's built-in AI features!**

---

## Why `vsrealesrgan` Dependencies Are Confusing

Looking at the code in `ai_models/engines/upscaling_realesrgan.py`:

```python
from vsrealesrgan import realesrgan, RealESRGANModel

def apply(clip, model="realesr_general_x4v3", ...):
    return realesrgan(
        clip,
        device_index=device_index,
        model=model_enum,
        auto_download=True,  # ← Models auto-download!
        denoise_strength=denoise_strength,
        tile=tile,
        tile_pad=tile_pad
    )
```

**Key points:**
1. `auto_download=True` - Models download automatically
2. `vsrealesrgan` plugin has **bundled PyTorch** inside the DLL
3. No separate PyTorch installation needed
4. Models cache in VapourSynth directory

---

## What Dependencies Do You Actually Have?

Based on the errors you're seeing, you're likely missing:

### Missing: VapourSynth Plugins
**Symptom:** "Total frames: 0" or "ffms2 not found"

**Fix:**
```powershell
# Find vsrepo.py:
dir "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"

# Install core plugins:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install vsutil
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install havsfunc
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install ffms2
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install mvtools

# Verify:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" installed
```

### NOT Missing: PyTorch (for app features)
You **don't need** PyTorch for RealESRGAN/RIFE in the main app!

---

## Common Misunderstandings

### ❌ Myth: "I need to install PyTorch for AI upscaling"
**Reality:** VapourSynth plugins have PyTorch built-in

### ❌ Myth: "Install_PyTorch_CUDA.bat is required"
**Reality:** Only for standalone external tools (ProPainter, etc.)

### ❌ Myth: "I need Python for video processing"
**Reality:** Python is only needed to run vsrepo.py to install plugins

### ❌ Myth: "AI models need manual installation"
**Reality:** `vsrealesrgan` and `vsrife` auto-download models

---

## Verification Checklist

Run these commands to verify your setup:

```powershell
# 1. Check FFmpeg
ffmpeg -version
# Should show: ffmpeg version x.x.x

# 2. Check VapourSynth
vspipe --version
# Should show: VapourSynth Video Processing Library

# 3. Check Python 3.12 (for vsrepo only)
py -3.12 --version
# Should show: Python 3.12.x

# 4. Find vsrepo.py
dir "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"
# Should show the file path

# 5. Check installed plugins
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" installed
# Should list: vsutil, havsfunc, ffms2, mvtools, etc.

# 6. Test VapourSynth can load plugins
python -c "import vapoursynth as vs; core = vs.core; print('ffms2:', hasattr(core, 'ffms2'))"
# Should show: ffms2: True

# 7. Check if PyTorch is installed (optional check)
python -c "import torch; print('PyTorch:', torch.__version__)"
# If this works: PyTorch is installed (but NOT required for app!)
# If this fails: That's OKAY - app will work fine!
```

---

## The Two Separate Systems

### System 1: VapourSynth Pipeline (What the App Uses)
```
Input Video
    ↓
FFmpeg (read video)
    ↓
VapourSynth (vspipe.exe - separate process)
    ↓ Uses plugins:
    - ffms2 (video source)
    - havsfunc (QTGMC deinterlacing)
    - vsrealesrgan (AI upscaling with bundled PyTorch)
    - vsrife (frame interpolation with bundled PyTorch)
    ↓
FFmpeg (encode output)
    ↓
Output Video
```

**No Python environment needed!** Runs in separate vspipe process.

### System 2: Standalone Python Tools (External Only)
```
Input Video
    ↓
Python script with PyTorch
    ↓
ProPainter / GFPGAN / Custom tools
    ↓
Output Video
```

**Requires:** Python + PyTorch + GPU drivers  
**NOT used by:** The main app's restoration features

---

## Final Answer to Your Question

### Do I need to run Install_PyTorch_CUDA.bat first?

**NO!** 

For **RealESRGAN in the app**, you need:
1. ✅ FFmpeg
2. ✅ VapourSynth R73
3. ✅ Python 3.12 (to run vsrepo.py)
4. ✅ VapourSynth plugins via vsrepo

You do **NOT** need:
- ❌ Install_PyTorch_CUDA.bat
- ❌ Separate PyTorch installation
- ❌ Manual model downloads

### The vsrealesrgan plugin handles everything:
- Bundles PyTorch inside the plugin DLL
- Auto-downloads models on first use
- Manages GPU/CUDA automatically
- Runs in isolated vspipe process

---

## Quick Start (Correct Order)

```powershell
# 1. Install prerequisites
cd "C:\Advanced Tape Restorer v3.0\DISTRIBUTION\Setup"
.\Install_Prerequisites_Auto.bat

# 2. Restart computer (for PATH changes)

# 3. Install VapourSynth plugins
.\Install_VapourSynth_Plugins.bat

# 4. Test everything
.\Check_Prerequisites.bat

# 5. Launch app and test RealESRGAN
# Models will auto-download on first use!
```

**No PyTorch installation needed!** 🎉

---

## What If I Already Installed PyTorch?

That's fine! It won't interfere with the app.

But know that:
- The app's AI features **don't use** your PyTorch installation
- They use the PyTorch **bundled inside** vsrealesrgan/vsrife plugins
- Your PyTorch is only used by standalone tools (ProPainter, etc.)

---

## Troubleshooting RealESRGAN Issues

### Error: "vsrealesrgan not found"
```powershell
# Install the plugin:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan
```

### Error: "Total frames: 0"
```powershell
# Missing core plugins (ffms2):
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install ffms2
```

### Error: "CUDA not available"
The `vsrealesrgan` plugin will fall back to CPU mode automatically.
For GPU acceleration, ensure:
- NVIDIA drivers installed (545.84+ for CUDA 12.x)
- GPU supports CUDA (GTX 900 series or newer)

### Models not downloading?
First run may take time to download (~500MB per model).
Check: `%APPDATA%\VapourSynth\models\` for downloaded models.

---

**Last Updated:** December 22, 2024  
**Issue:** Confusion between VapourSynth plugins (built-in PyTorch) vs standalone PyTorch installation  
**Clarification:** RealESRGAN works via vsrealesrgan plugin (auto-download, bundled PyTorch) - no separate PyTorch needed!
