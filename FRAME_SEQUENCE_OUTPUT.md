# Frame Sequence Output Feature

**Version:** 4.1  
**Date:** December 27, 2025  
**Feature Type:** Output Enhancement

## Overview

Advanced Tape Restorer now supports outputting individual frames instead of encoded video files. This enables professional workflows that require frame sequences for further processing in compositing, VFX, or color grading applications.

## Supported Formats

| Format | Bit Depth | Compression | Use Case |
|--------|-----------|-------------|----------|
| **PNG** | 8-bit | Lossless | General purpose, good compression |
| **TIFF** | 16-bit | LZW (lossless) | Professional archival, color grading |
| **JPEG** | 8-bit | Quality 95 | Small files, preview sequences |
| **DPX** | 10-bit | Uncompressed | Cinema standard, DI workflows |

## GUI Usage

### 1. Select Frame Sequence Mode

In the **Output** tab:

1. **Output Mode:** Select `Frame Sequence` (instead of `Video File`)
2. **Frame Format:** Choose desired format:
   - `PNG (Lossless)` - Best for general use
   - `TIFF 16-bit` - Best for color grading
   - `JPEG (Quality 95)` - Best for small file size
   - `DPX (Cinema)` - Best for cinema/DI workflows

### 2. Select Output Directory

1. Click **Browse...** button (now shows directory picker)
2. Choose destination folder for frame sequence
3. Pattern will be auto-generated: `frame_%06d.png` (or `.tif`, `.jpg`, `.dpx`)

### 3. Process Video

1. Configure restoration settings as usual (deinterlacing, AI upscaling, etc.)
2. Click **Start Processing**
3. Frames will be written to selected directory

## Output Naming Convention

Frames are numbered with 6-digit zero-padding:

```
frame_000000.png
frame_000001.png
frame_000002.png
...
frame_007559.png  (for 5-minute video at 25fps)
```

## Technical Details

### FFmpeg Commands Generated

**PNG (Lossless):**
```bash
ffmpeg -f yuv4mpegpipe -i pipe: \
  -f image2 -start_number 0 \
  -y frame_%06d.png
```

**TIFF 16-bit:**
```bash
ffmpeg -f yuv4mpegpipe -i pipe: \
  -pix_fmt rgb48le -compression_algo lzw \
  -f image2 -start_number 0 \
  -y frame_%06d.tif
```

**JPEG (Quality 95):**
```bash
ffmpeg -f yuv4mpegpipe -i pipe: \
  -qscale:v 2 \
  -f image2 -start_number 0 \
  -y frame_%06d.jpg
```

**DPX (Cinema):**
```bash
ffmpeg -f yuv4mpegpipe -i pipe: \
  -pix_fmt rgb48le -bits_per_raw_sample 10 \
  -f image2 -start_number 0 \
  -y frame_%06d.dpx
```

### Pattern Detection

Frame sequence mode is auto-detected when output path contains `%d` pattern:
- `C:\output\frame_%06d.png` → Frame sequence ✓
- `C:\output\video.mp4` → Video file ✓

### Audio Handling

**Frame sequences do NOT include audio.** Audio track is automatically skipped. To preserve audio:

1. Process video with frame sequence output
2. Separately extract audio: `ffmpeg -i input.mp4 -vn -c:a copy audio.aac`
3. Remux frames back to video: `ffmpeg -i frame_%06d.png -i audio.aac -c:v libx264 -c:a copy output.mp4`

## Performance Considerations

### File Size

| Format | Resolution | Frames/GB | Storage for 5min @25fps |
|--------|------------|-----------|-------------------------|
| PNG | 720x480 | ~5000 | 1.5 GB |
| PNG | 1920x1080 | ~1200 | 6.3 GB |
| TIFF 16-bit | 1920x1080 | ~400 | 18.9 GB |
| JPEG Q95 | 1920x1080 | ~6000 | 1.3 GB |
| DPX 10-bit | 1920x1080 | ~300 | 25.2 GB |

### Write Speed

- **PNG:** Fast write, good compression
- **TIFF:** Slower write, best quality
- **JPEG:** Fastest write, lossy compression
- **DPX:** Moderate write, uncompressed

## Workflow Examples

