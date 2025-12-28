# Test System Requirements Check
# Run this on the test system where RealESRGAN is failing

## What's Actually Needed for vsrealesrgan to Work:

### 1. VapourSynth R73 installed
- Check: `vspipe --version`

### 2. Python 3.12 installed (for vsrepo)
- Check: `py -3.12 --version`

### 3. VapourSynth plugins installed via vsrepo:
```powershell
# Locate vsrepo.py
dir "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py"

# Install required plugins
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" update
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install vsutil
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install havsfunc
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install ffms2
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install mvtools

# FOR REALESRGAN:
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan
```

### 4. Verify vsrealesrgan works:
```python
# Test script: test_vsrealesrgan.vpy
import vapoursynth as vs
from vsrealesrgan import realesrgan, RealESRGANModel

core = vs.core

# Create test clip
video = core.std.BlankClip(width=640, height=480, format=vs.RGB24, length=10)

# Try to use vsrealesrgan
try:
    print("[TEST] Attempting vsrealesrgan import...")
    video = realesrgan(
        video,
        model=RealESRGANModel.RealESRGAN_x2plus,
        auto_download=True,
        device_index=0
    )
    print("[OK] vsrealesrgan works!")
except Exception as e:
    print(f"[ERROR] vsrealesrgan failed: {e}")

video.set_output()
```

Test with: `vspipe --info test_vsrealesrgan.vpy -`

---

## The Problem with Your Current Scripts:

Your generated VapourSynth scripts are trying to import **your app's Python packages**:
```python
from ai_models.model_manager import ModelManager
from ai_models.engines.upscaling_realesrgan import apply as realesrgan_apply
```

These packages exist on your dev system (in the project folder) but NOT on virgin test systems!

## The Solution:

VapourSynth scripts should use **vsrealesrgan plugin directly**:
```python
from vsrealesrgan import realesrgan, RealESRGANModel
video = realesrgan(
    video,
    model=RealESRGANModel.RealESRGAN_x2plus,
    auto_download=True,
    device_index=0
)
```

This works because:
- vsrealesrgan is a VapourSynth plugin (installed via vsrepo)
- Plugin has bundled PyTorch inside the DLL
- Models auto-download to VapourSynth directory
- No Python package dependencies needed!

---

## Quick Fix for Test System:

Run on test system:
```bat
DISTRIBUTION\Setup\Install_VapourSynth_Plugins.bat
```

This will install:
- vsutil, havsfunc, ffms2, mvtools (required)
- Optional: znedi3, bm3d, realesrgan

Then test with: `DISTRIBUTION\Setup\Diagnose_Test_System.bat`
