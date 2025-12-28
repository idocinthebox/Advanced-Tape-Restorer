# Checkpoint System Scope - Which Methods Are Supported?

## Quick Answer

**Currently Implemented:** GFPGAN only  
**Can Be Extended To:** ProPainter (same architecture)  
**Not Applicable:** All VapourSynth-based methods (RealESRGAN, RIFE, etc.)

---

## Processing Method Categories

### Category 1: Frame Extraction Methods ✅ **Checkpoint System Applicable**

These methods extract ALL frames to disk before processing:

| Method | Extracts Frames? | Checkpoint Support | Disk Space Risk |
|--------|-----------------|-------------------|-----------------|
| **GFPGAN** | ✅ Yes (PNG) | ✅ **Implemented** | ⚠️ **HIGH** (508GB) |
| **ProPainter** | ✅ Yes (internal) | ✅ **Implemented** | ⚠️ **HIGH** (similar) |

**Architecture:**
```
Video → FFmpeg extract → PNG frames on disk → Python processing → Re-encode
```

**Why checkpoint system helps:**
- Frame extraction can use 400-500GB+ for 1-hour HD video
- Processing can take hours (GFPGAN: ~2-5 seconds per frame)
- Crash/stop = lose all progress without checkpoints
- Disk space can run out mid-processing

### Category 2: VapourSynth Pipeline Methods ❌ **Checkpoint System Not Needed**

These methods stream through memory without disk extraction:

| Method | Processing Type | Disk Usage | Resume Capability |
|--------|----------------|------------|-------------------|
| **RealESRGAN** | vs-realesrgan plugin | Minimal (cache only) | ❌ Not needed |
| **RIFE** | vs-rife plugin | Minimal (cache only) | ❌ Not needed |
| **BasicVSR++** | VapourSynth filter | Minimal | ❌ Not needed |
| **SwinIR** | VapourSynth filter | Minimal | ❌ Not needed |
| **ZNEDI3** | VapourSynth filter | Minimal | ❌ Not needed |
| **QTGMC** | VapourSynth filter | Minimal | ❌ Not needed |
| **DeOldify** | VapourSynth filter | Minimal | ❌ Not needed |

**Architecture:**
```
Video → VapourSynth script → vspipe.exe → FFmpeg encoder → Output video
               ↑                                ↑
           (RAM only)                      (RAM only)
```

