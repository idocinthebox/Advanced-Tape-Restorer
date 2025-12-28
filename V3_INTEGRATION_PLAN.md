# Advanced Tape Restorer v3.0 - Integration Plan
## Merging AI Model Manager with v2.0

**Date:** November 23, 2025  
**Status:** Planning → Implementation

---

## Overview

Integrating the standalone AI Model Manager (`restoration_pipeline`) into Advanced Tape Restorer v2.0 to create v3.0 with:
- Centralized model management
- Auto-downloading with progress tracking
- Support for 11+ AI engines
- Modular, extensible architecture
- Backward compatibility with v2.0 features

---

## Existing Systems Analysis

### v2.0 Current AI Implementation:
- **Location:** `core/vapoursynth_engine.py` (hardcoded AI logic)
- **Features:**
  - RealESRGAN (inline, auto_download via vsrealesrgan)
  - RIFE (basic support)
  - ZNEDI3 (fast upscaling)
- **Issues:**
  - Hardcoded in VapourSynth script generation
  - No centralized model management
  - Limited extensibility
  - No progress tracking for downloads

### AI Model Manager System:
- **Location:** `ai_models/` (formerly `restoration_pipeline/`)
- **Features:**
  - Model registry (YAML/JSON) with 11+ models
  - Auto-download with verification (SHA256)
  - License management (commercial/non-commercial)
  - Modular engines (each engine in separate file)
  - Pipeline runner (chain multiple AI steps)
- **Engines Supported:**
  1. **Upscaling:** BasicVSR++, RealESRGAN, SwinIR
  2. **Interpolation:** RIFE, DAIN, FILM, AMT
  3. **Color:** DeOldify, SVDiffusion
  4. **Face:** GFPGAN
  5. **Forensic:** Video Cleaner

---

## v3.0 Architecture

### Directory Structure:
```
Advanced Tape Restorer v3.0/
├── core/
│   ├── processor.py                    (main orchestrator)
│   ├── vapoursynth_engine.py          (✨ REFACTORED - uses AI bridge)
│   ├── ffmpeg_encoder.py
│   ├── video_analyzer.py
│   └── ai_bridge.py                   (✨ NEW - connects v2.0 to AI system)
│
├── ai_models/                          (✨ INTEGRATED from restoration_pipeline)
│   ├── __init__.py                    (✨ UPDATED - v3.0 exports)
│   ├── model_manager.py               (core model management)
│   ├── pipeline_runner.py             (orchestrates AI steps)
│   ├── compute_hashes.py              (SHA256 utilities)
│   ├── engines/                       (11 AI engine wrappers)
│   │   ├── upscaling_realesrgan.py
│   │   ├── upscaling_basicvsrpp.py
│   │   ├── upscaling_swinir.py
│   │   ├── interpolation_rife.py
│   │   ├── interpolation_dain.py
│   │   ├── interpolation_film.py
│   │   ├── interpolation_amt.py
│   │   ├── color_deoldify.py
│   │   ├── color_svdiffusion.py
│   │   ├── face_gfpgan.py
│   │   └── forensic_videocleaner.py
│   ├── models/
│   │   └── registry.yaml              (model definitions + URLs)
│   └── ui/
│       └── model_browser.py           (model download UI)
│
├── gui/
│   ├── main_window.py                 (✨ ENHANCED - AI model UI)
│   ├── ai_model_dialog.py             (✨ NEW - model manager dialog)
│   ├── processing_thread.py
│   └── settings_manager.py
│
└── config/
    └── default_settings.json          (✨ UPDATED - AI model settings)
```

---

## Integration Strategy

### Phase 1: Core Integration (Bridge Pattern)
**Goal:** Connect existing v2.0 code to new AI system without breaking changes

**New File:** `core/ai_bridge.py`
```python
\"\"\"
AI Bridge - Connects v2.0 VapourSynth engine to AI Model Manager
\"\"\"
from ai_models.model_manager import ModelManager
from ai_models.pipeline_runner import PipelineStep, PipelineConfig, run_pipeline
import vapoursynth as vs

class AIBridge:
    def __init__(self, registry_path, model_root, commercial_mode=True):
        self.manager = ModelManager(registry_path, model_root, commercial_mode)
    
    def apply_realesrgan(self, clip: vs.VideoNode, model_id=None, **kwargs):
        # Wrapper for RealESRGAN using new system
        pass
    
    def apply_rife(self, clip: vs.VideoNode, model_id=None, **kwargs):
        # Wrapper for RIFE using new system
        pass
```

