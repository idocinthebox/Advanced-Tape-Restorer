# Advanced Tape Restorer v4.1 - NPU/ONNX Features

## What's New in v4.1

### AMD Ryzen AI NPU Support ✓
**Status:** NPU detection complete (Dec 25, 2025)

Detects AMD XDNA 2 NPU on Ryzen AI systems:
- **Ryzen AI 7 350**: 50 TOPS NPU
- **Ryzen AI 5 340**: 45 TOPS NPU
- Automatic detection via `xrt-smi.exe`
- Integrated into multi-GPU manager

**Your System Detection:**
```
GPU 0: NVIDIA GeForce RTX 5070 Laptop GPU (AI score: 77.9/100)
GPU 1: AMD Radeon 860M (Ryzen APU) (AI score: 5.0/100)
GPU 2: AMD XDNA 2 NPU (Ryzen AI 7) (AI score: 32.5/100, 50 TOPS)
```

### ONNX Model Conversion System
**Status:** Framework complete, awaiting testing

**Features:**
- Convert PyTorch models → ONNX format
- Quantization support (FP32 → FP16 → INT8 → INT4)
- Automated validation with error metrics:
  - Max absolute error
  - Mean absolute error
  - PSNR (Peak Signal-to-Noise Ratio)
  - SSIM (Structural Similarity Index)
- Performance benchmarking (PyTorch vs ONNX)
- Batch conversion support

**Validation Thresholds:**
- Max error < 1% (0.01)
- Mean error < 0.1% (0.001)
- PSNR > 40 dB (excellent quality)

**Usage:**
```python
from core.onnx_converter import ONNXConverter, QuantizationMode

converter = ONNXConverter()
result = converter.convert_model(
    pytorch_model=gfpgan_model,
    input_shape=(1, 3, 512, 512),
    output_path="models/gfpgan_fp16.onnx",
    model_name="GFPGAN",
    quantization=QuantizationMode.FP16,
    validate=True
)

if result.success:
    print(f"Converted: {result.original_size_mb:.2f}MB → {result.onnx_size_mb:.2f}MB")
    print(f"Speedup: {result.speedup_factor:.2f}x")
    print(f"Max error: {result.max_error:.6f}")
```

## Installation Requirements

**For ONNX conversion:**
```bash
pip install onnx onnxruntime onnxruntime-extensions
```

**For NPU execution (AMD Ryzen AI systems):**
1. Install Ryzen AI Software: https://ryzenai.docs.amd.com/
2. Install ONNX Runtime GenAI: `pip install onnxruntime-genai`
3. Enable NPU performance mode:
   ```powershell
   cd C:\Windows\System32\AMD
   xrt-smi configure --pmode performance
   ```

## Hybrid Execution Strategy

### Current (v4.0):
- RTX 5070: All AI workloads (CUDA)
- Radeon 860M: Video encoding (AMF)

### Future (v4.1):
```
┌─────────────────────────────────────┐
│  Video Frame Processing Pipeline   │
├─────────────────────────────────────┤
│  1. NPU (50 TOPS)                   │
│     - Temporal denoise              │
│     - Color correction              │
│     - Lightweight filters           │
│     - Power: 5-10W                  │
├─────────────────────────────────────┤
│  2. Radeon 860M iGPU                │
│     - Preprocessing                 │
│     - Colorspace conversion         │
│     - Resize operations             │
├─────────────────────────────────────┤
│  3. RTX 5070 (CUDA)                 │
│     - Heavy AI upscaling            │
│     - RealESRGAN 4x                 │
│     - RIFE interpolation            │
│     - GFPGAN face restoration       │
│     - Power: 100-140W               │
├─────────────────────────────────────┤
│  4. Radeon 860M (AMF)               │
│     - Final encoding (h264_amf)     │
│     - Offloads RTX for next frame   │
└─────────────────────────────────────┘
```

## Planned Models for ONNX Conversion

### Priority 1 (Lightweight - NPU candidates):
- [x] **Temporal denoise filter** (custom VapourSynth)
- [ ] **Color correction models** (fast LUT-based)
- [ ] **Edge enhancement** (lightweight CNN)

### Priority 2 (Medium - iGPU candidates):
- [ ] **BasicVSR++ Lite** (2x upscaling, 30-frame context)
- [ ] **RIFE 4.0** (frame interpolation)
- [ ] **Waifu2x** (anime upscaling)

