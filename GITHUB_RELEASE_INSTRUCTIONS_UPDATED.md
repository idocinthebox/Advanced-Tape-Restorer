# GitHub Release v4.1.0 - Updated Instructions (File Too Large)

## ⚠️ GitHub File Size Limit: 2GB

Your EXE is **2.93GB** - exceeds GitHub's 2GB release asset limit.

**Solution:** Use Cloudflare R2 hosting + GitHub release notes with download link.

---

## Step 1: Upload to Cloudflare R2

1. Go to **Cloudflare Dashboard** → **R2**
2. Create a bucket (e.g., `tape-restorer-releases`)
3. Click **"Upload"** and select `dist/Advanced_Tape_Restorer_v4.1.exe`
4. Wait for upload to complete (~5-15 minutes depending on connection)
5. Click the uploaded file → **"Create Public URL"** or configure custom domain
6. **Copy the public URL**

**Your link will look like:**
```
https://pub-abc123.r2.dev/Advanced_Tape_Restorer_v4.1.exe
```

**Or with custom domain:**
```
https://downloads.yourdomain.com/Advanced_Tape_Restorer_v4.1.exe
```

**R2 Advantages:**
- ✅ No egress fees (free bandwidth)
- ✅ Fast global CDN (Cloudflare's network)
- ✅ Direct download links (no "Are you sure?" warnings)
- ✅ Custom domain support
- ✅ 10GB free storage per month

---

## Step 2: Create GitHub Release (With External Link)

1. Go to: https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer/releases
2. Click **"Draft a new release"**
3. **Tag version:** `v4.1.0`
4. **Release title:** `Advanced Tape Restorer v4.1.0 (FREE - MIT Licensed)`
5. **Target:** `main` branch

---

## Step 3: Use This Updated Release Notes Template

```markdown
# Advanced Tape Restorer v4.1.0

**FREE and Open Source** (MIT Licensed)

Professional video restoration suite for analog/DV tape capture with AI-powered restoration.

> ⚠️ **Note:** The executable is 3GB and exceeds GitHub's 2GB file limit. Download from Google Drive below.

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
**File:** Advanced_Tape_Restorer_v4.1.exe (2.93 GB)

> ⚠️ **Large Download Warning**  
> This file is **2.93 GB** and requires:
> - Stable internet connection (10+ Mbps recommended)
> - ~5GB free disk space
> - Estimated download time: 4-40 minutes depending on speed
> - **Wi-Fi recommended** for mobile users (saves cellular data)

⚠️ **Too large for GitHub** (2GB limit)

**Download from Cloudflare R2:**  
🔗 **[CLICK HERE TO DOWNLOAD](https://downloads.idocinthebox.com/Advanced_Tape_Restorer_v4.1_Windows.zip)**

**Download Tips:**
- Use a download manager for reliability ([Free Download Manager](https://www.freedownloadmanager.org/), [JDownloader](https://jdownloader.org/))
- Chrome/Edge browsers recommended (auto-resume on interruption)
- **Alternative:** Install from source below (only ~500MB total via pip)

**SHA256 Checksum:**
```
4293E5B971278E968BD3322E66EC9364ED834105ED87A03D50F31628982FEA98
```

**Download via Command Line (with resume support):**
```powershell
# Windows 10+ built-in curl (resumeable)
curl -L -C - -o Advanced_Tape_Restorer_v4.1_Windows.zip https://downloads.idocinthebox.com/Advanced_Tape_Restorer_v4.1_Windows.zip
```

**Verification (Windows PowerShell):**
```powershell
Get-FileHash "Advanced_Tape_Restorer_v4.1.exe" -Algorithm SHA256
```

**If hash doesn't match:** Re-download the file (likely corrupted/incomplete)

**What's Included:**
- Complete Python 3.13 runtime
- PyTorch 2.5 + ONNX Runtime
- All AI models and dependencies
- No installation required - just run!

---

### Option 2: Install from Source (Smaller Download)
**Best for:** Users comfortable with Python

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
- FFmpeg and VapourSynth (see Quick Start Guide)

**Recommended for AI:**
- NVIDIA GPU with 8GB+ VRAM (CUDA 11.8 or 12.1)
- 16GB+ system RAM
- NPU (Intel Core Ultra, AMD Ryzen AI) for ONNX acceleration

## 🚀 Quick Start

### For EXE Download:
1. **Download** from Google Drive link above
2. **Verify** SHA256 checksum matches
3. **Install prerequisites:**
   - FFmpeg: https://ffmpeg.org/download.html
   - VapourSynth R73: https://github.com/vapoursynth/vapoursynth/releases
4. **Run** the EXE - no installation needed!

### For Source Install:
1. **Install Python 3.11+** from https://python.org
2. **Clone repo** and install dependencies (see Option 2 above)
3. **Install prerequisites** (FFmpeg, VapourSynth)
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

The standalone EXE includes:
- Python runtime (~50MB)
- PyTorch 2.5 (~2.2GB) - Required for AI models
- ONNX Runtime (~200MB)
- NumPy, SciPy, OpenCV (~300MB)
- Application code (~200MB)

**Alternative:** Install from source to avoid large download. Pip manages dependencies more efficiently (~500MB total).

---

**⭐ If this project helped you restore precious memories, please star the repo!**

**💾 Recommended:** Bookmark the R2 download link for future downloads.
```

---

## Step 4: Attach Checksum File Only

Since the EXE is on Cloudflare R2, only attach:
- ✅ `Advanced_Tape_Restorer_v4.1_SHA256.txt`

Users will download the EXE from Cloudflare R2 and verify with your checksum.

---

## Step 5: Publish Release

1. Paste release notes above (URL already updated: downloads.idocinthebox.com)
2. Attach SHA256.txt file
3. Check **"Set as the latest release"**
4. Click **"Publish release"**

---

## Alternative Hosting Options

**Cloudflare R2 is ideal** for this use case (no egress fees, fast CDN). But if you need alternatives, see `ALTERNATIVE_HOSTING_OPTIONS.md` for:
- Google Drive (15GB free)
- OneDrive (5GB free)
- Mega.nz (50GB free)
- SourceForge (unlimited bandwidth)

**For v4.2 commercial:** Use Gumroad or Sellfy (handles payments + hosting).

---

## Pro Tip: Add Download Badge to README

Update your README.md with a download badge:

```markdown
[![Download v4.1](https://img.shields.io/badge/Download-v4.1.0-blue?style=for-the-badge&logo=cloudflare)](https://downloads.idocinthebox.com/Advanced_Tape_Restorer_v4.1_Windows.zip)
```

This makes it easy for users to find the download link directly from your repo homepage.

---

## Next Steps After Release

1. **Test download link** - Make sure it works in incognito mode
2. **Update README.md** with Google Drive link
3. **Announce release** on Reddit, forums, social media
4. **Monitor GitHub Issues** for bug reports
5. **Consider creating** a smaller build without PyTorch for future releases

---

**File size limits are a common issue for AI apps.** Many projects use external hosting. You're in good company! 🚀
