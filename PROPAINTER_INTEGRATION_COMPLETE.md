# ProPainter Integration - Complete

## Summary

ProPainter AI video inpainting has been **fully integrated** into the Advanced Tape Restorer v2.0 processing pipeline.

## How It Works

### Architecture

ProPainter runs as a **pre-processing step** before VapourSynth restoration:

```
Input Video → ProPainter (if enabled) → VapourSynth → FFmpeg → Output
                    ↓
            Cleaned Video (temp file)
```

### Processing Flow

1. **User enables AI Inpainting** in Advanced tab
2. **User configures ProPainter** via Settings → AI Features → Setup ProPainter
3. **Start Processing** clicked
4. **ProPainter pre-processing**:
   - Creates temp directory: `%TEMP%\tape_restorer_propainter\`
   - Runs ProPainter on original video
   - Outputs cleaned video: `propainter_<filename>.mp4`
5. **VapourSynth restoration**:
   - Uses ProPainter output as input
   - Applies deinterlacing, denoise, RIFE, RealESRGAN, etc.
6. **FFmpeg encoding**:
   - Final encode to user's chosen format
7. **Cleanup**:
   - Temp ProPainter files deleted automatically

## What Was Changed

### 1. Core Processing (`core/processor.py`)
- Added `ProPainterEngine` import and initialization
- Added `_run_propainter_preprocessing()` method
- Added `_cleanup_temp_files()` method
- Modified `process_video()` to run ProPainter before VapourSynth
- Updated step numbers in processing flow

### 2. ProPainter Engine (`core/propainter_engine.py`)
- Already existed, no changes needed
- Handles external ProPainter CLI tool execution
- Supports three modes:
  - `auto_detect`: Automatically detect and remove artifacts
  - `object_removal`: Remove objects (requires mask)
  - `video_completion`: Fill missing areas (requires mask)

### 3. VapourSynth Engine (`core/vapoursynth_engine.py`)
- Removed placeholder ProPainter code
- Updated AI features logging to reflect pre-processing
- ProPainter-cleaned video loaded as normal input

### 4. Processing Thread (`gui/processing_thread.py`)
- Added `propainter_path` parameter to `__init__`
- Passes ProPainter path to `VideoProcessor` constructor

### 5. Main Window (`gui/main_window.py`)
- Added `"propainter_path": ""` to `DEFAULT_SETTINGS`
- Modified `start_processing()` to get ProPainter path from settings
- Passes `propainter_path` to `ProcessingThread`
- ProPainter path already saved by setup dialog (no changes needed)

### 6. Setup Dialog (`gui/propainter_setup_dialog.py`)
- Updated instructions to clarify nested directory structure
- Added auto-detection for nested `ProPainter/ProPainter` folders
- Test function already uses venv Python (fixed previously)

## User Workflow

### First-Time Setup

1. **Install ProPainter** (one-time):
   ```bash
   cd C:\ProPainterInstall
   git clone https://github.com/sczhou/ProPainter.git
   cd ProPainter
   python -m venv venv
   venv\Scripts\activate
   pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu121
   pip install opencv-python pillow numpy scipy scikit-image imageio imageio-ffmpeg tqdm tensorboard pyyaml einops timm kornia accelerate requests matplotlib
   ```

2. **Configure in App**:
   - Open Advanced Tape Restorer
   - Settings → AI Features → Setup ProPainter
   - Select: `C:\ProPainterInstall\ProPainter` (nested folder)
   - Click "Test Installation" to verify
   - Click "OK" to save

### Using ProPainter

1. Load input video
2. Go to **Advanced** tab
3. Check ☑ **AI Video Inpainting (ProPainter)**
4. Select mode:
   - **Remove Artifacts**: Auto-detect and fix VHS artifacts
   - **Object Removal**: Remove objects (requires mask folder)
   - **Restore Damaged Areas**: Heavy damage restoration (requires mask)
5. Configure other restoration settings (deinterlacing, denoise, etc.)
6. Click **Start Processing**
7. Monitor console for ProPainter progress:
   ```
   === ProPainter AI Inpainting ===
   Mode: Remove Artifacts
   Estimated VRAM needed: 7 GB (FP16)
   🎨 Starting ProPainter processing...
   ...
   ✅ ProPainter completed, using cleaned video
   
   === Generating restoration script ===
   🤖 AI FEATURES (VapourSynth Pipeline):
      ✓ RIFE Frame Interpolation (2x)
      ✓ RealESRGAN Upscaling
   ```

## Verification

### How to Confirm ProPainter Is Working

**Method 1: Console Output**
Look for these messages during processing:
```
=== ProPainter AI Inpainting ===
Mode: Remove Artifacts
🎨 Starting ProPainter processing...
✅ ProPainter completed, using cleaned video
```

**Method 2: Processing Time**
ProPainter adds **significant** processing time:
- 640x480 video: +5-10 minutes per minute of video
- 720x480 video: +10-15 minutes per minute of video
- Requires GPU with 7+ GB VRAM (11+ GB for HD)

**Method 3: Check Script**
Run `python check_ai_processing.py` while processing to see active features.

## ProPainter Modes Explained

### Remove Artifacts (Auto-Detect)
- **Use for**: VHS tapes with dropouts, scratches, noise
- **Mask**: Not required (auto-detects problems)
- **Best for**: General tape restoration
- **Speed**: Moderate (FP16 mode)

### Object Removal
- **Use for**: Removing unwanted objects/people from scenes
- **Mask**: Required - paint white on objects to remove
- **Best for**: Cleaning up test shots, removing timestamps
- **Speed**: Same as auto-detect

### Restore Damaged Areas (Video Completion)
- **Use for**: Heavily damaged tape with missing frames
- **Mask**: Required - mark damaged regions
- **Best for**: Tapes with physical damage, missing sections
- **Speed**: Slowest (most aggressive processing)

## GPU Memory Requirements

| Resolution | FP16 (Recommended) | FP32 (Full Precision) |
|------------|-------------------:|----------------------:|
| 320x240    | 2 GB              | 3 GB                  |
| 640x480    | 6 GB              | 10 GB                 |
| 720x480    | 7 GB              | 11 GB                 |
| 1280x720   | 19 GB             | 28 GB                 |

**Tips**:
- FP16 (half precision) is always enabled for efficiency
- For HD content (1280x720+), consider downscaling first
- Batch processing uses chunks (80 frames) to manage memory

## Troubleshooting

### ❌ ProPainter not installed or configured
**Solution**: Run Settings → AI Features → Setup ProPainter

### ❌ ProPainter failed with exit code X
**Check**:
- Verify venv is activated: `C:\ProPainterInstall\ProPainter\venv\Scripts\python.exe`
- Check weights exist: `C:\ProPainterInstall\ProPainter\weights\*.pth`
- Ensure GPU has enough VRAM (see table above)

### ⚠️ ProPainter failed or not available, using original video
**Result**: Processing continues with standard restoration (no ProPainter)
**Fix**: Verify installation path and test button

### Processing is extremely slow
**Normal behavior**: ProPainter is GPU-intensive
- 5-15 minutes per minute of video is expected
- Progress shown in real-time in console
- Consider using on short clips first

## Next Steps

To rebuild the EXE with ProPainter integration:

1. **Close the running app**
2. Run: `cd "c:\Advanced Tape Restorer v2.0"; .\build.bat`
3. New EXE will be: `dist\Advanced_Tape_Restorer_v2.exe`

## Technical Details

### Temp File Management
- ProPainter output stored in: `%TEMP%\tape_restorer_propainter\`
- Files auto-deleted after processing completes
- Named: `propainter_<original_filename>.mp4`

### Error Handling
- If ProPainter fails, processing continues with original video
- No crash or data loss
- Errors logged to console

### Performance Notes
- ProPainter runs single-threaded (GPU-bound)
- VapourSynth + FFmpeg run in parallel after ProPainter completes
- Total processing time = ProPainter time + VapourSynth time

## Files Modified

```
core/processor.py                  - Added ProPainter pre-processing
core/vapoursynth_engine.py         - Removed placeholder code
gui/processing_thread.py           - Pass ProPainter path
gui/main_window.py                 - Add ProPainter path to settings
gui/propainter_setup_dialog.py    - Better directory handling (already done)
```

## Status

✅ **Complete and Tested**
- Core integration: ✅
- GUI integration: ✅
- Error handling: ✅
- Cleanup: ✅
- Documentation: ✅
- Ready for build: ✅ (waiting for user to close app)

---

**ProPainter is now fully functional in the restoration pipeline!**
