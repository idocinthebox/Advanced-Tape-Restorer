# Capture Feature Guide - Advanced Tape Restorer v2.0

## Overview

The capture feature allows you to digitize analog tapes (VHS, Hi8, Video8, Betamax) and DV/miniDV tapes directly within the application. Captured files are saved to a user-specified directory with full control over format and location.

---

## Quick Answers to Your Questions

### ✅ **Q: Does the captured file go to a place I can use with other programs?**

**YES!** Captured files are saved to a folder **YOU choose**:
- Standard file formats: `.avi`, `.mkv` (playable in VLC, Premiere, DaVinci Resolve, etc.)
- Lossless codecs: HuffYUV, FFV1, Lagarith (professional archival quality)
- Files are immediately accessible after capture stops
- No temporary locations - files saved directly to your chosen directory

### ✅ **Q: What format is the capture?**

**You control the format** via dropdown menus:

**Codec Options:**
- **HuffYUV (Lossless)** - `.avi` file
  - Fast encoding, moderate file size
  - Industry standard for capture
  - ~60-80 GB/hour for SD (720x480)
  
- **FFV1 (Lossless)** - `.mkv` file
  - Best compression, slower encoding
  - Archival standard
  - ~40-60 GB/hour for SD
  
- **Lagarith** - `.avi` file
  - Windows-specific lossless codec
  - Good compression, fast
  - ~50-70 GB/hour for SD

**Resolution Options:**
- 720x480 (NTSC) - Standard US/Japan VHS
- 720x576 (PAL) - European VHS
- 640x480 - Alternative SD
- Custom - Future support

**Frame Rate Options:**
- 29.97 fps (NTSC)
- 25 fps (PAL)
- 23.976 fps (Film transfers)
- 30 fps (Standard)

### ✅ **Q: Can we specify a directory so we won't run out of space?**

**ABSOLUTELY!** This is built-in:

1. **Click "Browse..." button** in Capture tab
2. **Choose ANY folder** on ANY drive:
   - External USB drive ✓
   - Network drive ✓
   - Second internal drive ✓
   - Even UNC paths (\\\\server\\share)
3. **Application shows available space** after selecting folder
4. **Setting is saved** - remembered across sessions

**Space Requirements:**
- SD capture (720x480, HuffYUV): ~60-80 GB/hour
- HD capture (1920x1080, HuffYUV): ~200-300 GB/hour
- Always check free space before long captures!

---

## Capture Workflow

### Step 1: Connect Hardware
- Plug in USB capture device (Elgato, AVerMedia, Hauppauge, etc.)
- Or FireWire DV/miniDV device
- Insert tape in player and connect to capture device

### Step 2: Configure Capture Settings

**In the Capture Tab:**

1. **Device Type**: Select "Analog (VHS/Hi8)" or "DV/miniDV (FireWire)"

2. **Refresh Devices**: Click to detect connected hardware
   - Video devices populate in dropdown
   - Audio devices populate in dropdown

3. **Video Device**: Select your capture card

4. **Audio Device**: Select audio input (usually same device)

5. **Codec**: Choose lossless format
   - **HuffYUV** for speed (recommended)
   - **FFV1** for smallest files
   - **Lagarith** for Windows compatibility

6. **Resolution**: Match your source
   - NTSC VHS → 720x480
   - PAL VHS → 720x576

7. **Frame Rate**: Match your source
   - NTSC → 29.97 fps
   - PAL → 25 fps

8. **Output Folder**: **CRITICAL!**
   - Click **Browse...** button
   - Choose drive with sufficient free space
   - Application saves this location

9. **Auto-restore checkbox**: (Optional)
   - If checked: After capture, application prompts to process the file
   - If unchecked: File is captured only (use other software later)

### Step 3: Start Capture

1. **Cue tape** to starting position in player

2. Click **Start Capture** button
   - Confirmation dialog shows all settings
   - Output filename displayed (e.g., `capture_20251118_143052.avi`)

3. **Press Play** on tape player

4. Monitor capture:
   - Console shows capture started
   - Status shows filename being captured
   - Green status indicator