**Benefits:**
- Minimal changes to `vapoursynth_engine.py`
- Backward compatible with v2.0 AI features
- Gradual migration path

### Phase 2: VapourSynth Engine Refactoring
**Goal:** Replace hardcoded AI logic with bridge calls

**Changes to `core/vapoursynth_engine.py`:**
1. Import AI Bridge at top
2. Replace inline RealESRGAN code with `ai_bridge.apply_realesrgan()`
3. Replace inline RIFE code with `ai_bridge.apply_rife()`
4. Keep ZNEDI3 as-is (it's fast and doesn't need model management)

**Before (v2.0):**
```python
# 30+ lines of hardcoded RealESRGAN
from vsrealesrgan import realesrgan, RealESRGANModel
video = realesrgan(video, model=RealESRGANModel.RealESRGAN_x2plus, auto_download=True)
```

**After (v3.0):**
```python
# 3 lines using bridge
from core.ai_bridge import AIBridge
ai = AIBridge(registry_path, model_root)
video = ai.apply_realesrgan(video, model_id="realesrgan_x2plus")
```

### Phase 3: GUI Integration
**Goal:** Add model management UI and enhanced AI controls

**New Dialog:** `gui/ai_model_dialog.py`
- List available models from registry
- Show download status (installed/not installed)
- Download button with progress bar
- Model details (size, license, version)
- Auto-update from registry

**Enhanced Main Window:**
- "Manage AI Models" button → opens ai_model_dialog
- Enhanced AI upscaling dropdown (all 3 engines: BasicVSR++, RealESRGAN, SwinIR)
- Enhanced interpolation dropdown (RIFE, DAIN, FILM, AMT)
- New "Advanced AI" section for:
  - Colorization (DeOldify, SVDiffusion)
  - Face enhancement (GFPGAN)
  - Forensic cleaning (Video Cleaner)

### Phase 4: Settings Migration
**Goal:** Extend settings.json for AI models

**New Settings Keys:**
```json
{
  "ai_model_dir": "%LOCALAPPDATA%\\Advanced_Tape_Restorer\\ai_models",
  "ai_commercial_mode": true,
  "ai_auto_download": true,
  "ai_upscaling_engine": "realesrgan",  // or basicvsrpp, swinir
  "ai_interpolation_engine": "rife",    // or dain, film, amt
  "ai_enable_colorization": false,
  "ai_colorization_engine": "deoldify",
  "ai_enable_face_enhancement": false,
  "ai_enable_forensic_cleaning": false
}
```

---

## Migration Path

### Step 1: Copy Files (✅ DONE)
- Copied `restoration_pipeline/` → `ai_models/`

### Step 2: Create AI Bridge
- Implement `core/ai_bridge.py`
- Write wrappers for RealESRGAN, RIFE

### Step 3: Update VapourSynth Engine
- Replace hardcoded AI logic
- Add AI bridge initialization
- Keep backward compatibility

### Step 4: Enhance GUI
- Create AI Model Manager dialog
- Add to main window menu
- Enhanced AI controls

### Step 5: Update Settings
- Extend default_settings.json
- Add settings UI controls
- Migration script for existing users

### Step 6: Testing
- Test RealESRGAN (existing v2.0 feature)
- Test RIFE (existing v2.0 feature)
- Test new engines (BasicVSR++, SwinIR, etc.)
- Test model auto-download
- Test progress tracking

### Step 7: Documentation
- Update USER_GUIDE
- Create AI_FEATURES_GUIDE
- Update QUICK_START
- Update TROUBLESHOOTING

### Step 8: Build & Release
- Update version to 3.0.0
- Build EXE with PyInstaller
- Update .spec file with new modules
- Create distribution package

---

## Backward Compatibility

### v2.0 Features Preserved:
✅ RealESRGAN AI upscaling (now via model manager)
✅ RIFE frame interpolation (now via model manager)
✅ ZNEDI3 fast upscaling (unchanged)
✅ All restoration features (QTGMC, BM3D, etc.)
✅ All capture features
✅ All encoding options
✅ Existing settings files work

