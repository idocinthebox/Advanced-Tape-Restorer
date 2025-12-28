# Theatre Mode v4.0 - User Guide

## What is Theatre Mode?

Theatre Mode is a hardware-accurate analog video processing pipeline based on ATI Theatre chipset algorithms. It corrects common analog tape artifacts **before** deinterlacing, resulting in significantly better quality than standard processing.

**Key Features:**
- Chroma phase correction (fixes color misalignment)
- Field-aware deinterlacing (respects interlaced structure)
- Black/white level adjustment
- Saturation boost for faded tapes
- Auto-profiling (analyze tape to detect optimal settings)

---

## When to Use Theatre Mode

✅ **USE Theatre Mode for:**
- VHS tapes (NTSC/PAL/SECAM)
- Video8 / Hi8 analog tapes
- S-VHS tapes
- Betamax tapes
- LaserDisc captures (analog output)
- U-Matic tapes
- Any analog composite/S-Video capture

❌ **DON'T use Theatre Mode for:**
- DV / MiniDV / HDV (digital formats, no chroma shift)
- Digital broadcast recordings (already corrected)
- Modern digital cameras
- Computer-generated content

---

## Theatre Mode vs Standard QTGMC

### Theatre Mode Processing Pipeline:
```
Source → Chroma Correction → Deinterlace → Denoise → Level Adjust → Output
         ↑ Fixes alignment    ↑ Clean fields
```

### Standard QTGMC Pipeline:
```
Source → Deinterlace → Denoise → Output
         ↑ Chroma misalignment "baked in"
```

**Why Theatre Mode is Better for Analog:**
Analog tape capture often has **0.2-0.5 pixel chroma phase shift** (U/V channels misaligned from Y luma). Standard QTGMC deinterlaces this misalignment into the progressive output permanently. Theatre Mode fixes the alignment **first**, then deinterlaces clean, aligned fields = noticeably sharper colors and edges.

---

## Chroma Correction Presets

### Recommended Settings by Tape Format

| Format | Chroma Shift X | Chroma Shift Y | Notes |
|--------|----------------|----------------|-------|
| **Video8** | **0.25px** | 0.0px | Standard 8mm, similar to VHS |
| **Hi8** | 0.2px | 0.0px | Better than Video8, less shift |
| **VHS (NTSC)** | 0.25px | 0.0px | Typical NTSC analog shift |
| **VHS (PAL)** | 0.3px | 0.0px | PAL slightly worse |
| **S-VHS** | 0.15px | 0.0px | Better chroma separation |
| **Betamax** | 0.3px | 0.0px | Similar to VHS |
| **LaserDisc** | 0.0px | 0.0px | Digital source, minimal shift |
| **DV** | 0.0px | 0.0px | Digital format, no shift |

### Video8 vs Hi8 - Should They Be Separate?

**YES - Separate presets recommended:**

**Video8 (1985-1999):**
- 240 lines horizontal resolution
- Standard VHS-level chroma resolution
- More susceptible to chroma phase errors
- **Preset: 0.25px** (similar to VHS)
- Typical for: Camcorders, consumer recordings

**Hi8 (1989-2007):**
- 400+ lines horizontal resolution
- Improved chroma recording
- Better head alignment
- **Preset: 0.2px** (less shift than Video8)
- Typical for: Semi-pro camcorders, better consumer gear

**Recommendation:** Add "Video8" preset with 0.25px shift, keep "Hi8" at 0.2px.

---

## Deinterlace Variants

Theatre Mode offers three deinterlace modes:

### 1. Standard Progressive (Default)
- **Output:** 30fps (NTSC) or 25fps (PAL) progressive
- **Best for:** Modern displays, streaming, YouTube
- **File size:** Normal
- **Use case:** 99% of restoration projects

### 2. Bob (Double-Rate)
- **Output:** 60fps (NTSC) or 50fps (PAL) progressive
- **Best for:** Preserving all motion, sports, fast action
- **File size:** 2x larger (double frame count)
- **Use case:** Archival, smooth motion preference

### 3. Keep Interlaced
- **Output:** 30fps/25fps interlaced (maintains fields)
- **Best for:** Interlaced delivery, broadcast
- **File size:** Normal
- **Use case:** Re-encoding for interlaced display

---

## Compatibility with Other Features

### ⚠️ CONFLICTS (Do Not Use Together)

**When Theatre Mode is ENABLED, disable these:**

1. **❌ QTGMC Deinterlacing Checkbox**
   - Theatre Mode has built-in deinterlacing
   - Using both = double deinterlacing = artifacts
   - **Action:** Uncheck "Deinterlace (QTGMC)"

2. **❌ Standalone Color Correction** (if it adjusts levels)
   - Theatre Mode's Level Adjustment handles this
   - Using both = over-correction
   - **Action:** Disable color sliders if Theatre Mode level adjustment is enabled

### ✅ SAFE TO USE (Compatible Features)

**These work great WITH Theatre Mode:**

1. **✅ Chroma Denoise**
   - Reduces color noise independently
   - Applied after chroma correction

2. **✅ Temporal Denoise**
   - Time-based noise reduction
   - Works on corrected video