### Example 1: VFX/Compositing Workflow

**Goal:** Restore VHS tape, output frames for After Effects compositing

1. **Output tab:**
   - Output Mode: `Frame Sequence`
   - Frame Format: `PNG (Lossless)`
   - Browse: `C:\VFX_Project\footage\restored\`

2. **Process video** (applies deinterlacing, AI upscaling, etc.)

3. **Import to After Effects:**
   - File → Import → File
   - Select `frame_000000.png`
   - Check "PNG Sequence"
   - Framerate: Match original (e.g., 29.97fps)

### Example 2: Color Grading Workflow

**Goal:** Professional color grading in DaVinci Resolve

1. **Output tab:**
   - Output Mode: `Frame Sequence`
   - Frame Format: `TIFF 16-bit`
   - Browse: `C:\ColorGrade\scans\`

2. **Process video** (preserve maximum dynamic range)

3. **Import to DaVinci Resolve:**
   - Media Pool → Import Media
   - Select `frame_000000.tif`
   - Choose "Image Sequence"
   - Framerate: Match source

4. **Grade frames** (full 16-bit precision)

5. **Export back to video:**
   - Deliver → Format: MP4/ProRes
   - Codec: ProRes 4444 XQ (preserves grading)

### Example 3: Cinema DI Workflow

**Goal:** Cinema-grade Digital Intermediate

1. **Output tab:**
   - Output Mode: `Frame Sequence`
   - Frame Format: `DPX (Cinema)`
   - Browse: `D:\DI\project_name\scans\`

2. **Process video** (AI upscaling to 4K)

3. **Import to DaVinci Resolve/Baselight:**
   - Standard DPX import (10-bit log)
   - Apply LUT/color transform
   - Export to cinema package

## Limitations

1. **No audio in frame sequences** - Must be handled separately
2. **Large file sizes** - Especially TIFF/DPX at high resolutions
3. **Slower processing** - Frame write I/O can be bottleneck
4. **Manual remuxing required** - If final video output needed

## Troubleshooting

### Issue: "Out of disk space" error

**Cause:** Frame sequences consume significantly more space than video files.

**Solution:**
- Use JPEG format for smaller files
- Use PNG instead of TIFF
- Process shorter clips
- Free disk space (TIFF 1080p needs ~3.7GB per minute)

### Issue: Frames numbered incorrectly

**Cause:** Output pattern doesn't match %06d format.

**Solution:**
- Use Browse button (auto-generates correct pattern)
- Manual pattern: `frame_%06d.png` (exactly 6 digits with zero-padding)

### Issue: Missing frames

**Cause:** Processing stopped/crashed mid-encode.

**Solution:**
- Check console log for errors
- Verify sufficient disk space
- Resume from last frame number (if partial sequence)

## Code Implementation

### Files Modified

1. **`core/ffmpeg_encoder.py`** - Frame sequence detection and command building
2. **`gui/main_window.py`** - GUI controls for output mode selection

### Key Functions

```python
# Detect frame sequence pattern
is_frame_sequence = "%" in output_file and "d" in output_file

# Build FFmpeg command for PNG
if is_frame_sequence:
    cmd.extend(["-f", "image2", "-start_number", "0"])
    cmd.extend(["-y", output_file])  # e.g., "frame_%06d.png"
```

### Settings Persistence

Frame sequence options saved to `restoration_settings.json`:

```json
{
  "output_mode": "Frame Sequence",
  "frame_format": "PNG (Lossless)"
}
```

## Future Enhancements

**Potential additions (not yet implemented):**

1. **Custom frame numbering** - Start number, step size
2. **Subfolder organization** - Group frames by scene/shot
3. **Lossless video codecs** - FFV1, UT Video as alternative
4. **Batch frame processing** - Multi-threaded frame write
5. **OpenEXR support** - 32-bit float for HDR workflows

---

**Version History:**
- **v4.1** (Dec 27, 2025) - Initial implementation
  - PNG, TIFF, JPEG, DPX support
  - Automatic pattern generation
  - FFmpeg-based (zero dependencies)

**See also:**
- `test_frame_sequence.py` - Automated test suite
- FFmpeg image2 muxer documentation
- Professional video workflows guide
