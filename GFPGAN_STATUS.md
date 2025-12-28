# GFPGAN Face Enhancement - Future Development

## Current Status: ⏸️ Blocked by Python 3.13 Compatibility

### What's Implemented (Ready to Use)
- ✅ GFPGAN engine module (`ai_models/engines/face_gfpgan.py`)
- ✅ Model registry with 3 GFPGAN models and correct SHA256 hashes
- ✅ Post-processing integration in `core/processor.py`
- ✅ GUI checkbox in AI/Upscaling tab
- ✅ Automatic frame extraction and re-encoding pipeline
- ✅ Proper error handling with helpful messages

### Blocking Issue
**Python 3.13 Incompatibility:**
- The `basicsr` package (GFPGAN dependency) has a setup.py bug preventing installation on Python 3.13
- Error: `KeyError: '__version__'` during pip installation
- This is an upstream issue in the BasicSR library

### Models Downloaded
All GFPGAN models are already downloaded and verified:
- `GFPGANv1.3.pth` (348 MB) - Default model
- `GFPGANv1.4.pth` (348 MB) - Newer version
- `RestoreFormer.pth` (290 MB) - Best quality variant

Location: `%LOCALAPPDATA%\Advanced_Tape_Restorer\ai_models\gfpgan\`

### To Enable GFPGAN (Future)

**Option A: Wait for Upstream Fix**
- Monitor BasicSR repository: https://github.com/XPixelGroup/BasicSR
- Install when Python 3.13 support is added

**Option B: Use Python 3.11**
1. Create Python 3.11 virtual environment
2. Install dependencies: `pip install gfpgan facexlib basicsr`
3. Feature will work immediately (code is ready)

### Architecture Overview

**How it Works:**
1. Main VapourSynth processing completes (deinterlacing, upscaling, etc.)
2. FFmpeg encodes to output file
3. If `face_enhance` is enabled:
   - Extract frames from encoded video
   - Apply GFPGAN enhancement to each frame
   - Re-encode enhanced frames with original audio
   - Replace output file with enhanced version

**Processing Flow:**
```
Video Input → VapourSynth Pipeline → FFmpeg Encode → GFPGAN Post-Processing → Final Output
```

### File Locations
- Engine: `ai_models/engines/face_gfpgan.py`
- Registry: `ai_models/models/registry.yaml` (lines 106-167)
- Processor Integration: `core/processor.py` (lines 250-469)
- GUI: `gui/main_window.py` (lines 1222-1240, 2026)

### Next Steps (When Unblocked)
1. Wait for Python 3.13 compatibility in basicsr
2. OR create Python 3.11 environment for testing
3. Test with sample video containing faces
4. Verify frame extraction/re-encoding performance
5. Fine-tune enhancement strength defaults

---

**Last Updated:** 2025-11-29
**Status:** Feature complete but blocked by dependency incompatibility
