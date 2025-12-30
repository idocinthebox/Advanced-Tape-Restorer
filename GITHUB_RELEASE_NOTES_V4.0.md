# Advanced Tape Restorer v4.0.0 - Community Edition

**FREE Forever** (MIT Licensed) - No AI Features

Professional video restoration suite for analog/DV tape capture with traditional restoration filters. Perfect for users who need basic deinterlacing and cleanup without AI upscaling.

> 💡 **Want AI upscaling?** See [v4.1 Professional Edition](link-to-v4.1-release) - 8 AI models + ONNX/NPU ($45 Early Supporter / $150 Standard)

## 🎉 What's Included in v4.0 (FREE)

### 📹 Core Restoration Features
- **QTGMC deinterlacing** - 7 quality presets (Draft → Placebo)
- **Auto field-order detection** - TFF/BFF/Progressive
- **Temporal denoise** - FFT3D, KNLMeansCL, BM3D
- **Spatial denoise** - RemoveGrain, MCTemporalDenoise
- **Sharpening** - UnsharpMask, LSFmod
- **Color correction** - Auto levels, saturation, hue
- **Crop & resize** - Aspect ratio correction
- **Deflicker & degrain**

### 📹 Hardware Capture
- **DirectShow device detection** - Real analog capture cards
- **DV/FireWire support** - Digital camcorder capture
- **Analog inputs** - Composite, S-Video, Component selection
- **Lazy device loading** - Fast application startup

### ⚡ Performance Features
- **Multi-GPU support** - NVIDIA + AMD + Intel
- **Hardware encoders** - NVENC, AMF, Quick Sync
- **Threaded I/O** - 2-4x faster batch operations
- **Checkpoint/resume** - Continue interrupted jobs

### 💾 Output Formats
- H.264 (libx264, NVENC, AMF, Quick Sync)
- H.265/HEVC (libx265, NVENC HEVC, AMF HEVC)
- ProRes (all variants)
- DNxHD/DNxHR
- FFV1 (lossless archival)
- AV1 (experimental)

### 🖥️ User Interface
- PySide6 modern interface
- Restoration presets system
- Batch processing queue
- Real-time progress with ETA
- Preview window (before/after comparison)
- Settings persistence

## ❌ What's NOT Included (v4.0)

- ❌ AI upscaling models (RealESRGAN, RIFE, BasicVSR++, SwinIR, etc.)
- ❌ ONNX/NPU acceleration
- ❌ PyTorch JIT compilation
- ❌ Face restoration (GFPGAN)
- ❌ Colorization (DeOldify)
- ❌ Video inpainting (ProPainter)

