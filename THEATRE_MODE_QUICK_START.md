# Advanced Tape Restorer v4.0 - Theatre Mode Quick Start

## What is Theatre Mode?

**Theatre Mode** is a professional analog processing mode that replicates the signal processing used in broadcast-quality video capture hardware. It's specifically designed for **VHS, S-VHS, Hi8, Betamax, and LaserDisc** restoration.

**In simple terms:** Theatre Mode fixes color problems that are unique to analog tape, like color fringing and misaligned colors that happen when composite video is captured.

## Should I Use Theatre Mode?

### ✅ YES, use Theatre Mode if your video came from:
- VHS tapes
- S-VHS tapes  
- Hi8 / Video8 tapes
- Betamax tapes
- LaserDisc
- Any analog tape captured with composite (RCA/yellow cable) or S-Video connections

### ❌ NO, use Normal Mode if your video came from:
- Digital cameras (DV, HDV, AVCHD)
- Modern cameras (DSLR, mirrorless, smartphones)
- Downloaded video files
- DVD/Blu-ray rips

## 5-Minute Setup Guide

### Step 1: Enable Theatre Mode

1. Open Advanced Tape Restorer v4.0
2. Go to the **Restoration** tab
3. Find the section at the top: **"Processing Mode"**
4. Check the box: **☑ Theatre Mode (Hardware-Accurate Analog Processing)**

That's it! Theatre Mode is now active.

### Step 2: Choose Your Tape Format (Chroma Preset)

Right below the Theatre Mode checkbox, you'll see **"Chroma Correction Preset"** dropdown:

- **LaserDisc** - Highest quality analog format (default)
- **VHS Composite** - Standard VHS captured with RCA/composite connection
- **S-VHS** - Super VHS (higher quality, separate Y/C signal)
- **Hi8** - High-band 8mm tape format
- **Betamax** - Sony Betamax format
- **Custom** - Specify your own values (advanced users)

**Most common:** Choose **"VHS Composite"** for regular VHS tapes.

### Step 3: Run Auto-Profiling (Recommended)

Before processing your tape, let Theatre Mode analyze it:

1. Load your video file (Browse → select file)
2. Click the **"Analyze Tape"** button (appears when Theatre Mode is on)
3. Wait 30-60 seconds while it analyzes your tape
4. You'll see a popup with detected settings:
   - Field order (usually "Top Field First" for VHS)
   - Black/white levels
   - Color saturation
   - Recommendations (if any issues detected)

**What this does:** Automatically detects the best settings for YOUR specific tape. Every tape is slightly different, and auto-profiling finds the optimal correction values.

### Step 4: Process Your Video

1. Choose output file location (Browse button under "Output File")
2. Select codec (recommend: **libx264** for compatibility, **libx265** for smaller files)
3. Click **"Start Restoration"**

Theatre Mode will automatically apply:
- ✅ Chroma phase correction (fixes color alignment)
- ✅ Optimal deinterlacing (converts interlaced to progressive)
- ✅ Black/white level adjustment (improves contrast)
- ✅ Saturation boost (if tape is faded/dull)

## What Theatre Mode Fixes

### Problem: Color Fringing
**What you see:** Colors appear to "bleed" or shift slightly from where they should be, especially around edges.

**Why it happens:** Composite video combines color and brightness into one signal. During capture, the color can shift by a fraction of a pixel.

**Theatre Mode fix:** Chroma phase correction shifts the color back into perfect alignment with the brightness.

### Problem: Dull/Faded Colors
**What you see:** Tape looks washed out, low contrast, gray shadows.

**Why it happens:** Tapes fade over time, magnetic degradation reduces signal strength.

**Theatre Mode fix:** Auto-profiling detects the actual black/white levels and adjusts them back to proper broadcast range.

### Problem: Wrong Field Order
**What you see:** Combing artifacts (horizontal lines) during motion, or entire frame looks "jiggly."

**Why it happens:** Analog video is interlaced (60 fields per second), but capture might have wrong field order (top-first vs bottom-first).

**Theatre Mode fix:** Auto-detects field order and applies hardware-accurate deinterlacing.

## Advanced Options (Optional)

Once you're comfortable with the basics, you can fine-tune Theatre Mode:

### Manual Chroma Adjustment
If auto-profiling doesn't look perfect, you can manually adjust:
- **Chroma Shift X** slider: -2.0 to +2.0 pixels
  - Positive values shift color RIGHT
  - Negative values shift color LEFT
  - Start with small adjustments (0.1 - 0.3 pixels)
- **Chroma Shift Y** slider: -2.0 to +2.0 pixels (usually leave at 0.0)

### Deinterlacing Variants
Choose how Theatre Mode handles interlaced video:
- **Standard Progressive** (default) - Converts to 30fps progressive, best for modern displays
- **Bob (Double-Rate)** - Converts to 60fps progressive, preserves all motion but doubles file size
- **Keep Interlaced** - Maintains interlaced structure for archival or interlaced displays

