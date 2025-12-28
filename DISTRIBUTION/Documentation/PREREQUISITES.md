# Prerequisites for Advanced Tape Restorer .exe

## Required External Tools

The Advanced Tape Restorer executable bundles the Python application and its Python libraries, but **external video processing tools must be installed separately** on each computer where you run the .exe.

---

## ✅ **REQUIRED Prerequisites** (Application Won't Work Without These)

### 1. FFmpeg
**What it does:** Video encoding, decoding, format conversion, and analysis  
**Required for:** All video processing operations

**Installation:**
1. Download from https://www.gyan.dev/ffmpeg/builds/ (Windows builds)
2. Choose "ffmpeg-release-essentials.zip" or "ffmpeg-release-full.zip"
3. Extract to a folder (e.g., `C:\ffmpeg`)
4. **Add to PATH:**
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under System Variables, find "Path" and click Edit
   - Click New and add: `C:\ffmpeg\bin`
   - Click OK on all dialogs
5. **Verify:** Open Command Prompt and type `ffmpeg -version`

**Alternative:** Use Chocolatey package manager:
```powershell
choco install ffmpeg
```

### 2. VapourSynth
**What it does:** Video processing framework for restoration filters  
**Required for:** QTGMC deinterlacing, AI upscaling, denoising, all restoration features

**Installation:**
1. Download from https://github.com/vapoursynth/vapoursynth/releases
2. Get the latest R-series release (e.g., R70)
3. Install `VapourSynth64-Portable-RXX.7z` or the installer version
4. **If using portable:**
   - Extract to `C:\VapourSynth`
   - Add to PATH: `C:\VapourSynth`
5. **If using installer:** It will add itself to PATH automatically
6. **Verify:** Open Command Prompt and type `vspipe --version`

**Required VapourSynth Plugins:**
After installing VapourSynth, you need these plugins (typically installed to `VapourSynth\plugins`):

- **QTGMC** - Deinterlacing (required)
  - Download from: https://github.com/dubhater/vapoursynth-qtgmc
  - Also requires: MVTools, NNEDI3, ZNedi3

- **BM3D** - Denoising (optional but recommended)
  - https://github.com/HomeOfVapourSynthEvolution/VapourSynth-BM3D

- **RealESRGAN** - AI upscaling (optional, for HD/4K upscaling)
  - Requires: vs-rife, ncnn, and CUDA if using GPU

### 3. FFprobe (Usually included with FFmpeg)
**What it does:** Video file analysis and metadata extraction  
**Required for:** Field order detection, video information display

**Installation:** Included with FFmpeg automatically - no separate installation needed

---

## ⚠️ **OPTIONAL Prerequisites** (Enable Additional Features)

### 4. Python 3.8+ (Optional)
**What it does:** Allows package installation and advanced model management  
**Required for:** 
- Installing AI models via GUI
- ProPainter setup wizard
- Python package management from within the app

**When NOT needed:**
- Basic video restoration works without Python
- All processing features work without Python
- Only needed if you want to install additional AI models through the GUI

**Installation:**
1. Download from https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Install Python 3.8 or newer
4. **Verify:** Open Command Prompt and type `python --version`

**Why might you need this?**
- If you want to use the Model Installer dialog to download AI models
- If you want to use the ProPainter setup wizard
- For creating virtual environments for additional tools

---

## 📋 Quick Verification Checklist

Open Command Prompt (cmd.exe) or PowerShell and run these commands:

```powershell
# Test FFmpeg (REQUIRED)
ffmpeg -version
# Should show: ffmpeg version x.x.x

# Test FFprobe (REQUIRED)
ffprobe -version
# Should show: ffprobe version x.x.x

# Test VapourSynth (REQUIRED)
vspipe --version
# Should show: VapourSynth Video Processing Library

# Test Python (OPTIONAL)
python --version
# Should show: Python 3.x.x (only needed for model installation features)
```

**If any REQUIRED command fails:** That tool is not installed or not in PATH.

---

## 🚀 What the .exe INCLUDES (No Installation Needed)

