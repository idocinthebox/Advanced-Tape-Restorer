================================================================================
  ADVANCED TAPE RESTORER v3.0
  Professional Video Restoration & Capture Suite
================================================================================

Thank you for using Advanced Tape Restorer v3.0!

This professional-grade application helps you preserve your precious memories
by restoring VHS, Hi8, Video8, Betamax, and DV tapes to high-quality digital
video.

================================================================================
  WHAT'S IN THIS PACKAGE
================================================================================

Advanced_Tape_Restorer_v3.exe    Main application (portable executable)

Documentation:
  QUICK_START.txt                Quick start guide (READ THIS FIRST!)
  TROUBLESHOOTING.txt            Solutions to common problems
  USER_GUIDE.pdf                 Complete feature documentation
  CAPTURE_GUIDE.pdf              Capture hardware setup guide
  ARCHITECTURE.md                Technical architecture details
  CHANGELOG.txt                  Version history and updates

Setup Scripts:
  1_Install_VapourSynth.bat      VapourSynth installation helper
  2_Install_FFmpeg.bat           FFmpeg installation helper
  3_Check_Prerequisites.bat      Verify all dependencies installed

License:
  LICENSE.txt                    Software license agreement
  THIRD_PARTY_LICENSES.txt       Open source component licenses

================================================================================
  QUICK START (3 STEPS)
================================================================================

1. Install Dependencies:
   - Run "1_Install_VapourSynth.bat" (video processing framework)
   - Run "2_Install_FFmpeg.bat" (video encoding)

2. Verify Installation:
   - Run "3_Check_Prerequisites.bat"
   - All checks should pass

3. Launch Application:
   - Double-click "Advanced_Tape_Restorer_v3.exe"
   - Select input video → Configure settings → Start processing

See QUICK_START.txt for detailed instructions!

================================================================================
  KEY FEATURES
================================================================================

VIDEO RESTORATION:
  ✓ Professional QTGMC deinterlacing (7 quality presets)
  ✓ Automatic field order detection (TFF/BFF/Progressive)
  ✓ Advanced denoising (BM3D CPU/GPU)
  ✓ VHS artifact removal (combing, chroma noise)
  ✓ AI upscaling (SD → HD → 4K with RealESRGAN)
  ✓ Batch processing queue
  ✓ Multiple codec support (H.264/H.265/ProRes/FFV1)

TAPE CAPTURE:
  ✓ Analog capture (VHS, Hi8, Video8, Betamax, S-VHS)
  ✓ DV/miniDV FireWire capture (IEEE 1394)
  ✓ Lossless codecs (HuffYUV, Lagarith, FFV1, UT Video)
  ✓ User-specified output folder (any drive, any location)
  ✓ Auto-process after capture (optional)
  ✓ DirectShow device detection (Windows)
  ✓ Multiple resolution/framerate presets (NTSC/PAL)
  ✓ Real-time capture monitoring
  ✓ Manual or timed duration control
  ✓ Standard file formats (AVI/MKV) compatible with all video software

WORKFLOW:
  ✓ Save/load restoration presets
  ✓ Persistent batch queue
  ✓ Real-time progress monitoring
  ✓ Detailed logging
  ✓ Professional-grade results

================================================================================
  SYSTEM REQUIREMENTS
================================================================================

MINIMUM:
  - Windows 10 64-bit
  - Intel Core i5 (4 cores)
  - 8 GB RAM
  - 50 GB free disk space

RECOMMENDED:
  - Windows 10/11 64-bit
  - Intel Core i7/i9 (8+ cores) or AMD Ryzen 7/9
  - 16-32 GB RAM
  - 200+ GB free disk space (SSD recommended)
  - NVIDIA GPU (for GPU-accelerated features)

FOR CAPTURE:
  - USB 3.0 port for analog capture devices
  - FireWire (IEEE 1394) port for DV capture

================================================================================
  REQUIRED DEPENDENCIES
================================================================================

These must be installed before running the application:

1. VapourSynth R68+ (64-bit)
   Video processing framework
   https://github.com/vapoursynth/vapoursynth/releases
   
2. FFmpeg (64-bit)
   Video encoding and format conversion
   https://ffmpeg.org/download.html

Both can be installed automatically using the included batch files!

================================================================================
  TYPICAL WORKFLOW
================================================================================

