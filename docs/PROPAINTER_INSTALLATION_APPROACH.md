# ProPainter Installation Approach - Design Decision

## Question: Should we bundle ProPainter installer in the EXE?

## Answer: **Manual Installation with Guided Setup Wizard** ✅

---

## Why Not Bundle/Auto-Install?

### 1. **Size Constraints**
```
Current EXE: 43 MB
+ ProPainter core: 50 MB
+ Model weights: 500 MB
+ PyTorch: 2-3 GB
+ Dependencies: 500 MB
= Total: 3-4 GB package!
```

**Result:** Unacceptable for distribution

### 2. **License Restrictions**
- **ProPainter License:** NTU S-Lab License 1.0 (Non-Commercial Only)
- **Cannot redistribute** without explicit permission
- **Cannot bundle** in commercial-adjacent applications
- **Must reference** original repository and authors

**Legal Risk:** Violates license terms

### 3. **Environment Conflicts**
```
Your App:
├── Python 3.13
├── PySide6 6.10.0
├── VapourSynth dependencies
└── Windows-specific tools

ProPainter:
├── Python 3.8 (required)
├── PyTorch 1.7.1+
├── CUDA 9.2+
└── Separate conda environment
```

**Problem:** Version conflicts, DLL hell, impossible to manage in single EXE

### 4. **Not Everyone Needs It**
- ProPainter is an **advanced feature**
- Requires 8GB+ GPU
- Very slow processing (hours for full tapes)
- Most users just want basic restoration

**Principle:** Keep core app lightweight, optional features optional

---

## Our Solution: Integrated Setup Wizard ✅

### What We Built

**1. ProPainter Setup Dialog** (`gui/propainter_setup_dialog.py`)

**Features:**
- ✅ Auto-detects existing installations
- ✅ Checks requirements (conda, git, GPU)
- ✅ Shows GPU VRAM availability
- ✅ Validates installation paths
- ✅ Copy-paste installation commands
- ✅ Opens terminal in correct directory
- ✅ Opens GitHub page for reference
- ✅ Tests installation when complete
- ✅ Saves path to settings

**2. Menu Integration** (Tools → Setup ProPainter)

**3. Auto-Check on Processing**
- If ProPainter enabled but not configured
- Shows setup wizard automatically
- Option to proceed without or install now

**4. Full Documentation** (`PROPAINTER_INTEGRATION.md`)

---

## User Experience Flow

### First-Time Setup

```
1. User opens app
2. Sees "AI Video Inpainting (ProPainter)" checkbox
3. Enables it
4. Clicks "Start Processing"
5. App detects ProPainter not configured
   ┌─────────────────────────────────────┐
   │ ProPainter Not Configured           │
   │                                     │
   │ Would you like to set it up now?   │
   │                                     │
   │         [Yes]     [No]              │
   └─────────────────────────────────────┘
6. If Yes → Setup Wizard opens
   ┌─────────────────────────────────────────────┐
   │ ProPainter Setup Assistant                  │
   │                                             │
   │ Requirements Check:                         │
   │ ✅ Conda: 23.1.0                            │
   │ ✅ Git: 2.42.0                              │
   │ ✅ GPU: 12.0 GB VRAM (sufficient)           │
   │                                             │
   │ Installation Location:                      │
   │ [C:\ProPainter        ] [Browse...]         │
   │                                             │
   │ Installation Instructions:                  │
   │ ┌─────────────────────────────────────┐    │
   │ │ git clone https://github.com/...   │    │
   │ │ cd ProPainter                       │    │
   │ │ conda create -n propainter...       │    │
   │ └─────────────────────────────────────┘    │
   │                                             │
   │ [📋 Copy Commands] [🖥️ Open Terminal]      │
   │ [🌐 Open GitHub]                            │
   │                                             │
   │ [🧪 Test]  [Skip]  [Save & Close]          │
   └─────────────────────────────────────────────┘
```

### After Installation

```
1. User follows installation instructions
2. Comes back to app
3. Tools → Setup ProPainter
4. Browses to C:\ProPainter
5. Clicks "Test Installation"
   → ✅ Test passed!
6. Clicks "Save & Close"
7. ProPainter now available for use
```

---

## Comparison: Bundled vs Manual

| Aspect | Bundled Auto-Install | Manual with Wizard |
|--------|---------------------|-------------------|
| **EXE Size** | 3-4 GB ❌ | 43 MB ✅ |
| **License** | Violates terms ❌ | Compliant ✅ |
| **Conflicts** | Many ❌ | None ✅ |
| **Updates** | Hard to update ❌ | User updates independently ✅ |
| **User Choice** | Forced ❌ | Optional ✅ |
| **Setup Time** | Auto (5 min) | Manual (10 min) |
| **Maintenance** | Complex ❌ | Simple ✅ |
| **First Run** | Slow download ❌ | Fast app launch ✅ |

