# Advanced Tape Restorer v4.0 - Community Edition - AI Agent Instructions

## Project Overview
Advanced Tape Restorer Community Edition is a professional desktop restoration suite for analog and DV sources.

- GUI: PySide6
- Processing: VapourSynth -> FFmpeg pipeline
- Distribution: standalone Windows-focused build
- License: MIT for this public Community Edition repository

Community Edition scope is intentionally distinct from separate commercial products.

## Critical Execution Model

### VapourSynth External Process Constraint
- VapourSynth runs as a separate process via vspipe.exe
- VapourSynth cannot import from the frozen executable environment
- Models and required assets must be accessible by filesystem path
- Path handling is resolved through core bridge logic

### Threading Architecture
- Main thread: PySide6 GUI
- Worker thread: video processing
- Monitor threads: capture status and preview
- Use Qt signals/slots for cross-thread communication
- Never update GUI widgets directly from worker threads

## Module Responsibilities

### core.py
Primary processing pipeline components:
- VideoProcessor
- VideoAnalyzer
- VapourSynthEngine
- FFmpegEncoder

Responsibilities:
- Build and run vspipe -> ffmpeg pipeline
- Parse encoding progress
- Handle cancellation safely

### capture.py
Capture layer for analog and DV workflows:
- Capture device discovery
- Analog capture command construction
- DV capture command construction

### gui/main_window.py
Main UI host for restoration, capture, and batch workflows.

### ai_models/
Registry-driven AI model management and engine integrations used by Community Edition code paths.

## Build and Run

### Development
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### Test Mode
```powershell
python main.py --test
```

### Community Build Artifacts
- main_v4.0.spec
- Build_v4.0_Community_Edition.ps1

## External Dependencies

Required:
- FFmpeg on PATH (ffmpeg.exe, ffprobe.exe)
- VapourSynth on PATH (vspipe.exe)

Optional:
- Additional plugins/models depending on selected restoration features

## Common Workflows

### Add a Restoration Feature
1. Update VapourSynth script generation in processing engine code.
2. Add/adjust UI controls in the GUI layer.
3. Persist settings through settings manager.
4. Validate generated script and processing execution.

### Debug VapourSynth Scripts
Generated scripts are written to temporary files and can be validated with vspipe.

## Project Conventions

### Error Handling
- Wrap subprocess interactions in try/except
- Report errors through logging callbacks and user-visible UI feedback

### Settings
- Persist and restore settings consistently through settings manager

### Codec Naming
- GUI codec labels include descriptive text; processing extracts the codec token

## Testing
- Primary automated test entry: python main.py --test
- Verify cancellation path, progress updates, and prerequisite checks

## Known Limitations
- Full hardware validation depends on physical capture devices
- Some optional AI paths require separate model/plugin setup

## When Modifying This Codebase
1. Run test mode to verify imports and baseline behavior.
2. Verify generated processing scripts remain valid.
3. Confirm GUI responsiveness during processing.
4. Keep Community Edition messaging and scope consistent.

---

Version: 4.0.0
Last Updated: April 2026
Scope: Community Edition (MIT)