RESTORING OLD VIDEO:
  1. Open Restoration tab
  2. Select input file (your VHS capture or old video)
  3. Select output file (where to save restored video)
  4. Configure settings:
     - Field Order: Auto-Detect
     - QTGMC Preset: Slow (balanced quality/speed)
     - Codec: libx264 (H.264)
     - CRF: 18 (excellent quality)
  5. Click "Start Processing"
  6. Wait for completion (typically 2-4x real-time)

CAPTURING FROM TAPE:
  1. Connect hardware:
     - Analog: USB capture card (Elgato, AVerMedia, Hauppauge, etc.)
     - DV: FireWire cable from camera/deck to PC
  2. Connect tape player to capture device:
     - VHS/Hi8: Composite (RCA) or S-Video cables + audio
     - DV: FireWire cable only (carries video + audio)
  3. Open Capture tab in application
  4. Click "Refresh Devices" to detect hardware
  5. Select device type:
     - "Analog (VHS/Hi8/Video8/Betamax)" for analog sources
     - "DV/miniDV (FireWire)" for digital sources
  6. Choose output folder:
     - Click "Browse..." button
     - Select drive with sufficient free space (100+ GB recommended)
     - External USB 3.0 drive recommended for best performance
  7. Configure capture settings:
     - Resolution: 720x480 (NTSC) or 720x576 (PAL)
     - Frame rate: 29.97 fps (NTSC) or 25 fps (PAL)
     - Codec: HuffYUV (fastest), FFV1 (best compression), or Lagarith
     - Duration: Optional (leave blank for manual stop)
  8. Click "Start Capture"
  9. Press PLAY on tape player
  10. Monitor capture progress in console
  11. Click "Stop Capture" when tape finishes
  12. Files saved to YOUR chosen folder as:
      - capture_YYYYMMDD_HHMMSS.avi (immediately usable)
  13. Optional: Enable "Auto-restore after capture" for automatic processing

CAPTURE OUTPUT:
  - Files saved to user-specified folder (any drive, network paths supported)
  - Standard formats: AVI (HuffYUV/Lagarith), MKV (FFV1), DV (raw stream)
  - Lossless quality: No generation loss, perfect for archival
  - Compatible with: VLC, Premiere Pro, DaVinci Resolve, Final Cut Pro, etc.
  - File sizes:
      * SD analog (HuffYUV): ~60-80 GB/hour
      * SD analog (FFV1): ~40-60 GB/hour
      * DV (copy mode): ~13 GB/hour
  - Files immediately accessible after capture stops

BATCH PROCESSING:
  1. Open Batch tab
  2. Add multiple files to queue
  3. Configure settings for each job
  4. Click "Start Batch Processing"
  5. Let it run (great for overnight processing!)

================================================================================
  SUPPORT & DOCUMENTATION
================================================================================

For help, please consult in this order:

1. QUICK_START.txt - Getting started guide
2. TROUBLESHOOTING.txt - Common issues and solutions
3. USER_GUIDE.pdf - Complete feature documentation
4. last_error_log.txt - Generated when errors occur

================================================================================
  VERSION INFORMATION
================================================================================

Advanced Tape Restorer v3.0.0
Release Date: November 2025
Build: Python 3.13, PySide6 (Qt6), VapourSynth, FFmpeg

Changes from v1.0:
  ✓ Complete modular architecture
  ✓ Added tape capture functionality
  ✓ Improved field order detection
  ✓ Enhanced preset management
  ✓ Better error handling and logging
  ✓ Performance optimizations

See CHANGELOG.txt for complete version history.

================================================================================
  LICENSE
================================================================================

Advanced Tape Restorer v3.0
Copyright (c) 2025 - All Rights Reserved

This is professional software for personal and commercial use.
See LICENSE.txt for complete terms.

Uses open source components:
  - VapourSynth (LGPL)
  - FFmpeg (LGPL/GPL)
  - PySide6/Qt6 (LGPL)
  
See THIRD_PARTY_LICENSES.txt for complete third-party license information.

================================================================================
  CREDITS
================================================================================

Developed by: AI Agent Team
Architecture: Modular Python with PySide6 GUI

Built with:
  - VapourSynth (video processing framework)
  - QTGMC (industry-standard deinterlacing)
  - FFmpeg (universal video encoding)
  - PySide6 (Qt6 GUI framework)
  - Python 3.13

Special thanks to the open source community for VapourSynth, FFmpeg,
and all the amazing filters and plugins that make this possible.

================================================================================

HAPPY RESTORING! 🎬📼

Your memories are precious. We're honored to help you preserve them.

================================================================================
