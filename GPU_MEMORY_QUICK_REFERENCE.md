# GPU Memory Management - Quick Reference

## VRAM Requirements by Workflow

### SD Content (720×480)

| Workflow | VRAM Needed | RTX 5070 (8GB)? |
|----------|-------------|----------------|
| QTGMC only | 0.2 GB | ✅ Yes |
| QTGMC + BM3D (GPU) | 0.8 GB | ✅ Yes |
| QTGMC + BM3D + RealESRGAN 2x | 2.0 GB | ✅ Yes |
| QTGMC + BM3D + RealESRGAN + RIFE | 3.5 GB | ✅ Yes |

### HD Content (1920×1080)

| Workflow | VRAM Needed | RTX 5070 (8GB)? |
|----------|-------------|----------------|
| QTGMC only | 0.5 GB | ✅ Yes |
| QTGMC + BM3D (GPU) | 1.7 GB | ✅ Yes |
| QTGMC + BM3D + RealESRGAN 2x | 4.5 GB | ✅ Yes |
| QTGMC + BM3D + RealESRGAN + RIFE | **8.0 GB** | ⚠️ Tight fit |
| QTGMC + BM3D + RealESRGAN 4x + RIFE | **10.5 GB** | ❌ Too much |

### 4K Content (3840×2160)

| Workflow | VRAM Needed | RTX 5070 (8GB)? |
|----------|-------------|----------------|
| QTGMC only | 2.0 GB | ✅ Yes |
| QTGMC + BM3D (GPU) | 6.8 GB | ⚠️ High usage |
| QTGMC + BM3D + RealESRGAN | **18 GB+** | ❌ Needs 24GB GPU |

---

## Optimization Tips

### When You Get VRAM Warnings

1. **Disable RIFE first** → Saves ~3.5 GB
2. **Switch to ZNEDI3** (instead of RealESRGAN) → Saves ~2.5 GB  
3. **Use CPU BM3D** (instead of GPU) → Saves ~1.2 GB
4. **Reduce resolution** before AI processing → Scales with resolution²

### Best Settings for RTX 5070 (8GB)

**Maximum quality that fits:**
```
Resolution: 1920×1080 (HD)
QTGMC: Medium or Slow
BM3D: GPU, sigma 5.0
AI Upscaling: RealESRGAN 2x (not 4x)
AI Interpolation: OFF (or use separately)

Expected VRAM: ~4.5 GB ✅
```

**For 4K content:**
```
Option 1: Process without AI upscaling
Option 2: Downscale → Process → Upscale at end
Option 3: Use streaming mode (future feature)
```

---

## What the System Does Automatically

### ✅ Before Processing
- Checks available VRAM
- Estimates requirements based on resolution + filters
- Warns if insufficient (with suggestions)
- Sets VapourSynth memory limit to 80% available VRAM

### ✅ During Processing
- Monitors VRAM usage every 500ms
- Shows warnings at 85%, 90%, 95% usage
- Auto-splits large batches if needed
- Clears cache between batches when near limit

### ✅ If Memory Issues Occur
- Displays live VRAM usage in status bar
- Suggests which features to disable
- Prevents complete system freezes (reserves 20% for FFmpeg)

---

## Quick Diagnostic

### Test Your GPU
```bash
cd "C:\Advanced Tape Restorer v3.3"
.\.venv\Scripts\python.exe test_gpu_memory_optimization.py
```

**Expected output:**
```
✅ PASSED - GPU Detection
✅ PASSED - VapourSynth Memory Limit
✅ PASSED - VRAM Requirement Checking
✅ PASSED - Script Generation
```

### Check Current VRAM
In the app, look at bottom-right status bar:
```
VRAM: 2.1/8.0 GB
```

**Status indicators:**
- Normal: No warning
- ⚠️: 85-90% usage (caution)
- ⚠️ HIGH: 90-95% usage (reduce settings)
- ⚠️ CRITICAL: >95% usage (may crash)

