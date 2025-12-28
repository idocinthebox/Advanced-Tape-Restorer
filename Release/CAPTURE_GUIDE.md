# Video Capture Guide - Advanced Tape Restorer v3.0

## Overview

The capture module provides professional-grade video capture from analog and DV sources with support for lossless codecs and DirectShow devices.

## Supported Capture Sources

### Analog Sources
- **VHS** (Video Home System)
- **S-VHS** (Super VHS)
- **Video8** / **Hi8**
- **Betamax** / **Betacam**
- **U-matic**
- **Composite Video** (RCA, BNC)
- **S-Video** (Y/C)

### Digital Sources
- **DV** (Digital Video)
- **miniDV**
- **HDV** (High Definition Video)
- **DVCAM**
- **DVCPRO**

## Hardware Requirements

### Analog Capture
**Minimum**:
- USB video capture device or internal capture card
- Composite or S-Video input
- Audio input (line-in or USB audio)

**Recommended**:
- Professional capture card (Hauppauge, Pinnacle, BlackMagic)
- Time Base Corrector (TBC) for improved quality
- External proc amp for signal adjustment

**Professional**:
- BlackMagic Intensity or DeckLink
- Datavideo DAC or similar high-end converter
- Integrated TBC/frame sync

### DV Capture
**Minimum**:
- FireWire (IEEE 1394) port
- DV or miniDV camera/deck with FireWire output

**Recommended**:
- Dedicated DV deck with jog/shuttle controls
- Professional FireWire card (OHCI compliant)

## Capture Codecs

### Lossless Codecs (Recommended)

#### HuffYUV
- **Container**: AVI
- **Quality**: Lossless
- **Compression**: ~2:1
- **Speed**: Very fast
- **CPU**: Low
- **Best for**: Quick captures, VHS restoration

#### Lagarith
- **Container**: AVI
- **Quality**: Lossless
- **Compression**: ~2.5:1
- **Speed**: Fast
- **CPU**: Low
- **Best for**: General purpose, good compression

#### FFV1
- **Container**: MKV
- **Quality**: Lossless
- **Compression**: ~3:1
- **Speed**: Medium
- **CPU**: Medium
- **Best for**: Long-term archival, best compression

#### UT Video
- **Container**: AVI
- **Quality**: Lossless
- **Compression**: ~2:1
- **Speed**: Very fast
- **CPU**: Low
- **Best for**: High-speed captures

### DV Native
- **Format**: DV stream
- **Quality**: Near-lossless (5:1 DCT)
- **Bitrate**: 25 Mbps (DV), 19 Mbps (HDV)
- **Best for**: DV/miniDV tapes (preserves original quality)

## Capture Workflow

### Analog Capture Workflow

#### 1. Hardware Setup
```
VCR/Camera → (Composite/S-Video) → Capture Card → PC
             (Audio RCA)          → Audio Input →
```

**Steps**:
1. Connect video cable (composite or S-Video)
2. Connect audio cables (stereo RCA)
3. Power on VCR/camera
4. Insert tape and cue to start point

#### 2. Device Detection
```python
from capture import CaptureDeviceManager

manager = CaptureDeviceManager()
devices = manager.refresh_devices()

# List analog devices
for device in manager.get_analog_devices():
    print(device)
```

#### 3. Configure Capture Settings
```python
from capture.analog_capture import AnalogCaptureSettings

settings = AnalogCaptureSettings(
    device_name='video="USB Video Device"',
    resolution="720x480",      # NTSC (use 720x576 for PAL)
    framerate="29.97",         # NTSC (use 25 for PAL)
    codec="huffyuv",
    pixel_format="yuv422p",
    audio_device='audio="USB Audio Device"',
    audio_channels=2,
    duration=None              # Manual stop
)
```

#### 4. Start Capture
```python
from capture import AnalogCaptureEngine

engine = AnalogCaptureEngine()

def log_status(message):
    print(message, end='')

success = engine.start_capture(
    settings,
    "captured_tape01.avi",
    log_callback=log_status
)

# Press PLAY on VCR
# ... capture in progress ...

# When tape finishes, stop capture
engine.stop_capture(log_callback=log_status)
```

#### 5. Verify Capture
- Check file size (should be ~15-25 GB per hour for NTSC)
- Verify audio sync
- Check for dropped frames (review console output)

### DV Capture Workflow

#### 1. Hardware Setup
```
DV Camera/Deck → FireWire (1394) → PC
```

**Steps**:
1. Connect FireWire cable (4-pin or 6-pin)
2. Power on camera/deck
3. Insert tape and cue to start
4. Set device to VCR/PLAY mode

