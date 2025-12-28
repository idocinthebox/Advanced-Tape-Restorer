# Advanced Tape Restorer v2.0

**Professional Video Restoration & Capture Suite**

A modular, enterprise-grade application for capturing and restoring analog and DV tapes to high-quality digital video.

## 🎯 Project Vision

Version 2.0 represents a complete architectural redesign with clear separation of concerns:
- **Core Processing**: Independent video restoration engine
- **Capture Module**: Professional tape capture capabilities
- **GUI Layer**: Modern PySide6 interface
- **Modular Design**: Each component can be modified without affecting others

## 📁 Project Structure

```
Advanced Tape Restorer v2.0/
├── core/                      # Video processing engine (independent)
│   ├── __init__.py
│   ├── processor.py          # Main orchestrator
│   ├── video_analyzer.py     # Metadata & field order detection
│   ├── vapoursynth_engine.py # VapourSynth script generation
│   └── ffmpeg_encoder.py     # FFmpeg encoding with progress
│
├── capture/                   # Video capture module (NEW)
│   ├── __init__.py
│   ├── device_manager.py     # Device detection & management
│   ├── analog_capture.py     # Analog/VHS capture engine
│   └── dv_capture.py         # DV/miniDV FireWire capture
│
├── gui/                       # PySide6 GUI (to be created)
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── restoration_tab.py    # Restoration controls
│   ├── capture_tab.py        # Capture interface (NEW)
│   └── dialogs/              # Preset manager, batch queue, etc.
│
├── config/                    # Configuration & settings
│   └── default_settings.json
│
└── docs/                      # Documentation
    ├── API.md                # API reference for modules
    ├── CAPTURE_GUIDE.md      # Capture workflow documentation
    └── ARCHITECTURE.md       # Technical architecture details
```

## 🚀 Key Features

### Core Processing (v1.0 Proven Technology)
- ✅ VapourSynth-based restoration pipeline
- ✅ QTGMC deinterlacing (7 quality presets)
- ✅ Auto field order detection (TFF/BFF/Progressive)
- ✅ Smart source filter selection (Auto/bestsource/lsmas/ffms2)
- ✅ VHS artifact removal (TComb/Bifrost)
- ✅ AI upscaling (RealESRGAN for SD→HD/4K)
- ✅ BM3D denoising (CPU/GPU)
- ✅ Live preview during processing
- ✅ Batch processing queue
- ✅ All ProRes variants + DNxHD + H.264/H.265/AV1

### Capture Module (v2.0 NEW)
- 🆕 Analog capture (VHS, Hi8, Video8, Betamax, etc.)
  - DirectShow device detection
  - Lossless codecs (HuffYUV, Lagarith, FFV1, UT Video)
  - Configurable resolution & framerate
  - Audio sync support
- 🆕 DV/miniDV capture
  - FireWire (IEEE 1394) support
  - Native DV stream copy
  - HDV detection
  - Timecode extraction
- 🆕 Device management
  - Auto-detect capture hardware
  - Device type identification
  - Multi-device support

### GUI Enhancements (v2.0 Planned)
- 🔜 Integrated capture tab
- 🔜 Live capture preview
- 🔜 One-click Capture → Process workflow
- 🔜 Capture presets for different tape formats
- 🔜 Auto-processing after capture completion

## 🏗️ Architecture Principles

### 1. Separation of Concerns
Each module has a single, well-defined responsibility:
- **Core**: Video processing logic only
- **Capture**: Hardware interfacing and capture management
- **GUI**: User interface and workflow orchestration

### 2. Independent Testability
Modules can be tested in isolation:
```python
# Test core processing without GUI
from core import VideoProcessor
processor = VideoProcessor()
processor.process_video("input.avi", "output.mp4", options)

# Test capture without GUI
from capture import AnalogCaptureEngine
engine = AnalogCaptureEngine()
engine.start_capture(settings, "captured.avi")
```

