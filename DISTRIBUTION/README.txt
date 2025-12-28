================================================================================
  ADVANCED TAPE RESTORER v3.1 - COMPLETE DISTRIBUTION PACKAGE
  Professional Video Restoration & Analog Capture Suite
================================================================================

Version: 3.1.0
Build Date: ~0,8--
Platform: Windows 10/11 (64-bit)

================================================================================
  QUICK START - 3 STEPS TO GET RUNNING
================================================================================

STEP 1: AUTOMATIC INSTALLATION (RECOMMENDED)
-----------------------------------------------
Run: Setup\Install_Prerequisites_Auto.bat

This will automatically download and install:
  - FFmpeg (video encoding)
  - VapourSynth (video processing)
  - VapourSynth plugins (QTGMC, filters)
  - Python (optional, for AI models)

Total download: ~210MB
Time required: 10-15 minutes

STEP 2: RESTART YOUR COMPUTER
-------------------------------
After installation completes, restart Windows
(required for PATH changes to take effect)

STEP 3: LAUNCH THE APPLICATION
--------------------------------
Double-click: Advanced_Tape_Restorer_v3.1.exe

That's it

================================================================================
  ALTERNATIVE: MANUAL INSTALLATION
================================================================================

If automatic installation fails, use manual setup:
  Run: Setup\Install_Prerequisites.bat (guided manual process)

================================================================================
  VERIFY INSTALLATION
================================================================================

After installation and restart, run:
  Setup\Check_Prerequisites.bat

This will verify all components are properly installed.

================================================================================
  OPTIONAL: AI UPSCALING WITH GPU
================================================================================

For RealESRGAN AI upscaling with NVIDIA RTX GPU:
  Run: Setup\Install_PyTorch_CUDA.bat

Requires: NVIDIA RTX 2060 or newer with 6+ GB VRAM

================================================================================
  WHAT'S INCLUDED
================================================================================

Application:
  Advanced_Tape_Restorer_v3.1.exe - Main application ( MB)

Setup Scripts:
  Setup\Install_Prerequisites_Auto.bat - Automatic installer (RECOMMENDED)
  Setup\Install_Prerequisites.bat - Manual guided installation
  Setup\Check_Prerequisites.bat - Verify installation
  Setup\Install_PyTorch_CUDA.bat - Optional GPU acceleration

Documentation:
  QUICK_SETUP.txt - Fast setup reference
  Documentation\PREREQUISITES.md - Detailed prerequisites guide
  Documentation\QUICK_START_GUIDE.md - Getting started guide
  Documentation\README.md - Complete application documentation

Configuration:
  restoration_presets.json - Sample restoration presets
  tape_restorer_config.json - Application configuration

================================================================================
  SYSTEM REQUIREMENTS
================================================================================

MINIMUM:
  - Windows 10/11 (64-bit)
  - Intel Core i5 / AMD Ryzen 5 (4+ cores)
  - 8 GB RAM
  - 100 GB free disk space

RECOMMENDED FOR AI:
  - Intel Core i7/i9 / AMD Ryzen 7/9 (8+ cores)
  - 16-32 GB RAM
  - NVIDIA RTX 3060 or newer (8+ GB VRAM)
  - SSD with 500+ GB free space

================================================================================
  FEATURES
================================================================================

Video Restoration:
  - QTGMC Deinterlacing (7 quality presets)
  - Auto Field Order Detection
  - BM3D Denoising (CPU/GPU)
  - VHS Artifact Removal
  - Color Correction
  - AI Upscaling (RealESRGAN 2x)

Video Capture:
  - Analog capture (VHS, Hi8, Betamax)
  - DV/miniDV FireWire capture
  - Auto device detection
  - Lossless codecs (HuffYUV, FFV1)
  - User-specified output folders

Output Formats:
  - H.264/H.265 (CPU or NVIDIA NVENC)
  - ProRes 422/4444 (professional editing)
  - DNxHD (Avid workflows)
  - FFV1 (lossless archival)
  - AV1 (next-gen compression)

================================================================================
  GETTING HELP
================================================================================

If you encounter issues:
  1. Read: Documentation\PREREQUISITES.md
  2. Run: Setup\Check_Prerequisites.bat
  3. Check: Documentation\README.md for troubleshooting

Common issues are usually fixed by:
  - Restarting computer after installation
  - Running Check_Prerequisites.bat to diagnose
  - Reinstalling missing components

================================================================================
  DEPLOYMENT TO OTHER COMPUTERS
================================================================================

To use on another computer:
  1. Copy this entire folder to the new computer
  2. Run: Setup\Install_Prerequisites_Auto.bat
  3. Restart the computer
  4. Run: Advanced_Tape_Restorer_v3.1.exe

The EXE is portable - no installation needed for the application itself.
Only the external video processing tools (FFmpeg, VapourSynth) need setup.

================================================================================

Build Information:
  Build Date: ~0,4datetime:~4,2datetime:~6,2datetime:~8,2datetime:~10,2
  EXE Size:  MB
  Python Version: Embedded
  PyQt Version: 6.x

Ready for distribution

================================================================================
