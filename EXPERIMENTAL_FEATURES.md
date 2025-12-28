# Experimental Features Guide

## AI Frame Interpolation (RIFE)

### Current Status: ✅ ENABLED in Production (as of 11/23/2025)

**Solution Found**: PyTorch 2.9.1+cu128 (CUDA 12.8) **supports RTX 5070 Blackwell (sm_120)**!

### Test Results

✅ **RealESRGAN**: Successfully tested 320x240 → 640x480 upscaling (7.66 fps)  
✅ **RIFE**: Successfully tested 3 frames → 6 frames interpolation (19.05 fps)  
✅ **Compute Capability**: sm_120 (12.0) detected correctly  
✅ **CUDA Version**: 12.8  
✅ **PyTorch Version**: 2.9.1+cu128

### How to Install PyTorch with Blackwell Support

If you need to reinstall or update PyTorch for RTX 5070:

```powershell
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

**Important**: Use the `cu128` index URL (CUDA 12.8), not `cu124` (CUDA 12.4).

---

## Feature Flag

The feature flag in `gui/main_window.py` line ~557 is now set to `True`:

```python
ENABLE_EXPERIMENTAL_FEATURES = True  # ✅ PyTorch 2.9.1+cu128 has Blackwell support!
```

To disable RIFE in builds (if needed):
```python
ENABLE_EXPERIMENTAL_FEATURES = False  # Hides AI Frame Interpolation controls
```

4. **Test RIFE**:
   ```powershell
   python -c "from vsrife import rife; import torch; print('CUDA:', torch.cuda.is_available())"
   ```
   Should show `CUDA: True` without errors.

---

## Checking PyTorch CUDA Compatibility

Run this to verify your GPU is supported:
```python
import torch
if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    compute_capability = f"sm_{props.major}{props.minor}"
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Compute Capability: {compute_capability}")
    print(f"Supported by PyTorch: {compute_capability in ['sm_50', 'sm_60', 'sm_61', 'sm_70', 'sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_120']}")
else:
    print("CUDA not available")
```

---

## Alternative: RealESRGAN Upscaling

**Same PyTorch dependency** - RealESRGAN also requires PyTorch 2.7+ for RTX 5070.

**Current workaround**: Use **ZNEDI3 (Fast, VapourSynth)** in the AI Method dropdown. ZNEDI3 works perfectly and is often better for VHS restoration due to:
- Native deinterlacing integration
- Much faster processing (10-30x)
- No PyTorch dependency
- OpenCL GPU acceleration

---

## Production-Ready Features (Working Now)

✅ **ZNEDI3 AI Upscaling** - Fast, GPU-accelerated, perfect quality  
✅ **ProPainter AI Inpainting** - Uses separate venv, works great  
✅ **QTGMC Deinterlacing** - Industry standard  
✅ **BM3D Denoising** - CPU/GPU options  
✅ **Color Correction** - Auto white balance, fade restoration  
✅ **All standard filters** - Debanding, stabilization, chroma fix  

---

## Expected Timeline

**PyTorch 2.7** with Blackwell support is expected **Q1-Q2 2026**.

Monitor: https://github.com/pytorch/pytorch/issues (search for "Blackwell" or "sm_120")

When available, simply flip the feature flag and rebuild to enable RIFE interpolation.