### Breaking Changes:
❌ None! v3.0 is fully backward compatible

### Migration for Users:
1. Existing settings automatically migrated
2. First launch downloads required models (with progress)
3. All v2.0 workflows work identically

---

## New Features in v3.0

### AI Upscaling Engines (3 options):
1. **RealESRGAN** (existing) - Best quality, slowest
2. **BasicVSR++** (NEW) - Video-specific, temporal awareness
3. **SwinIR** (NEW) - Fast, good quality

### AI Frame Interpolation (4 options):
1. **RIFE** (existing) - Fast, good quality
2. **DAIN** (NEW) - Depth-aware, better motion
3. **FILM** (NEW) - Google research, excellent quality
4. **AMT** (NEW) - Adaptive, handles complex motion

### NEW AI Features:
5. **Colorization** - DeOldify or SVDiffusion (B&W → color)
6. **Face Enhancement** - GFPGAN (improve faces in old videos)
7. **Forensic Cleaning** - Video Cleaner (remove compression artifacts)

---

## Implementation Timeline

### Day 1 (Today):
- ✅ Copy AI Model Manager files
- ✅ Create integration plan
- ⏳ Implement AI Bridge
- ⏳ Basic VapourSynth integration

### Day 2:
- Refactor VapourSynth engine
- Test RealESRGAN migration
- Test RIFE migration
- Verify backward compatibility

### Day 3:
- Create AI Model Manager dialog
- Enhance main window UI
- Settings migration

### Day 4:
- Testing all AI engines
- Documentation updates
- Build v3.0 EXE

### Day 5:
- Final testing
- Distribution package
- Release!

---

## Technical Considerations

### PyInstaller Spec File Updates:
```python
# Add to hiddenimports:
'ai_models',
'ai_models.model_manager',
'ai_models.pipeline_runner',
'ai_models.engines.*',
'yaml',  # for registry.yaml loading
'requests',  # for model downloads
```

### Dependencies:
**New Required:**
- PyYAML (for registry.yaml)
- requests (for model downloads)

**Already Have:**
- torch (PyTorch CUDA)
- vapoursynth
- vsrealesrgan
- vsrife

### Model Storage:
**Default Location:** `%LOCALAPPDATA%\Advanced_Tape_Restorer\ai_models\`
- Configurable via settings
- Auto-creates directory structure
- Organized by engine:
  ```
  ai_models/
  ├── realesrgan/
  │   └── RealESRGAN_x2plus.pth
  ├── rife/
  │   └── v4.22/
  │       └── flownet.pth
  ├── basicvsrpp/
  └── swinir/
  ```

---

## Risk Mitigation

### Risk 1: Breaking v2.0 Features
**Mitigation:** Bridge pattern preserves existing API, extensive testing

### Risk 2: Model Download Failures
**Mitigation:** Graceful fallbacks, clear error messages, manual download option

### Risk 3: Increased EXE Size
**Mitigation:** Models downloaded separately (not bundled), registry is small (5KB)

### Risk 4: Performance Regression
**Mitigation:** Bridge adds minimal overhead, same underlying engines

### Risk 5: PyInstaller Packaging Issues
**Mitigation:** Update .spec with all new imports, test bundled EXE

---

## Success Criteria

### Must Have (v3.0 Launch):
✅ All v2.0 features working
✅ RealESRGAN via new system
✅ RIFE via new system
✅ Model auto-download working
✅ Model manager UI functional
✅ Backward compatible settings

### Should Have (v3.1):
- BasicVSR++ upscaling
- Additional interpolation engines (DAIN, FILM)
- Enhanced progress tracking

### Nice to Have (v3.2):
- Colorization features
- Face enhancement
- Forensic cleaning
- Custom model import

---

## Next Steps

1. **Implement AI Bridge** (`core/ai_bridge.py`)
2. **Test Bridge** with RealESRGAN
3. **Refactor VapourSynth Engine** to use bridge
4. **Create GUI Dialog** for model management
5. **Update Settings** system
6. **Comprehensive Testing**
7. **Documentation**
8. **Build & Release**

---

**Ready to proceed with implementation!**

*Advanced Tape Restorer v3.0 - Next Generation AI Video Restoration*
