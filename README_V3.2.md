# Advanced Tape Restorer v3.2

**Professional Video Restoration & Capture Suite**  
**Release Date:** December 22, 2025

---

## 🆕 What's New in v3.2?

### Critical Fix: Simplified AI Plugin Integration

v3.2 fixes the dependency cascade issues that affected virgin installs in v3.0/v3.1:

- **Direct VapourSynth plugin usage** - no Python package imports needed
- **Auto-downloading models** - plugins handle everything internally
- **Better error messages** - shows exact installation commands
- **Zero Python dependencies** for AI upscaling features

**Result:** AI upscaling now works immediately after installing VapourSynth plugins via vsrepo!

---

## 📥 Quick Start (New Installation)

### 1. Install Prerequisites
```powershell
cd "C:\Advanced Tape Restorer v3.2\DISTRIBUTION\Setup"
.\Install_Prerequisites_Auto.bat
```

This installs:
- Python 3.12 (for vsrepo tool only)
- VapourSynth R73 (processing framework)
- FFmpeg (encoding/decoding)

### 2. Install VapourSynth Plugins
```powershell
.\Install_VapourSynth_Plugins.bat
```

This installs:
- Core plugins: `vsutil`, `havsfunc`, `ffms2`, `mvtools`
- AI plugins: `znedi3`, `bm3d`, `realesrgan` (optional)

### 3. Restart Computer
Restart to apply PATH changes.

### 4. Launch Application
```powershell
cd "C:\Advanced Tape Restorer v3.2"
python main.py
```

Or run the compiled EXE (after building):
```powershell
.\dist\Advanced_Tape_Restorer_v3.2.exe
```

---

## 🎯 Key Features

### Video Restoration
- **QTGMC Deinterlacing** - 7 quality presets (Draft to Placebo)
- **AI Upscaling** - RealESRGAN, BasicVSR++, SwinIR, ZNEDI3
- **Noise Reduction** - BM3D (GPU), Temporal denoise, FFT3D
- **Stabilization** - MVTools, Depan, SubShaker (auto-detect mode)
- **Artifact Removal** - VHS artifacts, ghosting, ringing, debanding
- **Color Correction** - Auto white balance, faded color restoration

### Capture (Mock Implementation)
- Analog device detection (VHS, Hi8, Video8)
- DV/miniDV FireWire capture
- **Note:** Capture backend not yet connected to real hardware

### Batch Processing
- Queue multiple restoration jobs
- Different settings per job
- Background processing
- Progress tracking

---

## 🔧 System Requirements

### Required:
- **OS:** Windows 10/11 (64-bit)
- **CPU:** Intel Core i5 or AMD Ryzen 5 (minimum)
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 100GB+ free space for video projects

### For AI Features:
- **GPU:** NVIDIA GTX 900 series or newer (CUDA support)
- **VRAM:** 4GB minimum, 8GB+ recommended for 4K
- **Drivers:** NVIDIA 545.84+ for CUDA 12.x support

---

## 📦 Dependencies

### External Tools (Must Install):
1. **FFmpeg** - Video encoding/decoding
2. **VapourSynth R73** - Processing framework
3. **Python 3.12** - To run vsrepo plugin installer
4. **VapourSynth Plugins** - Core and AI plugins

### Installation Scripts:
- `DISTRIBUTION/Setup/Install_Prerequisites_Auto.bat` - Installs FFmpeg, VapourSynth, Python
- `DISTRIBUTION/Setup/Install_VapourSynth_Plugins.bat` - Installs plugins via vsrepo
- `DISTRIBUTION/Setup/Diagnose_Test_System.bat` - Checks what's installed

---

## 🆚 v3.2 vs v3.1 vs v3.0

| Feature | v3.0 | v3.1 | v3.2 |
|---------|------|------|------|
| AI Upscaling | ✅ | ✅ | ✅ |
| Model Manager | ✅ | ✅ | 🔄 Bypassed |
| Direct Plugin Use | ❌ | ❌ | ✅ |
| Virgin Install Works | ❌ | ❌ | ✅ |
| Python Dependencies | Many | Many | None* |
| Auto-Download Models | Via Manager | Via Manager | Via Plugin |

*Python 3.12 still needed to run vsrepo for plugin installation

---

## 🚀 Usage

### Basic Restoration Workflow:

