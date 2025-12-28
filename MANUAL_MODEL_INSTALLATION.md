# Manual Model Installation Guide
**Advanced Tape Restorer v3.0**

This guide covers models that require manual installation.

---

## 📋 Quick Reference Table

| Model | Source Type | Auto Install? | Plugin Required | Notes |
|-------|-------------|---------------|-----------------|-------|
| **BasicVSR++** | huggingface | ✅ Automatic | `vsbasicvsrpp` | Auto-downloads .pth |
| **RealESRGAN** | github_release | ✅ Automatic | `vsrealesrgan` | Auto-downloads .pth |
| **SwinIR** | huggingface | ✅ Automatic | `vsswinir` | Auto-downloads .pth |
| **RIFE** | huggingface | ✅ Automatic | `vsrife` | Auto-downloads .pth |
| **GFPGAN** | github_release | ✅ Automatic | `vsgfpgan` | Auto-downloads .pth |
| **DeOldify** | manual | ❌ Manual | ❌ No plugin | License restricted |
| **FILM** | github_repo | ⚠️ Complex | ❌ No plugin | Requires setup |
| **DAIN** | github_repo | ⚠️ Complex | ❌ No plugin | Requires compilation |
| **SVD** | huggingface | ✅ Automatic | Python script | HuggingFace login |

---

## ✅ Models That Work Automatically

These models can be downloaded with the **"Download"** button in the Model Manager:

### 1. BasicVSR++ ✅
- **Plugin:** `pip install vsbasicvsrpp`
- **Model:** Auto-downloads from HuggingFace
- **Size:** ~36 MB
- **Requirements:** PyTorch CUDA, 2GB+ VRAM

### 2. RealESRGAN ✅
- **Plugin:** Included with VapourSynth
- **Model:** Auto-downloads from GitHub Releases
- **Size:** ~67 MB
- **Requirements:** CUDA GPU

### 3. SwinIR ✅
- **Plugin:** `pip install vsswinir`
- **Model:** Auto-downloads from HuggingFace
- **Size:** ~30 MB
- **Requirements:** PyTorch CUDA, 1.5GB+ VRAM

### 4. RIFE ✅
- **Plugin:** Included with application
- **Model:** Auto-downloads from HuggingFace
- **Size:** ~25 MB
- **Requirements:** CUDA GPU

### 5. GFPGAN ✅
- **Plugin:** `pip install vsgfpgan`
- **Model:** Auto-downloads from GitHub Releases
- **Size:** ~350 MB
- **Requirements:** PyTorch CUDA, 4GB+ VRAM

---

## ❌ Models Requiring Manual Installation

These models show an **"Install..."** button in the Model Manager.

### 🔴 DeOldify (Manual - License Restricted)

**Why Manual?** DeOldify model weights cannot be redistributed.

**Installation Steps:**

1. **Download Model:**
   - Visit: https://github.com/jantic/DeOldify
   - Navigate to `models/` folder or check README
   - Download: `video.pth` or `video_model.pth` (~190 MB)
   - Alternative mirror: https://data.deepai.org/deoldify/ColorizeVideo_gen.pth

2. **Create Folders:**
   ```
   C:\Users\<YourUser>\AppData\Local\Advanced_Tape_Restorer\ai_models\deoldify\video\
   ```

3. **Place File:**
   - Rename to: `video_model.pth` (if needed)
   - Full path: `...\ai_models\deoldify\video\video_model.pth`

4. **Verify:**
   - Click "Refresh Status" in Model Manager
   - Status should show: ✓ Installed

**Plugin Note:** No `vsdeoldify` pip package exists. Requires manual VapourSynth plugin installation from GitHub.

---

###  VideoCleaner (External Application)

**Type:** Standalone Windows application (not a VapourSynth plugin)

**Installation:**

1. **Download:**
   - Visit: https://www.videocleaner.com
   - Download the installer

2. **Install:**
   - Run installer
   - Default path: `C:\Program Files\Video Cleaner\`

3. **Usage:**
   - Export clips from Advanced Tape Restorer
   - Open in VideoCleaner for specialized cleaning
   - Import cleaned clips back

**Note:** Commercial software, separate license required.

---

## 🎯 Recommended Models for Typical Users

**For Upscaling:**
- ✅ **RealESRGAN** - Best quality, automatic installation
- ✅ **BasicVSR++** - Video-aware, automatic installation
- ✅ **SwinIR** - Transformer-based, automatic installation

**For Frame Interpolation:**
- ✅ **RIFE** - Easy, fast, automatic installation (RECOMMENDED)

**For Face Enhancement:**
- ✅ **GFPGAN** - Automatic installation

**For Colorization:**
- ⚠️ **DeOldify** - Manual setup required
- Consider external tools instead

---

## 🔧 Troubleshooting

### Model Shows "Not Installed" After Manual Installation

1. Check file path exactly matches registry requirements
2. Check filename is exactly correct (case-sensitive)
3. Click "Refresh Status" button in Model Manager
4. Check folder permissions

### "Download" Button Not Working

1. Check internet connection
2. Check if model URL is accessible
3. Check antivirus/firewall not blocking downloads
4. Try manual installation instead

### Plugin Installation Fails

**For working plugins:**
```bash
# Install PyTorch CUDA first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Then install plugin
pip install vsbasicvsrpp  # or vsswinir, vsgfpgan, etc.
```

**For non-existent plugins (vsfilm, vsdain, vsdeoldify, vsamt):**
- These do NOT exist on PyPI
- Manual GitHub installation required
- Very complex - not recommended for typical users

---

## 📁 Default Model Storage Location

**Windows:**
```
C:\Users\<YourUser>\AppData\Local\Advanced_Tape_Restorer\ai_models\
```

You can change this location in the Model Manager dialog.

**Folder Structure:**
```
ai_models/
├── basicvsrpp/
│   └── BasicVSRPP_x2.pth
├── realesrgan/
│   └── RealESRGAN_x4plus.pth
├── swinir/
│   └── RealSR_x4.pth
├── rife/
│   └── flownet-4.22.pkl
├── gfpgan/
│   └── GFPGANv1.4.pth
├── deoldify/
│   └── video/
│       └── video_model.pth
├── film/
│   └── film-model.pt
└── dain/
    └── DAIN.pth
```

---

## ✨ Summary

**Easy (Automatic):** RealESRGAN, BasicVSR++, SwinIR, RIFE, GFPGAN
- Just click "Download" button
- Install required plugin via pip
- Done!

**Manual (License Restricted):** DeOldify
- Download from official sources
- Place in correct folder
- Use Model Manager "Install..." button for guidance

**External:** VideoCleaner
- Separate application
- Commercial license required
- Used outside the main workflow

---

**For most users, stick to the automatic installation models for the best experience!**
