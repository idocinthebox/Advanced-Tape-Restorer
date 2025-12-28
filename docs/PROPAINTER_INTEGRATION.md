# ProPainter Integration Guide

## Overview

ProPainter is an external AI tool for video inpainting that can:
- Remove scratches and tape damage
- Fill missing/corrupted areas
- Remove unwanted objects
- Restore heavily degraded footage

**Important:** ProPainter is **non-commercial use only** and requires separate installation.

---

## Installation Steps

### 1. Install ProPainter

```bash
# Clone repository
git clone https://github.com/sczhou/ProPainter.git
cd ProPainter

# Create conda environment
conda create -n propainter python=3.8 -y
conda activate propainter

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Model Weights

Models will auto-download on first use, or manually download from:
https://github.com/sczhou/ProPainter/releases/tag/v0.1.0

Place these files in `ProPainter/weights/`:
- `ProPainter.pth`
- `recurrent_flow_completion.pth`
- `raft-things.pth`

### 3. Verify Installation

```bash
# Test with sample video
python inference_propainter.py --video inputs/object_removal/bmx-trees --mask inputs/object_removal/bmx-trees_mask
```

### 4. Configure Path in Application

In Advanced Tape Restorer:
1. Go to **Tools** → **Settings**
2. Set "ProPainter Installation Path" to your ProPainter directory
   - Example: `C:\Users\YourName\ProPainter`
3. Click "Test ProPainter" to verify connection

---

## Integration Architecture

### How It Works

```
1. User enables ProPainter in Advanced tab
2. Application exports VapourSynth output to temp file
3. ProPainter processes temp file → creates cleaned version
4. Application re-imports cleaned video
5. Continues with remaining filters (if any)
6. Final encoding
```

### Processing Flow

```
VHS Tape
  ↓
Capture (lossless)
  ↓
VapourSynth Pre-Processing:
  - QTGMC deinterlace
  - BM3D denoise
  ↓
Export to temp file (.mp4)
  ↓
ProPainter Processing:
  - Analyze 10+ surrounding frames
  - Detect artifacts/damage
  - Temporal inpainting
  ↓
Re-import cleaned video
  ↓
VapourSynth Post-Processing:
  - RIFE interpolation (optional)
  - RealESRGAN upscaling (optional)
  ↓
Final Encode
```

---

## Usage in Application

### Option 1: Automatic Mode (Recommended)

**Location:** Advanced Tab → "AI Video Inpainting (ProPainter)"

**Steps:**
1. ✅ Check "AI Video Inpainting (ProPainter)"
2. Select Mode: **"Remove Artifacts"** (auto-detection)
3. Configure other restoration filters as normal
4. Click "Start Processing"

**What Happens:**
- Application runs initial denoising/deinterlacing
- Exports intermediate file
- ProPainter automatically detects and removes:
  - Scratches
  - Dust spots
  - Tape tracking errors
  - Mold damage
  - Dropout artifacts
- Imports cleaned video
- Continues with remaining processing

### Option 2: Object Removal Mode

**Use Case:** Remove specific objects (date stamps, logos, unwanted elements)

**Steps:**
1. ✅ Check "AI Video Inpainting (ProPainter)"
2. Select Mode: **"Object Removal"**
3. Click "Create Mask" button
4. Use mask editor to mark objects to remove
5. Start processing

**Manual Mask Creation:**
- Use external tool (Photoshop, GIMP) to create mask
- Black = keep, White = remove
- Save as PNG sequence or single mask
- Specify mask path in settings

### Option 3: Restore Damaged Areas

**Use Case:** Heavily degraded tapes with large damaged regions

**Steps:**
1. ✅ Check "AI Video Inpainting (ProPainter)"
2. Select Mode: **"Restore Damaged Areas"**
3. Optionally provide mask for specific regions
4. Start processing (expect long processing time)

---

## Performance Considerations

### GPU Memory Requirements

| Resolution | FP32 (Full) | FP16 (Half) |
|------------|-------------|-------------|
| 320x240    | 3 GB        | 2 GB        |
| 640x480    | 10 GB       | 6 GB        |
| 720x480    | 11 GB       | 7 GB        |
| 1280x720   | 28 GB       | 19 GB       |

**Recommendations:**
- Always enable FP16 (half precision) for memory savings
- Process SD content (720x480) on 8GB+ GPUs
- HD content requires 16GB+ VRAM
- Consider downscaling before ProPainter, upscale after

### Processing Speed

**Very slow** - this is normal for AI inpainting!

**Example Times (RTX 3060, 720x480, 1-minute video):**
- Auto-detect mode: 15-30 minutes
- Object removal: 20-40 minutes
- Heavy restoration: 30-60 minutes

**Full 2-hour VHS tape:**
- Expect 30-120 hours of processing!
- Recommended: Process in segments

### Memory-Efficient Settings

ProPainter settings automatically applied by integration:
- `--neighbor_length 10` (reduce local neighbors)
- `--ref_stride 10` (reduce global references)
- `--subvideo_length 80` (process in 80-frame chunks)
- `--fp16` (half precision)

---

## Workflow Recommendations

### Workflow 1: Standard Cleanup (Most Common)

**Goal:** Remove tape scratches and minor damage

**Settings:**
```
Restoration Tab:
  - QTGMC deinterlacing: Enabled
  - BM3D denoise: Light/Medium