---

## Industry Precedents

**Other apps using external AI tools:**

1. **DaVinci Resolve:**
   - Core app: 500 MB
   - AI features: Separate 3GB download
   - User installs Studio version for AI

2. **Adobe Premiere:**
   - Base app: Small
   - AI plugins: Separate downloads
   - Optional neural filters

3. **Topaz Video AI:**
   - Core app + models: Separate installers
   - Models downloaded on demand

**Standard Practice:** Separate heavy AI components

---

## Implementation Details

### Setup Wizard Features

**Auto-Detection:**
```python
# Checks common installation paths
common_paths = [
    Path.home() / "ProPainter",
    Path("C:/ProPainter"),
    # ...
]

# Validates directory structure
if (path / "inference_propainter.py").exists():
    if (path / "weights").exists():
        ✅ Valid installation
```

**Requirements Check:**
```python
# Conda
subprocess.run(["conda", "--version"])

# Git
subprocess.run(["git", "--version"])

# GPU VRAM
subprocess.run(["nvidia-smi", "--query-gpu=memory.total"])
```

**Installation Test:**
```python
# Verify ProPainter works
subprocess.run([
    "python", "inference_propainter.py", "--help"
], cwd=propainter_path)
```

### Integration Points

**1. Menu Access:**
```
Tools → Setup ProPainter (AI Inpainting)...
```

**2. Pre-Processing Check:**
```python
if options.get('ai_inpainting', False):
    if not propainter_configured():
        show_setup_wizard()
        return  # Don't start yet
```

**3. Settings Persistence:**
```json
{
    "propainter_path": "C:/ProPainter",
    "ai_inpainting": false,
    "inpainting_mode": "Remove Artifacts"
}
```

---

## User Instructions (In App)

### Installation Commands (Copy-Paste Ready)

```bash
# Clone repository
git clone https://github.com/sczhou/ProPainter.git
cd ProPainter

# Create environment
conda create -n propainter python=3.8 -y
conda activate propainter

# Install dependencies
pip install -r requirements.txt

# Test installation
python inference_propainter.py --video inputs/object_removal/bmx-trees --mask inputs/object_removal/bmx-trees_mask
```

### Quick Links in Wizard

- 🖥️ **Open Terminal Here** → Opens PowerShell in selected directory
- 🌐 **Open GitHub Page** → Opens ProPainter repo
- 📋 **Copy Commands** → Copies installation commands to clipboard
- 🧪 **Test Installation** → Validates ProPainter works

---

## Advantages of This Approach

✅ **Lightweight EXE** - App stays small and fast

✅ **License Compliant** - No redistribution concerns

✅ **Clean Separation** - No dependency conflicts

✅ **User Control** - Install only if needed

✅ **Easy Updates** - User updates ProPainter independently

✅ **Professional UX** - Guided setup feels polished

✅ **Flexible** - Works with different ProPainter versions

✅ **Maintainable** - No complex bundling logic

---

## Future Enhancements

### Possible Improvements

1. **Auto-Update Check:**
   - Check GitHub for new ProPainter versions
   - Notify user if update available

2. **Cloud Processing:**
   - Offer cloud-based ProPainter processing
   - No local installation needed
   - Pay-per-use model

3. **Docker Container:**
   - Pre-configured Docker image
   - One-command setup
   - Isolated environment

4. **Portable Version:**
   - Self-contained ProPainter package
   - No conda needed
   - Larger but simpler

---

## Conclusion

**Best approach:** Manual installation with integrated setup wizard

**Rationale:**
- Keeps app lightweight (43 MB vs 4 GB)
- License compliant
- No environment conflicts
- Professional user experience
- Industry standard practice

**User Impact:**
- 10 minutes one-time setup
- Clear guided instructions
- Full control and flexibility
- No forced downloads

**Developer Impact:**
- Simple integration
- Easy to maintain
- No legal concerns
- Clean architecture

---

## Summary

❌ **Don't bundle ProPainter because:**
1. 3-4 GB bloat
2. License violations
3. Environment conflicts
4. Maintenance nightmare

✅ **Do provide setup wizard because:**
1. Guides user through manual installation
2. Validates installation works
3. Saves configuration
4. Professional UX
5. Clean and maintainable

**Result:** Best of both worlds - powerful feature when needed, lightweight app for everyone.
