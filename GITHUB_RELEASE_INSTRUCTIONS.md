# GitHub Release v4.1.0 - Upload Instructions

## Build Complete! ✅

**Built files ready for GitHub:**
- `dist/Advanced_Tape_Restorer_v4.1.exe` (3.0 GB)
- `Advanced_Tape_Restorer_v4.1_SHA256.txt` (checksums)

---

## Upload to GitHub Releases

### Step 1: Create New Release
1. Go to: https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer/releases
2. Click **"Draft a new release"**
3. **Tag version:** `v4.1.0`
4. **Release title:** `Advanced Tape Restorer v4.1.0 (FREE - MIT Licensed)`
5. **Target:** `main` branch

### Step 2: Release Notes Template
```markdown
# Advanced Tape Restorer v4.1.0

**FREE and Open Source** (MIT Licensed)

Professional video restoration suite for analog/DV tape capture with AI-powered restoration.

## 🎉 What's New in v4.1

### ONNX/NPU Acceleration (NEW!)
- **98% model compression** - RealESRGAN 3.82MB → 0.16MB
- **40x faster inference** - 2.5ms vs 100ms per frame on NPU
- **DirectML support** - NPU + GPU + CPU fallback
- **VRAM savings** - Offload models to NPU, free 6-8GB GPU memory
- **Enable 4K processing** - Models that failed on 8GB GPUs now work

### AI Models
- RealESRGAN 4x upscaling (ONNX + PyTorch)
- RIFE frame interpolation (ONNX + PyTorch)
- BasicVSR++ video restoration (ONNX + PyTorch)
- SwinIR 2x/3x/4x upscaling (ONNX + PyTorch)
- GFPGAN face restoration
- DeOldify colorization

### Performance Enhancements
- Multi-GPU support (NVIDIA + AMD + Intel)
- PyTorch JIT compilation (20-30% speedup)
- Threaded I/O (2-4x faster batch operations)
- Checkpoint/resume system (continue interrupted jobs)

### Capture Hardware (DirectShow)
- Real analog capture device detection
- DV/FireWire camera support
- Lazy device loading (faster startup)

## 📥 Downloads

### Option 1: Standalone Executable (Recommended)
**File:** `Advanced_Tape_Restorer_v4.1.exe` (3.0 GB)

**Includes:**
- Complete Python 3.13 runtime
- PyTorch 2.5 + ONNX Runtime
- All AI models and dependencies
- No installation required - just run!

**SHA256:** See `Advanced_Tape_Restorer_v4.1_SHA256.txt`

### Option 2: Source Code
Clone the repository and install dependencies:
```bash
git clone https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer
pip install -r requirements.txt
python main.py
```

## ⚙️ System Requirements

**Minimum:**
- Windows 10/11 (64-bit)
- 8GB RAM
- 10GB disk space
- FFmpeg and VapourSynth (see Quick Start Guide)

**Recommended for AI:**
- NVIDIA GPU with 8GB+ VRAM (CUDA 11.8 or 12.1)
- 16GB+ system RAM
- NPU (Intel Core Ultra, AMD Ryzen AI) for ONNX acceleration

## 🚀 Quick Start

1. **Download** `Advanced_Tape_Restorer_v4.1.exe`
2. **Verify** SHA256 checksum (see .txt file)
3. **Install prerequisites:**
   - FFmpeg: https://ffmpeg.org/download.html
   - VapourSynth R73: https://github.com/vapoursynth/vapoursynth/releases
4. **Run** the EXE - no installation needed!
5. **Read** QUICK_START_GUIDE.md for detailed setup

## 📖 Documentation

- [README.md](../README.md) - Project overview
- [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) - Setup instructions
- [LICENSE](../LICENSE) - MIT License terms
- [VERSION_FEATURE_MATRIX.md](../VERSION_FEATURE_MATRIX.md) - v4.2/v5.0 roadmap

## 🆓 Free Forever (MIT License)

This version (v4.1) will **always remain free** under the MIT License. Future commercial versions (v4.2+) will add premium features while keeping the core v4.1 functionality open source.

## 🐛 Known Issues

- First ONNX inference slow (~500ms) - subsequent frames 2-5ms
- GFPGAN requires Python 3.11/3.12 (3.13 incompatible)
- Some AI models require 12GB+ VRAM (use ONNX to reduce)

## 💬 Support

- **Community:** GitHub Issues (free support)
- **Commercial:** Coming in v4.2 (priority support available)

## 📅 Roadmap

**v4.2 (Q2 2026) - Commercial Release:**
- Audio restoration (FFT noise reduction, declicking)
- Project management system
- Scene detection
- Batch presets
- 1-year priority support ($45 Early Supporter, $150 Standard)

**v5.0 Pro/Enterprise - Network Rendering:**
- Multi-machine distributed processing
- Render farm support
- REST API
- Subscription pricing ($75-150/node/month)

See [VERSION_FEATURE_MATRIX.md](../VERSION_FEATURE_MATRIX.md) for complete feature comparison.

---

## ❤️ Credits

Developed by: [Your Name]
Built with: Python, PySide6, VapourSynth, FFmpeg, PyTorch, ONNX

**AI Models:**
- RealESRGAN (Tencent)
- RIFE (MEGVII)
- BasicVSR++ (CUHK)
- SwinIR (Microsoft Research)
- GFPGAN (Tencent)
- DeOldify (Jason Antic)

**Special Thanks:**
- VapourSynth community
- PyInstaller team
- All contributors and testers

---

**⭐ If this project helped you restore precious memories, please star the repo!**
```

### Step 3: Attach Files
1. Drag `dist/Advanced_Tape_Restorer_v4.1.exe` into the release assets
2. Drag `Advanced_Tape_Restorer_v4.1_SHA256.txt` into the release assets

### Step 4: Publish
1. Check **"Set as the latest release"**
2. Click **"Publish release"**

---

## 📊 File Information

**Advanced_Tape_Restorer_v4.1.exe:**
- Size: 3,147,364,855 bytes (~3.0 GB)
- SHA256: 4293E5B971278E968BD3322E66EC9364ED834105ED87A03D50F31628982FEA98
- Python: 3.13.9
- PyInstaller: 6.16.0
- License: MIT

**Why so large?**
The EXE includes the complete Python runtime, PyTorch (~2GB), ONNX Runtime, all dependencies, and AI model loaders. Users don't need to install anything except FFmpeg and VapourSynth.

**Alternative:** Users can also clone the repo and install via `pip install -r requirements.txt` for a smaller installation (dependencies managed separately).

---

## ⚠️ Important: Do NOT Upload v4.2 Files

Keep these files **private** (not on GitHub):
- LICENSE_V4.2.txt (commercial EULA)
- LICENSE_SUMMARY_FOR_BUYERS.md
- LICENSING_GUIDE.md (contains pricing)
- CODE_SEPARATION_IMPLEMENTATION.md

These will be used for the paid v4.2 release on a private distribution platform (Gumroad, Sellfy, etc.) in Q2 2026.

---

## Next Steps After Release

1. **Announce** on social media, Reddit (r/DataHoarder, r/VHS), video forums
2. **Monitor** GitHub Issues for bug reports
3. **Update** README.md with download badge/link
4. **Collect feedback** to improve v4.2 features
5. **Implement** code separation (/core_mit/ and /proprietary_v42/) before v4.2 development

---

**Build completed:** December 29, 2025  
**Ready for upload!** 🚀