---

## Common Scenarios

### ✅ "I want maximum quality"
**Use RealESRGAN 4x + RIFE?**
- 1080p: Needs ~10 GB VRAM ❌ Too much for RTX 5070
- **Solution:** Process in two passes:
  1. First: QTGMC + BM3D + RIFE (interpolation only)
  2. Second: RealESRGAN 4x (upscaling only on interpolated video)

### ✅ "Processing keeps failing at 50%"
**Likely cause:** VRAM running out during processing

**Solutions:**
1. Check VRAM usage in status bar when it fails
2. If >90%: Disable RIFE or use RealESRGAN 2x instead of 4x
3. Process shorter segments (split video into clips)
4. Close other applications using GPU (Chrome, games)

### ✅ "I have a 16GB+ GPU"
**Lucky you!** You can use all features simultaneously:
- 1080p: All features at once ✅
- 4K: QTGMC + BM3D + RealESRGAN 2x ✅
- 4K + RIFE: May still need 20GB+ (depends on clip length)

---

## Memory Limit Explained

### What Is `core.max_cache_size`?

VapourSynth caches processed frames in GPU memory. Without a limit, it will:
1. Fill entire VRAM
2. Leave no room for FFmpeg encoding
3. Cause system freeze or crash

**Our system sets:**
```python
core.max_cache_size = <80% of available VRAM in MB>
```

**Example for 8GB GPU:**
- Total VRAM: 8192 MB
- VapourSynth limit: 6553 MB (80%)
- FFmpeg reserved: 1639 MB (20%)

---

## Troubleshooting

### "Memory limit shows 2048 MB but I have 8GB GPU"

**Cause:** GPU not detected

**Check:**
1. Install CUDA Toolkit (11.8 or 12.1)
2. Install PyTorch with CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
3. Verify: `python -c "import torch; print(torch.cuda.is_available())"`

### "Still running out of memory"

**Try:**
1. **Clear cache before processing:**
   - Close app completely
   - Restart computer (clears GPU memory)
   
2. **Check other GPU apps:**
   ```bash
   nvidia-smi
   ```
   - Close Chrome (uses 1-2GB VRAM)
   - Close games, OBS, any video apps

3. **Reduce batch size:**
   - System auto-adjusts, but you can lower resolution temporarily
   - Process 10-minute segments instead of full video

---

## Advanced: Manual Override

### Force Higher Memory Limit

**Edit:** `core/vapoursynth_engine.py`

```python
def _calculate_memory_limit(self) -> int:
    # Original: 80% reservation
    usable_gb = free_gb * 0.80
    
    # Override to 90% (riskier, but more cache)
    usable_gb = free_gb * 0.90
    
    usable_mb = int(usable_gb * 1024)
    return max(512, usable_mb)
```

**⚠️ Warning:** May cause FFmpeg buffer underruns (stuttering)

### Disable VRAM Checks

**Edit:** `core/processor.py`

```python
# In process_video() method, comment out:
# vram_check = self._check_vram_requirements(options)
# if not vram_check['ok']:
#     # ... warning code ...
```

**⚠️ Warning:** You may start jobs that will crash later

---

## Summary

### What You Need to Know

1. **RTX 5070 (8GB) sweet spot:** 1080p + QTGMC + BM3D GPU + RealESRGAN 2x
2. **RIFE uses most VRAM:** ~3.5 GB, disable if running out of memory
3. **System auto-protects:** Sets VapourSynth limits, warns before processing
4. **Monitor status bar:** VRAM display shows live usage

### When to Worry

- ⚠️ warning icon appears in VRAM display
- Processing becomes very slow mid-job
- System fan goes to 100% and stays there

### Quick Fix

1. Stop processing
2. Close other GPU apps
3. Reduce one setting (RIFE → OFF or RealESRGAN 4x → 2x)
4. Try again

---

**For More Details:** See `GPU_MEMORY_OPTIMIZATION_IMPLEMENTATION.md`