#### 2. Device Detection
```python
from capture import CaptureDeviceManager

manager = CaptureDeviceManager()
dv_devices = manager.get_dv_devices()

for device in dv_devices:
    print(device)
```

#### 3. Configure DV Settings
```python
from capture.dv_capture import DVCaptureSettings

settings = DVCaptureSettings(
    device_name='video="Sony DV Device"',
    format="dv",               # or "hdv"
    codec="copy",              # Preserve DV stream
    duration=None              # Manual stop
)
```

#### 4. Start DV Capture
```python
from capture import DVCaptureEngine

engine = DVCaptureEngine()

success = engine.start_capture(
    settings,
    "dv_tape01.avi",
    log_callback=log_status
)

# Press PLAY on deck
# ... capture in progress ...

# When tape finishes
engine.stop_capture(log_callback=log_status)
```

## Resolution & Format Guide

### NTSC (North America, Japan)
- **Resolution**: 720x480 (4:3), 720x480 (16:9 anamorphic)
- **Frame Rate**: 29.97 fps
- **Aspect Ratio**: 10:11 pixel (4:3) or 40:33 (16:9)
- **Field Order**: Usually BFF (Bottom Field First)

### PAL (Europe, Asia, Australia)
- **Resolution**: 720x576 (4:3), 720x576 (16:9 anamorphic)
- **Frame Rate**: 25 fps
- **Aspect Ratio**: 12:11 pixel (4:3) or 16:11 (16:9)
- **Field Order**: Usually TFF (Top Field First)

### DV/miniDV
- **NTSC**: 720x480, 29.97 fps
- **PAL**: 720x576, 25 fps
- **Bitrate**: 25 Mbps (video + audio)
- **Audio**: 48 kHz, 16-bit, stereo

### HDV
- **Format**: 1440x1080 (1080i) or 1280x720 (720p)
- **Bitrate**: 19-25 Mbps (MPEG-2)
- **Frame Rate**: 29.97i/59.94p (NTSC) or 25i/50p (PAL)

## Capture Best Practices

### Before Capture
1. **Clean Equipment**
   - Clean VCR heads with cleaning tape
   - Inspect tape for damage/mold
   - Test playback before full capture

2. **Test Signal**
   - Verify video signal appears in capture software
   - Check audio levels (not too loud/quiet)
   - Confirm correct resolution detected

3. **Disk Space**
   - Ensure sufficient space (~20-30 GB per hour)
   - Use fast drive (SSD preferred for capture)
   - Monitor drive space during capture

### During Capture
1. **Monitor Quality**
   - Watch live preview (if available)
   - Check for dropouts or glitches
   - Verify audio sync every 10-15 minutes

2. **Avoid Interruptions**
   - Disable screen saver
   - Close unnecessary programs
   - Don't use PC during capture

3. **Take Notes**
   - Note tape timecode/counter at start
   - Record any issues or bad sections
   - Document tape metadata (date, content, etc.)

### After Capture
1. **Verify File**
   - Play back captured file fully
   - Check file size is reasonable
   - Verify no corruption

2. **Backup**
   - Make backup copy immediately
   - Store on separate drive
   - Consider cloud backup for important content

3. **Process**
   - Use restoration module to enhance quality
   - Apply appropriate filters for source type
   - Output to modern codec (H.264/H.265)

## Troubleshooting

### No Video Signal
**Problem**: Capture software shows black screen

**Solutions**:
- Check cable connections (video and audio)
- Verify VCR/camera is powered on and in PLAY mode
- Try different video input (composite vs S-Video)
- Reinstall capture card drivers
- Test with different capture software

### Dropped Frames
**Problem**: Capture reports dropped frames

**Solutions**:
- Close background applications
- Use faster storage drive (SSD)
- Lower capture resolution if possible
- Update capture card drivers
- Check CPU usage during capture

### Audio Sync Issues
**Problem**: Audio drifts out of sync with video

**Solutions**:
- Verify correct audio device selected
- Use same sample rate as source (48 kHz for DV, 48 kHz or 44.1 kHz for analog)
- Try different codec (HuffYUV tends to have good sync)
- Check VCR playback speed (some VCRs have speed issues)

### Poor Video Quality
**Problem**: Capture looks worse than VCR playback

**Solutions**:
- Clean VCR heads thoroughly
- Try different video input (S-Video is better than composite)
- Adjust VCR tracking control
- Use Time Base Corrector (TBC) if available
- Check for ground loops (audio hum)