**Why checkpoint system not needed:**
- No frame extraction to disk
- Processing streams through RAM
- VapourSynth cache: ~2-5GB max (not 508GB)
- If stopped, just restart encoding (FFmpeg is fast)
- Typical encoding time: Real-time to 0.5x (vs GFPGAN's 2-5 sec/frame)

---

## What Parts of the Solution Apply to All Methods?

### ✅ Disk Space Manager (Universal)

The `core/disk_space_manager.py` module can help ALL methods:

1. **Output video size estimation**
   - Calculate final video file size based on codec/bitrate
   - Warn if output drive full
   - Applies to: ALL methods

2. **VapourSynth cache monitoring**
   - Check available space for VapourSynth temp cache
   - Typical need: 5-10GB for HD video
   - Applies to: All VapourSynth methods

3. **Alternative drive recommendations**
   - Suggest D:\, E:\, F:\ if C:\ full
   - Applies to: ALL methods

**Example usage for all methods:**
```python
# Before any processing
disk_manager = DiskSpaceManager()
required_gb = disk_manager.estimate_output_size(
    video_path, codec="libx264", bitrate=10
)
has_space = disk_manager.check_disk_space("C:\\", required_gb)

if not has_space:
    alternatives = disk_manager.find_alternative_drives(required_gb)
    # Offer to user
```

### ❌ Checkpoint System (Frame Extraction Only)

The checkpoint/resume/migration system ONLY helps methods that:
1. Extract all frames to disk
2. Process frames one-by-one in Python
3. Can run out of disk space during extraction

**Currently:** GFPGAN only  
**Future:** ProPainter (needs implementation)

---

## Implementation Status

### ✅ Currently Implemented: GFPGAN & ProPainter

**GFPGAN:**
- `core/gfpgan_checkpoint_processor.py` (~540 lines)
- Frame-by-frame checkpoint control
- Saves every 50 frames

**ProPainter:**
- `core/propainter_checkpoint_processor.py` (~380 lines)
- Process-level checkpoint control
- Monitors external CLI subprocess
- Handles intermediate file migration

**Shared Infrastructure:**
- `gui/checkpoint_resume_dialog.py` (274 lines)
- `core/resumable_processor.py` (385 lines)
- `core/disk_space_manager.py` (376 lines)
- Integration in `core/processor.py`

**Features:**
- ✅ Checkpoint save/resume
- ✅ Startup resume dialog
- ✅ Frame/file migration on drive switch
- ✅ Alternative drive discovery
- ✅ Disk space pre-flight checks

### ❌ Not Applicable: VapourSynth Methods

These methods don't need checkpoints because:
- No disk extraction (everything in RAM)
- Fast encoding (restart is cheap)
- Minimal disk space usage

If you stop a VapourSynth-based encode:
1. Just restart it
2. FFmpeg will re-encode from scratch
3. Typical loss: 5-30 minutes (vs GFPGAN's 2-10 hours)

---

## User Experience: What Changes for Each Method?

### GFPGAN (✅ Full Checkpoint Support)

**Before checkpoint system:**
```
1. Start GFPGAN processing
2. [508GB later] Disk full, crash
3. ❌ All progress lost
4. 😢 Manual cleanup required
```

**After checkpoint system:**
```
1. Start GFPGAN processing
2. [Pre-flight check] "Need 508GB, only 200GB available"
3. [System] "Use D:\ instead? (1.5TB free)"
4. User switches to D:\
5. ✅ Processing completes
6. OR: If stopped, resume from checkpoint later
```

### ProPainter (✅ Full Checkpoint Support)

**Before checkpoint system:**
```
1. Start ProPainter inpainting
2. Extract 30,000 frames (200GB)
3. Process for 10-15 hours
4. [Stop/crash at hour 8]
5. ❌ All 8 hours of progress lost
6. Must restart from scratch
```

**After checkpoint system:**
```
1. Start ProPainter inpainting
2. [Pre-flight check] Space validated
3. Process frames 0-15,000 (8 hours)
4. [Stop/crash]
5. [Resume] System detects incomplete job
6. Continue from last checkpoint
7. ✅ Only lost minutes, not hours
```

### RealESRGAN / RIFE / Others (❌ No Checkpoints Needed)

**Normal workflow:**
```
1. Start processing with RealESRGAN 4x
2. VapourSynth streams frames through RAM
3. FFmpeg encodes to final video
4. [If stopped] Just restart
5. Loss: 5-30 minutes of encoding time
6. No disk space issues (only RAM + cache)
```

**Disk space check still helps:**
```
[Pre-flight check] "Output video will be 50GB, C:\ only has 20GB"
[System] "Save to D:\ instead?"
```

---

## Recommended Next Steps

### Priority 1: Document Limitations ✅ (Completed)

Users now understand:
- Checkpoint system = GFPGAN & ProPainter
- Other methods don't need it (streaming pipeline)
- Disk space manager helps all methods

### Priority 2: Add ProPainter Checkpoints ✅ (Completed December 28, 2025)

**Implementation complete:**
- Created `core/propainter_checkpoint_processor.py` (~380 lines)
- Integrated into `core/processor.py`
- Reuses existing infrastructure
- Handles external CLI subprocess monitoring
- Supports intermediate file migration on drive switch

**Benefits:**
- 10-15 hour processing times protected
- Same 508GB disk space protection as GFPGAN
- Resume after crashes (high VRAM = more instability)
- Alternative drive discovery when space low

### Priority 3: Universal Disk Space Checks (Enhancement)

**Add pre-flight checks to all processing methods:**

```python
# In processor.py, before ANY video processing
def _pre_flight_checks(self, video_path, output_path, options):
    """Universal pre-flight checks for all processing methods."""
    
    # 1. Estimate output video size
    estimated_gb = estimate_output_size(video_path, options.codec, options.bitrate)
    
    # 2. Check output drive space
    has_space = check_disk_space(output_path.parent, estimated_gb)
    
    # 3. If insufficient, offer alternatives
    if not has_space:
        alternatives = find_alternative_drives(estimated_gb)
        # Show dialog to user
    
    # 4. For frame extraction methods, check extraction space
    if options.enable_gfpgan or options.enable_propainter:
        extraction_gb = estimate_frame_extraction_size(video_path)
        has_space = check_disk_space(temp_dir, extraction_gb)
        # ... handle as above
```

**Benefits:**
- Prevents "output drive full" errors during encoding
- Catches issues before processing starts
- Applies to ALL methods

---

## Technical Comparison

### Frame Extraction Methods (GFPGAN, ProPainter)

| Metric | Value | Impact |
|--------|-------|--------|
| **Disk usage** | 400-500GB (1 hour HD) | ⚠️ **CRITICAL** |
| **Processing time** | 2-10 hours | ⚠️ **CRITICAL** |
| **Frame count** | 30,000-50,000+ | Large checkpoint state |
| **Failure cost** | Lose hours of work | ⚠️ **CRITICAL** |
| **Resume value** | ✅ **VERY HIGH** | Worth implementing |

**Why checkpoints essential:**
- High disk usage → likely to exhaust space
- Long processing → likely to fail/interrupt
- Python processing → can save state easily

### VapourSynth Pipeline Methods (Everything Else)

| Metric | Value | Impact |
|--------|-------|--------|
| **Disk usage** | 2-5GB (VapourSynth cache) | ✅ **LOW RISK** |
| **Processing time** | 10 min - 2 hours | ✅ **TOLERABLE** |
| **Restart cost** | Re-encode from scratch | ✅ **ACCEPTABLE** |
| **Failure cost** | 10-30 minutes lost | ✅ **LOW** |
| **Resume value** | ❌ **LOW** | Not worth complexity |

**Why checkpoints not needed:**
- Low disk usage → rarely exhausts space
- Fast encoding → restart is acceptable
- Streaming pipeline → hard to checkpoint (would need FFmpeg segment encoding)

---

## Frequently Asked Questions

### Q: Can I resume a RealESRGAN encode if I stop it?

**A:** No, but you don't need to. Just restart the encode:
- RealESRGAN runs through VapourSynth (RAM only)
- FFmpeg encodes at 0.5x - 2x real-time
- Restarting loses 10-30 minutes of work
- **Alternative:** Use FFmpeg segment encoding for very long videos

### Q: What if my output drive fills up during encoding?

**A:** The disk space manager will help (future enhancement):
- Pre-flight check estimates final video size
- Warns if output drive insufficient
- Suggests alternative drives (D:\, E:\, etc.)
- **Currently:** You'll get an FFmpeg error, change output path, restart

### Q: Can I switch output paths mid-processing for VapourSynth methods?

**A:** Not without restarting:
- VapourSynth pipeline is one continuous stream
- FFmpeg outputs to file path specified at start
- **Workaround:** Stop encoding, change path, restart (loss: 10-30 min)

### Q: What about batch processing multiple videos?

**A:** Batch queue continues on failure:
- If video 2/5 fails, videos 3-5 still process
- Checkpoints help GFPGAN/ProPainter within each video
- Batch system already handles per-video failures

### Q: Why not implement segment encoding for VapourSynth methods?

**A:** Complexity vs benefit:
- FFmpeg supports `-f segment` for splitting output
- Would allow resume from last segment
- **Complexity:** 
  - Need to track segment progress
  - Concatenate segments at end
  - Handle codec keyframe issues
- **Benefit:** Save 10-30 minutes on restart
- **Conclusion:** Not worth it (vs GFPGAN's 2-10 hours saved)

---

## Summary

### What the Checkpoint System Solves

✅ **GFPGAN:** 508GB disk exhaustion, 2-10 hour processing, frame-by-frame recovery  
✅ **ProPainter:** 10-15 hour processing, disk exhaustion, subprocess crash recovery  
❌ **VapourSynth methods:** Different architecture, checkpoints not applicable

### What Applies to All Methods

✅ **Disk space manager:** Pre-flight checks, alternative drives, space monitoring  
✅ **Error handling:** Graceful failures, clear messages  
✅ **Progress tracking:** Real-time progress bars and ETAs

### Recommendation

**Current implementation is complete:**
- ✅ Checkpoint system for GFPGAN (solves critical 508GB problem)
- ✅ Checkpoint system for ProPainter (solves 10-15 hour crash risk)
- ✅ VapourSynth methods don't need checkpoints (different architecture)
- ✅ Disk space manager provides universal pre-flight checks

**Optional future work:**
- Add universal output space checks for all methods (minor enhancement)
- Add FFmpeg segment encoding for VapourSynth methods (low priority, complex)

---

**Version:** 4.1.0  
**Last Updated:** December 28, 2025  
**Status:** ✅ Documented - GFPGAN only, by design
