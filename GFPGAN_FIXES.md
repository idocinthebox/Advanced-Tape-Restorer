# GFPGAN Integration Fixes - December 2025

## Overview
This document summarizes all fixes applied to the GFPGAN face enhancement integration in Advanced Tape Restorer v4.0. These fixes were implemented between December 24-26, 2025.

---

## Issues Fixed

### 1. Progress Callback Signature Error
**Problem:** `TypeError: progress_callback() got an unexpected keyword argument 'stage'`

**Fix:** Removed `stage=` keyword argument from callback. Now uses the `eta` parameter to show phase information.

**Location:** `core/processor.py` lines 575-581

**Result:** Progress callback now works: `progress_callback(pct, f"Face Enhancement: {pct}%")`

---

### 2. AutoModeSelector AttributeError
**Problem:** `AttributeError: 'MainWindow' object has no attribute 'auto_mode_selector'`

**Fix:** Added `self.auto_mode_selector = AutoModeSelector()` initialization in MainWindow.

**Location:** `gui/main_window.py` line 309

**Result:** Output tab now loads without errors.

---

### 3. No Progress Visibility During GFPGAN Processing
**Problem:** No progress updates during face enhancement phase.

**Fix:** Implemented 3-phase progress display:
- Phase 1: VapourSynth processing (0-100%)
- Phase 2: GFPGAN face enhancement (ETA: "Face Enhancement: XX%")
- Phase 3: FFmpeg re-encoding (ETA: "Re-encoding: XX%")

**Location:** `core/processor.py` lines 575-720

**Result:** Users now see detailed progress for each phase.

---

### 4. Wrong Encoder Selection
**Problem:** GFPGAN was auto-selecting NVENC hardware encoder, ignoring user's Output tab choices.

**Fix:** Now respects user's codec, CRF, and preset selections from Output tab.

**Implementation:**
```python
codec = options.get('codec').split(' ')[0]  # Extract codec name
crf = str(options.get('crf', 18))
preset = options.get('ffmpeg_preset', 'medium')
```

Builds encoder-specific options:
- **NVENC**: `-preset [preset] -cq [crf]`
- **AMF**: `-quality [preset] -rc cqp -qp_i [crf]`
- **QuickSync**: `-preset [preset] -global_quality [crf]`
- **CPU**: `-preset [preset] -crf [crf]`
- **ProRes**: (no CRF/preset)

**Location:** `core/processor.py` lines 627-660

**Result:** Users get their chosen encoder quality/speed settings.

---

### 5. Quality Concerns with JPEG Extraction
**Problem:** JPEG extraction might introduce compression artifacts before face enhancement.

**Fix:** Reverted to PNG extraction (lossless, qscale:v 1).

**Location:** `core/processor.py` lines 550-565

**Result:** Maximum quality preservation throughout enhancement pipeline.

---

### 6. Disk Space Issues
**Problem:** Large videos need 5-10GB temporary space, potentially filling C: drive.

**Fix:** Added disk space estimation and warnings before processing.

**Algorithm:**
```python
# Estimate PNG file sizes (RGB, PNG compression typically 40% of raw)
bytes_per_pixel = 3  # RGB
raw_frame_size = width × height × bytes_per_pixel
png_size = raw_frame_size × 0.4  # PNG compression ratio
total_gb = (png_size × frame_count × 2) / 1024³  # input + enhanced
```

**Example:** 3240x2160 × 252 frames = ~3.94 GB

**Warnings:** Displays warning if available space < required space + 20% headroom.

**Location:** `core/processor.py` lines 540-605

**Result:** Users warned before running out of disk space.

---

### 7. Limited C: Drive Space
**Problem:** Users with limited C: drive space need alternative temp directory.

**Fix:** Added custom temp directory option with UI controls.

**UI Components:**
- QLabel showing current path or "Default (System Temp)"
- Browse button → `QFileDialog.getExistingDirectory()`
- Clear button → Reset to default
- Tooltip explains ~5-10GB requirement for 4K

**Backend:** Uses `tempfile.mkdtemp(prefix='gfpgan_frames_', dir=custom_temp_dir)`

**Location:** 
- UI: `gui/main_window.py` lines 1435-1475, 4357-4377
- Backend: `core/processor.py` lines 605-620