3. **✅ Spatial Denoise**
   - Smooths noise within frames
   - Compatible with all Theatre Mode settings

4. **✅ Sharpening**
   - Applied after all corrections
   - Enhances cleaned-up video

5. **✅ AI Upscaling** (RealESRGAN, SwinIR, BasicVSR++)
   - Upscales corrected progressive output
   - Theatre Mode provides cleaner input

6. **✅ AI Interpolation** (RIFE)
   - Frame rate boosting (30→60fps)
   - Works after Theatre Mode processing

7. **✅ Crop/Resize**
   - Geometric operations
   - Independent of Theatre Mode

---

## Recommended Workflows

### Workflow 1: Basic VHS Restoration
```
1. ✅ Enable Theatre Mode
2. ✅ Select "VHS (NTSC)" preset (0.25px)
3. ✅ Deinterlace variant: Standard Progressive
4. ❌ Disable QTGMC checkbox
5. ✅ Add Chroma Denoise: 2-3
6. ✅ Add Temporal Denoise: Low
7. ✅ Encode to H.264
```

### Workflow 2: Hi8 with AI Upscaling
```
1. ✅ Enable Theatre Mode
2. ✅ Select "Hi8 (0.2px)" preset
3. ✅ Deinterlace variant: Standard Progressive
4. ❌ Disable QTGMC checkbox
5. ✅ Enable RealESRGAN 4x upscaling
6. ✅ Add Temporal Denoise: Low
7. ✅ Encode to H.265 (HEVC)
```

### Workflow 3: Auto-Profiling for Unknown Tape
```
1. ✅ Enable Theatre Mode
2. ✅ Click "Analyze Tape (Auto-Profile)"
3. ✅ Wait for analysis (uses vspipe)
4. ✅ Review detected settings
5. ✅ Adjust manually if needed
6. ❌ Disable QTGMC checkbox
7. ✅ Add denoise/upscaling as needed
8. ✅ Encode
```

### Workflow 4: DV Digital Tape (Theatre Mode OFF)
```
1. ❌ Disable Theatre Mode (DV is digital)
2. ✅ Enable QTGMC checkbox
3. ✅ Select DV preset (if available)
4. ✅ Add denoise if needed
5. ✅ Encode
```

---

## Auto-Profiling Guide

Theatre Mode includes an auto-profiling tool that analyzes your tape and recommends optimal settings.

### How to Use Auto-Profiling

1. **Load your video file**
2. **Enable Theatre Mode** checkbox
3. **Click "Analyze Tape (Auto-Profile)"** button
4. **Wait 10-60 seconds** (depends on video length)
5. **Review detected settings:**
   - Field order (TFF/BFF)
   - Chroma shift X/Y
   - Black/white levels
   - Saturation boost

6. **Adjust manually if needed**
7. **Process video**

### What Auto-Profiling Detects

- ✅ Field order (TFF/BFF/Progressive)
- ✅ Black level (0.0-1.0)
- ✅ White level (0.0-1.0)
- ✅ Average saturation
- ✅ Recommended saturation boost
- ⚠️ Chroma shift (uses default preset values)

**Note:** Chroma shift detection is difficult to automate, so auto-profiling uses sensible defaults (0.25px). You can manually adjust based on your tape format.

### When Auto-Profiling is Useful

- Unknown tape source
- Mixed tape formats (compilation)
- Badly faded/damaged tapes
- Unusual black/white levels
- Quick first pass before fine-tuning

---

## Level Adjustment

Theatre Mode includes black/white point correction and saturation boost.

### When to Use Level Adjustment

✅ **Enable Level Adjustment for:**
- Faded tapes (low white point)
- Crushed blacks (elevated black point)
- Washed-out colors (low saturation)
- Tapes stored poorly (age-related fading)

❌ **Skip Level Adjustment for:**
- Well-preserved tapes
- Recent captures (good levels)
- When you'll color-grade later

### Level Settings Explained

**Black Point (0.0-0.5):**
- Darker values = more shadow detail
- Typical range: 0.05-0.15
- Auto-detected by profiler

**White Point (0.5-1.0):**
- Brighter values = more highlight detail
- Typical range: 0.85-0.95
- Auto-detected by profiler

**Saturation Boost (0.5-2.0):**
- 1.0 = no change
- >1.0 = more vibrant colors
- <1.0 = desaturate
- Typical boost: 1.1-1.3 for faded tapes

---

## Performance Considerations

### Processing Speed

Theatre Mode adds minimal overhead:
- Chroma correction: ~2-5% slower
- Level adjustment: ~1-2% slower
- **Total impact: ~5-10% slower than QTGMC alone**

### When Theatre Mode is Slower

- High-resolution sources (>1080p)
- Combined with heavy AI upscaling
- Combined with multiple denoise passes

### Speed Optimization Tips

1. Use "Standard Progressive" instead of "Bob" (half the frames)
2. Disable level adjustment if not needed
3. Reduce denoise strength if combined with AI
4. Use hardware encoding (NVENC/QuickSync)

---

## Troubleshooting

### Colors Look Worse After Theatre Mode