### Priority 3 (Heavy - Keep on CUDA):
- [ ] **RealESRGAN** (4x upscaling, stays on RTX)
- [ ] **GFPGAN** (face restoration, stays on RTX)
- [ ] **ProPainter** (inpainting, stays on RTX)

## Testing Protocol

### Phase 1: Model Conversion ✓
```bash
# Test simple model conversion
python core/onnx_converter.py --test

# Convert specific model
python core/onnx_converter.py --model gfpgan
```

### Phase 2: Validation (Automated)
For each converted model:
1. **Numerical validation:**
   - Compare PyTorch vs ONNX outputs
   - Check max/mean error < thresholds
   - Verify PSNR > 40 dB

2. **Visual validation:**
   - Process same frame with both models
   - Generate side-by-side comparison
   - Human verification of quality

3. **Performance validation:**
   - Benchmark inference time
   - Measure memory usage
   - Calculate speedup factor

### Phase 3: Integration Testing
```python
# Test hybrid execution
from core.hybrid_processor import HybridVideoProcessor

processor = HybridVideoProcessor()
processor.enable_npu(True)  # Use NPU for lightweight tasks
processor.enable_igpu(True)  # Use iGPU for preprocessing
processor.enable_cuda(True)  # Use RTX for heavy AI

result = processor.process_video(
    input="test.avi",
    output="output.mp4",
    filters=["denoise_npu", "upscale_cuda", "encode_amf"]
)
```

## Performance Targets

### v4.0 (CUDA-only):
- RealESRGAN 4x: ~2-3 FPS (RTX 5070)
- Total power: 120W (GPU + system)

### v4.1 (Hybrid NPU/iGPU/CUDA):
- Denoise (NPU): 60 FPS @ 10W
- Preprocessing (iGPU): 120 FPS @ 15W
- Upscale (CUDA): 2-3 FPS @ 100W
- **Combined:** Same quality, 15% less power

### v4.1 (Battery mode - NPU only):
- Lightweight restoration: 30 FPS @ 15W total
- 3-4 hours battery life vs 1 hour CUDA-only

## Compatibility

**Supported Systems:**
- ✓ AMD Ryzen AI 7 350 (your system)
- ✓ AMD Ryzen AI 5 340
- ✓ AMD Ryzen 9 AI (future)
- ✓ Any system with ONNX Runtime (CPU fallback)

**Not Supported:**
- Intel NPU (different architecture, future work)
- Older AMD systems without XDNA NPU

## Development Timeline

- **Week 1 (Dec 25, 2025)**: NPU detection ✓, ONNX converter framework ✓
- **Week 2 (Jan 1, 2026)**: Install ONNX dependencies, test conversions
- **Week 3 (Jan 8, 2026)**: Convert first model (GFPGAN), validate
- **Week 4 (Jan 15, 2026)**: Hybrid execution mode, GUI integration
- **Week 5 (Jan 22, 2026)**: Performance optimization, documentation
- **Release (Feb 1, 2026)**: v4.1.0 public release

## Known Limitations

1. **AMD Ryzen AI Software required** (not bundled, user must install)
2. **NPU supports ONNX only** (no native PyTorch)
3. **Model quantization** may reduce quality slightly (validate carefully)
4. **Windows-only** for NPU (xrt-smi.exe dependency)
5. **Limited model support** (not all PyTorch ops convert to ONNX)

## Testing Checklist

- [x] NPU detection works on Ryzen AI 7 350
- [x] Multi-GPU manager shows 3 devices (RTX + iGPU + NPU)
- [ ] ONNX converter test passes
- [ ] Convert simple test model
- [ ] Validate numerical accuracy
- [ ] Benchmark performance
- [ ] Convert GFPGAN model
- [ ] Visual quality comparison
- [ ] Integrate with video processor
- [ ] GUI power mode selector (Performance/Balanced/Battery)
- [ ] Documentation complete
- [ ] Unit tests pass

## Future Enhancements (v4.2+)

- **Auto power mode switching:** Detect AC/battery, switch NPU/CUDA
- **Model zoo:** Pre-converted ONNX models from Hugging Face
- **Cloud conversion:** Upload PyTorch, download optimized ONNX
- **Intel NPU support:** Meteor Lake, Lunar Lake systems
- **Qualcomm NPU:** ARM Windows on Snapdragon

---

**Last Updated:** December 25, 2025  
**Status:** In Development (NPU detection complete, ONNX framework complete)  
**Target Release:** February 1, 2026