The compiled executable bundles:
- ✅ Python runtime (embedded)
- ✅ PySide6 (Qt GUI framework)
- ✅ All Python dependencies (PyYAML, requests, etc.)
- ✅ Application code and GUI resources
- ✅ AI model management system

---

## 🎬 What's NOT Included (Must Install Separately)

The executable does NOT include:
- ❌ FFmpeg
- ❌ FFprobe  
- ❌ VapourSynth
- ❌ VapourSynth plugins
- ❌ Python interpreter (unless you need model installation features)
- ❌ AI model weights (downloaded on-demand through GUI)

---

## 💡 Why These Tools Are Separate

**Technical Reasons:**
1. **License compliance** - FFmpeg and VapourSynth have different licenses
2. **Size** - Including these would make the exe 500MB+ instead of ~50MB
3. **Updates** - Users can update FFmpeg/VapourSynth independently
4. **Flexibility** - Users can use custom FFmpeg builds (with hardware acceleration)
5. **System-wide** - These tools are useful for other applications too

---

## 🔧 Installation Time Estimate

- **FFmpeg:** 5 minutes
- **VapourSynth + plugins:** 10-15 minutes
- **Python (if needed):** 5 minutes
- **Total:** 20-25 minutes for complete setup

---

## 📦 Recommended Installation Order

1. **Install FFmpeg** → Test with `ffmpeg -version`
2. **Install VapourSynth** → Test with `vspipe --version`
3. **Install VapourSynth plugins** (QTGMC at minimum)
4. **Run Advanced_Tape_Restorer.exe** → Should work for basic operations
5. **(Optional) Install Python** → Only if you want model management features

---

## 🐛 Troubleshooting

### "ffmpeg executable not found in system PATH"
- FFmpeg is not installed OR not added to PATH
- Solution: Install FFmpeg and add to PATH, then restart the application

### "vspipe executable not found in system PATH"
- VapourSynth is not installed OR not added to PATH
- Solution: Install VapourSynth and add to PATH, then restart the application

### "Warning: No Python interpreter found"
- This is OKAY for video processing
- Only matters if you want to use model installation features
- Solution: Install Python 3.8+ and add to PATH if you need those features

### Application launches but processing fails
1. Open Command Prompt
2. Run verification checklist above
3. Check which tools are missing
4. Install missing tools and add to PATH
5. Restart application

---

## 📖 Detailed Installation Guide

For step-by-step installation with screenshots, see:
- **FFmpeg Installation:** https://www.wikihow.com/Install-FFmpeg-on-Windows
- **VapourSynth Guide:** Included in VapourSynth documentation

---

## ✨ After Installation

Once prerequisites are installed:

1. **Launch** `Advanced_Tape_Restorer.exe`
2. **Check startup messages** for any warnings about missing tools
3. **Test with a video file:**
   - File → Select Input
   - Choose a test video
   - Configure basic restoration settings
   - Start Processing
4. **If successful:** You'll see progress bar and output video will be created
5. **If errors:** Check console output for which tool is missing

---

## 🎯 Summary

| Tool | Required? | Used For | Size | Install Time |
|------|-----------|----------|------|--------------|
| FFmpeg | ✅ YES | Encoding, decoding, analysis | ~70MB | 5 min |
| VapourSynth | ✅ YES | Video processing, filters | ~50MB | 10 min |
| FFprobe | ✅ YES | Metadata (included with FFmpeg) | - | - |
| Python 3.8+ | ⚠️ OPTIONAL | Model management GUI features | ~30MB | 5 min |

**Total disk space needed:** ~150MB for required tools  
**One-time setup:** ~20 minutes

---

## 📞 Need Help?

If you have issues installing prerequisites:
1. Check the troubleshooting section above
2. Verify each tool individually using the verification checklist
3. Make sure to restart Command Prompt/application after adding tools to PATH
4. Check Windows Environment Variables to confirm PATH entries

---

**Last Updated:** December 19, 2025  
**Compatible with:** Advanced Tape Restorer v3.1