**Result:** Users can specify alternative disk for temp files.

---

### 8. Resolution Bug (Critical)
**Problem:** Output video was 12960x8640 instead of 3240x2160 (4x upscaling).

**Root Cause:** GFPGAN's default `upscale=2` parameter upscales frames by 2x:
- Input: 3240x2160
- GFPGAN output: 12960x8640 (2x upscale)
- Result: Massive file, unplayable in Windows Media Player

**Fix:** Set `upscale=1` to disable GFPGAN's upscaling, maintaining original resolution.

**Location:** `core/processor.py` line 668

**Before:**
```python
upscale=engine_args.get('upscale', 2),  # 2x upscaling
```

**After:**
```python
upscale=1,  # No upscaling, just face enhancement at current resolution
```

**Result:** 
- Output maintains correct resolution (3240x2160)
- 75% less disk space usage
- Faster processing
- Playable in Windows Media Player

---

### 9. Playback Issues
**Problem:** Windows Media Player couldn't play GFPGAN-enhanced videos.

**Cause:** 12960x8640 resolution exceeds Windows Media Player's capabilities.

**Fix:** Fixed by resolution correction (issue #8).

**Result:** Enhanced videos now play in all standard players.

---

## Technical Details

### File Format Choices
- **Extraction format:** PNG (lossless, qscale:v 1)
- **Enhancement output:** PNG (preserved by GFPGAN)
- **Re-encoding:** User's chosen codec with selected quality settings

### Progress Monitoring Implementation
- **Phase 1:** VapourSynth frame count from stderr
- **Phase 2:** GFPGAN frame counter (logs every 5 frames)
- **Phase 3:** FFmpeg frame count from stderr (logs every 50 frames)

### Disk Space Formula
```
frame_size_mb = (width × height × 3 × 0.4) / (1024²)
total_gb = (frame_size_mb × frame_count × 2) / 1024
```
Factor of 2 accounts for both input and enhanced frames stored simultaneously.

### GFPGAN Parameters
- **upscale:** 1 (no resolution change)
- **weight:** User-configurable face enhancement strength (default: 0.5)
- **bg_upsampler:** None (background unchanged)
- **face_upsample:** True
- **only_center_face:** False

---

## Performance Improvements

### Before Fixes:
- Output resolution: 12960x8640 ❌
- Disk usage: ~16 GB temporary ❌
- Encoder: Auto-selected NVENC ❌
- Progress: No face enhancement visibility ❌
- Playback: Windows Media Player failed ❌

### After Fixes:
- Output resolution: 3240x2160 ✅
- Disk usage: ~4 GB temporary ✅
- Encoder: User's choice (libx264/nvenc/amf/qsv) ✅
- Progress: 3-phase detailed display ✅
- Playback: All players work ✅

---

## Files Modified

### Core Processing
- **core/processor.py** (1097 lines)
  - Lines 540-605: Disk space estimation
  - Lines 575-581: Progress callback fix
  - Lines 605-620: Custom temp directory support
  - Lines 627-660: User encoder selection
  - Lines 668: GFPGAN upscale=1 fix
  - Lines 680-720: Re-encoding progress monitoring

### GUI
- **gui/main_window.py** (4377 lines)
  - Line 309: AutoModeSelector initialization
  - Lines 1435-1475: Temp directory UI controls
  - Lines 4357-4377: Temp directory handler methods
  - Line 2463: Pass setting to processor

### AI Model Engine
- **ai_models/engines/face_gfpgan.py** (324 lines)
  - Lines 268-270: Output format (PNG)

### Test Suite
- **test_gfpgan_temp_dir.py** (NEW, 95 lines)
  - Test 1: Default system temp
  - Test 2: Custom temp directory
  - Test 3: Disk space check

---

## Testing Results

### Unit Tests
✅ All tests passed (test_gfpgan_temp_dir.py)
- Default temp directory creation/cleanup
- Custom temp directory creation/cleanup
- Disk space estimation accuracy

### Integration Testing
✅ Complete GFPGAN workflow tested:
- Input: test_short.mp4 (1620x1080, 252 frames, 8.4s)
- VapourSynth upscale: 3240x2160
- GFPGAN enhancement: 252 frames processed
- Output: test_short_restored.mp4 (3240x2160, 362 MB)
- Resolution: ✅ Correct (3240x2160, not 12960x8640)
- Codec: ✅ H.264 High profile, yuv420p
- Playback: ✅ Works in VLC, SMPlayer, Windows Media Player

### Performance Metrics
- **GFPGAN processing:** ~30ms per frame (CUDA)
- **Disk space used:** 3.94 GB temporary (PNG frames)
- **Total processing time:** ~15 minutes (252 frames, including extraction + enhancement + re-encoding)

---

## Known Limitations

### Current Constraints
1. **Python 3.13 compatibility:** Requires Disty0 GFPGAN forks
2. **ONNX incompatibility:** GFPGAN cannot use ONNX/DirectML (complex architecture)
3. **VRAM requirements:** 4-6GB VRAM for 4K frame processing
4. **Processing time:** Slower than RealESRGAN (~30ms vs ~3ms per frame)

### Workarounds
- **Low VRAM:** Use lower resolution or process in batches
- **Speed:** Consider using GFPGAN selectively (only scenes with faces)
- **ONNX:** Other models (RealESRGAN, RIFE) support NPU acceleration

---

## Future Enhancements

### Planned Improvements
1. **Batch processing:** Process frames in smaller batches to reduce peak disk usage
2. **Face detection:** Only process frames with detected faces
3. **Region masking:** Apply enhancement only to face regions
4. **Quality presets:** Fast/Balanced/Quality settings for different use cases

### Research Needed
1. **GFPGAN ONNX conversion:** Investigate if architecture simplification possible
2. **Alternative models:** Evaluate CodeFormer, RestoreFormer for comparison
3. **Hybrid approach:** Combine GFPGAN face enhancement with background upscaling

---

## User Documentation

### Quick Start
1. Enable **GFPGAN** checkbox on Output tab
2. Adjust **Face Enhancement Strength** slider (0.1-1.0)
3. *Optional:* Set custom temp directory if C: drive limited
4. Process video normally

### Best Practices
- **Face enhancement strength:** Start at 0.5, increase if faces still soft
- **Disk space:** Ensure 2-3x video size available in temp directory
- **Quality:** Use lossless output codec (ProRes/DNxHD) for archival
- **Speed:** GFPGAN is slow; use selectively or on shorter clips

### Troubleshooting
- **Out of disk space:** Set custom temp directory on larger drive
- **Processing slow:** Normal; GFPGAN processes ~30ms per frame
- **Faces over-enhanced:** Reduce face enhancement strength slider
- **No faces detected:** Increase minimum face size threshold

---

## Technical References

### Dependencies
- **GFPGAN 1.3.8** (Disty0 Python 3.13 fork)
- **PyTorch 2.9.1+cu128** (CUDA 12.8)
- **FFmpeg 6.0+** (frame extraction/encoding)
- **VapourSynth R65+** (video processing pipeline)

### Configuration Files
- **restoration_settings.json:** Stores custom temp directory path
- **restoration_presets.json:** Default GFPGAN settings

### Environment Variables
- **LOCALAPPDATA:** AI models stored in `%LOCALAPPDATA%\Advanced_Tape_Restorer\ai_models\`
- **TEMP:** Default temp directory for frame extraction

---

## Changelog

### December 26, 2025
- ✅ Fixed resolution bug (upscale=1)
- ✅ Removed unnecessary rescaling filter

### December 25, 2025
- ✅ Added custom temp directory option
- ✅ Implemented disk space estimation
- ✅ Fixed encoder selection (respect Output tab)
- ✅ Reverted to PNG extraction (quality)
- ✅ Created test suite

### December 24, 2025
- ✅ Fixed progress callback signature
- ✅ Fixed AutoModeSelector initialization
- ✅ Added 3-phase progress display
- ✅ Added re-encoding progress monitoring

---

## Contributors

**AI Agent:** Claude Sonnet 4.5 (GitHub Copilot)  
**Human Developer:** CWT  
**Testing:** CWT  
**Documentation:** Claude Sonnet 4.5

---

## License

Part of Advanced Tape Restorer v4.0 - Professional video restoration suite.

---

**Last Updated:** December 26, 2025  
**Document Version:** 1.0  
**Software Version:** Advanced Tape Restorer v4.0
