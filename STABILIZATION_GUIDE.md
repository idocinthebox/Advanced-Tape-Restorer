# Video Stabilization Guide

## Overview

The Advanced Tape Restorer now includes comprehensive video stabilization with multiple methods optimized for different types of camera motion. This guide explains when and how to use each stabilization mode.

---

## Stabilization Methods

### 🎯 **Auto (Detect Best Method)** - *DEFAULT* - ⭐ **NEW: Intelligent Detection**

**Best For:** General use when you're unsure what type of shake to fix

**How It Works:** *(IMPROVED)*
1. **Samples 20 frames** from your video
2. **Analyzes motion statistics:**
   - Average motion magnitude
   - Maximum motion (shake intensity)
   - Motion variance (consistency)
3. **Automatically selects the best method:**
   - **Very shaky** (max motion > 15, variance > 5) → **Aggressive Multi-Pass**
   - **Moderate shake with rotation** (avg motion > 8) → **Depan**
   - **Linear motion** (low variance, moderate motion) → **SubShaker**
   - **General shake** (default) → **MVTools**
4. **Applies the optimal stabilization** based on analysis

**Detection Examples:**
- 📹 Handheld VHS camcorder → Detects general shake → Uses MVTools
- 🏃 Running POV action cam → Detects high variance → Uses Aggressive
- 📏 Tripod pan with judder → Detects linear motion → Uses SubShaker
- 🔄 GoPro with horizon tilt → Detects moderate shake → Uses Depan

**Pros:**
- ✅ **Intelligent analysis** - No guessing required
- ✅ **Adapts to footage type** - Picks the best method automatically
- ✅ **Shows detection reasoning** - Logs why it chose each method
- ✅ **Graceful fallbacks** - Uses MVTools if specialized plugins unavailable
- ✅ **No additional plugins required** - Works with built-in MVTools

**Cons:**
- ⚠️ Adds ~2-3 seconds for initial motion analysis
- ⚠️ May not be perfect for mixed content (multiple scene types)

**When to Override Auto:**
- You know the specific motion type and want maximum control
- Video has multiple scenes with different stabilization needs
- You want to avoid the initial analysis time

**Recommended Settings:**
- ✅ Enable for: Any footage when you're unsure
- ✅ Perfect for: Batch processing mixed content
- ⚠️ Skip for: Intentional camera movement (smooth pans, zooms)

---

### 🎬 **General Shake (MVTools)**

**Best For:** Overall camera shake with mixed movement directions

**How It Works:**
- Motion vector analysis (MVAnalyse)
- Block-based motion estimation
- Compensates for:
  - Horizontal translation
  - Vertical translation
  - Zoom (scaling)
- Two-pass analysis (forward + backward vectors)

**Technical Details:**
- Block size: 16×16 pixels
- Overlap: 8 pixels (50% block overlap)
- Subpixel precision: 2 (quarter-pixel accuracy)
- Search mode: 3 (exhaustive search)

**Use Cases:**
- ✅ VHS camcorder footage (typical handheld shake)
- ✅ Home movies with general instability
- ✅ Tripod footage with slight vibration
- ✅ Drone footage with minor oscillation

**Limitations:**
- ❌ Does not correct rotation
- ❌ May struggle with very fast motion
- ❌ Cannot fix motion blur (use before denoising)

---

### 📏 **Horizontal/Vertical (SubShaker)**

**Best For:** Linear panning or tilting movement

**How It Works:**
- Specialized for linear motion along single axis
- Analyzes sub-pixel motion patterns
- Smooths out jitter while preserving intentional movement
- Mode 1: Corrects both horizontal AND vertical

**Use Cases:**
- ✅ Tripod pans with slight bumps
- ✅ Vertical tilt shots with judder
- ✅ Dolly shots with track vibration
- ✅ Cable-cam footage with linear sway

**When NOT to Use:**
- ❌ Rotational camera movement
- ❌ Complex multi-axis shake
- ❌ Static shots (use MVTools instead)

**Fallback:**
If SubShaker plugin is not installed, automatically falls back to MVTools.

---

### 🔄 **Roll Correction (Depan)**

**Best For:** Rotational camera movement and horizon tilt

**How It Works:**
- DePanEstimate: Analyzes rotation, zoom, and translation
- DePanStabilise: Applies smoothing transformations
- Corrects:
  - **Rotation** (roll around Z-axis)
  - Zoom (in/out)
  - Position (X/Y translation)

**Technical Details:**
- Trust parameter: 4.0 (moderate confidence in motion data)
- Max displacement: ±10 pixels (prevents over-correction)
- Cutoff frequency: 1.0 Hz (smooth out motion above 1 Hz)
- Damping: 0.9 (90% motion retention)
- Mirror: 15 pixels (fills edges after rotation)

**Use Cases:**
- ✅ Handheld footage with horizon tilt
- ✅ Action camera footage (GoPro, etc.)
- ✅ Skateboarding/biking videos
- ✅ Footage with noticeable roll/twist
- ✅ Gimbal footage with slight rotation

