# Advanced Tape Restorer v2.0 - Architecture Overview

## Design Philosophy

Version 2.0 is built on three core principles:

1. **Modularity**: Each component is self-contained with well-defined interfaces
2. **Testability**: Components can be tested independently without GUI dependencies
3. **Extensibility**: New features can be added without modifying core functionality

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         GUI Layer                           │
│                       (PySide6/Qt6)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │Restoration │  │  Capture   │  │   Batch    │           │
│  │    Tab     │  │    Tab     │  │   Queue    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────┬──────────────┬───────────────────────────────────┘
           │              │
           │              │ API Calls
           │              │
┌──────────▼──────────────▼───────────────────────────────────┐
│                    Application Layer                        │
│         (Workflow Orchestration & State Management)         │
└──────────┬──────────────┬───────────────────────────────────┘
           │              │
           │              │
  ┌────────▼────────┐  ┌──▼──────────────┐
  │                 │  │                  │
  │  Core Module    │  │ Capture Module   │
  │                 │  │                  │
  │ ┌─────────────┐ │  │ ┌──────────────┐│
  │ │  Processor  │ │  │ │   Device     ││
  │ │             │ │  │ │   Manager    ││
  │ └─────────────┘ │  │ └──────────────┘│
  │                 │  │                  │
  │ ┌─────────────┐ │  │ ┌──────────────┐│
  │ │   Video     │ │  │ │   Analog     ││
  │ │  Analyzer   │ │  │ │   Capture    ││
  │ └─────────────┘ │  │ └──────────────┘│
  │                 │  │                  │
  │ ┌─────────────┐ │  │ ┌──────────────┐│
  │ │VapourSynth  │ │  │ │     DV       ││
  │ │   Engine    │ │  │ │   Capture    ││
  │ └─────────────┘ │  │ └──────────────┘│
  │                 │  │                  │
  │ ┌─────────────┐ │  │                  │
  │ │   FFmpeg    │ │  │                  │
  │ │   Encoder   │ │  │                  │
  │ └─────────────┘ │  │                  │
  └─────────────────┘  └──────────────────┘
           │                    │
           │                    │
  ┌────────▼────────────────────▼─────────┐
  │       External Dependencies           │
  │  ┌──────┐  ┌───────┐  ┌──────────┐   │
  │  │FFmpeg│  │vspipe │  │DirectShow│   │
  │  └──────┘  └───────┘  └──────────┘   │
  └───────────────────────────────────────┘
```

## Data Flow

### Restoration Workflow
```
Input Video
    │
    ▼
VideoAnalyzer.get_video_info()
    │ (width, height, fps, codec)
    ▼
VideoAnalyzer.detect_field_order()  [if Auto-Detect]
    │ (TFF/BFF/Progressive)
    ▼
VapourSynthEngine.create_script()
    │ (generates .vpy restoration script)
    ▼
VapourSynthEngine.get_total_frames()
    │ (total frame count)
    ▼
vspipe subprocess
    │ (Y4M stream via stdout)
    ▼
FFmpegEncoder.encode()
    │ (encoding with progress callbacks)
    │
    ├─► progress_callback(percent, eta)
    └─► log_callback(message)
    │
    ▼
Output Video
```

### Capture Workflow
```
CaptureDeviceManager.refresh_devices()
    │ (detect available capture devices)
    ▼
User Selects Device
    │
    ▼
AnalogCaptureEngine.start_capture()  OR  DVCaptureEngine.start_capture()
    │ (FFmpeg DirectShow capture)
    │
    ├─► log_callback(status_message)
    └─► [monitor capture progress]
    │
    ▼
User Stops Capture
    │
    ▼
AnalogCaptureEngine.stop_capture()
    │
    ▼
Captured Video File
    │
    ▼
[Optional] VideoProcessor.process_video()
    │
    ▼
Restored Output
```

## Module Interfaces

### Core Module API

#### VideoProcessor
**Purpose**: Main orchestrator for video restoration pipeline

**Public Methods**:
```python
check_prerequisites() -> None
    """Verify FFmpeg, VapourSynth, vspipe are installed"""
    Raises: RuntimeError if tools missing

process_video(
    input_file: str,
    output_file: str,
    options: Dict,
    progress_callback: Callable[[float, str], None],
    log_callback: Callable[[str], None]
) -> bool
    """Process video with restoration filters"""
    Returns: True if successful

get_video_info(input_file: str) -> Dict
    """Get comprehensive video metadata"""
    Returns: {width, height, par, fps, codec_name, etc.}

request_stop() -> None
    """Cancel ongoing processing"""

cleanup() -> None
    """Clean up processes and temp files"""
```

**Dependencies**:
- VideoAnalyzer: Metadata extraction
- VapourSynthEngine: Script generation
- FFmpegEncoder: Video encoding
- subprocess: External tool execution

#### VideoAnalyzer
**Purpose**: Extract metadata and detect field order

**Public Methods**:
```python
get_video_info(input_file: str) -> Tuple[int, int, str, int, float]
    """Get basic video info via ffprobe"""
    Returns: (width, height, PAR, frame_count, fps)