1. **Select Input Video:**
   - File → Select Input
   - Choose your VHS/analog/DV tape capture

2. **Configure Settings:**
   - **Restoration Tab:** QTGMC preset, sharpness, denoise
   - **Advanced Tab:** Temporal denoise, chroma denoise, color correction
   - **Output Tab:** Codec, quality (CRF), resolution

3. **Enable AI Upscaling (Optional):**
   - Check "Use AI Upscaling"
   - Select method: RealESRGAN (General 4x), BasicVSR++, SwinIR, or ZNEDI3
   - Models auto-download on first use!

4. **Start Processing:**
   - Click "Start Processing"
   - Monitor progress bar and console output
   - Output saved to specified location

### AI Upscaling Methods:

- **RealESRGAN (General 4x)** - Best for real-world footage, 4x upscale
- **RealESRGAN (2x)** - Faster, less aggressive upscaling
- **BasicVSR++** - Video-specific, temporal awareness (2x)
- **SwinIR** - Transformer-based, excellent quality (2x/4x)
- **ZNEDI3** - Fast CPU/GPU upscaling (2x, no model download)

---

## 🔍 Troubleshooting

### "vsrealesrgan plugin not installed"
```powershell
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install realesrgan
```

### "Total frames: 0" error
Missing ffms2 plugin:
```powershell
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install ffms2
```

### "No module named 'havsfunc'"
```powershell
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install vsutil
py -3.12 "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" install havsfunc
```

### Models not downloading?
- Check internet connection
- First run downloads ~500MB per model
- Models cache in: `%APPDATA%\VapourSynth\models\`

### Run Diagnostics:
```powershell
.\DISTRIBUTION\Setup\Diagnose_Test_System.bat
```

---

## 📚 Documentation

- **CHANGELOG_V3.2.md** - What's new in this release
- **REALESRGAN_DEPENDENCY_CLARIFICATION.md** - Explains dependency workflow
- **TEST_SYSTEM_REQUIREMENTS.md** - Virgin install requirements
- **.github/copilot-instructions.md** - Architecture and development guide
- **QUICK_START_GUIDE.md** - Step-by-step usage instructions

---

## 🏗️ Building from Source

### Development Setup:
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install PySide6 PyYAML requests

# Run from source
python main.py
```

### Build Executable:
```powershell
# Install PyInstaller
pip install pyinstaller

# Build single-file EXE
pyinstaller main.spec

# EXE output: dist\Advanced_Tape_Restorer_v3.2.exe
```

---

## 🤝 Contributing

### Development Philosophy (v3.2):
1. **Simplicity over abstraction** - Direct plugin usage beats complex managers
2. **Test on virgin installs** - Don't hide dependency issues
3. **Clear error messages** - Show exact installation commands
4. **Minimize dependencies** - Avoid Python packages in VapourSynth scripts

### Reporting Issues:
1. Run `Diagnose_Test_System.bat` and include output
2. Provide generated `.vpy` script (in project root or `%TEMP%`)
3. Include console error messages
4. Specify system specs (CPU, RAM, GPU)

---

## 📜 License

Advanced Tape Restorer v3.2 - Proprietary  
**External Dependencies:**
- VapourSynth: LGPL 2.1
- FFmpeg: LGPL 2.1 / GPL 2.0
- PySide6: LGPL 3.0
- vs-realesrgan: BSD-3-Clause
- RealESRGAN models: BSD-3-Clause

See `docs/THIRD_PARTY_LICENSES.md` for complete license information.

---

## 🔗 Links

- **VapourSynth:** https://github.com/vapoursynth/vapoursynth
- **FFmpeg:** https://ffmpeg.org/
- **vsrepo (plugin manager):** https://github.com/vapoursynth/vsrepo
- **vs-realesrgan:** https://github.com/HolyWu/vs-realesrgan
- **RealESRGAN:** https://github.com/xinntao/Real-ESRGAN

---

## 💬 Support

For issues, questions, or feature requests:
1. Check `TROUBLESHOOTING.md` documentation
2. Run diagnostic script: `Diagnose_Test_System.bat`
3. Review console output for specific error messages
4. Check VapourSynth plugin installation status

---

**Version:** 3.2.0  
**Release Date:** December 22, 2025  
**Critical Fix:** Direct VapourSynth plugin usage for virgin installs  
**Happy Restoring!** 🎬📼
