# Advanced Tape Restorer v4.0 - Community Edition - Project Context

## Project Summary
Advanced Tape Restorer Community Edition is a Windows-first desktop application for capture and restoration of analog and DV video using VapourSynth and FFmpeg.

Primary goals:
- Preserve legacy media with practical community workflows
- Keep the user experience simple and reliable
- Maintain clear boundaries between Community Edition and separate commercial offerings

## High-Level Architecture

GUI (PySide6)
    |
    v
Processing Orchestrator (Python)
    |
    +--> VapourSynth (vspipe.exe, external process)
    |
    +--> FFmpeg (capture, encode, metadata)

## Critical Constraint
- VapourSynth always runs in a separate process.
- Processing scripts must resolve required resources from filesystem paths.

## Execution and Packaging
- Distributed as a standalone executable build for Windows.
- Community build artifacts include main_v4.0.spec and Build_v4.0_Community_Edition.ps1.

## Canonical Runtime Areas
Default runtime data can include:
- ai_models/
- temporary processing scripts
- cache and logs

## Threading Model
- UI thread: PySide6 event loop
- Worker thread(s): processing and monitoring
- Cross-thread communication: Qt signals/slots only

## Core Processing Components
### core.py
Includes VideoProcessor, VapourSynthEngine, and FFmpegEncoder integration.

Pipeline behavior:
1. Generate processing script
2. Run vspipe
3. Pipe output to ffmpeg
4. Parse and report progress

Cancellation behavior:
- Coordinated stop path for both vspipe and ffmpeg subprocesses

## AI Model System
- Registry-driven metadata in ai_models/models/registry.yaml
- Model manager handles download/verify/cache behavior
- Engine modules live under ai_models/engines/

## UI and Settings
- Main UI in gui/main_window.py
- Settings persisted and restored via gui/settings_manager.py
- Presets stored in restoration_presets.json

## Hardware Capture
- Capture logic in capture.py
- Device detection and command construction for analog and DV workflows

## Development and Validation
Development run:
```powershell
python main.py
```

Test mode:
```powershell
python main.py --test
```

Manual script validation (when needed):
```powershell
vspipe --info <script>.vpy -
vspipe --y4m <script>.vpy - | ffplay -i -
```

## Documentation Scope
Community Edition repository docs should stay aligned with v4.0 identity and MIT licensing scope.

## Guiding Principle
This is a production-oriented community tool.
If a workflow depends on hidden assumptions or developer-only setup, it is incomplete.

---

Version: 4.0.0
Last Updated: April 2026
Scope: Community Edition (MIT)
