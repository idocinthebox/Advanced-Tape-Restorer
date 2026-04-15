# Advanced Tape Restorer v4.1.0

**FREE and Open Source** (MIT Licensed)

Professional video restoration suite for analog/DV tape capture with AI-powered restoration.

> ⚠️ **Note:** The distribution package is 3GB. Download from Cloudflare R2 (free bandwidth, fast CDN).

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

### Complete Distribution Package (Recommended)
**File:** Advanced_Tape_Restorer_v4.1_Windows.zip (2.93 GB)

> ⚠️ **Large Download Warning**  
> This file is **2.93 GB** and requires:
> - Stable internet connection (10+ Mbps recommended)
> - ~5GB free disk space
> - Estimated download time: 4-40 minutes depending on speed
> - **Wi-Fi recommended** for mobile users (saves cellular data)

**Download from Cloudflare R2:**  
🔗 **[CLICK HERE TO DOWNLOAD](https://downloads.idocinthebox.com/Advanced_Tape_Restorer_v4.1_Windows.zip)**

**Download Tips:**
- Use a download manager for reliability ([Free Download Manager](https://www.freedownloadmanager.org/), [JDownloader](https://jdownloader.org/))
- Chrome/Edge browsers recommended (auto-resume on interruption)
- **Alternative:** Install from source below (only ~500MB total via pip)

**Download via Command Line (with resume support):**
```powershell
# Windows 10+ built-in curl (resumeable)
curl -L -C - -o Advanced_Tape_Restorer_v4.1_Windows.zip https://downloads.idocinthebox.com/Advanced_Tape_Restorer_v4.1_Windows.zip
```

**SHA256 Checksum:**
```
FD48768F78ED28DDEAC024CD39BC155A0C8ADAF88247318F08C5CF4EFF527F62
```

**Verification (Windows PowerShell):**
```powershell
Get-FileHash "Advanced_Tape_Restorer_v4.1_Windows.zip" -Algorithm SHA256
```

**If hash doesn't match:** Re-download the file (likely corrupted/incomplete)

**What's Included:**
- Advanced_Tape_Restorer_v4.1.exe (standalone executable)
- Complete Python 3.13 runtime + PyTorch 2.5 + ONNX Runtime
- All AI models and dependencies
- LICENSE, README, configuration files
- **13 setup batch files** (one-click installation)
- No additional installation required - just extract and run!

---

### Option 2: Install from Source (Smaller Download)
**Best for:** Users comfortable with Python, slow connections, or developers

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer

# Install dependencies (~500MB total, managed by pip)
pip install -r requirements.txt

# Run application
python main.py
```

**Advantages:**
- **Much smaller download** (~500MB total vs 3GB)
- Faster setup on slow connections
- Easier to update dependencies
- Can modify source code

**Disadvantages:**
- Requires Python 3.11+ installed
- More setup steps (5-10 minutes)

**Recommended for:** Users with slow internet, mobile data users, or developers

---

## ⚙️ System Requirements

**Minimum:**
- Windows 10/11 (64-bit)
- 8GB RAM
- 10GB disk space
- FFmpeg and VapourSynth (auto-installed via FIRST_TIME_SETUP.bat)

**Recommended for AI:**
- NVIDIA GPU with 8GB+ VRAM (CUDA 11.8 or 12.1)
- 16GB+ system RAM
- NPU (Intel Core Ultra, AMD Ryzen AI) for ONNX acceleration

## 🚀 Quick Start

### For ZIP Download:
1. **Download** ZIP from link above
2. **Verify** SHA256 checksum matches
3. **Extract** to any folder
4. **Run FIRST_TIME_SETUP.bat** (installs FFmpeg + VapourSynth automatically)
5. **Restart** computer
6. **Launch** Advanced_Tape_Restorer_v4.1.exe
7. **Start restoring!**

### For Source Install:
1. **Install Python 3.11+** from https://python.org
2. **Clone repo** and install dependencies (see Option 2 above)
3. **Run FIRST_TIME_SETUP.bat** or manually install FFmpeg + VapourSynth
4. **Run** `python main.py`

**Detailed setup guide:** See [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md)

---

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

## 📊 Why 3GB?

The standalone ZIP includes:
- Python runtime (~50MB)
- PyTorch 2.5 (~2.2GB) - Required for AI models
- ONNX Runtime (~200MB)
- NumPy, SciPy, OpenCV (~300MB)
- Application code + setup scripts (~200MB)

**Alternative:** Install from source to avoid large download. Pip manages dependencies more efficiently (~500MB total).

---

**⭐ If this project helped you restore precious memories, please star the repo!**

**💾 Recommended:** Bookmark the download link for future updates.

**🔒 Secure:** Hosted on Cloudflare R2 with SHA256 verification - always verify checksum after download!
