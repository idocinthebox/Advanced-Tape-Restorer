# VRAM Memory Management Fix - v4.0

## Issue Identified
VRAM usage was decreasing across versions, and system crashes were occurring due to:

1. **Missing GPU memory cleanup** - No automatic VRAM cache clearing after processing
2. **Memory accumulation** - PyTorch CUDA tensors not being released properly
3. **No garbage collection** - Python objects holding GPU references not cleaned up
4. **Insufficient synchronization** - CUDA operations not completing before next task

## Changes Implemented (December 24, 2025)

### 1. GPU Memory Cleanup System
**File: `core/processor.py`**

Added `_cleanup_gpu_memory()` method that:
- Checks VRAM usage before and after cleanup
- Logs freed memory amount
- Forces Python garbage collection
- Called automatically after every processing session

```python
def _cleanup_gpu_memory(self):
    """Clean up GPU memory to prevent VRAM leaks."""
    # Logs VRAM before/after
    # Calls gpu.clear_cache()
    # Forces gc.collect()
```

### 2. Enhanced CUDA Cache Clearing
**File: `core/gpu_accelerator.py`**

Improved `clear_cache()` method to:
- Run Python garbage collection first
- Empty CUDA cache with `torch.cuda.empty_cache()`
- Synchronize GPU with `torch.cuda.synchronize()` to ensure completion
- Better error handling and logging

```python
def clear_cache(self):
    """Clear GPU memory cache with synchronization."""
    gc.collect()  # Python GC first
    torch.cuda.empty_cache()  # Clear CUDA cache
    torch.cuda.synchronize()  # Wait for completion
```

### 3. Processing Thread Cleanup
**File: `gui/processing_thread.py`**

Added `finally` block to ensure GPU cleanup even on crashes:
- Calls `processor._cleanup_gpu_memory()` after processing
- Runs even if exceptions occur
- Prevents VRAM leaks between processing sessions

### 4. Main Processing Loop
**File: `core/processor.py` - process_video()**

Modified finally block:
```python
finally:
    self.cleanup()  # Existing cleanup
    self._cleanup_gpu_memory()  # NEW: GPU memory cleanup
```

## Expected Results

### Before Fix:
- ❌ VRAM usage accumulated across multiple processing sessions
- ❌ System crashes after 3-4 processing runs
- ❌ Memory not released until application closed
- ❌ No visibility into VRAM usage

### After Fix:
- ✅ VRAM properly released after each processing session
- ✅ System stability improved
- ✅ VRAM usage logged for troubleshooting
- ✅ Automatic memory cleanup on errors

## How to Verify the Fix

### 1. Monitor VRAM Usage
Look for these log messages after each processing session:

```
[GPU] VRAM before cleanup: 5.23 GB used, 2.77 GB free
[OK] CUDA cache cleared and synchronized
[GPU] VRAM after cleanup: 0.45 GB used, 7.55 GB free (freed 4.78 GB)
```

### 2. Test Multiple Runs
1. Process a video with AI upscaling (RealESRGAN/BasicVSR++)
2. Check VRAM usage in Task Manager or nvidia-smi
3. Process another video
4. VRAM should return to baseline between runs

### 3. Stress Test
Process 5-10 videos back-to-back:
- Monitor VRAM after each completion
- Should see consistent cleanup
- No gradual increase in baseline VRAM

## Additional Recommendations

### 1. Use Task Manager to Monitor VRAM
**Windows Task Manager:**
- Performance tab → GPU → Dedicated GPU Memory
- Watch for memory spikes and cleanup

### 2. Use nvidia-smi for Detailed Monitoring
```powershell
# Real-time VRAM monitoring (updates every 1 second)
nvidia-smi -l 1

# Or one-time check
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv
```

### 3. Optimal Processing Settings
To minimize VRAM usage while maintaining quality:

**For 8GB VRAM GPUs:**
- Use Conservative tile size (384x384)
- Avoid combining multiple AI features
- Process one video at a time

**For 6GB VRAM GPUs:**
- Use Safe tile size (256x256)
- Disable BM3D GPU if using RealESRGAN
- Consider ZNEDI3 instead of RealESRGAN for upscaling

**For 4GB VRAM GPUs:**
- Use Auto tile sizing
- CPU-only denoising
- ZNEDI3 for upscaling only

### 4. If Crashes Still Occur

**Check these:**
1. **GPU Driver** - Update to latest NVIDIA drivers
2. **CUDA Version** - Ensure CUDA 11.8 or 12.1 installed
3. **PyTorch Version** - Check compatibility with CUDA
4. **System RAM** - Ensure 16GB+ system RAM available
5. **Page File** - Windows needs sufficient virtual memory

**Diagnostic Commands:**
```powershell
# Check CUDA version
nvcc --version

# Check PyTorch CUDA availability
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Version: {torch.version.cuda}')"

# Check GPU info
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

## Code Locations Summary

| File | Change | Purpose |
|------|--------|---------|
| `core/processor.py` | Added `_cleanup_gpu_memory()` | Clean VRAM after processing |
| `core/processor.py` | Modified `finally` in `process_video()` | Call cleanup on exit |
| `core/gpu_accelerator.py` | Enhanced `clear_cache()` | Better CUDA cleanup |
| `gui/processing_thread.py` | Added `finally` block | GUI thread cleanup |

## Version History

**v4.0.1 (December 24, 2025):**
- Added comprehensive GPU memory management
- Fixed VRAM leak causing system crashes
- Added VRAM usage logging for diagnostics
- Improved CUDA synchronization

## Testing Checklist

- [ ] Process video with RealESRGAN 4x upscaling
- [ ] Check VRAM cleanup in logs
- [ ] Process 5 videos back-to-back without crashes
- [ ] Monitor Task Manager GPU memory during processing
- [ ] Verify baseline VRAM returns after each video
- [ ] Test with different GPU memory configurations
- [ ] Test cancellation mid-process (cleanup should still run)

## Support

If crashes persist after this fix:
1. Check Windows Event Viewer for driver crashes
2. Monitor GPU temperature (overheating can cause crashes)
3. Test with CPU-only processing to isolate GPU issues
4. Report issue with:
   - GPU model and VRAM amount
   - Log output showing VRAM usage
   - Processing settings used
   - Any error messages from Event Viewer

---

**Author:** GitHub Copilot (Claude Sonnet 4.5)  
**Date:** December 24, 2025  
**Applies to:** Advanced Tape Restorer v4.0+