### FireWire Device Not Detected
**Problem**: DV camera/deck not appearing

**Solutions**:
- Check FireWire cable connection
- Power cycle camera/deck
- Update FireWire controller drivers
- Try different FireWire port
- Verify device is in VCR/PLAY mode (not CAMERA mode)

### Capture Software Crashes
**Problem**: Application crashes during capture

**Solutions**:
- Update FFmpeg to latest version
- Check available RAM (need 4+ GB)
- Try different codec (HuffYUV is most stable)
- Reduce buffer sizes if memory constrained
- Check for Windows updates

## Advanced Techniques

### Time Base Correction
Use external TBC between VCR and capture card:
```
VCR → TBC → Capture Card → PC
```

Benefits:
- Stabilizes unstable signals
- Corrects timing errors
- Reduces jitter
- Improves color consistency

### Batch Capture Multiple Tapes
```python
tape_list = [
    ("Tape 01 - Family Vacation 1995", 7200),  # 2 hours
    ("Tape 02 - Birthday Party 1996", 3600),   # 1 hour
    ("Tape 03 - Wedding 1998", 5400)           # 1.5 hours
]

for tape_name, duration in tape_list:
    print(f"\nInsert: {tape_name}")
    input("Press Enter when ready...")
    
    settings.duration = duration
    output_file = f"{tape_name}.avi"
    
    engine.start_capture(settings, output_file, log_callback)
    # Wait for capture to complete
    engine.stop_capture(log_callback)
    
    print(f"Completed: {tape_name}")
```

### Scene Detection During Capture
Capture in segments based on tape timecode:
```python
# Capture 30-minute segments
segment_duration = 1800  # 30 minutes

for segment in range(4):  # 4 segments = 2 hours
    output_file = f"tape01_segment{segment+1:02d}.avi"
    
    settings.duration = segment_duration
    engine.start_capture(settings, output_file, log_callback)
    # Automatically stops after 30 minutes
    
    # Optional: Quick verification
    print(f"Segment {segment+1} captured")
```

### Automatic Post-Processing
Capture then immediately process:
```python
from core import VideoProcessor

# Capture
engine.start_capture(settings, "captured.avi", log_callback)
# ... wait for capture ...
engine.stop_capture(log_callback)

# Process
processor = VideoProcessor()
restoration_options = {
    'field_order': 'Auto-Detect',
    'qtgmc_preset': 'Slow',
    'denoise_strength': 'Medium (Slow)',
    'codec': 'libx264 (H.264, CPU)',
    'crf': '18'
}

processor.process_video(
    "captured.avi",
    "restored.mp4",
    restoration_options,
    progress_callback=lambda p, e: print(f"{p:.1f}%"),
    log_callback=print
)
```

## File Size Estimates

### Analog Capture (NTSC 720x480)
- **HuffYUV**: ~20 GB/hour
- **Lagarith**: ~15 GB/hour
- **FFV1**: ~12 GB/hour
- **UT Video**: ~18 GB/hour

### Analog Capture (PAL 720x576)
- **HuffYUV**: ~24 GB/hour
- **Lagarith**: ~18 GB/hour
- **FFV1**: ~14 GB/hour

### DV Capture
- **DV (NTSC)**: ~13 GB/hour (25 Mbps)
- **DV (PAL)**: ~13 GB/hour (25 Mbps)
- **HDV (1080i)**: ~9 GB/hour (19 Mbps MPEG-2)

## Recommended Workflows

### Workflow 1: Quick VHS Capture
```
1. Connect VHS player via composite
2. Select HuffYUV codec
3. Capture at 720x480, 29.97 fps
4. Process with "VHS Standard" preset
5. Output H.264 MP4
```

### Workflow 2: Professional Archival
```
1. Use S-Video connection with TBC
2. Select FFV1 codec (best compression)
3. Capture at native resolution
4. Keep lossless master
5. Create H.265 viewing copy
```

### Workflow 3: DV Transfer
```
1. Connect via FireWire
2. Use "copy" codec to preserve DV stream
3. Capture to .avi or .dv file
4. Optional: Transcode to modern codec
5. Keep DV master for archive
```

### Workflow 4: Batch Project
```
1. Capture all tapes (10-20 tapes)
2. Store as lossless files
3. Batch process with consistent settings
4. Create viewing copies (H.264)
5. Upload to cloud/archive original captures
```

## Resources

### External Tools
- **VirtualDub**: Advanced capture features
- **Scenalyzer Live**: DV-specific capture & scene detection
- **AmaRecTV**: Alternative capture software
- **AVISynth/VapourSynth**: Advanced filtering