detect_field_order(
    input_file: str,
    probe_frames: int = 900,
    prog_dom_ratio: float = 1.5,
    prog_min: int = 150,
    field_dom_ratio: float = 1.3,
    field_min: int = 80,
    field_fallback_min: int = 200
) -> str
    """Auto-detect field order using FFmpeg idet"""
    Returns: 'TFF (Top Field First)' | 'BFF (Bottom Field First)' | 'Disabled (Progressive)'

get_codec_info(input_file: str) -> Dict
    """Get codec details"""
    Returns: {codec_name, codec_long_name, pix_fmt}
```

**Dependencies**:
- subprocess: Execute ffprobe/ffmpeg
- json: Parse ffprobe output
- re: Parse idet statistics

#### VapourSynthEngine
**Purpose**: Generate VapourSynth restoration scripts

**Public Methods**:
```python
create_script(input_file: str, options: Dict) -> None
    """Generate VapourSynth script from options"""
    Creates: temp_restoration_script.vpy

get_total_frames() -> int
    """Get frame count from generated script"""
    Returns: Total frames or 0 if error

cleanup() -> None
    """Remove generated script file"""
```

**Script Generation Logic**:
- Source filter selection (Auto/bestsource/lsmas/ffms2)
- Cropping
- QTGMC deinterlacing (7 presets)
- Denoising (BM3D CPU/GPU)
- Artifact removal (TComb/Bifrost)
- Additional filters (debanding, etc.)
- Frame rate handling
- AI upscaling (RealESRGAN)

**Dependencies**:
- os: File operations
- subprocess: Execute vspipe

#### FFmpegEncoder
**Purpose**: Encode video with multiple codec support

**Public Methods**:
```python
build_command(
    input_source: str,
    output_file: str,
    options: Dict,
    pipe_input: bool = True
) -> list
    """Build FFmpeg command from options"""
    Returns: Command as list of arguments

encode(
    vspipe_process: subprocess.Popen,
    output_file: str,
    options: Dict,
    total_frames: int,
    progress_callback: Callable,
    log_callback: Callable
) -> bool
    """Encode video from vspipe output"""
    Returns: True if successful

cleanup() -> None
    """Terminate FFmpeg process"""
```

**Supported Codecs**:
- H.264: libx264, h264_nvenc
- H.265: libx265, hevc_nvenc
- AV1: libsvtav1
- ProRes: All 6 variants (4444 XQ, 4444, 422 HQ, 422, LT, Proxy)
- DNxHD: 175 Mbps
- FFV1: Lossless

**Dependencies**:
- subprocess: Execute FFmpeg
- re: Parse progress output
- Path: File operations

### Capture Module API

#### CaptureDeviceManager
**Purpose**: Detect and manage video capture devices

**Public Methods**:
```python
refresh_devices() -> List[CaptureDevice]
    """Scan for available capture devices"""
    Returns: List of detected devices

get_device_by_index(index: int) -> Optional[CaptureDevice]
    """Get specific device"""
    Returns: CaptureDevice or None

get_analog_devices() -> List[CaptureDevice]
    """Get all analog capture cards"""

get_dv_devices() -> List[CaptureDevice]
    """Get all DV/FireWire devices"""
```

**Device Detection**:
- Windows: DirectShow via FFmpeg
- macOS: AVFoundation (planned)
- Linux: Video4Linux2 (planned)

**Device Types**:
- analog: VHS, Hi8, Video8, Betamax
- dv: DV, miniDV, HDV via FireWire
- hdmi: HDMI capture cards
- webcam: USB cameras (filtered out)

#### AnalogCaptureEngine
**Purpose**: Capture from analog sources

**Public Methods**:
```python
start_capture(
    settings: AnalogCaptureSettings,
    output_file: str,
    log_callback: Callable
) -> bool
    """Start analog capture"""
    Returns: True if started successfully

stop_capture(log_callback: Callable) -> bool
    """Stop ongoing capture"""
    Returns: True if stopped successfully

get_capture_stats() -> Optional[Dict]
    """Get current capture statistics"""
    Returns: {status, frames, duration} or None
```

**AnalogCaptureSettings**:
```python
@dataclass
class AnalogCaptureSettings:
    device_name: str
    resolution: str = "720x480"  # NTSC
    framerate: str = "29.97"
    codec: str = "huffyuv"
    pixel_format: str = "yuv422p"
    audio_device: Optional[str] = None
    audio_channels: int = 2
    duration: Optional[int] = None  # None = manual stop
```

**Supported Codecs**:
- huffyuv: HuffYUV lossless
- lagarith: Lagarith lossless
- ffv1: FFV1 lossless (MKV)
- utvideo: UT Video lossless

#### DVCaptureEngine
**Purpose**: Capture from DV/miniDV sources

**Public Methods**:
```python
start_capture(
    settings: DVCaptureSettings,
    output_file: str,
    log_callback: Callable
) -> bool
    """Start DV capture"""

