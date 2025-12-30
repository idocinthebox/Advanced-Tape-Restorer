# Quick Start Guide - Advanced Tape Restorer v2.0

## What's New in v2.0

🎉 **Complete GUI with modular architecture**
🎉 **NEW Capture tab for analog (VHS/Hi8) and DV capture**
🎉 **All v1.0 restoration features ported**
🎉 **43MB single-file EXE (down from 80MB)**

---

## Running the Application

### From Executable (Recommended)
1. Navigate to `dist\` folder
2. Double-click `Advanced_Tape_Restorer_v2.exe`
3. Application opens with no console window

### From Source (For Development)
```bash
cd "c:\Advanced Tape Restorer v2.0"
python main.py
```

---

## Quick Test Workflow

### 1. Test GUI Launch
- ✅ Application should open with 5 tabs: Capture, Input, Restoration, Advanced, Output
- ✅ Console at bottom should show: "Advanced Tape Restorer v2.0 - Ready"
- ✅ Capture devices should refresh automatically (0 found = normal without hardware)

### 2. Test File Selection
1. **File Menu** → **Select Input**
2. Choose any video file (MP4, MKV, AVI, etc.)
3. Output file should auto-populate with `_restored.mp4` suffix
4. Both file paths should display in the file selection section

### 3. Test Field Order Detection
1. After selecting input file, click **Detect Now** button (Input tab)
2. FFmpeg will analyze the video and detect field order
3. Field Order combo should update with result (TFF/BFF/Progressive)
4. Dialog shows detection complete

### 4. Configure Restoration Settings

**Input Tab:**
- Source Filter: `ffms2` (recommended)
- Field Order: `Auto-Detect` or use Detect Now button

**Restoration Tab:**
- QTGMC Preset: `Medium` (balanced speed/quality)
- Sharpness: `0.5` (default)
- Enable BM3D if video is very noisy
- Check "Remove VHS Artifacts" for analog tapes

**Advanced Tab:**
- Temporal Denoise: `Light` or `Medium` for flickering
- Chroma Denoise: `Light` for color noise
- Debanding: Enable if color gradients look banded
- Color Correction: `Auto White Balance` or `Restore Faded Colors`

**Output Tab:**
- Codec: `libx264 (H.264, CPU)` (universal compatibility)
- Audio: `Copy Audio` (fastest)
- Quality (CRF): `18` (visually lossless) to `28` (high quality)
- Encoder Preset: `medium` (balanced)

### 5. Start Processing
1. Click **Start Processing** button
2. Progress bar updates with percentage
3. ETA shows estimated time remaining
4. Console shows detailed log
5. **Stop Processing** button becomes active
6. Dialog shows when complete

### 6. Test Settings Persistence
1. Change some settings
2. Close application
3. Reopen application
4. Settings should be restored (saved to `restoration_settings.json`)

### 7. Test Preset Management
1. **Presets Menu** → **Save Current Settings...**
2. Enter preset name (e.g., "VHS Standard")
3. Preset saved to `restoration_presets.json`
4. (Load dialog not yet implemented - coming soon)

---

## Capture Tab Testing (Hardware Required)

### Device Detection
1. Switch to **Capture** tab
2. Click **Refresh Devices** button
3. If capture hardware connected:
   - Video devices populate in dropdown
   - Audio devices populate in dropdown
4. Without hardware: No devices found (expected)

### Capture Configuration
- **Device Type**: Analog (VHS/Hi8) or DV/miniDV (FireWire)
- **Video Device**: Select from detected devices
- **Audio Device**: Select from detected devices
- **Codec**: HuffYUV (lossless, fast) or FFV1 (archival)
- **Resolution**: 720x480 (NTSC) or 720x576 (PAL)
- **Frame Rate**: 29.97 fps (NTSC) or 25 fps (PAL)
- **Output Folder**: Browse to select destination

### Capture Controls (Not Yet Functional)
- **Start Capture**: Begin recording from device
- **Stop Capture**: End recording
- **Auto-restore checkbox**: Automatically process captured video

---

## Testing Checklist

### Core Functionality
- [ ] GUI launches without errors
- [ ] All tabs display correctly
- [ ] File selection (input/output) works
- [ ] Field order detection works
- [ ] Settings save/load automatically
- [ ] All combo boxes, spinboxes, checkboxes functional
- [ ] Menu bar items accessible

### Processing (Requires Test Video)
- [ ] Select input video
- [ ] Configure settings
- [ ] Start processing
- [ ] Progress bar updates
- [ ] ETA displays correctly
- [ ] Console shows log messages
- [ ] Stop button cancels processing
- [ ] Output file created successfully
- [ ] Output playable in media player

### Capture (Requires Hardware)
- [ ] Devices detected
- [ ] Video device selected
- [ ] Audio device selected
- [ ] Output folder selected
- [ ] Start capture (pending implementation)
- [ ] Stop capture (pending implementation)

---

## Troubleshooting

### "No file selected" warning
- You must select both input and output files before processing
- Use File menu or Browse buttons

### "Detection Failed" error
- Input file may be corrupted or unsupported format
- Try different file or use manual field order selection

### Processing fails immediately
- Check console output for error details
- Verify FFmpeg and VapourSynth installed
- Check input file is valid video

### Capture devices not detected
- Ensure capture hardware connected
- Check Windows Device Manager
- Click Refresh Devices button
- Some devices may require specific drivers

### EXE doesn't launch
- Check Windows Defender/antivirus (may block unknown EXE)
- Right-click EXE → Properties → Unblock
- Run as Administrator if needed

---

## File Locations

### Application Files
- **EXE**: `dist\Advanced_Tape_Restorer_v2.exe`
- **Source**: `main.py` (entry point)
- **GUI**: `gui\main_window.py`, `gui\processing_thread.py`, `gui\settings_manager.py`
- **Core**: `core\processor.py`, `core\vapoursynth_engine.py`, `core\ffmpeg_encoder.py`
- **Capture**: `capture\device_manager.py`, `capture\analog_capture.py`, `capture\dv_capture.py`

### User Data Files (Created at Runtime)
- **Settings**: `restoration_settings.json` (auto-saves current settings)
- **Presets**: `restoration_presets.json` (user-saved presets)
- **Default Config**: `config\default_settings.json` (fallback defaults)

### Temporary Files
- **VapourSynth Script**: `temp_restoration_script.vpy` (deleted after processing)
- **Preview Cache**: Deleted automatically on exit

---

## Next Steps

### For Users
1. Test with real VHS/analog footage
2. Experiment with different QTGMC presets
3. Save presets for common scenarios (VHS, Hi8, DV)
4. Report any issues or suggestions

### For Developers
1. **Implement capture backend** (connect buttons to `AnalogCaptureEngine`/`DVCaptureEngine`)
2. **Create batch queue dialog** (port from v1.0)
3. **Create preset load dialog** (list saved presets)
4. **Add live preview window** (optional, complex)
5. **Validate settings** (warn on invalid combinations)
6. **Add tooltips** (more extensive help text)

---

## Support

### Documentation
- **Full Architecture**: `docs/ARCHITECTURE.md`
- **Capture Guide**: `docs/CAPTURE_GUIDE.md`
- **GUI Complete Report**: `GUI_INTEGRATION_COMPLETE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`

### Known Issues
- Capture Start/Stop buttons are placeholders (backend not connected yet)
- Batch queue menu items are placeholders (dialog not created)
- Preset load dialog not implemented (save works)
- Live preview disabled (complex feature, coming later)

### Reporting Issues
When reporting issues, include:
1. Error message from console output
2. Input file format and size
3. Settings used (take screenshot of tabs)
4. Steps to reproduce
5. Expected vs actual behavior

---

## Credits

**Advanced Tape Restorer v2.0**
- Modular architecture design
- PySide6/Qt6 GUI
- VapourSynth processing engine
- FFmpeg encoding pipeline
- DirectShow capture integration

**Built with:**
- Python 3.13.9
- PySide6 6.10.0
- PyInstaller 6.16.0
- VapourSynth (external dependency)
- FFmpeg (external dependency)

---

## Version History

**v2.0.0** (Current)
- ✅ Complete GUI rewrite with modular architecture
- ✅ NEW Capture tab (analog + DV)
- ✅ All v1.0 restoration features
- ✅ 43MB single-file EXE
- ✅ Settings/preset management
- ✅ Field order auto-detection

**v1.0**
- Original monolithic version
- 2900-line single file
- No capture support
- 80MB EXE

---

**Happy Restoring!** 🎬📼