Advanced Tab:
  - ProPainter: ✅ Enabled
  - Mode: Remove Artifacts
  - RIFE interpolation: Optional (2x)

Output Tab:
  - RealESRGAN: Optional
  - Codec: H.265, CRF 20
```

**Processing Time:** 2-4x real-time (1 hour tape = 2-4 hours)

### Workflow 2: Heavy Damage Restoration

**Goal:** Restore severely degraded tapes

**Settings:**
```
Restoration Tab:
  - QTGMC deinterlacing: Enabled
  - BM3D denoise: Strong

Advanced Tab:
  - ProPainter: ✅ Enabled
  - Mode: Restore Damaged Areas
  - Temporal denoise: Medium
  - Debanding: Enabled

Output Tab:
  - RealESRGAN: ✅ Enabled (720p → 1080p)
  - Codec: ProRes 422 HQ (archival)
```

**Processing Time:** 10-20x real-time (1 hour tape = 10-20 hours)

### Workflow 3: Object Removal (Date Stamps)

**Goal:** Remove date/time stamps from camcorder footage

**Settings:**
```
Advanced Tab:
  - ProPainter: ✅ Enabled
  - Mode: Object Removal
  - Mask: Create mask covering date stamp area
```

**Processing Time:** 3-5x real-time

### Workflow 4: Segment Processing (Large Projects)

**For 2+ hour tapes:**

1. **Split video into segments:**
   ```bash
   ffmpeg -i input.avi -c copy -segment_time 600 -f segment segment_%03d.avi
   ```
   (Creates 10-minute segments)

2. **Process each segment:**
   - Use batch queue to add all segments
   - Enable ProPainter
   - Process overnight

3. **Concatenate results:**
   ```bash
   ffmpeg -f concat -i filelist.txt -c copy final_output.mp4
   ```

---

## Troubleshooting

### "ProPainter not found"

**Solution:**
1. Verify ProPainter installed: `conda activate propainter && python --version`
2. Check path in Settings → Tools → ProPainter Path
3. Path should point to ProPainter folder containing `inference_propainter.py`

### "Out of Memory" Error

**Solutions:**
1. Enable FP16 (always recommended)
2. Reduce video resolution before processing
3. Use memory-efficient mode (automatically enabled)
4. Process shorter segments
5. Close other GPU applications

### ProPainter Processing Hangs

**Common Causes:**
- GPU driver crash (update drivers)
- Out of VRAM (reduce resolution)
- Scene with very complex motion

**Solutions:**
- Check GPU temperature (thermal throttling)
- Enable `--fp16` flag
- Split video into smaller segments
- Skip problematic scenes

### Results Not Good

**Improve Quality:**
1. **Pre-processing matters:**
   - Always denoise first (BM3D)
   - Deinterlace properly
   - Remove obvious artifacts before ProPainter

2. **Mask quality:**
   - For object removal: Create precise masks
   - Use mask feathering for smooth edges
   - Test on short clips first

3. **Settings adjustment:**
   - Increase `neighbor_length` for better quality (uses more memory)
   - Decrease `ref_stride` for more reference frames

---

## Technical Details

### How ProPainter Uses Surrounding Frames

**Temporal Window:**
```
Frames: [..., t-5, t-4, t-3, t-2, t-1, t, t+1, t+2, t+3, t+4, t+5, ...]
                                        ↑
                                  Current frame