stop_capture(log_callback: Callable) -> bool
    """Stop DV capture"""

get_timecode() -> Optional[str]
    """Get current DV timecode"""
    Returns: "HH:MM:SS:FF" or None

detect_format(device_name: str) -> str
    """Auto-detect DV vs HDV"""
    Returns: 'dv' | 'hdv'
```

**DVCaptureSettings**:
```python
@dataclass
class DVCaptureSettings:
    device_name: str
    format: str = "dv"  # 'dv' or 'hdv'
    codec: str = "copy"  # 'copy' or 'huffyuv'
    duration: Optional[int] = None
```

## Threading Model

### Core Module Threading
- **Main Thread**: GUI event loop
- **ProcessingThread**: Video processing (QThread)
  - Spawns: vspipe subprocess
  - Spawns: FFmpeg subprocess
  - Optional: Preview extraction subprocess

### Capture Module Threading
- **Main Thread**: GUI event loop
- **CaptureThread**: Capture monitoring (planned)
  - Spawns: FFmpeg capture subprocess
  - Monitors: Progress and statistics

## Error Handling

### Core Module
- **Prerequisites Check**: RuntimeError if tools missing
- **Script Generation**: RuntimeError if write fails
- **Frame Count**: Returns 0 on error (non-fatal)
- **Encoding**: Returns False on failure

### Capture Module
- **Device Detection**: Returns empty list on error
- **Capture Start**: Returns False if failed
- **Capture Stop**: Returns False if failed

## Configuration Management

### Settings Files (JSON)
- `tape_restoration_settings.json`: User preferences
- `restoration_presets.json`: Named restoration presets
- `batch_queue.json`: Pending batch jobs
- `processing_stats.json`: Historical processing times

### Default Settings
```python
DEFAULT_SETTINGS = {
    # Field Order & Deinterlacing
    'field_order': 'Auto-Detect',
    'qtgmc_preset': 'Slow',
    'frame_rate': 'Double (Default)',
    
    # Source
    'source_filter': 'Auto',
    
    # Restoration
    'denoise_strength': 'None',
    'remove_artifacts': False,
    'use_ai_upscaling': False,
    
    # Encoding
    'codec': 'libx264 (H.264, CPU)',
    'crf': '18',
    'ffmpeg_preset': 'slow',
    'audio': 'Copy Audio',
    
    # Detection Thresholds
    'idet_probe_frames': 900,
    'idet_prog_dom_ratio': 1.5,
    'idet_prog_min': 150,
    'idet_field_dom_ratio': 1.3,
    'idet_field_min': 80
}
```

## Testing Strategy

### Unit Testing
```python
# Test VideoAnalyzer
def test_video_info():
    analyzer = VideoAnalyzer()
    width, height, par, frames, fps = analyzer.get_video_info("test.avi")
    assert width > 0 and height > 0

# Test VapourSynthEngine
def test_script_generation():
    engine = VapourSynthEngine()
    engine.create_script("test.avi", options)
    assert os.path.exists(engine.script_file)
    engine.cleanup()

# Test CaptureDeviceManager
def test_device_detection():
    manager = CaptureDeviceManager()
    devices = manager.refresh_devices()
    assert isinstance(devices, list)
```

### Integration Testing
```python
# Test full restoration pipeline
def test_full_restoration():
    processor = VideoProcessor()
    success = processor.process_video(
        "test_input.avi",
        "test_output.mp4",
        options
    )
    assert success
    assert os.path.exists("test_output.mp4")
```

## Performance Considerations

### Processing Optimization
- **CPU Threading**: Limited to 8 threads for VapourSynth stability
- **Buffer Sizes**: 10MB buffers for vspipe/FFmpeg pipes
- **Progress Updates**: Throttled to prevent UI freeze

### Memory Management
- **Stream Processing**: No full video loading into memory
- **Temp Files**: Cleaned up automatically on exit
- **Process Cleanup**: Proper subprocess termination

## Security Considerations

### Input Validation
- File paths: Validated before subprocess execution
- User inputs: Integers validated via try-except
- Options dict: Type checking on critical values

### Subprocess Safety
- **Shell Injection**: All subprocess calls use list format (no shell=True)
- **Path Traversal**: Input/output paths validated
- **Process Limits**: Timeouts on long-running operations

## Future Enhancements

### Planned Features
1. **Multi-threaded Batch Processing**: Process multiple files simultaneously
2. **GPU Acceleration**: Utilize CUDA/OpenCL for filters
3. **Cloud Integration**: Upload/download from cloud storage
4. **Machine Learning**: Auto-detect optimal restoration settings
5. **Project Files**: Save/load multi-tape restoration projects

### API Extensions
- **Plugin System**: Allow custom VapourSynth filter plugins
- **Custom Codecs**: User-defined FFmpeg encoder presets
- **Event Hooks**: Pre/post processing callbacks
- **Metrics Collection**: Detailed processing statistics

---

**Last Updated**: November 2025  
**Maintainer**: AI Agent Team