**Problem:** Chroma shift value is wrong for your tape  
**Solution:**
1. Try different presets (VHS → S-VHS → Hi8)
2. Adjust X shift manually: -0.5px to +0.5px
3. Use "Analyze Tape" to check levels
4. Compare with/without Theatre Mode

### Still Seeing Interlacing Artifacts

**Problem:** QTGMC checkbox is still enabled  
**Solution:**
1. Uncheck "Deinterlace (QTGMC)" checkbox
2. Let Theatre Mode handle deinterlacing
3. Check deinterlace variant setting

### Output is Too Dark/Bright

**Problem:** Level adjustment needs tuning  
**Solution:**
1. Enable "Apply Level Adjustment"
2. Run "Analyze Tape" for auto-detected values
3. Manually adjust black/white points
4. Try 0.05 black point, 0.9 white point as starting values

### Processing Takes Forever

**Problem:** Multiple filters stacked  
**Solution:**
1. Reduce denoise strength
2. Use faster AI upscaling (ZNEDI3 instead of RealESRGAN)
3. Process shorter clips for testing
4. Check CPU/GPU usage

---

## Advanced: Custom Chroma Values

If presets don't match your tape, use custom values:

### Finding the Right Chroma Shift

1. **Process a 10-second test clip** with Theatre Mode
2. **Try different X shift values:**
   - Start with preset (e.g., 0.25px for VHS)
   - Increase by 0.05px if colors bleed right
   - Decrease by 0.05px if colors bleed left
3. **Look for these indicators:**
   - Sharp color edges (good)
   - Color fringing on edges (wrong shift)
   - Colors "sliding" horizontally (wrong shift)
4. **Save optimal value** for your capture setup

### Y Shift (Vertical)

Most analog tapes don't need Y shift (vertical chroma misalignment is rare). Leave at 0.0px unless you see:
- Color bars misaligned vertically
- Horizontal lines with color offset
- Obvious vertical chroma smear

---

## Preset Reference Table

### Complete Preset List (Recommended)

| Preset Name | X Shift | Y Shift | Use Case |
|-------------|---------|---------|----------|
| Custom | Manual | Manual | User-defined |
| LaserDisc | 0.0px | 0.0px | Analog LD output |
| VHS (NTSC) | 0.25px | 0.0px | Standard VHS NTSC |
| VHS (PAL) | 0.3px | 0.0px | Standard VHS PAL |
| S-VHS | 0.15px | 0.0px | Super VHS |
| Video8 | 0.25px | 0.0px | Standard 8mm analog |
| Hi8 | 0.2px | 0.0px | High-band 8mm |
| Betamax | 0.3px | 0.0px | Beta format |
| DV | 0.0px | 0.0px | Digital Video (no shift) |

### Proposed Additional Presets

| Format | X Shift | Notes |
|--------|---------|-------|
| VHS (SECAM) | 0.35px | SECAM worse than PAL |
| U-Matic | 0.2px | Professional format |
| Video 2000 | 0.25px | Rare European format |
| Betacam SP | 0.1px | Professional Betamax |
| MII | 0.1px | Professional Panasonic |

---

## Summary: Theatre Mode Best Practices

### ✅ DO:
1. Use Theatre Mode for ALL analog tape captures
2. Choose the correct preset for your tape format
3. Use "Analyze Tape" for unknown sources
4. Disable QTGMC checkbox when Theatre Mode is enabled
5. Combine with denoise and AI upscaling
6. Test 10-second clips before full processing

### ❌ DON'T:
1. Use Theatre Mode with DV/HDV/MiniDV (digital formats)
2. Enable both Theatre Mode and QTGMC checkbox
3. Over-boost saturation (>1.5x typically looks artificial)
4. Skip level adjustment on badly faded tapes
5. Assume all VHS tapes need the same shift (capture hardware varies)

---

## Version History

**v4.0.0 (December 2025):**
- Initial Theatre Mode release
- 8 hardware presets (LaserDisc → DV)
- Auto-profiling via vspipe
- Level adjustment
- Three deinterlace variants
- VapourSynth integration

**Recommended Update: Add Video8 Preset**
- Separate Video8 (0.25px) from Hi8 (0.2px)
- Better matches standard 8mm tape characteristics

---

## Support & Resources

**Documentation:**
- [copilot-instructions.md](.github/copilot-instructions.md) - AI agent context
- [THEATRE_MODE_GUI_IMPLEMENTATION_COMPLETE.md](THEATRE_MODE_GUI_IMPLEMENTATION_COMPLETE.md) - Implementation details
- [test_theatre_mode_script_generation.py](test_theatre_mode_script_generation.py) - Test suite

**Getting Help:**
- Check console log for detailed processing information
- Enable "Analyze Tape" to verify settings
- Test with short clips before full processing
- Compare with/without Theatre Mode to validate improvement

**Known Limitations:**
- Auto-profiling requires vspipe (VapourSynth) installed
- Chroma shift detection is not fully automated (uses presets)
- Processing slightly slower than QTGMC alone (~5-10%)

---

**Advanced Tape Restorer v4.0 with Theatre Mode**  
Professional analog tape restoration with hardware-accurate processing.