### Hardware Recommendations
- **Budget**: USB EasyCap (~$10-30)
- **Mid-Range**: Hauppauge USB-Live2 (~$60-100)
- **Professional**: BlackMagic Intensity Shuttle (~$200-300)
- **High-End**: BlackMagic DeckLink (~$400+)

### Further Reading
- VapourSynth Documentation: http://vapoursynth.com
- FFmpeg Capture Guide: https://trac.ffmpeg.org/wiki/Capture
- Doom9 Forum: https://forum.doom9.org (restoration community)

---

**Version**: 3.1.0
**Last Updated**: November 2025

## What's New in v3.1

### User-Specified Output Folders
- **Choose ANY drive or folder** for capture output
- Network paths supported (UNC paths)
- External USB drives recommended for best performance
- Settings saved and persisted across sessions
- Application shows available disk space after folder selection

### Improved Device Detection
- Better DirectShow device enumeration
- Auto-identification of device types (analog, DV, HDMI, webcam)
- More reliable device refresh
- Support for more capture hardware brands

### Enhanced Capture Workflow
- Automatic filename generation with timestamps
- Optional auto-restore after capture completes
- Real-time capture monitoring in console
- Better error handling and logging
- Graceful capture termination
- **Video Input Source Selection (Crossbar)** - Switch between Composite/S-Video/Component

### File Format Flexibility
- Standard AVI/MKV formats compatible with all software
- Files immediately accessible after capture
- No temporary locations or hidden directories
- Direct compatibility with:
  * Adobe Premiere Pro
  * DaVinci Resolve
  * Final Cut Pro
  * VLC Media Player
  * Any FFmpeg-compatible software

### Storage Management
- User controls output location completely
- Disk space warnings before capture
- Support for very large captures (>2GB AVI auto-split)
- Better handling of drive speed limitations

### Crossbar / Input Source Selection (NEW in v3.0)

Many capture cards have multiple video inputs that can be selected:
- **Composite (Pin 0)**: RCA yellow connector - standard VHS quality
- **S-Video (Pin 1)**: Y/C connector - better quality for S-VHS tapes
- **Component (Pin 2)**: YPbPr connectors - highest quality analog
- **HDMI/Digital (Pin 4)**: Digital inputs on professional cards

**How to Use:**
1. In Capture tab, use the **Video Input** dropdown
2. Select input matching your cable connection:
   - VHS with yellow RCA → Select "Composite (RCA)"
   - S-VHS with Y/C cable → Select "S-Video (Y/C)"
   - Component with RGB → Select "Component (YPbPr)"
3. If unsure or capture fails → Select "Auto (Default)"

**Technical Details:**
- Uses DirectShow crossbar API
- FFmpeg parameters: `-crossbar_video_input_pin_number`
- Not all capture cards support input switching
- Consumer USB cards typically have Composite (0) and S-Video (1)
- Professional PCIe cards may have all inputs (0-4)

**Troubleshooting:**
- If capture fails after selecting input: Use "Auto (Default)"
- If wrong signal appears: Try different input (card may auto-switch)
- If no video signal: Check cable is connected to correct port

### Capture Presets (NEW in v3.0)

Quickly configure capture settings with built-in or custom presets.

**Built-in Presets:**
- **VHS NTSC (Composite)** - 720x480, 29.97fps, HuffYUV, Composite input
- **VHS PAL (Composite)** - 720x576, 25fps, HuffYUV, Composite input
- **S-VHS NTSC (S-Video)** - 720x480, 29.97fps, HuffYUV, S-Video input
- **S-VHS PAL (S-Video)** - 720x576, 25fps, HuffYUV, S-Video input
- **DV NTSC (FireWire)** - 720x480, 29.97fps, Copy codec
- **DV PAL (FireWire)** - 720x576, 25fps, Copy codec
- **Component NTSC (YPbPr)** - 720x480, 29.97fps, HuffYUV, Component input
- **Component PAL (YPbPr)** - 720x576, 25fps, HuffYUV, Component input

**How to Use:**
1. In Capture tab, select preset from "Capture Preset" dropdown
2. Preset automatically configures:
   - Codec (HuffYUV, FFV1, Lagarith, or Copy)
   - Resolution (720x480 or 720x576)
   - Frame rate (29.97 or 25fps)
   - Video input source (Composite, S-Video, Component)
   - Audio input source (Line In)
3. Fine-tune settings if needed after applying preset
4. Click "Save as Preset" to save your custom configuration