### Step 4: Stop Capture

1. When tape finishes (or manual stop desired):
   - Click **Stop Capture** button

2. Capture completes:
   - File saved to your specified folder
   - File is immediately usable

3. If **Auto-restore** was checked:
   - Dialog asks "Process captured video?"
   - Click **Yes**: File loads into restoration workflow
   - Click **No**: File remains in capture folder for later

---

## File Locations & Organization

### Recommended Folder Structure

```
E:\Tape_Captures\              ← Your chosen output folder
├── 2025-11-18_Family_1985\
│   ├── capture_20251118_140000.avi   (Raw capture)
│   └── capture_20251118_140000_restored.mp4  (After processing)
├── 2025-11-18_Wedding_1992\
│   ├── capture_20251118_150000.avi
│   └── capture_20251118_150000_restored.mp4
└── 2025-11-19_Vacation_1998\
    ├── capture_20251119_100000.avi
    └── capture_20251119_100000_restored.mp4
```

### File Naming Convention

**Automatic naming**: `capture_YYYYMMDD_HHMMSS.{avi|mkv}`

**Examples:**
- `capture_20251118_143052.avi` - Captured Nov 18, 2025 at 2:30:52 PM
- `capture_20251118_143052_restored.mp4` - Restored version

**You can rename files** after capture if desired.

---

## Using Captured Files with Other Software

### Compatibility

Captured files work with **any** professional video software:

**Editing Software:**
- Adobe Premiere Pro ✓
- DaVinci Resolve ✓
- Final Cut Pro ✓
- Vegas Pro ✓
- Kdenlive ✓

**Players:**
- VLC Media Player ✓
- MPV ✓
- Media Player Classic ✓
- Windows Media Player (HuffYUV/Lagarith with codecs installed)

**Restoration Software:**
- VirtualDub ✓
- Avisynth/VapourSynth scripts ✓
- ffmpeg command line ✓

### Workflow Options

**Option A: Capture → Process in App**
1. Capture with Advanced Tape Restorer
2. Check "Auto-restore" checkbox
3. Process immediately with built-in filters
4. Output: restored MP4/MKV

**Option B: Capture → Process Elsewhere**
1. Capture with Advanced Tape Restorer
2. Uncheck "Auto-restore"
3. Use file with other software:
   - Import into Premiere/Resolve
   - Process with VirtualDub
   - Apply custom Avisynth scripts

**Option C: Capture → Archive → Process Later**
1. Capture to large external drive
2. Archive raw lossless files
3. Process copies when needed
4. Preserve originals for future re-processing

---

## Storage Planning

### Space Requirements by Format

**SD Content (720x480, 29.97fps):**
| Codec | GB/Hour | 2-Hour Tape | Notes |
|-------|---------|-------------|-------|
| HuffYUV | 60-80 GB | 120-160 GB | Fastest |
| FFV1 | 40-60 GB | 80-120 GB | Best compression |
| Lagarith | 50-70 GB | 100-140 GB | Balanced |

**HD Content (1920x1080, 29.97fps):**
| Codec | GB/Hour | Notes |
|-------|---------|-------|
| HuffYUV | 200-300 GB | Very large |
| FFV1 | 150-250 GB | Recommended for HD |

**DV Content (720x480, 29.97fps):**
| Codec | GB/Hour | Notes |
|-------|---------|-------|
| Copy (raw DV) | 13 GB | No re-encoding |

### Drive Recommendations

**For Capture:**
- **USB 3.0 or faster** required
- SSD preferred for HD capture
- 7200 RPM HDD minimum for SD
- Dedicated capture drive (not system drive)

**For Archival:**
- External USB drives (8TB+ recommended)
- NAS/RAID for critical content
- Cloud backup for irreplaceable footage

---

## Troubleshooting

### "No devices found" after Refresh
- Check USB connections
- Verify drivers installed (Device Manager)
- Try different USB port
- Restart application

### "Failed to start capture"
- Check output folder is writable
- Ensure sufficient disk space (at least 100 GB free)
- Close other applications using capture device
- Check console output for detailed error