**For AI features:** Upgrade to [v4.1 Professional Edition](#) ($45 Early Supporter / $150 Standard)

## 📥 Downloads

### Complete Package (Recommended)
**File:** Advanced_Tape_Restorer_v4.0_Community_Edition.zip (45.64 MB)

> ✅ **Lightweight Download!**  
> Only **46 MB** - perfect for:
> - Slow internet connections
> - Mobile data users
> - Quick setup (2-5 minutes download)
> - Low disk space environments

**Download from GitHub:**  
🔗 **[CLICK HERE TO DOWNLOAD v4.0 (46 MB)](Advanced_Tape_Restorer_v4.0_Community_Edition.zip)**

**SHA256 Checksum:**
```
91BD692ED4EB6336A86AEEAE68D160F72457FB337FD82E840AB95274BE246BD0
```

**Verification (Windows PowerShell):**
```powershell
Get-FileHash "Advanced_Tape_Restorer_v4.0_Community_Edition.zip" -Algorithm SHA256
```

**If hash doesn't match:** Re-download the file (likely corrupted/incomplete)

**What's Included:**
- Advanced_Tape_Restorer_v4.0.exe (45.92 MB standalone executable)
- LICENSE (MIT)
- README.md
- restoration_presets.json
- restoration_settings.json
- No additional installation required - just extract and run!

**Note:** FFmpeg and VapourSynth required (see Quick Start below)

---

### Option 2: Install from Source
**Best for:** Developers or users who want to modify the code

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer

# Checkout v4.0 branch/tag
git checkout v4.0

# Install dependencies (only core packages, no PyTorch)
pip install PySide6 PyYAML requests

# Run application
python main.py
```

**Advantages:**
- See and modify source code
- Smaller install (~100MB vs 46MB EXE)
- Easy to update dependencies
- No PyInstaller overhead

**Disadvantages:**
- Requires Python 3.11+ installed
- More setup steps (5 minutes)

---

## ⚙️ System Requirements

**Minimum:**
- Windows 10/11 (64-bit)
- 4GB RAM
- 1GB disk space
- FFmpeg and VapourSynth (see Quick Start)

**Recommended:**
- 8GB+ RAM
- NVIDIA/AMD/Intel GPU (hardware encoding)
- 5GB+ disk space (for temporary files)

**No GPU required!** Basic restoration works on CPU only.

---

## 🚀 Quick Start

### Windows (ZIP Download):
1. **Download** ZIP from link above (46 MB)
2. **Verify** SHA256 checksum matches
3. **Extract** to any folder (e.g., `C:\Programs\TapeRestorer`)
4. **Install dependencies:**
   - **FFmpeg:** Download from https://ffmpeg.org/download.html
   - **VapourSynth:** Download from https://www.vapoursynth.com/
   - Add both to Windows PATH
5. **Launch** Advanced_Tape_Restorer_v4.0.exe
6. **Start restoring!** No license key needed

**Detailed setup guide:** See [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md)

---

## 📖 Documentation

- [README.md](../README.md) - Project overview
- [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) - Detailed setup instructions
- [LICENSE](../LICENSE) - MIT License terms
- [VERSION_FEATURE_MATRIX.md](../VERSION_FEATURE_MATRIX.md) - v4.0 vs v4.1 vs v4.2 comparison

## 🆓 Free Forever (MIT License)

**v4.0 will ALWAYS remain free** under the MIT License. You can:
- ✅ Use commercially without restrictions
- ✅ Modify and redistribute the source code
- ✅ Fork and create derivative works
- ✅ No license keys or activation required
- ✅ No usage limits or restrictions

See [LICENSE](../LICENSE) for complete terms.

## 🔄 Upgrade to v4.1 for AI Features

**Want professional AI upscaling?**

**v4.1 Professional Edition ($45 Early Supporter / $150 Standard)** includes:
- ✅ All v4.0 features (MIT components remain free)
- ✅ 8 AI models (RealESRGAN 4x, RIFE, BasicVSR++, SwinIR, ZNEDI3, GFPGAN, DeOldify, ProPainter)
- ✅ ONNX/NPU acceleration (98% compression, 40x speedup, 4K support)
- ✅ PyTorch JIT compilation (20-30% AI speedup)
- ✅ Priority support (Standard edition - 48h email response)

**[Purchase v4.1 Early Supporter ($45) - Save 70%!](your-payment-link)**  
**[Purchase v4.1 Standard ($150) - Includes Priority Support](your-payment-link)**

**Compare versions:** [VERSION_FEATURE_MATRIX.md](../VERSION_FEATURE_MATRIX.md)

---

## 🐛 Known Issues

- VapourSynth plugins must be installed manually (vsrepo)
- Some capture cards may not be detected (DirectShow compatibility)
- Real-time preview can be slow on low-end CPUs

## 💬 Support

- **Community support:** GitHub Issues (free)
- **Documentation:** GitHub wiki and guides
- **No priority support** - v4.0 is community-maintained

For priority support, upgrade to [v4.1 Standard Edition](#).

## 📅 Roadmap

**v4.0 (FREE - Released December 2025):**
- ✅ Basic restoration features
- ✅ Hardware capture
- ✅ MIT licensed forever

**v4.1 (PAID - Released December 2025):**
- All 8 AI models + ONNX/NPU
- $45 Early Supporter / $150 Standard
- [See v4.1 Release](link-to-v4.1-release)

**v4.2 (Q2 2026) - Advanced Professional:**
- Audio restoration
- Project management
- Scene detection
- $150 one-time (free upgrade for v4.1 first year)

**v5.0 Pro/Enterprise (Q3-Q4 2026):**
- Network distributed rendering
- Render farm support
- Subscription pricing ($75-150/node/month)

See [VERSION_FEATURE_MATRIX.md](../VERSION_FEATURE_MATRIX.md) for complete comparison.

---

## ❤️ Credits

**Developed by:** [Your Name]  
**Built with:** Python, PySide6, VapourSynth, FFmpeg

**Special Thanks:**
- VapourSynth community
- FFmpeg team
- PyInstaller developers
- All contributors and testers

---

## 🆚 v4.0 vs v4.1 Comparison

| Feature | v4.0 (FREE) | v4.1 (PAID) |
|---------|-------------|-------------|
| **Download Size** | 46 MB | 2,944 MB |
| **Price** | Free forever | $45 / $150 |
| **License** | MIT | Dual (MIT + Proprietary) |
| **QTGMC Deinterlacing** | ✅ | ✅ |
| **Denoise/Color** | ✅ | ✅ |
| **Hardware Capture** | ✅ | ✅ |
| **Multi-GPU** | ✅ | ✅ |
| **AI Upscaling** | ❌ | ✅ 8 models |
| **ONNX/NPU** | ❌ | ✅ 40x speedup |
| **Face Restoration** | ❌ | ✅ GFPGAN |
| **Colorization** | ❌ | ✅ DeOldify |
| **Priority Support** | ❌ | ✅ (Standard) |

**Need AI features?** [Upgrade to v4.1](#)

---

## 📊 Why Only 46 MB?

**v4.0 excludes:**
- ❌ PyTorch 2.5 (~2.2GB)
- ❌ ONNX Runtime (~200MB)
- ❌ AI model files (~500MB)
- ❌ TorchScript compiler (~100MB)

**Result:** 98.4% smaller than v4.1!

**Perfect for:**
- Slow internet connections
- Limited disk space
- Users who don't need AI
- Quick deployment

---

## ⭐ If This Helped You

**This project is free and open source!**

If Advanced Tape Restorer helped you preserve precious memories:
- ⭐ **Star the repository** on GitHub
- 🐛 **Report bugs** via Issues
- 💡 **Suggest features** via Discussions
- 🤝 **Contribute** via Pull Requests

**Want to support development?**
- Consider purchasing [v4.1 Professional Edition](#) ($45 Early Supporter)
- Your purchase funds future v4.0 improvements!

---

## 🔒 Security & Privacy

- ✅ **Open source** - Inspect the code yourself (MIT licensed)
- ✅ **No telemetry** - Zero data collection
- ✅ **No internet required** - Works completely offline
- ✅ **SHA256 verified** - Always verify checksums after download
- ✅ **No license server** - No activation or registration

---

**💾 Recommended:** Bookmark this page for future updates  
**🆓 Always free:** v4.0 will never become paid software  
**🚀 Ready to start?** [Download v4.0 (46 MB)](#)  
**🤖 Want AI features?** [Upgrade to v4.1 ($45)](#)