### 3. API-First Design
All modules expose clean, documented APIs:
```python
# Core API
VideoProcessor.process_video(input, output, options, callbacks)
VideoAnalyzer.get_video_info(input_file)
VideoAnalyzer.detect_field_order(input_file, thresholds)

# Capture API
CaptureDeviceManager.refresh_devices()
AnalogCaptureEngine.start_capture(settings, output, callback)
DVCaptureEngine.stop_capture(callback)
```

### 4. Callback-Based Progress
All long-running operations use callbacks for progress updates:
```python
def on_progress(percent, eta_str):
    print(f"Progress: {percent:.1f}% - ETA: {eta_str}")

def on_log(message):
    print(message)

processor.process_video(
    "input.avi", "output.mp4", options,
    progress_callback=on_progress,
    log_callback=on_log
)
```

## 🔧 Development Workflow

### Setting Up Development Environment
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install PySide6 vapoursynth-portable ffmpeg-python
```

### Testing Core Module
```python
from core import VideoProcessor

processor = VideoProcessor()

# Check prerequisites
processor.check_prerequisites()

# Get video info
info = processor.get_video_info("test.avi")
print(f"Resolution: {info['width']}x{info['height']}")

# Process video
options = {
    'field_order': 'Auto-Detect',
    'qtgmc_preset': 'Slow',
    'codec': 'libx264 (H.264, CPU)',
    'crf': '18'
}

success = processor.process_video(
    "input.avi",
    "output.mp4",
    options,
    progress_callback=lambda p, e: print(f"{p:.1f}%"),
    log_callback=print
)
```

### Testing Capture Module
```python
from capture import CaptureDeviceManager, AnalogCaptureEngine

# Detect devices
manager = CaptureDeviceManager()
devices = manager.refresh_devices()

for device in devices:
    print(device)

# Capture from analog device
if devices:
    from capture.analog_capture import AnalogCaptureSettings
    
    settings = AnalogCaptureSettings(
        device_name=devices[0].path,
        resolution="720x480",
        codec="huffyuv",
        duration=60  # 60 seconds
    )
    
    engine = AnalogCaptureEngine()
    engine.start_capture(settings, "captured.avi", log_callback=print)
```

## 📚 Core API Reference

### VideoProcessor
Main orchestration class for video restoration.

**Methods:**
- `check_prerequisites()` - Verify FFmpeg, VapourSynth, vspipe installed
- `process_video(input, output, options, callbacks)` - Process video with restoration
- `get_video_info(input_file)` - Get metadata (resolution, fps, codec, etc.)
- `request_stop()` - Cancel ongoing processing
- `cleanup()` - Clean up processes and temp files

### VideoAnalyzer
Video metadata extraction and analysis.

**Methods:**
- `get_video_info(input_file)` - Returns (width, height, PAR, frame_count, fps)
- `detect_field_order(input_file, thresholds)` - Auto-detect TFF/BFF/Progressive
- `get_codec_info(input_file)` - Get codec name and pixel format

### VapourSynthEngine
VapourSynth script generation and management.

**Methods:**
- `create_script(input_file, options)` - Generate restoration script
- `get_total_frames()` - Get frame count from script
- `cleanup()` - Remove temporary script file

### FFmpegEncoder
FFmpeg encoding with progress monitoring.

**Methods:**
- `build_command(input, output, options, pipe_input)` - Build FFmpeg command
- `encode(vspipe_proc, output, options, total_frames, callbacks)` - Encode with progress
- `cleanup()` - Terminate encoder process

## 📚 Capture API Reference

### CaptureDeviceManager
Detect and manage video capture devices.

**Methods:**
- `refresh_devices()` - Scan for available capture devices
- `get_device_by_index(index)` - Get specific device
- `get_analog_devices()` - Get all analog capture cards
- `get_dv_devices()` - Get all DV/FireWire devices

### AnalogCaptureEngine
Capture from analog sources (VHS, Hi8, etc.).

**Methods:**
- `build_capture_command(settings, output)` - Build FFmpeg capture command
- `start_capture(settings, output, log_callback)` - Start capturing
- `stop_capture(log_callback)` - Stop capture gracefully
- `get_capture_stats()` - Get current capture statistics

### DVCaptureEngine
Capture from DV/miniDV sources via FireWire.

**Methods:**
- `build_capture_command(settings, output)` - Build FFmpeg DV capture command
- `start_capture(settings, output, log_callback)` - Start DV capture
- `stop_capture(log_callback)` - Stop DV capture
- `get_timecode()` - Get current DV timecode
- `detect_format(device)` - Auto-detect DV vs HDV

## 🎬 Usage Examples

### Example 1: Simple Video Restoration
```python
from core import VideoProcessor