### Level Adjustment
Fine-tune brightness and contrast:
- **Black Point** - Where pure black starts (0.0 - 0.3)
- **White Point** - Where pure white starts (0.7 - 1.0)
- **Saturation Boost** - Increase color intensity (1.0x - 1.5x)

## Comparison: Before and After

### Without Theatre Mode (Normal Mode):
- Color fringing around text and edges
- Slightly wrong colors (skin tones too orange/pink)
- Low contrast (washed out appearance)
- Standard deinterlacing

### With Theatre Mode:
- ✅ Perfect color alignment (no fringing)
- ✅ Accurate colors matching original tape
- ✅ Proper black/white levels (broadcast-quality contrast)
- ✅ Hardware-accurate deinterlacing

**Expected improvement:** Most users report "significant" or "dramatic" improvement in color accuracy and overall quality, especially for old/faded tapes.

## FAQ

**Q: Will Theatre Mode make my video look perfect?**  
A: Theatre Mode fixes color alignment and levels, but it can't fix physical damage to the tape (tracking errors, dropouts, noise). Combine with other features like BM3D denoising and AI upscaling for best results.

**Q: How long does auto-profiling take?**  
A: 30-60 seconds for most tapes. It only analyzes 40 sample frames, not the entire tape.

**Q: Do I need to profile every tape?**  
A: Ideally yes, since each tape has slightly different characteristics. But you can also just use the presets (VHS, S-VHS, etc.) without profiling.

**Q: Can I use Theatre Mode with AI upscaling?**  
A: Yes! Theatre Mode runs BEFORE AI upscaling, so the AI gets better input with accurate colors.

**Q: Will Theatre Mode work on already-digitized files?**  
A: Yes, as long as the original source was analog tape. Theatre Mode fixes composite video issues that exist in the captured file.

**Q: My video looks worse after Theatre Mode. What happened?**  
A: Try these steps:
  1. Re-run auto-profiling (click "Analyze Tape" again)
  2. Try a different chroma preset (VHS vs S-VHS vs LaserDisc)
  3. Disable level adjustment if colors look too saturated
  4. Check that your source is actually analog tape (Theatre Mode makes digital video worse)

**Q: Can I save my Theatre Mode settings as a preset?**  
A: Yes! Use the "Save Preset" button after configuring Theatre Mode. Name it something like "My VHS Deck Settings" for reuse.

## Recommended Workflows

### Workflow 1: Quick Processing (5 minutes)
1. Enable Theatre Mode
2. Select chroma preset matching your tape format
3. Click "Start Restoration" (skip auto-profiling)
4. Uses hardware defaults optimized for your format

### Workflow 2: Optimal Quality (10 minutes)
1. Enable Theatre Mode
2. Click "Analyze Tape" and wait for profiling
3. Review recommendations, adjust if needed
4. Click "Start Restoration"
5. Best quality, personalized for your specific tape

### Workflow 3: Batch Processing (Multiple Tapes)
1. Enable Theatre Mode
2. Profile first tape, save as preset ("Tape Set 1")
3. Process first tape
4. For subsequent tapes from same recording session:
   - Load preset "Tape Set 1"
   - Process (skip re-profiling if tapes are similar)
5. If tapes look different, re-profile individual tapes

## Technical Details (For Experts)

**Chroma Phase Correction Algorithm:**
- Subpixel bicubic resampling of U/V planes
- Uses zimg resize with `src_left`/`src_top` offsets
- Luma (Y) plane untouched for maximum sharpness
- Hardware-accurate: matches ATI Theatre chipset processing

**Auto-Profiling Method:**
- Samples 40 frames at stride 150 (~1 frame per 5 seconds)
- Analyzes luma distribution (black: 5th percentile, white: 95th percentile)
- Calculates chroma saturation from U/V deviation
- Skips first/last 120 seconds (avoids leader/trailer)

**Performance Impact:**
- Chroma correction: +2-5% processing time
- Auto-profiling: 30-60 seconds one-time cost per tape
- Overall: ~5-8% slower than Normal Mode

**VapourSynth Pipeline:**
```
Source → Chroma Correction → Deinterlace → Denoise → AI Processing → Encode
```

## Support and Resources

- **Full Documentation:** `THEATRE_MODE_FEATURES.md`
- **Technical Implementation:** `core/theatre_mode.py`, `core/chroma_correction.py`
- **GUI Controls:** Restoration tab → Processing Mode section
- **Reference:** `ati_theatre_pipeline_extracted/` (source algorithms)

## Version

Theatre Mode introduced in **Advanced Tape Restorer v4.0.0** (December 2025)

---

**Ready to start? Enable Theatre Mode and click "Analyze Tape" on your first VHS!**