**Limitations:**
- ⚠️ Requires Depan plugin (not included by default)
- ⚠️ Crops image slightly to fill rotated edges
- ⚠️ May introduce slight warping on edges

**Installation:**
```bash
# Install Depan plugin (Windows)
pip install https://github.com/myrsloik/depan/releases
```

---

### 💪 **Aggressive (Multi-Pass)**

**Best For:** Extremely shaky footage requiring maximum correction

**How It Works:**
1. **Pass 1 - MVTools**: Removes translation and zoom shake
   - Block size: 16×16, overlap: 8
   - Exhaustive motion search
   - Compensates horizontal/vertical/zoom
   
2. **Pass 2 - Depan**: Corrects remaining rotation
   - Analyzes residual motion after Pass 1
   - Applies rotation and fine position correction
   - Tighter constraints (dxmax/dymax=5) for stability

**Technical Details:**
- Cutoff: 1.5 Hz (more aggressive smoothing than single-pass)
- Damping: 0.95 (95% motion retention)
- Falls back to MVTools-only if Depan unavailable

**Use Cases:**
- ✅ Very shaky handheld footage
- ✅ Running/walking POV shots
- ✅ Vehicle-mounted cameras on rough terrain
- ✅ Storm/wind-affected footage
- ✅ Rescue/emergency documentation

**Trade-offs:**
- ⚠️ **Slower processing** (2× stabilization passes)
- ⚠️ **More cropping** (to fill transformed edges)
- ⚠️ **May reduce perceived "energy"** in action shots
- ⚠️ **Can introduce artifacts** on fast motion

**When NOT to Use:**
- ❌ Footage with rapid intentional movement (sports)
- ❌ Time-sensitive processing
- ❌ Content where some shake is desirable (documentary feel)

---

## Comparison Table

| Method | Translation | Rotation | Zoom | Speed | Cropping | Plugin Required |
|--------|------------|----------|------|-------|----------|-----------------|
| **Auto (MVTools)** | ✅ Excellent | ❌ No | ✅ Good | ⚡ Fast | Minimal | None (built-in) |
| **General Shake** | ✅ Excellent | ❌ No | ✅ Good | ⚡ Fast | Minimal | None (built-in) |
| **Horizontal/Vertical** | ✅ Excellent | ❌ No | ❌ No | ⚡⚡ Very Fast | None | SubShaker (optional) |
| **Roll Correction** | ✅ Good | ✅ Excellent | ✅ Good | ⚡ Fast | Moderate | Depan (required) |
| **Aggressive** | ✅ Excellent | ✅ Excellent | ✅ Good | 🐌 Slow | Heavy | Depan (optional) |

---

## Best Practices

### ✅ DO

1. **Test on short clips first** - Stabilization can change the feel of footage significantly
2. **Use before AI upscaling** - Stabilize at original resolution for best results
3. **Combine with deinterlacing** - QTGMC → Stabilization → Upscaling (proper order)
4. **Check edges** - Stabilization crops slightly, ensure important content isn't lost
5. **Use Auto mode first** - Only switch to specialized modes if needed

### ❌ DON'T

1. **Stabilize already-stable footage** - Can introduce warping artifacts
2. **Use on intentional camera movement** - Pans/zooms will be ruined
3. **Expect miracles** - Cannot fix severe motion blur
4. **Over-stabilize** - Some natural movement is good
5. **Skip testing** - Always preview before full processing

---

## Common Issues & Solutions

### Issue: "Stabilization makes footage look 'floaty'"

**Cause:** Over-stabilization removes natural camera movement

**Solutions:**
- Try a less aggressive mode (Auto instead of Aggressive)
- Consider disabling stabilization for some shots
- Preserve some motion for a natural feel

---

### Issue: "Edges are cropped too much"

**Cause:** Stabilization transforms require cropping to fill frame

**Solutions:**
- Use less aggressive mode
- Reduce Depan mirror parameter (advanced)
- Accept cropping or shoot with extra border space

---

### Issue: "Rotation not corrected"