processor = VideoProcessor()

options = {
    'field_order': 'Auto-Detect',
    'qtgmc_preset': 'Slow',
    'denoise_strength': 'Medium (Slow)',
    'codec': 'libx264 (H.264, CPU)',
    'crf': '18',
    'ffmpeg_preset': 'slow'
}

processor.process_video(
    "old_vhs_tape.avi",
    "restored.mp4",
    options
)
```

### Example 2: Capture Then Process
```python
from capture import CaptureDeviceManager, AnalogCaptureEngine
from capture.analog_capture import AnalogCaptureSettings
from core import VideoProcessor

# Step 1: Capture from VHS
manager = CaptureDeviceManager()
devices = manager.get_analog_devices()

settings = AnalogCaptureSettings(
    device_name=devices[0].path,
    resolution="720x480",
    codec="huffyuv"
)

capture_engine = AnalogCaptureEngine()
capture_engine.start_capture(settings, "captured.avi")

# ... wait for capture to complete ...

# Step 2: Process captured video
processor = VideoProcessor()
processor.process_video(
    "captured.avi",
    "restored.mp4",
    restoration_options
)
```

### Example 3: Batch Processing
```python
from core import VideoProcessor

processor = VideoProcessor()
files = ["tape1.avi", "tape2.avi", "tape3.avi"]

for input_file in files:
    output_file = input_file.replace(".avi", "_restored.mp4")
    processor.process_video(input_file, output_file, options)
```

## 🔮 Roadmap

### Phase 1: Core Extraction (✅ Complete)
- [x] Modular architecture design
- [x] Core processing module
- [x] Capture module foundation
- [x] API documentation

### Phase 2: Capture Integration (Current)
- [ ] Complete DirectShow device detection testing
- [ ] Implement live capture preview
- [ ] Add capture monitoring thread
- [ ] Implement timecode extraction for DV
- [ ] Create capture presets for common tape formats

### Phase 3: GUI Refactoring
- [ ] Create modular GUI using new core API
- [ ] Implement capture tab with device selection
- [ ] Add one-click Capture → Process workflow
- [ ] Integrate live capture preview in GUI
- [ ] Add capture history and management

### Phase 4: Advanced Features
- [ ] Scene detection during capture
- [ ] Automatic tape format detection
- [ ] Batch capture from multiple tapes
- [ ] Cloud backup integration
- [ ] Project file format for multi-tape projects

## 🤝 Contributing

This is a modular architecture designed for easy contribution:

1. **Core Processing**: Enhance restoration filters, add new codecs
2. **Capture Module**: Add support for new capture devices, improve detection
3. **GUI**: Improve user experience, add new workflows
4. **Documentation**: Improve guides, add tutorials

Each module is independent - changes to one don't affect others!

## 📄 License

Professional Edition - All Rights Reserved

## 🙏 Acknowledgments

Built on proven v1.0 technology with 2+ years of production testing.

### Core Technologies
- **VapourSynth**: Video processing framework
- **QTGMC**: World-class deinterlacing
- **FFmpeg**: Universal video encoding
- **PySide6**: Modern Qt6 GUI framework

### Key Filters
- BM3D, TComb, Bifrost, RealESRGAN, f3kdb

---

**Version**: 2.0.0-alpha  
**Status**: Active Development  
**Last Updated**: November 2025
