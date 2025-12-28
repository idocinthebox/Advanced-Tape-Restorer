# Pipe Format Fix for AI Upscaling

## Issue
When using AI upscaling (RealESRGAN) or frame interpolation (RIFE), the video processing would fail with:
```
[yuv4mpegpipe @ 0000023eff354800] Header too large.
[in#0 @ 0000023eff354580] Error opening input: Invalid argument
Error opening input file pipe:.
```

## Root Cause
- VapourSynth was outputting Y4M format through a pipe to FFmpeg
- Y4M format includes a text header with video metadata (resolution, framerate, etc.)
- When AI upscaling produces very high resolutions (e.g., 3240x2160), the Y4M header becomes too large
- FFmpeg's Y4M parser couldn't handle the large header size, causing "Header too large" error

## Solution
Implemented dynamic pipe format selection:

### 1. **Processor (core/processor.py)**
- Added logic to detect when AI features are enabled
- Switches vspipe output format based on AI usage:
  - **Normal processing**: `vspipe -c y4m` (Y4M format with self-describing header)
  - **AI processing**: `vspipe -c i420` (raw I420 format, no header)

```python
# Use Y4M for most cases, but switch to rawvideo for AI upscaling
# (Y4M headers can become too large for FFmpeg to parse with very high res)
uses_ai = options.get('use_ai_upscaling', False) or options.get('ai_interpolation', False)
if uses_ai:
    vspipe_cmd = ["vspipe", "-c", "i420", self.vs_engine.script_file, "-"]
else:
    vspipe_cmd = ["vspipe", "-c", "y4m", self.vs_engine.script_file, "-"]
```

### 2. **Output Dimensions Calculation (core/processor.py)**
- Calculate output resolution and framerate before script generation
- Account for AI upscaling (2x scale factor)
- Account for frame interpolation (2x/3x/4x framerate)
- Store dimensions in options for FFmpeg

```python
# Apply AI upscaling factor
if options.get('use_ai_upscaling', False):
    scale_factor = 2  # RealESRGAN/ZNEDI3 2x upscaling
    output_width = width * scale_factor
    output_height = height * scale_factor

# Apply frame interpolation
if options.get('ai_interpolation', False):
    factor_str = options.get('interpolation_factor', '2x (30fps→60fps)')
    if '2x' in factor_str:
        output_fps = fps * 2
```

### 3. **FFmpeg Encoder (core/ffmpeg_encoder.py)**
- Updated to handle both Y4M and raw I420 input
- When using raw I420, explicitly specify format parameters to FFmpeg:
  - Video format: `rawvideo`
  - Pixel format: `yuv420p`
  - Resolution: `{width}x{height}`
  - Frame rate: `{fps}`

```python
if uses_ai:
    # Raw I420 format - need to specify format parameters
    width = options.get('output_width', 1920)
    height = options.get('output_height', 1080)
    fps = options.get('output_fps', 30.0)
    
    cmd.extend([
        "-f", "rawvideo",
        "-pix_fmt", "yuv420p",
        "-s:v", f"{width}x{height}",
        "-r", str(fps),
        "-i", "pipe:"
    ])
else:
    # Y4M format (self-describing, includes header)
    cmd.extend(["-f", "yuv4mpegpipe", "-i", "pipe:"])
```

## Benefits
- **Fixed AI upscaling**: RealESRGAN and frame interpolation now work reliably
- **No quality loss**: Raw I420 format is lossless during pipe transfer
- **Backward compatible**: Normal processing still uses Y4M (more robust for standard resolutions)
- **Memory efficient**: Raw format has less overhead than Y4M for very high resolutions

## Testing
Test with:
1. **AI Upscaling**: Enable RealESRGAN 2x → Should output 3240x2160 without pipe errors
2. **Frame Interpolation**: Enable RIFE 2x → Should double framerate without errors
3. **Combined**: Both AI upscaling + interpolation → Should produce high-res, high-fps output
4. **Normal Processing**: Without AI → Should still work with Y4M format

## Technical Details
- **Y4M Format**: Self-describing format with plaintext header (resolution, FPS, colorspace)
- **Raw I420 Format**: Just raw YUV 4:2:0 pixel data, no header
- **FFmpeg Requirements**: When using raw format, must specify all parameters manually
- **VapourSynth**: Supports multiple output formats via `-c` flag

## Files Modified
1. `core/processor.py` - Dynamic vspipe format selection + output dimension calculation
2. `core/ffmpeg_encoder.py` - Raw video input handling with explicit format parameters