```

**Processing Steps:**
1. **Flow Completion Network:**
   - Calculates optical flow between frames
   - Propagates content from clean areas to damaged areas
   - Bidirectional propagation (past + future)

2. **ProPainter Transformer:**
   - Analyzes texture patterns across temporal window
   - Reconstructs missing content using multi-frame context
   - Ensures temporal consistency

3. **Output:**
   - Seamlessly filled damaged areas
   - Temporally consistent across frames
   - Natural texture reconstruction

### Command Line Integration

Application calls ProPainter internally:

```python
python {propainter_path}/inference_propainter.py \
    --video {input_video} \
    --output {output_video} \
    --mask {mask_path} \
    --width 720 \
    --height 480 \
    --fp16 \
    --neighbor_length 10 \
    --ref_stride 10 \
    --subvideo_length 80
```

### File I/O During Processing

```
Temp Directory Structure:
propainter_temp/
├── input_preprocessed.mp4     (VapourSynth output)
├── auto_mask/                  (Auto-generated masks, if used)
│   ├── 00000.png
│   ├── 00001.png
│   └── ...
└── output_cleaned.mp4          (ProPainter result)
```

Files automatically cleaned after processing completes.

---

## API Integration (For Developers)

### Using ProPainterEngine Class

```python
from core.propainter_engine import ProPainterEngine

# Initialize
engine = ProPainterEngine(propainter_path="C:/ProPainter")

# Check availability
if engine.is_available():
    print("ProPainter ready!")

# Process video
success = engine.process_video(
    input_video="input.mp4",
    output_video="output.mp4",
    mode="auto_detect",
    width=720,
    height=480,
    use_fp16=True,
    log_callback=print
)

# Check GPU requirements
requirements = engine.get_gpu_requirements(1280, 720, use_fp16=True)
print(f"Estimated VRAM: {requirements['estimated_vram_gb']} GB")
```

### Custom Mask Creation

```python
# Auto-generate mask from video
engine.create_auto_mask(
    video_path="input.mp4",
    output_mask_dir="masks/",
    threshold=0.5,
    log_callback=print
)
```

---

## License & Attribution

**ProPainter License:** Non-Commercial Use Only (NTU S-Lab License 1.0)

**Citation:**
```bibtex
@inproceedings{zhou2023propainter,
  title={{ProPainter}: Improving Propagation and Transformer for Video Inpainting},
  author={Zhou, Shangchen and Li, Chongyi and Chan, Kelvin C.K and Loy, Chen Change},
  booktitle={ICCV},
  year={2023}
}
```

**Commercial Use:** Contact Dr. Shangchen Zhou (shangchenzhou@gmail.com)

---

## Summary

✅ **ProPainter provides:**
- AI-powered artifact/damage removal
- Temporal context from 10+ surrounding frames
- Professional restoration quality
- Object removal capabilities

⚠️ **Requirements:**
- Separate installation (not bundled)
- Non-commercial use only
- GPU with 8GB+ VRAM
- Very slow processing (plan accordingly)

🔧 **Integration:**
- Automatic detection mode for ease of use
- External CLI tool called during processing
- Seamless workflow with other filters

**Best Use Cases:**
- VHS tapes with scratches/mold
- Remove date stamps from camcorder footage
- Restore heavily degraded archival material
- Fill tape dropout/tracking errors

For installation help, see: https://github.com/sczhou/ProPainter