**Cause:** Using MVTools-only mode (doesn't handle rotation)

**Solutions:**
- Switch to "Roll Correction (Depan)"
- Install Depan plugin
- Use "Aggressive" mode for multi-axis correction

---

### Issue: "Stabilization failed - plugin not found"

**Cause:** Missing optional plugins (Depan or SubShaker)

**Solutions:**
```bash
# Install Depan (Windows)
pip install https://github.com/myrsloik/depan/releases

# Install SubShaker (if available)
# Check VapourSynth plugin repository
```

**Fallback:** Auto/General modes always work (built-in MVTools)

---

### Issue: "Processing is very slow"

**Cause:** Motion vector analysis is computationally intensive

**Solutions:**
- Use "Auto" or "General" mode (single-pass)
- Avoid "Aggressive" mode unless necessary
- Stabilize after cropping/before upscaling
- Process overnight for large projects

---

## Technical Notes

### MVTools Motion Estimation

MVTools analyzes motion by:
1. Dividing frame into blocks (16×16 pixels)
2. Searching for matching blocks in adjacent frames
3. Computing motion vectors (dx, dy per block)
4. Interpolating sub-pixel motion (pel=2 = ¼ pixel accuracy)
5. Compensating frame based on vectors

**Parameters Explained:**
- `pel=2`: Quarter-pixel precision (higher = slower but smoother)
- `sharp=2`: Sharpness of resampling (0-2, higher = sharper but artifacts)
- `blksize=16`: Block size (8/16/32, smaller = more detail but slower)
- `overlap=8`: Block overlap (prevents blocky artifacts)
- `search=3`: Exhaustive search (0-7, higher = better but slower)

---

### Depan Stabilization

Depan uses global motion estimation:
1. Estimates affine transform between frames (rotation + scale + translation)
2. Smooths transform parameters over time
3. Applies inverse transform to stabilize

**Parameters Explained:**
- `trust=4.0`: Confidence in motion data (1-10, higher = trust more)
- `dxmax/dymax=10`: Maximum X/Y displacement (pixels, prevents errors)
- `cutoff=1.0`: Low-pass filter frequency (Hz, smooths jitter above)
- `damping=0.9`: Motion retention (0-1, higher = smoother)
- `initzoom=1.0`: Starting zoom level (>1 = pre-crop)
- `mirror=15`: Edge fill width (pixels, fills black borders)

---

### Processing Order

**Recommended Pipeline:**

1. **Source** - Load video
2. **Deinterlace** - QTGMC (if interlaced)
3. **Crop** - Remove letterbox/pillarbox
4. **Denoise** - BM3D/temporal (if needed)
5. **🎬 STABILIZE** ← Insert here
6. **Debanding** - f3kdb (if needed)
7. **Color Correction** - Levels/saturation
8. **AI Upscaling** - RealESRGAN/ZNEDI3
9. **Sharpen** - Final touch-up
10. **Encode** - FFmpeg output

**Why This Order:**
- Stabilize AFTER deinterlacing (avoid field artifacts)
- Stabilize BEFORE upscaling (less computation)
- Stabilize AFTER denoising (cleaner motion vectors)

---

## Examples

### Example 1: Home Video (VHS Camcorder)

**Symptoms:** General handheld shake, slight horizontal wobble

**Recommended Settings:**
- Mode: **Auto (Detect Best Method)**
- Why: General shake, no rotation, MVTools handles it well

**Alternative:** General Shake (MVTools) - same result, explicit choice

---

### Example 2: Action Camera (GoPro on Chest Mount)

**Symptoms:** Rotation from body movement, horizon tilt

**Recommended Settings:**
- Mode: **Roll Correction (Depan)**
- Why: Rotational correction needed for horizon stabilization

**Alternative:** Aggressive (Multi-Pass) - if very shaky

---

### Example 3: Tripod Pan with Jitter

**Symptoms:** Smooth pan but with judder/bumps

**Recommended Settings:**
- Mode: **Horizontal/Vertical (SubShaker)**
- Why: Linear motion, SubShaker preserves pan while smoothing jitter

**Alternative:** General Shake - works but may over-stabilize pan

---

### Example 4: Earthquake Documentation

**Symptoms:** Extreme multi-axis shake, rotation, constant motion

**Recommended Settings:**
- Mode: **Aggressive (Multi-Pass)**
- Why: Needs maximum correction on all axes

**Trade-off:** Heavy cropping, slower processing

---

## Performance Impact

| Mode | Processing Speed | VRAM Usage | CPU Usage |
|------|-----------------|------------|-----------|
| Auto/General | ~80% normal speed | Low | High |
| Horizontal/Vertical | ~90% normal speed | None | Medium |
| Roll Correction | ~75% normal speed | Low | High |
| Aggressive | ~50% normal speed | Low | Very High |

**Note:** Stabilization is CPU-intensive (motion vector calculation). GPU is not typically used.

---

## Frequently Asked Questions

**Q: Can I stabilize after AI upscaling?**

A: Not recommended. Stabilize at original resolution for better motion vector accuracy and faster processing.

---

**Q: Does stabilization remove motion blur?**

A: No. Motion blur is baked into frames. Stabilization only corrects frame-to-frame position/rotation. Use denoising for blur reduction.

---

**Q: Will stabilization slow down my encoding?**

A: Yes. Motion analysis adds 20-50% processing time depending on mode. Aggressive mode can double processing time.

---

**Q: Can I use stabilization with ProPainter?**

A: Yes! Use this order: ProPainter → Stabilization → Upscaling. ProPainter removes artifacts, then stabilize clean frames.

---

**Q: Why are my edges cropped/black?**

A: Stabilization repositions frames, creating empty borders. These are either cropped or filled (mirrored). This is normal.

---

**Q: Should I always use Aggressive mode?**

A: No! Use only for very shaky footage. Auto/General is sufficient for most home videos and faster.

---

## Conclusion

Video stabilization is a powerful tool for improving shaky footage, but it's not always necessary. Start with **Auto mode** for general use, and switch to specialized modes only when specific motion types need correction. Always preview a short section before processing entire videos.

For best results, combine stabilization with proper deinterlacing, denoising, and AI upscaling in the correct processing order.

**Happy Restoring! 🎬**