**Custom Presets:**
1. Configure all capture settings manually
2. Click "Save as Preset" button
3. Enter preset name (e.g., "My VHS Setup")
4. Preset saved to settings and appears in dropdown
5. Available for all future capture sessions

**Benefits:**
- One-click configuration for common tape formats
- No need to remember resolution/framerate combinations
- Automatically selects correct input source
- Saves time when switching between tape types
- Custom presets for unique hardware configurations

### Live Preview Window (NEW in v3.0)

View real-time video feed before and during capture.

**How to Enable:**
1. Check "Enable Live Preview" checkbox in Capture tab
2. Click "Start Capture"
3. Separate preview window opens showing live video feed
4. Preview continues during capture
5. Window closes automatically when capture stops

**Features:**
- **Real-time display**: See video signal as it's being captured
- **Low-latency**: Uses ffplay for minimal delay (~100-300ms)
- **Scaled output**: Preview scaled to 640x480 for performance
- **No audio**: Preview is video-only to reduce CPU load
- **Independent window**: Can be moved/resized separately

**Use Cases:**
- **Signal verification**: Confirm video signal before starting capture
- **Framing check**: Ensure entire image is captured correctly
- **Color/quality preview**: Verify colors and image quality
- **Troubleshooting**: Diagnose "no signal" or wrong input issues
- **Live monitoring**: Watch capture in real-time

**Performance Impact:**
- CPU usage: ~5-15% additional (depends on resolution)
- Recommended: Disable on slower systems (Core i3, older CPUs)
- No impact on capture quality (independent process)
- Can enable/disable per capture session

**Technical Details:**
- Uses ffplay (FFmpeg's video player)
- Reads directly from capture device (duplicate stream)
- Frame dropping enabled to prevent buffer overflow
- Low-delay flags for minimal latency

**Troubleshooting:**
- Preview shows black: Check Video Input selection
- Preview stutters: Disable preview, system may be too slow
- No preview window: Check ffplay is installed with FFmpeg
- Preview doesn't match capture: Normal ~300ms delay

### Real-Time Monitoring (NEW in v3.0)

Monitor capture quality and disk space during active captures.

#### Dropped Frame Counter

Shows number of frames dropped by capture hardware/software.

**Display States:**
- **Green (0 frames)**: Perfect capture, no frames dropped
- **Yellow (1-9 frames)**: Acceptable, minor glitches possible
- **Red (10+ frames)**: Warning! Capture quality compromised

**What Causes Dropped Frames:**
- Slow hard drive (mechanical HDD can't keep up)
- High CPU usage (other programs running)
- USB bandwidth issues (other USB devices competing)
- Insufficient RAM (system swapping to disk)
- Bad capture hardware drivers

**How to Fix:**
- Use faster drive (SSD recommended)
- Close unnecessary programs
- Disconnect other USB devices
- Lower capture resolution if persistent
- Use PCIe capture card instead of USB

**Technical Details:**
- Parses FFmpeg stderr output every second
- Looks for "drop=" field in FFmpeg stats
- Updates display in real-time during capture
- Counter resets when new capture starts

#### Disk Space Monitor

Shows available space on output drive during capture.

**Display States:**
- **Normal (>100 GB)**: Sufficient space, normal display
- **Orange (50-100 GB)**: Low space warning
- **Red (<50 GB)**: Critical! May run out during long captures

**What It Shows:**
- Free space on selected output drive/folder
- Updates every second during capture
- Color-coded for quick visual check
- Shows space before capture starts (when folder selected)

**Storage Recommendations:**
- Plan 100+ GB per hour for HuffYUV (NTSC)
- Plan 120+ GB per hour for HuffYUV (PAL)
- Plan 60+ GB per hour for FFV1
- Plan 15+ GB per hour for DV copy mode
- Always maintain 50+ GB free buffer

**Technical Details:**
- Uses shutil.disk_usage() to query drive
- Updates every second via QThread
- Thread-safe GUI updates via Qt signals
- Works with local, external, and network drives

**Capture Monitoring Workflow:**
```
1. Select output folder → Disk space shown immediately
2. Start capture → Monitoring thread starts
3. During capture:
   - Dropped frames counter updates every second
   - Disk space updates every second
   - Console shows FFmpeg progress
4. Stop capture → Monitoring thread stops gracefully
```

**Benefits:**
- **Early warning**: Know about problems before tape finishes
- **Quality assurance**: Confirm capture is proceeding correctly
- **Proactive management**: Stop and fix issues if frames dropping
- **Peace of mind**: Visual confirmation capture is working

---

**End of Capture Guide**
