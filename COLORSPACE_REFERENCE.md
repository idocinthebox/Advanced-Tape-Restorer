# Colorspace Reference Guide
**Advanced Tape Restorer v4.0 - Plugin & AI Model Colorspace Requirements**

This document provides a comprehensive reference for colorspace requirements across all VapourSynth plugins, AI models, and encoding pipelines used in the project.

---

## Table of Contents
- [Understanding Colorspaces](#understanding-colorspaces)
- [VapourSynth Plugins](#vapoursynth-plugins)
- [AI Models](#ai-models)
- [FFmpeg Encoding](#ffmpeg-encoding)
- [Common Conversion Patterns](#common-conversion-patterns)
- [Troubleshooting](#troubleshooting)

---

## Understanding Colorspaces

### YUV Formats (Video Standard)
- **YUV420P8**: 8-bit 4:2:0 chroma subsampling (most common video format)
- **YUV420P10**: 10-bit 4:2:0 (HDR, high-quality archival)
- **YUV444P8**: 8-bit 4:4:4 (no chroma subsampling, lossless workflows)
- **Characteristics**: 
  - Y = Luma (brightness)
  - U/V = Chroma (color)
  - Efficient for video compression (smaller file sizes)
  - Used by: QTGMC, EEDI3, NNEDI3, ZNEDI3, most video codecs

### RGB Formats (Computer Graphics)
- **RGB24**: 8-bit RGB with 3 bytes per pixel (24-bit color)
- **RGB48**: 16-bit RGB with 6 bytes per pixel (48-bit color, high precision)
- **RGBS**: 32-bit floating-point RGB (single-precision, AI models)
- **Characteristics**:
  - R/G/B = Red/Green/Blue channels
  - No chroma subsampling (full color resolution)
  - Used by: RealESRGAN, GFPGAN, DeOldify, image processing

### Grayscale Formats
- **GRAY8**: 8-bit grayscale (1 byte per pixel)
- **GRAY16**: 16-bit grayscale (2 bytes per pixel)
- **Characteristics**:
  - Single channel (luminance only)
  - Used by: Some AI models for internal processing

### Matrix Coefficients
- **'709'**: BT.709 (HDTV standard, 1080p and below)
- **'470bg'**: BT.601 PAL (analog PAL/SECAM)
- **'170m'**: BT.601 NTSC (analog NTSC, VHS tapes)
- **'2020'**: BT.2020 (UHD, 4K HDR)

**IMPORTANT**: Always specify `matrix_in_s` when converting FROM YUV and `matrix_s` when converting TO YUV to preserve color accuracy.

---

## VapourSynth Plugins

### Source Filters

#### BestSource2 (core.bs.VideoSource)
- **Output**: YUV420P8, YUV420P10, or RGB24 (depends on source)
- **Auto-detection**: Automatically selects best format for input
- **Conversion**: None needed (outputs native format)
- **Notes**: Preferred source filter for v4.0 (best accuracy)

#### FFMS2 (core.ffms2.Source)
- **Output**: YUV420P8 (default), can output RGB24 with `format` parameter
- **Conversion**: None needed for standard processing
- **Notes**: Legacy fallback, less accurate than BestSource2

#### L-SMASH (core.lsmas.LWLibavSource, LibavSMASHSource)
- **Output**: YUV420P8 (default), supports multiple formats
- **Conversion**: None needed for standard processing
- **Notes**: Fast indexing, good for quick tests

### Deinterlacing & Upscaling

#### QTGMC (via havsfunc)
- **Input**: YUV420P8 (recommended), YUV420P10 (10-bit sources)
- **Output**: Same as input (preserves format)
- **Conversion**: Not required (works in YUV space)
- **Notes**: 
  - Operates natively in YUV
  - Uses EEDI3/NNEDI3 internally (also YUV-native)
  - DO NOT convert to RGB before QTGMC (massive quality loss)

#### EEDI3/EEDI3CL (core.eedi3m.EEDI3, EEDI3CL)
- **Input**: YUV420P8, YUV444P8, GRAY8
- **Output**: Same as input
- **Conversion**: Not required
- **Notes**: Used internally by QTGMC for edge-directed interpolation

#### NNEDI3 (core.nnedi3.nnedi3)
- **Input**: YUV420P8, GRAY8
- **Output**: Same as input
- **Conversion**: Not required
- **Notes**: Neural network deinterlacer, YUV-native

#### ZNEDI3 (core.znedi3.nnedi3)
- **Input**: YUV420P8, YUV444P8, GRAY8
- **Output**: Same as input
- **Conversion**: Not required
- **Notes**: Faster NNEDI3 implementation, GPU-accelerated

### Image I/O

#### fpng (core.fpng.Write) ⚠️ REQUIRES RGB24
- **Input**: **RGB24 ONLY** (strict requirement)
- **Output**: PNG files (RGB24)
- **Conversion**: **ALWAYS REQUIRED** from YUV
- **Example**:
  ```python
  clip = core.lsmas.LWLibavSource(video)  # YUV420P8
  clip = core.resize.Bicubic(clip, format=vs.RGB24, matrix_in_s='709')  # Convert to RGB24
  clip.fpng.Write("output/frame_%06d.png")  # Now safe to use
  ```
- **Notes**: 
  - 142x faster than imwri for PNG writing (871 fps vs 6 fps)
  - Requires exact RGB24 format (not RGB48, not RGBS)
  - Fixed in v4.0: Added automatic conversion in `processor.py::_extract_frames_fpng()`

#### imwri (core.imwri.Write)
- **Input**: RGB24, RGB48, GRAY8, GRAY16
- **Output**: PNG, TIFF, JPEG files
- **Conversion**: Required if source is YUV
- **Example**:
  ```python
  clip = core.lsmas.LWLibavSource(video)  # YUV420P8
  clip = core.resize.Bicubic(clip, format=vs.RGB24, matrix_in_s='709')
  clip.imwri.Write("output/frame_%06d.png")
  ```
- **Notes**: Slower than fpng but more flexible (supports JPEG, TIFF)

### AI Upscaling Plugins

#### vs-realesrgan (core.realesrgan.RealESRGAN)
- **Input**: RGBS (32-bit float RGB) **ONLY**
- **Output**: RGBS
- **Conversion**: **ALWAYS REQUIRED** from YUV
- **Example**:
  ```python
  clip = core.lsmas.LWLibavSource(video)  # YUV420P8
  clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')  # Convert to RGBS
  clip = core.realesrgan.RealESRGAN(clip, model='realesr-animevideov3')
  clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s='709')  # Convert back
  ```
- **Notes**:
  - Uses CUDA/ROCm for GPU acceleration
  - Tile size auto-calculated based on VRAM (see `gpu_accelerator.py`)
  - Supports 2x, 4x upscaling

#### vs-rife (core.rife.RIFE)
- **Input**: RGBS (32-bit float RGB)
- **Output**: RGBS
- **Conversion**: Required from YUV
- **Example**:
  ```python
  clip = core.lsmas.LWLibavSource(video)  # YUV420P8
  clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')
  clip = core.rife.RIFE(clip, model='4.6', factor_num=2, factor_den=1)  # 2x interpolation
  clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s='709')
  ```
- **Notes**:
  - Frame interpolation (increases FPS)
  - Supports 2x, 3x, 4x frame rate multiplication

---

## AI Models

### RealESRGAN (Upscaling)
- **Input**: RGB (3-channel, 8-bit or float)
- **Output**: RGB (same bit depth as input)
- **Conversion**: YUV → RGB before inference
- **PyTorch Input**: `torch.Tensor` shape `[B, C, H, W]` with C=3 (RGB)
- **ONNX Input**: `float32[1,3,H,W]` (NCHW layout, RGB order)
- **Notes**:
  - v4.1: ONNX version reduces 3.82MB → 0.16MB (95.9% compression)
  - NPU-compatible via DirectML (40x speedup)
  - Used in VapourSynth via `vs-realesrgan` plugin (handles conversion internally)

### RIFE (Frame Interpolation)
- **Input**: RGB (3-channel float32)
- **Output**: RGB (3-channel float32)
- **Conversion**: YUV → RGB before inference
- **PyTorch Input**: 2 frames as `torch.Tensor` `[2, 3, H, W]` (RGB)
- **ONNX Input**: `float32[2,3,H,W]` (stacked frame pairs)
- **Notes**:
  - v4.1: ONNX version reduces 2.11MB → 0.01MB (99.8% compression)
  - NPU-compatible via DirectML
  - Requires temporal consistency (2+ frames)

### GFPGAN (Face Restoration)
- **Input**: RGB (3-channel, 8-bit BGR format via OpenCV)
- **Output**: RGB (3-channel, 8-bit BGR)
- **Conversion**: YUV → RGB (via FFmpeg frame extraction or cv2.cvtColor)
- **PyTorch Input**: `torch.Tensor` `[1, 3, 512, 512]` normalized to [-1, 1]
- **ONNX**: ⚠️ **Not compatible** with Python 3.13 (requires 3.11/3.12)
- **OpenCV Format**: BGR (not RGB!) - `cv2.imread()` returns BGR
- **Notes**:
  - Face detection uses `retinaface_resnet50` (RGB input)
  - Enhancement model uses BGR (OpenCV standard)
  - Color space conversion: `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` for display
  - v4.0: Scene-change detection disabled (caused duplicate frames)
  - v4.0: JIT compilation disabled (signature mismatch)

### BasicVSR++ (Video Restoration)
- **Input**: RGB (3-channel float32)
- **Output**: RGB (3-channel float32)
- **Conversion**: YUV → RGB before inference
- **PyTorch Input**: `torch.Tensor` `[1, T, 3, H, W]` (T = temporal frames, typically 7-15)
- **ONNX Input**: `float32[1,T,3,H,W]` (5D tensor with temporal dimension)
- **Notes**:
  - v4.1: ONNX version reduces 2.69MB → 0.01MB (99.6% compression)
  - Requires multiple frames for temporal processing
  - NPU-compatible via DirectML

### SwinIR (Transformer Upscaling)
- **Input**: RGB (3-channel float32)
- **Output**: RGB (3-channel float32)
- **Conversion**: YUV → RGB before inference
- **PyTorch Input**: `torch.Tensor` `[1, 3, H, W]` (RGB)
- **ONNX Input**: `float32[1,3,H,W]` (NCHW layout)
- **Notes**:
  - v4.1: ONNX version reduces 2.13MB → 0.01MB (99.7% compression)
  - Supports 2x, 3x, 4x upscaling
  - NPU-compatible via DirectML

### DeOldify (Colorization)
- **Input**: RGB (3-channel, expects grayscale as RGB with R=G=B)
- **Output**: RGB (3-channel, colorized)
- **Conversion**: YUV → RGB, optionally desaturate for B&W sources
- **PyTorch Input**: `torch.Tensor` `[1, 3, H, W]` normalized
- **ONNX**: Requires fastai architecture (complex conversion)
- **Notes**:
  - Uses fastai framework (not pure PyTorch)
  - Artistic colorization (not photorealistic)

### ProPainter (Video Inpainting)
- **Input**: RGB (3-channel float32)
- **Output**: RGB (3-channel float32)
- **Conversion**: YUV → RGB before inference
- **PyTorch Input**: `torch.Tensor` `[1, T, 3, H, W]` + mask `[1, T, 1, H, W]`
- **ONNX**: Large model, requires external installation
- **Notes**:
  - Requires 12GB+ VRAM
  - Temporal model (needs multiple frames)
  - Not bundled in default distribution

### ZNEDI3 (Fast Upscaling)
- **Input**: YUV420P8, YUV444P8, GRAY8
- **Output**: Same as input
- **Conversion**: **NOT REQUIRED** (works in YUV space)
- **Notes**:
  - VapourSynth native plugin (not PyTorch)
  - Faster than neural network methods
  - Used for quick 2x upscaling in QTGMC

---

## FFmpeg Encoding

### Input to FFmpeg (from VapourSynth)
- **Y4M Pipe**: **YUV420P8 REQUIRED** (VapourSynth → FFmpeg pipe)
- **Conversion**: Final VapourSynth script MUST output YUV420P8
- **Enforcement**: `processor.py` automatically converts at end of pipeline:
  ```python
  if video.format.id != vs.YUV420P8:
      video = core.resize.Bicubic(video, format=vs.YUV420P8, matrix_s='709')
  ```

### Codec Requirements

#### libx264/libx265 (H.264/H.265)
- **Input**: YUV420P8 (standard), YUV420P10 (10-bit variant)
- **Output**: Compressed H.264/H.265 bitstream
- **Notes**: Most compatible format for playback

#### NVENC (NVIDIA Hardware Encoder)
- **Input**: YUV420P8, NV12 (hardware-accelerated)
- **Output**: Compressed H.264/H.265
- **Notes**: Faster encoding, slightly lower quality than CPU

#### AMF (AMD Hardware Encoder)
- **Input**: YUV420P8, NV12
- **Output**: Compressed H.264/H.265
- **Notes**: AMD GPU acceleration

#### QuickSync (Intel Hardware Encoder)
- **Input**: YUV420P8, NV12
- **Output**: Compressed H.264/H.265
- **Notes**: Intel iGPU acceleration

#### ProRes (Apple ProRes)
- **Input**: YUV422P10 (preferred), YUV420P10
- **Output**: ProRes 422 HQ
- **Notes**: High-quality intermediate codec

### Frame Extraction (for GFPGAN)
- **Output**: PNG files (RGB24 for fpng, RGB24/48 for imwri)
- **Conversion**: FFmpeg automatically converts YUV → RGB when extracting to PNG
- **Command**: `ffmpeg -i video.mp4 frame_%06d.png` (auto-converts to RGB24)

---

## Common Conversion Patterns

### Pattern 1: YUV → RGB for AI Processing (VapourSynth)
```python
# Load video (typically YUV420P8)
clip = core.lsmas.LWLibavSource("input.mp4")

# Convert to RGB for AI model
clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')

# Apply AI processing (RealESRGAN, RIFE, etc.)
clip = core.realesrgan.RealESRGAN(clip, model='realesr-animevideov3')

# Convert back to YUV420P8 for encoding
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s='709')
```

### Pattern 2: YUV → RGB24 for fpng Export
```python
# Load video (YUV420P8)
clip = core.lsmas.LWLibavSource("input.mp4")

# Convert to RGB24 (fpng requirement)
clip = core.resize.Bicubic(clip, format=vs.RGB24, matrix_in_s='709')

# Write frames
clip.fpng.Write("output/frame_%06d.png")
```

### Pattern 3: GFPGAN Frame Processing (OpenCV)
```python
import cv2

# Read frame (OpenCV reads as BGR)
frame = cv2.imread("frame_000001.png")  # BGR format

# GFPGAN expects BGR (OpenCV native format)
enhanced = enhancer.enhance(frame)  # Input: BGR, Output: BGR

# Save or display (OpenCV writes BGR to file correctly)
cv2.imwrite("enhanced_000001.png", enhanced)

# Convert to RGB only for display or non-OpenCV processing
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

### Pattern 4: Theatre Mode (YUV Chroma Correction)
```python
# Theatre Mode operates in YUV space (no RGB conversion)
clip = core.lsmas.LWLibavSource("input.mp4")

# Chroma correction in YUV (no conversion needed)
clip = apply_chroma_correction(clip, shift_x=0.5, shift_y=0.0)

# QTGMC deinterlacing (YUV native)
clip = haf.QTGMC(clip, Preset='Medium', TFF=True)

# Levels adjustment (YUV native)
clip = apply_levels(clip, black_point=16, white_point=235)

# Output as YUV420P8 for encoding
```

### Pattern 5: Mixed Processing Pipeline
```python
# Load video
clip = core.lsmas.LWLibavSource("input.mp4")  # YUV420P8

# Stage 1: Deinterlacing (YUV native)
clip = haf.QTGMC(clip, Preset='Medium', TFF=True)

# Stage 2: AI Upscaling (requires RGB)
clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')
clip = core.realesrgan.RealESRGAN(clip, model='realesr-animevideov3')

# Stage 3: Frame Interpolation (already in RGB)
clip = core.rife.RIFE(clip, model='4.6', factor_num=2, factor_den=1)

# Stage 4: Convert back to YUV for encoding
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s='709')
```

---

## Troubleshooting

### Error: "Write: Only RGB24 input is supported"
**Plugin**: fpng  
**Cause**: Video is in YUV format but fpng requires RGB24  
**Solution**: Add conversion before fpng.Write():
```python
clip = core.resize.Bicubic(clip, format=vs.RGB24, matrix_in_s='709')
clip.fpng.Write("output/frame_%06d.png")
```

### Error: "RealESRGAN: Expected RGBS format"
**Plugin**: vs-realesrgan  
**Cause**: Video is in YUV but RealESRGAN requires RGBS (float RGB)  
**Solution**: Add conversion before RealESRGAN:
```python
clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')
clip = core.realesrgan.RealESRGAN(clip, model='realesr-animevideov3')
```

### Error: FFmpeg "Incompatible pixel format 'rgb24' for codec 'libx264'"
**Cause**: Trying to encode RGB directly with H.264  
**Solution**: Convert to YUV420P8 at end of VapourSynth script:
```python
if video.format.id != vs.YUV420P8:
    video = core.resize.Bicubic(video, format=vs.YUV420P8, matrix_s='709')
```

### Color Shift After Processing
**Cause**: Missing or incorrect matrix coefficients during YUV↔RGB conversion  
**Solution**: Always specify matrix:
```python
# YUV → RGB
clip = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s='709')

# RGB → YUV
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s='709')
```

### GFPGAN Color Issues
**Cause**: OpenCV uses BGR, not RGB  
**Solution**: No conversion needed! GFPGAN expects BGR:
```python
frame_bgr = cv2.imread("frame.png")  # Already BGR
enhanced = enhancer.enhance(frame_bgr)  # Expects BGR, outputs BGR
cv2.imwrite("enhanced.png", enhanced)  # OpenCV saves BGR correctly
```

---

## Performance Notes

### Conversion Overhead
- **YUV → RGB**: ~5-10% performance penalty
- **RGB → YUV**: ~5-10% performance penalty
- **Recommendation**: Minimize conversions by grouping RGB operations together

### fpng vs imwri
- **fpng**: 871 fps (RGB24 only, strict requirement)
- **imwri**: 6 fps (flexible formats, slower)
- **Speedup**: 142x faster with fpng (when RGB24 available)
- **Usage**: Prefer fpng for GFPGAN frame extraction (after conversion)

### Matrix Coefficients Impact
- **Incorrect matrix**: Color shift (reds become orange, blues become purple)
- **Missing matrix**: VapourSynth uses BT.601 as default (wrong for HD video)
- **Correct matrix**: Use '709' for HD content (1080p), '170m' for NTSC analog

---

## Version History

### v4.0 (December 2025)
- Fixed fpng RGB24 requirement (added automatic conversion in `processor.py::_extract_frames_fpng()`)
- Documented all colorspace requirements for plugins and AI models
- Added Theatre Mode YUV-native processing documentation

### v4.1 (December 2025)
- Added ONNX model colorspace requirements (NPU/DirectML support)
- Documented PyTorch vs ONNX tensor formats
- Added model compression statistics (95-99% size reduction)

---

## References

- VapourSynth Documentation: http://www.vapoursynth.com/doc/
- BT.709 Color Space: https://en.wikipedia.org/wiki/Rec._709
- GFPGAN Repository: https://github.com/TencentARC/GFPGAN
- RealESRGAN Repository: https://github.com/xinntao/Real-ESRGAN
- RIFE Repository: https://github.com/megvii-research/ECCV2022-RIFE
- fpng Plugin: https://github.com/Mikewando/vsfpng

---

**Last Updated**: December 26, 2025  
**Maintainer**: Advanced Tape Restorer Development Team  
**AI Agent Optimized**: Claude Sonnet 4.5, GitHub Copilot
