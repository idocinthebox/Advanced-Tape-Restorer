# Quick Start Guide - Community Edition

This guide covers the public Community Edition repository workflow.

## 1. Prerequisites

- Windows 10 or 11
- FFmpeg installed and available on PATH
- VapourSynth installed and available on PATH
- Python 3.10+ recommended for source workflow

## 2. Clone and Run from Source

```powershell
git clone https://github.com/idocinthebox/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 3. Basic Community Workflow

1. Open the app.
2. Select an input video.
3. Choose restoration settings appropriate for your source.
4. Select output location and output format.
5. Start processing and monitor progress.

## 4. Capture Workflow (if hardware is available)

1. Open the capture section.
2. Refresh/select the video and audio device.
3. Choose input type and output codec.
4. Start capture and verify output file playback.

## 5. Troubleshooting

- If FFmpeg is not detected, verify PATH and restart terminal/app.
- If VapourSynth is not detected, verify installation and plugin environment.
- If processing fails, check console/log output and dependency availability.

## 6. Product-Line Reminder

- This repository is Community Edition (MIT).
- ATR 6.0 Professional is separate.
- LTX Generative Repair is a separate paid add-on for ATR 6.0 Professional.