### Capture file is choppy/dropped frames
- Drive too slow (upgrade to faster drive)
- Other programs using CPU/disk
- Change codec to HuffYUV (faster encoding)
- Close background applications

### Audio out of sync
- Verify audio device selected
- Check audio channels setting (usually 2)
- Ensure audio device isn't in use by other apps

### File won't play in other software
- Install codec pack (K-Lite Codec Pack for Windows)
- Use VLC (plays everything)
- Convert to MP4 using application's restoration feature

---

## Advanced Features

### Auto-Processing After Capture

**What it does:**
- When capture stops, application prompts to process file
- Automatically loads captured file as input
- Applies restoration filters (QTGMC, denoise, etc.)
- Saves restored version alongside raw capture

**Best for:**
- Quick digitization workflow
- Consistent restoration settings
- Batch tape processing

**To enable:**
1. Check "Automatically restore captured video" checkbox
2. Capture as normal
3. When prompted, click "Yes" to process
4. Configure restoration settings
5. Click "Start Processing"

### Capture + Batch Processing

**Workflow:**
1. Capture multiple tapes to folder
2. Disable auto-restore
3. After all captures complete, use File menu
4. Add all captured files to batch queue
5. Process overnight/unattended

---

## Technical Details

### Capture Pipeline

```
Analog Tape Player
    ↓
USB Capture Device (DirectShow on Windows)
    ↓
FFmpeg (dshow input)
    ↓
Lossless Codec Encoding (HuffYUV/FFV1/Lagarith)
    ↓
AVI/MKV File (your chosen folder)
```

### Command Example (Internal)

```bash
ffmpeg -f dshow 
  -video_size 720x480 
  -framerate 29.97 
  -pixel_format yuv422p 
  -i video="USB Video Device":audio="USB Audio Device"
  -c:v huffyuv 
  -pix_fmt yuv422p 
  -c:a pcm_s16le 
  "E:\Captures\capture_20251118_143052.avi"
```

### Color Space

- **YUV422**: Standard for analog capture (preserves chroma detail)
- **Audio**: PCM 16-bit (lossless, 1.4 Mbps)
- **No quality loss**: Bit-perfect capture from source

---

## FAQ

**Q: Can I pause and resume capture?**
A: No, each capture is one continuous file. Stop and start new capture if needed.

**Q: Can I schedule captures?**
A: Not currently. Manual start/stop only.

**Q: Does it work with HDMI capture cards?**
A: Yes, if recognized by DirectShow (Windows). Test with "Refresh Devices".

**Q: Can I capture from webcam?**
A: Technically yes (appears in device list), but not recommended. Use dedicated webcam software.

**Q: What's the maximum capture duration?**
A: Unlimited (until disk full). AVI files split at 2GB (automatic in FFmpeg).

**Q: Can I capture to network drive?**
A: Yes, but USB 3.0+ direct-attached drive strongly recommended for reliability.

**Q: Does it support 4K capture?**
A: Codec/device dependent. HuffYUV can handle it, but requires very fast storage.

---

## Best Practices

1. **Test capture settings** with 30-second test before full tape
2. **Monitor disk space** - keep at least 100 GB free
3. **Dedicated capture drive** - not your system drive
4. **Close other programs** during capture
5. **Archive raw captures** - never delete lossless originals
6. **Label tapes** before capture for easy file renaming
7. **Clean tape heads** regularly for best quality
8. **Use quality capture hardware** (Elgato, Blackmagic Design)

---

## Summary

✅ **Files saved to YOUR chosen folder** (any drive, any location)
✅ **Standard formats** (AVI/MKV - playable everywhere)
✅ **Lossless quality** (professional archival codecs)
✅ **Full control** over output location and format
✅ **Immediate access** - files ready to use after capture
✅ **Works with other software** - Premiere, Resolve, VLC, etc.
✅ **Space management** - shows available space, you choose drive
✅ **Optional auto-processing** - or use files elsewhere

The capture feature is **production-ready** for professional tape digitization workflows! 🎬📼
