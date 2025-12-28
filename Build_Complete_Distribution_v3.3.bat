@echo off
REM ================================================================================
REM  Advanced Tape Restorer v3.3 - Complete Distribution Builder
REM  Creates production-ready release package with all documentation and setup files
REM ================================================================================

setlocal enabledelayedexpansion

set VERSION=3.3
set DIST_NAME=Advanced_Tape_Restorer_v3.3_Release
set DIST_DIR=dist_package\%DIST_NAME%
set SRC_DIR=%~dp0

color 0A
cls
echo.
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - DISTRIBUTION BUILDER
echo ================================================================================
echo.
echo This will create a complete distribution package including:
echo   - Compiled EXE (PyInstaller)
echo   - All documentation (25+ files)
echo   - Setup scripts and installers
echo   - Configuration templates
echo   - Quick start guides
echo   - Uninstall instructions
echo.
echo ================================================================================
echo.
pause

echo.
echo [1/8] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist dist_package\%DIST_NAME% rmdir /s /q dist_package\%DIST_NAME%
echo       Done.

echo.
echo [2/8] Building EXE with PyInstaller...
echo       This may take 2-5 minutes...
python -m PyInstaller --onefile --windowed --name "Advanced_Tape_Restorer_v%VERSION%" ^
    --icon=app_icon_multi_res.ico ^
    --add-data "ai_models/models/registry.yaml;ai_models/models" ^
    --hidden-import=PySide6 ^
    --hidden-import=vapoursynth ^
    --hidden-import=havsfunc ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)
echo       Done.

echo.
echo [3/8] Creating distribution folder structure...
mkdir %DIST_DIR%
mkdir %DIST_DIR%\Documentation
mkdir %DIST_DIR%\Setup
mkdir %DIST_DIR%\Config
mkdir %DIST_DIR%\Examples
echo       Done.

echo.
echo [4/8] Copying main executable...
copy dist\Advanced_Tape_Restorer_v%VERSION%.exe %DIST_DIR%\Advanced_Tape_Restorer_v%VERSION%.exe
echo       Done.

echo.
echo [5/8] Copying configuration files...
copy restoration_presets.json %DIST_DIR%\Config\
copy restoration_settings.json %DIST_DIR%\Config\
if exist tape_restorer_config.json copy tape_restorer_config.json %DIST_DIR%\Config\
echo       Done.

echo.
echo [6/8] Copying documentation files...
REM Main documentation
copy README.md %DIST_DIR%\README.txt
copy QUICK_START_GUIDE.md %DIST_DIR%\QUICK_START_GUIDE.txt
copy CHANGELOG.txt %DIST_DIR%\CHANGELOG.txt

REM Feature documentation
copy GPU_MEMORY_OPTIMIZATION_SUMMARY.md %DIST_DIR%\Documentation\GPU_Memory_Guide.txt
copy GPU_MEMORY_QUICK_REFERENCE.md %DIST_DIR%\Documentation\GPU_Quick_Reference.txt
copy EDITABLE_PATHS_QUICK_GUIDE.md %DIST_DIR%\Documentation\Editable_File_Paths.txt
copy PERFORMANCE_GUIDE.md %DIST_DIR%\Documentation\Performance_Guide.txt 2>nul

REM Technical documentation
copy PROJECT_SUMMARY.md %DIST_DIR%\Documentation\Project_Overview.txt
copy V3_INTEGRATION_COMPLETE.md %DIST_DIR%\Documentation\AI_Integration_Guide.txt
copy PROPAINTER_INTEGRATION_COMPLETE.md %DIST_DIR%\Documentation\ProPainter_Guide.txt 2>nul

REM API documentation
if exist docs xcopy docs %DIST_DIR%\Documentation\API /E /I /Y

echo       Done.

echo.
echo [7/8] Copying setup scripts...
xcopy DISTRIBUTION\Setup\*.bat %DIST_DIR%\Setup\ /Y
copy DISTRIBUTION\FIRST_TIME_SETUP.bat %DIST_DIR%\

REM Create setup shortcuts
echo @echo off > %DIST_DIR%\Setup\1_Check_Prerequisites.bat
echo cd /d "%%~dp0" >> %DIST_DIR%\Setup\1_Check_Prerequisites.bat
echo call Check_Prerequisites.bat >> %DIST_DIR%\Setup\1_Check_Prerequisites.bat
echo pause >> %DIST_DIR%\Setup\1_Check_Prerequisites.bat

echo @echo off > %DIST_DIR%\Setup\2_Install_All_Prerequisites.bat
echo cd /d "%%~dp0" >> %DIST_DIR%\Setup\2_Install_All_Prerequisites.bat
echo call Install_Prerequisites_Auto.bat >> %DIST_DIR%\Setup\2_Install_All_Prerequisites.bat
echo pause >> %DIST_DIR%\Setup\2_Install_All_Prerequisites.bat

echo @echo off > %DIST_DIR%\Setup\3_Install_GPU_Support.bat
echo cd /d "%%~dp0" >> %DIST_DIR%\Setup\3_Install_GPU_Support.bat
echo call Install_PyTorch_CUDA.bat >> %DIST_DIR%\Setup\3_Install_GPU_Support.bat
echo pause >> %DIST_DIR%\Setup\3_Install_GPU_Support.bat

echo       Done.

echo.
echo [8/8] Creating user documentation files...
call :CREATE_INSTALLATION_GUIDE
call :CREATE_UNINSTALL_GUIDE
call :CREATE_QUICK_START
call :CREATE_TROUBLESHOOTING
call :CREATE_PACKAGE_INFO
echo       Done.

echo.
echo ================================================================================
echo   BUILD COMPLETE!
echo ================================================================================
echo.
echo Distribution package created at:
echo   %DIST_DIR%
echo.
echo Package contents:
dir /b %DIST_DIR%
echo.
echo Package size:
powershell -Command "'{0:N2} MB' -f ((Get-ChildItem '%DIST_DIR%' -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB)"
echo.
echo Ready to distribute!
echo ================================================================================
echo.
pause
exit /b 0

REM ================================================================================
REM  Documentation Creation Functions
REM ================================================================================

:CREATE_INSTALLATION_GUIDE
(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - INSTALLATION GUIDE
echo ================================================================================
echo.
echo SYSTEM REQUIREMENTS
echo -------------------
echo   - Windows 10/11 ^(64-bit^)
echo   - 8 GB RAM minimum ^(16 GB recommended^)
echo   - 2 GB free disk space
echo   - NVIDIA RTX GPU ^(optional, for AI features^)
echo.
echo.
echo FIRST-TIME INSTALLATION ^(Virgin System^)
echo ========================================
echo.
echo STEP 1: Check Prerequisites
echo ----------------------------
echo   Run: Setup\1_Check_Prerequisites.bat
echo.
echo   This will verify your system has:
echo     - FFmpeg ^(video encoding^)
echo     - VapourSynth R65+ ^(video processing^)
echo     - Python 3.8+ ^(for plugins^)
echo.
echo   If anything is missing, continue to Step 2.
echo.
echo.
echo STEP 2: Install All Prerequisites ^(REQUIRED^)
echo ----------------------------------------------
echo   Run: Setup\2_Install_All_Prerequisites.bat
echo.
echo   This will automatically install:
echo     [√] FFmpeg 6.0+ with full codec support
echo     [√] VapourSynth R73 ^(R65-R73 compatible^)
echo     [√] VapourSynth plugins: QTGMC, BM3D, filters
echo.
echo   Download size: ~180 MB
echo   Installation time: 5-10 minutes
echo.
echo   **IMPORTANT**: RESTART YOUR COMPUTER after this step!
echo                  PATH environment changes require a restart.
echo.
echo.
echo STEP 3: Install GPU Support ^(OPTIONAL^)
echo ----------------------------------------
echo   Run: Setup\3_Install_GPU_Support.bat
echo.
echo   Only needed if you have an NVIDIA RTX GPU and want:
echo     - AI upscaling ^(RealESRGAN^)
echo     - AI interpolation ^(RIFE^)
echo     - GPU-accelerated BM3D denoising
echo.
echo   Requirements:
echo     - NVIDIA RTX 2060 or newer
echo     - 8 GB VRAM minimum
echo     - CUDA 11.8 or 12.1
echo.
echo   Download size: ~2.5 GB ^(PyTorch + CUDA^)
echo   Installation time: 10-20 minutes
echo.
echo.
echo STEP 4: Launch Application
echo ---------------------------
echo   Double-click: Advanced_Tape_Restorer_v%VERSION%.exe
echo.
echo   First launch will:
echo     - Create configuration files
echo     - Extract AI model registry
echo     - Initialize performance monitor
echo.
echo   Time: 5-10 seconds
echo.
echo.
echo STEP 5: Test Basic Functionality
echo ---------------------------------
echo   1. Click "Browse" to select a test video
echo   2. Choose output location
echo   3. Select "Quick Preview" preset
echo   4. Click "Start Processing"
echo.
echo   If successful, you're ready to restore videos!
echo.
echo.
echo ================================================================================
echo.
echo UPGRADE FROM PREVIOUS VERSION
echo ==============================
echo.
echo If you already have v2.0 or v3.0-3.2 installed:
echo.
echo   1. Copy your old settings:
echo      - restoration_settings.json
echo      - restoration_presets.json ^(if custom^)
echo.
echo   2. No need to reinstall FFmpeg/VapourSynth
echo.
echo   3. GPU support ^(PyTorch^) carries over
echo.
echo   4. Run the new EXE - settings auto-migrate
echo.
echo.
echo ================================================================================
echo.
echo TROUBLESHOOTING
echo ===============
echo.
echo "vspipe not found" error:
echo   → Run Step 2 again to install VapourSynth
echo   → RESTART computer after installation
echo   → Verify: Open CMD and type "vspipe --version"
echo.
echo "FFmpeg not found" error:
echo   → Run Step 2 again to install FFmpeg
echo   → RESTART computer
echo   → Verify: Open CMD and type "ffmpeg -version"
echo.
echo GPU features not working:
echo   → Check GPU: Open CMD and type "nvidia-smi"
echo   → Reinstall: Run Setup\3_Install_GPU_Support.bat
echo   → Update NVIDIA drivers to latest version
echo.
echo Processing very slow:
echo   → Use "Fast" or "Medium" QTGMC preset
echo   → Disable AI features for testing
echo   → Check CPU usage in Task Manager
echo.
echo Out of memory errors:
echo   → Lower output resolution
echo   → Disable RIFE interpolation
echo   → Use ZNEDI3 instead of RealESRGAN
echo   → See: Documentation\GPU_Quick_Reference.txt
echo.
echo.
echo For detailed troubleshooting, see: TROUBLESHOOTING.txt
echo.
echo ================================================================================
) > %DIST_DIR%\INSTALLATION_GUIDE.txt
exit /b

:CREATE_UNINSTALL_GUIDE
(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - COMPLETE UNINSTALL GUIDE
echo ================================================================================
echo.
echo This guide shows how to completely remove Advanced Tape Restorer and all
echo prerequisites from your system.
echo.
echo.
echo UNINSTALL ORDER
echo ===============
echo.
echo Follow these steps in order for complete removal:
echo.
echo   [1] Remove Advanced Tape Restorer
echo   [2] Uninstall VapourSynth
echo   [3] Uninstall FFmpeg
echo   [4] Remove PyTorch/CUDA ^(optional^)
echo   [5] Clean up configuration files
echo   [6] Remove environment variables
echo.
echo.
echo ================================================================================
echo.
echo [STEP 1] REMOVE ADVANCED TAPE RESTORER
echo ================================================================================
echo.
echo 1.1 Delete Application Folder
echo ------------------------------
echo   - Delete the folder containing Advanced_Tape_Restorer_v%VERSION%.exe
echo   - This removes the application and documentation
echo.
echo 1.2 Delete Configuration Files
echo -------------------------------
echo   Location: %%LOCALAPPDATA%%\Advanced_Tape_Restorer
echo   Full path: C:\Users\^<YourName^>\AppData\Local\Advanced_Tape_Restorer
echo.
echo   Contains:
echo     - restoration_settings.json
echo     - restoration_presets.json
echo     - ai_models\ ^(downloaded AI models^)
echo     - debug logs
echo.
echo   To delete:
echo     1. Press Win+R
echo     2. Type: %%LOCALAPPDATA%%\Advanced_Tape_Restorer
echo     3. Delete the entire folder
echo.
echo.
echo ================================================================================
echo.
echo [STEP 2] UNINSTALL VAPOURSYNTH
echo ================================================================================
echo.
echo 2.1 Uninstall via Windows Settings
echo -----------------------------------
echo   Method 1 ^(Windows 11^):
echo     1. Settings → Apps → Installed apps
echo     2. Search for "VapourSynth"
echo     3. Click "..." → Uninstall
echo.
echo   Method 2 ^(Windows 10^):
echo     1. Settings → Apps → Apps ^& features
echo     2. Search for "VapourSynth"
echo     3. Click → Uninstall
echo.
echo   Method 3 ^(Control Panel^):
echo     1. Control Panel → Programs → Uninstall a program
echo     2. Find "VapourSynth R73" ^(or R65-R72^)
echo     3. Right-click → Uninstall
echo.
echo 2.2 Delete VapourSynth Folders
echo -------------------------------
echo   These folders may remain after uninstall:
echo.
echo   Program Files:
echo     C:\Program Files\VapourSynth\
echo.
echo   User AppData:
echo     C:\Users\^<YourName^>\AppData\Roaming\VapourSynth\
echo.
echo   Python site-packages:
echo     C:\Python3X\Lib\site-packages\vapoursynth\
echo.
echo   Delete these manually if they exist.
echo.
echo 2.3 Remove VapourSynth Plugins
echo -------------------------------
echo   Location: %%APPDATA%%\VapourSynth\plugins64\
echo.
echo   Contains:
echo     - QTGMC
echo     - BM3D / BM3DCUDA
echo     - ZNEDI3
echo     - Other plugins
echo.
echo   To delete:
echo     1. Press Win+R
echo     2. Type: %%APPDATA%%\VapourSynth
echo     3. Delete the entire folder
echo.
echo.
echo ================================================================================
echo.
echo [STEP 3] UNINSTALL FFMPEG
echo ================================================================================
echo.
echo FFmpeg is typically installed as a portable tool, not via installer.
echo.
echo 3.1 Locate FFmpeg Installation
echo -------------------------------
echo   Common locations:
echo     - C:\ffmpeg\
echo     - C:\Program Files\ffmpeg\
echo     - C:\Users\^<YourName^>\ffmpeg\
echo.
echo   To find it:
echo     1. Open Command Prompt
echo     2. Type: where ffmpeg
echo     3. Note the folder path
echo.
echo 3.2 Delete FFmpeg Folder
echo -------------------------
echo   Delete the entire ffmpeg folder found in Step 3.1
echo.
echo 3.3 Remove from PATH Environment Variable
echo ------------------------------------------
echo   1. Press Win+R, type: sysdm.cpl
echo   2. Click "Advanced" tab → "Environment Variables"
echo   3. Under "System variables", select "Path" → "Edit"
echo   4. Find entries containing "ffmpeg"
echo   5. Select each → "Delete"
echo   6. Click "OK" on all dialogs
echo.
echo 3.4 Verify Removal
echo -------------------
echo   1. Open NEW Command Prompt window
echo   2. Type: ffmpeg -version
echo   3. Should get: "not recognized as an internal or external command"
echo.
echo.
echo ================================================================================
echo.
echo [STEP 4] REMOVE PYTORCH/CUDA ^(OPTIONAL^)
echo ================================================================================
echo.
echo Only needed if you installed GPU support.
echo.
echo 4.1 Uninstall PyTorch via pip
echo ------------------------------
echo   1. Open Command Prompt as Administrator
echo   2. Run these commands:
echo.
echo      pip uninstall torch torchvision torchaudio -y
echo      pip uninstall numpy -y
echo.
echo 4.2 Delete PyTorch Cache
echo -------------------------
echo   Location: %%LOCALAPPDATA%%\torch
echo   Full path: C:\Users\^<YourName^>\AppData\Local\torch
echo.
echo   Contains:
echo     - Downloaded models
echo     - CUDA kernels
echo     - Cache files
echo.
echo   To delete:
echo     1. Press Win+R
echo     2. Type: %%LOCALAPPDATA%%
echo     3. Delete "torch" folder
echo.
echo 4.3 Uninstall CUDA Toolkit ^(OPTIONAL^)
echo ----------------------------------------
echo   Only if you installed CUDA specifically for this app.
echo.
echo   1. Control Panel → Programs → Uninstall a program
echo   2. Find "NVIDIA CUDA Toolkit 11.8" ^(or 12.1^)
echo   3. Right-click → Uninstall
echo.
echo   **WARNING**: Don't uninstall if other programs use CUDA!
echo.
echo.
echo ================================================================================
echo.
echo [STEP 5] CLEAN UP TEMP FILES
echo ================================================================================
echo.
echo 5.1 Delete Temporary VapourSynth Scripts
echo -----------------------------------------
echo   Location: %%TEMP%%\tape_restorer_*.vpy
echo   Full path: C:\Users\^<YourName^>\AppData\Local\Temp\
echo.
echo   To delete:
echo     1. Press Win+R
echo     2. Type: %%TEMP%%
echo     3. Search for files starting with "tape_restorer"
echo     4. Delete all found files
echo.
echo 5.2 Clear Python __pycache__
echo -----------------------------
echo   If you have Python installed:
echo.
echo   Run in Command Prompt:
echo     del /s /q __pycache__
echo.
echo.
echo ================================================================================
echo.
echo [STEP 6] REMOVE ENVIRONMENT VARIABLES ^(OPTIONAL^)
echo ================================================================================
echo.
echo Check for leftover environment variables:
echo.
echo 1. Press Win+R, type: sysdm.cpl
echo 2. "Advanced" tab → "Environment Variables"
echo 3. Check both "User variables" and "System variables"
echo 4. Remove any containing:
echo    - VAPOURSYNTH
echo    - FFMPEG
echo    - TORCH
echo    - CUDA ^(only if you don't need CUDA for other apps^)
echo.
echo.
echo ================================================================================
echo.
echo [STEP 7] VERIFY COMPLETE REMOVAL
echo ================================================================================
echo.
echo Open a NEW Command Prompt and test:
echo.
echo   Test VapourSynth:
echo     vspipe --version
echo     → Should get: "not recognized..."
echo.
echo   Test FFmpeg:
echo     ffmpeg -version
echo     → Should get: "not recognized..."
echo.
echo   Test PyTorch:
echo     python -c "import torch"
echo     → Should get: "No module named 'torch'"
echo.
echo If all three fail as expected, removal is complete!
echo.
echo.
echo ================================================================================
echo.
echo KEEP VS. REMOVE DECISION TREE
echo ==============================
echo.
echo VapourSynth:
echo   REMOVE if: Only used for tape restoration
echo   KEEP if: Used for other video editing projects
echo.
echo FFmpeg:
echo   REMOVE if: Only used for tape restoration
echo   KEEP if: Used for video conversion, OBS, other tools
echo   NOTE: Many applications depend on FFmpeg!
echo.
echo PyTorch/CUDA:
echo   REMOVE if: Only installed for AI upscaling
echo   KEEP if: Used for machine learning, AI projects
echo   KEEP if: Other apps need CUDA ^(gaming, 3D, video editing^)
echo.
echo Python:
echo   REMOVE if: Only installed for VapourSynth plugins
echo   KEEP if: Used for programming or other scripts
echo.
echo.
echo ================================================================================
echo.
echo QUICK UNINSTALL SCRIPT
echo =======================
echo.
echo For fastest removal, run these commands in Administrator Command Prompt:
echo.
echo   REM Uninstall PyTorch
echo   pip uninstall torch torchvision torchaudio -y
echo.
echo   REM Remove app config
echo   rmdir /s /q "%%LOCALAPPDATA%%\Advanced_Tape_Restorer"
echo.
echo   REM Remove VapourSynth config
echo   rmdir /s /q "%%APPDATA%%\VapourSynth"
echo.
echo   REM Remove PyTorch cache
echo   rmdir /s /q "%%LOCALAPPDATA%%\torch"
echo.
echo   REM Clean temp files
echo   del /q "%%TEMP%%\tape_restorer_*.vpy"
echo.
echo Then uninstall VapourSynth and delete FFmpeg folder manually.
echo.
echo.
echo ================================================================================
echo.
echo TROUBLESHOOTING UNINSTALL
echo ==========================
echo.
echo "Access Denied" errors:
echo   → Run Command Prompt as Administrator
echo   → Close all programs that might use these files
echo   → Restart computer and try again
echo.
echo Files won't delete:
echo   → Use Windows Safe Mode
echo   → Use third-party uninstaller ^(Revo Uninstaller, etc.^)
echo.
echo PATH still shows removed programs:
echo   → Restart computer ^(changes take effect after reboot^)
echo   → Open NEW Command Prompt to test
echo.
echo.
echo ================================================================================
echo   UNINSTALLATION COMPLETE
echo ================================================================================
echo.
echo Your system is now clean of all Advanced Tape Restorer components.
echo.
echo If you reinstall later, you'll need to run the setup scripts again.
echo.
echo Thank you for using Advanced Tape Restorer!
echo.
echo ================================================================================
) > %DIST_DIR%\UNINSTALL_GUIDE.txt
exit /b

:CREATE_QUICK_START
(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - QUICK START
echo ================================================================================
echo.
echo NEW USER? START HERE!
echo =====================
echo.
echo 1. FIRST-TIME SETUP ^(5-15 minutes^)
echo    └─→ Run: FIRST_TIME_SETUP.bat
echo        - Installs FFmpeg, VapourSynth, plugins
echo        - **RESTART COMPUTER** after installation
echo.
echo 2. LAUNCH APPLICATION
echo    └─→ Double-click: Advanced_Tape_Restorer_v%VERSION%.exe
echo.
echo 3. QUICK TEST
echo    └─→ Select test video → Choose output → Click "Start Processing"
echo.
echo.
echo ================================================================================
echo.
echo BASIC WORKFLOW
echo ==============
echo.
echo [INPUT] Select Video
echo   → Click "Browse" next to "Input File"
echo   → Choose your VHS/tape capture file
echo   → Supports: AVI, MP4, MKV, MTS, M2TS
echo.
echo [OUTPUT] Choose Destination
echo   → Click "Browse" next to "Output File"
echo   → Name your restored video
echo   → Default: input_name_restored.mp4
echo.
echo [PRESET] Select Quality
echo   → Dropdown: Choose restoration preset
echo   → Recommended for beginners: "Standard Quality"
echo   → For best quality: "Maximum Quality"
echo   → For speed: "Quick Preview"
echo.
echo [PROCESS] Start Restoration
echo   → Click "Start Processing" button
echo   → Watch progress bar and console log
echo   → Typical speed: 2-10 fps ^(depends on settings^)
echo.
echo.
echo ================================================================================
echo.
echo RECOMMENDED SETTINGS BY SOURCE
echo ===============================
echo.
echo VHS TAPES ^(Standard^):
echo   Preset: Standard Quality
echo   QTGMC: Medium
echo   Denoise: BM3D ^(sigma 5.0^)
echo   Upscaling: OFF ^(for first test^)
echo.
echo VHS ^(High Quality^):
echo   Preset: Maximum Quality
echo   QTGMC: Slower
echo   Denoise: BM3D GPU ^(sigma 7.0^)
echo   Upscaling: RealESRGAN 2x
echo.
echo Hi8/Digital8:
echo   Preset: High Quality
echo   QTGMC: Slow
echo   Denoise: BM3D ^(sigma 3.0^)
echo   Upscaling: ZNEDI3 2x
echo.
echo MiniDV:
echo   Preset: Digital Source
echo   QTGMC: Fast ^(progressive scan^)
echo   Denoise: BM3D ^(sigma 2.0^)
echo   Upscaling: Optional
echo.
echo.
echo ================================================================================
echo.
echo COMMON TASKS
echo ============
echo.
echo Basic Deinterlacing Only:
echo   1. Uncheck all AI features
echo   2. Set QTGMC to "Medium"
echo   3. Process
echo   Speed: 20-30 fps
echo.
echo Denoise ^+ Deinterlace:
echo   1. Enable "BM3D Denoising"
echo   2. Set sigma: 5.0 ^(VHS^), 3.0 ^(Hi8^)
echo   3. Check "Use GPU" if available
echo   Speed: 10-15 fps
echo.
echo Upscale to HD:
echo   1. Enable "AI Upscaling"
echo   2. Choose "RealESRGAN 2x" or "ZNEDI3 2x"
echo   3. Output: 1440x1080 or 1920x1080
echo   Speed: 2-5 fps
echo.
echo Smooth Motion:
echo   1. Enable "AI Frame Interpolation"
echo   2. Choose "RIFE 2x" ^(30fps → 60fps^)
echo   3. Requires good GPU
echo   Speed: 1-3 fps
echo.
echo.
echo ================================================================================
echo.
echo KEYBOARD SHORTCUTS
echo ==================
echo.
echo   Ctrl+O : Open input file
echo   Ctrl+S : Save current settings
echo   Ctrl+P : Start processing
echo   Ctrl+Q : Stop processing
echo   F5     : Refresh settings
echo   F11    : Toggle fullscreen console
echo.
echo.
echo ================================================================================
echo.
echo PERFORMANCE TIPS
echo ================
echo.
echo FAST PROCESSING:
echo   √ Use "Fast" or "Medium" QTGMC preset
echo   √ Disable AI upscaling for testing
echo   √ Process short clips first ^(1-2 minutes^)
echo   √ Use NVENC encoding if you have NVIDIA GPU
echo.
echo BEST QUALITY:
echo   √ Use "Slower" or "Placebo" QTGMC
echo   √ Enable BM3D GPU denoising
echo   √ Use RealESRGAN for upscaling
echo   √ Use ProRes for archival ^(large files^)
echo.
echo GPU OPTIMIZATION:
echo   √ Monitor VRAM in status bar
echo   √ See: Documentation\GPU_Quick_Reference.txt
echo   √ Reduce RIFE if VRAM ^>85%%
echo.
echo.
echo ================================================================================
echo.
echo TROUBLESHOOTING
echo ===============
echo.
echo No video output:
echo   → Check console log for errors
echo   → Verify input file plays in media player
echo   → Try "Quick Preview" preset first
echo.
echo Processing stops at 0%%:
echo   → Check "vspipe" is installed: Setup\1_Check_Prerequisites.bat
echo   → Restart computer if just installed VapourSynth
echo.
echo Very slow ^(^<1 fps^):
echo   → Disable AI features temporarily
echo   → Use "Fast" QTGMC preset
echo   → Lower output resolution
echo.
echo Out of memory:
echo   → See: Documentation\GPU_Quick_Reference.txt
echo   → Disable RIFE interpolation
echo   → Use ZNEDI3 instead of RealESRGAN
echo.
echo Green/pink colors:
echo   → Video is RGB not YUV - processing will fix it
echo   → Use "Bicubic" resize algorithm
echo.
echo.
echo ================================================================================
echo.
echo NEXT STEPS
echo ==========
echo.
echo 1. Read: INSTALLATION_GUIDE.txt ^(detailed setup^)
echo 2. Read: Documentation\GPU_Quick_Reference.txt ^(VRAM guide^)
echo 3. Read: Documentation\Performance_Guide.txt ^(optimization^)
echo 4. Check: TROUBLESHOOTING.txt ^(common issues^)
echo.
echo.
echo SUPPORT
echo =======
echo.
echo   Website: [Your website URL]
echo   Email:   [Your email]
echo   GitHub:  [Your GitHub repo]
echo.
echo.
echo ================================================================================
echo   Happy restoring!
echo ================================================================================
) > %DIST_DIR%\QUICK_START.txt
exit /b

:CREATE_TROUBLESHOOTING
(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - TROUBLESHOOTING GUIDE
echo ================================================================================
echo.
echo This document covers solutions to common problems.
echo Use Ctrl+F to search for specific error messages.
echo.
echo.
echo INDEX
echo =====
echo   [A] Installation Issues
echo   [B] Processing Errors
echo   [C] Performance Problems
echo   [D] Output Quality Issues
echo   [E] GPU/VRAM Issues
echo   [F] Audio Problems
echo   [G] File Format Issues
echo.
echo.
echo ================================================================================
echo.
echo [A] INSTALLATION ISSUES
echo ================================================================================
echo.
echo A1. "vspipe is not recognized as internal or external command"
echo ----------------------------------------------------------------
echo   CAUSE: VapourSynth not installed or not in PATH
echo.
echo   SOLUTION 1:
echo     1. Run: Setup\2_Install_All_Prerequisites.bat
echo     2. RESTART COMPUTER ^(required!^)
echo     3. Open new Command Prompt
echo     4. Test: vspipe --version
echo.
echo   SOLUTION 2 ^(Manual verification^):
echo     1. Check C:\Program Files\VapourSynth\ exists
echo     2. Win+R → sysdm.cpl → Advanced → Environment Variables
echo     3. System variables → Path → should contain VapourSynth path
echo     4. If missing, add: C:\Program Files\VapourSynth\core64
echo     5. RESTART COMPUTER
echo.
echo.
echo A2. "FFmpeg is not recognized as internal or external command"
echo ----------------------------------------------------------------
echo   CAUSE: FFmpeg not installed or not in PATH
echo.
echo   SOLUTION 1:
echo     1. Run: Setup\2_Install_All_Prerequisites.bat
echo     2. RESTART COMPUTER
echo     3. Test: ffmpeg -version
echo.
echo   SOLUTION 2 ^(Manual^):
echo     1. Download FFmpeg from: https://ffmpeg.org/download.html
echo     2. Extract to: C:\ffmpeg\
echo     3. Add to PATH: C:\ffmpeg\bin
echo     4. RESTART COMPUTER
echo.
echo.
echo A3. "Failed to load VapourSynth plugin"
echo -----------------------------------------
echo   CAUSE: Plugin not installed or wrong version
echo.
echo   SOLUTION:
echo     1. Run: Setup\Install_VapourSynth_Plugins.bat
echo     2. Verify: Setup\Test_VapourSynth_Plugins.bat
echo     3. For QTGMC: Requires havsfunc
echo     4. For BM3D GPU: Requires vs-bm3dcuda
echo.
echo.
echo A4. GPU Support Not Working
echo ----------------------------
echo   SYMPTOMS: AI features grayed out or slow
echo.
echo   DIAGNOSTICS:
echo     1. Open Command Prompt
echo     2. Run: nvidia-smi
echo     3. Should show GPU info
echo.
echo   SOLUTION 1 ^(No NVIDIA GPU^):
echo     - AI features require NVIDIA RTX 2060+
echo     - Use CPU alternatives ^(ZNEDI3, CPU BM3D^)
echo.
echo   SOLUTION 2 ^(GPU exists but not detected^):
echo     1. Update NVIDIA drivers: geforce.com/drivers
echo     2. Run: Setup\3_Install_GPU_Support.bat
echo     3. Verify PyTorch: python -c "import torch; print(torch.cuda.is_available())"
echo     4. Should print: True
echo.
echo.
echo ================================================================================
echo.
echo [B] PROCESSING ERRORS
echo ================================================================================
echo.
echo B1. Processing Stops at 0%% / Hangs
echo -------------------------------------
echo   CAUSE: VapourSynth script error or file access issue
echo.
echo   SOLUTION:
echo     1. Check console log for error messages
echo     2. Verify input file plays in VLC/MPC-HC
echo     3. Try processing a different file
echo     4. Check: last_generated_script.vpy for errors
echo     5. Run manually: vspipe --info last_generated_script.vpy -
echo.
echo   Common causes:
echo     - Corrupted input file
echo     - Unsupported codec
echo     - File path contains special characters
echo     - Insufficient permissions
echo.
echo.
echo B2. "Out of memory" / "OOM" Error
echo -----------------------------------
echo   CAUSE: Insufficient RAM or VRAM
echo.
echo   SOLUTION 1 ^(System RAM^):
echo     - Close other applications
echo     - Process shorter clips
echo     - Lower output resolution
echo     - Use H.264 instead of ProRes
echo.
echo   SOLUTION 2 ^(GPU VRAM^):
echo     - See section [E] GPU/VRAM Issues
echo     - Disable RIFE interpolation
echo     - Use RealESRGAN 2x instead of 4x
echo     - Use ZNEDI3 instead of RealESRGAN
echo     - See: Documentation\GPU_Quick_Reference.txt
echo.
echo.
echo B3. Processing Crashes Midway
echo -------------------------------
echo   CAUSE: Various - check console log
echo.
echo   DIAGNOSTICS:
echo     1. Note the frame number where it crashed
echo     2. Check console log for last error
echo     3. Check Windows Event Viewer
echo     4. Test with shorter clip
echo.
echo   Common causes:
echo     - Bad frame in source video
echo     - VRAM exhausted
echo     - Disk full
echo     - Thermal throttling
echo.
echo   SOLUTION:
echo     - Split video into segments
echo     - Lower quality settings
echo     - Check disk space ^(need 2x input size^)
echo     - Monitor temperatures
echo.
echo.
echo B4. "Access Denied" / Permission Errors
echo -----------------------------------------
echo   CAUSE: No write permission to output folder
echo.
echo   SOLUTION:
echo     1. Choose different output location
echo     2. Try desktop or Documents folder
echo     3. Run as Administrator ^(not recommended^)
echo     4. Check folder permissions
echo.
echo.
echo ================================================================================
echo.
echo [C] PERFORMANCE PROBLEMS
echo ================================================================================
echo.
echo C1. Very Slow Processing ^(^<2 fps^)
echo --------------------------------------
echo   NORMAL SPEEDS:
echo     - QTGMC only: 15-30 fps
echo     - QTGMC + BM3D: 8-15 fps
echo     - QTGMC + RealESRGAN: 2-5 fps
echo     - QTGMC + RealESRGAN + RIFE: 1-3 fps
echo.
echo   OPTIMIZATION:
echo     1. Use "Fast" or "Medium" QTGMC preset
echo     2. Disable AI features temporarily
echo     3. Use NVENC encoding if available
echo     4. Close other applications
echo     5. Process at native resolution first
echo.
echo.
echo C2. CPU at 100%% but GPU Idle
echo -------------------------------
echo   CAUSE: GPU features not enabled or not working
echo.
echo   CHECK:
echo     1. Status bar shows: "CUDA: Available ✓"
echo     2. BM3D "Use GPU" is checked
echo     3. AI upscaling uses CUDA variant
echo.
echo   FIX:
echo     1. Install GPU support: Setup\3_Install_GPU_Support.bat
echo     2. Select "BM3DCUDA" not "BM3D Basic"
echo     3. Select "RealESRGAN ^(CUDA^)" not "ZNEDI3"
echo.
echo.
echo C3. GPU at 100%% but Slow
echo ---------------------------
echo   NORMAL: GPU should be busy during AI processing
echo.
echo   BOTTLENECKS:
echo     - Disk I/O: Use SSD, not HDD
echo     - RAM: Need 16GB+ for HD content
echo     - VRAM: Monitor usage, reduce if ^>90%%
echo     - CPU: Should be 30-60%% during processing
echo.
echo.
echo ================================================================================
echo.
echo [D] OUTPUT QUALITY ISSUES
echo ================================================================================
echo.
echo D1. Output Looks Blurry
echo ------------------------
echo   CAUSES:
echo     - QTGMC preset too low ^(Draft/Fast^)
echo     - Wrong resize algorithm
echo     - Input resolution too low
echo.
echo   FIX:
echo     1. Use "Medium" or "Slow" QTGMC
echo     2. Use "Bicubic" resize
echo     3. Don't upscale SD content ^>2x without AI
echo     4. Enable BM3D carefully ^(high sigma = blur^)
echo.
echo.
echo D2. Output Has Combing/Interlacing
echo ------------------------------------
echo   CAUSE: Deinterlacing failed or disabled
echo.
echo   FIX:
echo     1. Ensure QTGMC is enabled
echo     2. Check field order: Auto-detect or TFF
echo     3. Don't use "Progressive" for VHS
echo     4. Increase QTGMC preset quality
echo.
echo.
echo D3. Colors Look Wrong ^(Green/Pink^)
echo --------------------------------------
echo   CAUSE: Color space mismatch ^(RGB vs YUV^)
echo.
echo   FIX:
echo     - Automatic: VapourSynth converts to YUV420P8
echo     - Check: last_generated_script.vpy
echo     - Should see: resize.Bicubic^(format=vs.YUV420P8^)
echo.
echo.
echo D4. Blocky/Pixelated Output
echo ----------------------------
echo   CAUSES:
echo     - CRF too high ^(lower quality^)
echo     - Bitrate too low
echo     - Wrong codec
echo.
echo   FIX:
echo     1. Lower CRF: 18-20 for high quality
echo     2. Use H.264 or H.265
echo     3. For archival: Use ProRes or FFV1
echo     4. Check output file size ^(should be large^)
echo.
echo.
echo ================================================================================
echo.
echo [E] GPU/VRAM ISSUES
echo ================================================================================
echo.
echo E1. "VRAM Warning: Insufficient Memory"
echo ----------------------------------------
echo   See: Documentation\GPU_Quick_Reference.txt for detailed guide
echo.
echo   QUICK FIX:
echo     1. Disable RIFE interpolation ^(saves 3.5 GB^)
echo     2. Use RealESRGAN 2x not 4x ^(saves 1.5 GB^)
echo     3. Use CPU BM3D ^(saves 1.2 GB^)
echo     4. Lower resolution
echo.
echo.
echo E2. VRAM Usage Keeps Climbing
echo ------------------------------
echo   CAUSE: Memory leak or batch accumulation
echo.
echo   FIX:
echo     1. Process shorter clips
echo     2. Restart application between jobs
echo     3. Close and reopen if VRAM ^>90%%
echo     4. Check for Windows/driver updates
echo.
echo.
echo E3. "CUDA out of memory" Error
echo --------------------------------
echo   CAUSE: PyTorch VRAM exhausted
echo.
echo   FIX:
echo     1. Lower resolution before processing
echo     2. Disable multiple AI features
echo     3. Monitor: Status bar VRAM display
echo     4. System auto-adjusts batches, but may need manual reduction
echo.
echo.
echo ================================================================================
echo.
echo [F] AUDIO PROBLEMS
echo ================================================================================
echo.
echo F1. No Audio in Output
echo -----------------------
echo   CHECK:
echo     1. Output format supports audio ^(MP4/MKV yes, AVI maybe^)
echo     2. "Copy Audio" is selected ^(not "No Audio"^)
echo     3. Input file has audio track
echo.
echo   FIX:
echo     1. Select "Copy Audio" in settings
echo     2. Use MP4 or MKV output
echo     3. Verify input: ffprobe input.avi
echo.
echo.
echo F2. Audio Out of Sync
echo ----------------------
echo   CAUSE: Frame rate mismatch or variable frame rate
echo.
echo   FIX:
echo     1. Don't use RIFE with VFR ^(variable frame rate^) sources
echo     2. Convert to CFR first: ffmpeg -i input.avi -r 29.97 -c:v copy output.avi
echo     3. Check audio delay in original file
echo.
echo.
echo ================================================================================
echo.
echo [G] FILE FORMAT ISSUES
echo ================================================================================
echo.
echo G1. "Unsupported file format"
echo ------------------------------
echo   SUPPORTED INPUTS:
echo     - AVI, MP4, MKV, MOV
echo     - MTS, M2TS, TS ^(AVCHD/DV^)
echo.
echo   FIX:
echo     1. Convert to AVI: ffmpeg -i input.xxx -c:v copy -c:a copy output.avi
echo     2. Use VLC to remux to MP4
echo.
echo.
echo G2. Very Large Output Files
echo ----------------------------
echo   CAUSES:
echo     - Lossless codec ^(FFV1, ProRes^)
echo     - CRF too low ^(high quality^)
echo     - High resolution
echo.
echo   NORMAL SIZES:
echo     - SD to HD: 500MB - 2GB per hour
echo     - HD with AI: 1GB - 4GB per hour
echo     - ProRes: 10GB - 50GB per hour
echo.
echo   REDUCE SIZE:
echo     1. Use H.264 not ProRes
echo     2. Increase CRF: 20-23
echo     3. Use "Slower" preset ^(better compression^)
echo.
echo.
echo ================================================================================
echo.
echo DIAGNOSTIC TOOLS
echo ================
echo.
echo Check System Info:
echo   - Run: Setup\Diagnose_Test_System.bat
echo   - Shows: CPU, RAM, GPU, disk space
echo.
echo Test Prerequisites:
echo   - Run: Setup\1_Check_Prerequisites.bat
echo   - Verifies: FFmpeg, VapourSynth, plugins
echo.
echo Test VapourSynth Plugins:
echo   - Run: Setup\Test_VapourSynth_Plugins.bat
echo   - Tests: QTGMC, BM3D, filters
echo.
echo Check GPU:
echo   - Command Prompt: nvidia-smi
echo   - Shows: GPU model, VRAM, temperature
echo.
echo Test PyTorch:
echo   - Command Prompt: python -c "import torch; print(torch.cuda.is_available())"
echo   - Should print: True
echo.
echo.
echo ================================================================================
echo.
echo REPORTING BUGS
echo ==============
echo.
echo If you can't solve the issue:
echo.
echo 1. Enable Debug Mode ^(if available^)
echo 2. Reproduce the problem
echo 3. Collect these files:
echo    - Console log ^(copy all text^)
echo    - last_generated_script.vpy
echo    - restoration_settings.json
echo.
echo 4. Report via:
echo    - GitHub Issues: [Your repo]
echo    - Email: [Your email]
echo.
echo Include:
echo   - Windows version
echo   - GPU model ^(if applicable^)
echo   - Input file format
echo   - Exact error message
echo   - Steps to reproduce
echo.
echo.
echo ================================================================================
echo   Most issues are solved by reinstalling prerequisites and restarting!
echo ================================================================================
) > %DIST_DIR%\TROUBLESHOOTING.txt
exit /b

:CREATE_PACKAGE_INFO
(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v%VERSION% - PACKAGE INFORMATION
echo ================================================================================
echo.
echo Version: %VERSION%
echo Build Date: %DATE%
echo Platform: Windows 10/11 ^(64-bit^)
echo.
echo.
echo PACKAGE CONTENTS
echo ================
echo.
echo Executable:
echo   Advanced_Tape_Restorer_v%VERSION%.exe - Main application
echo.
echo Configuration:
echo   Config\restoration_presets.json - Built-in presets
echo   Config\restoration_settings.json - Default settings template
echo   Config\tape_restorer_config.json - Application configuration
echo.
echo Setup Scripts:
echo   FIRST_TIME_SETUP.bat - One-click automated setup
echo   Setup\1_Check_Prerequisites.bat - Verify installation
echo   Setup\2_Install_All_Prerequisites.bat - Install FFmpeg/VapourSynth
echo   Setup\3_Install_GPU_Support.bat - Install PyTorch/CUDA
echo   Setup\Install_VapourSynth_Plugins.bat - Install plugins
echo   Setup\Test_VapourSynth_Plugins.bat - Test plugin installation
echo   Setup\Diagnose_Test_System.bat - System information
echo.
echo Documentation:
echo   INSTALLATION_GUIDE.txt - Complete installation instructions
echo   QUICK_START.txt - Get started in 5 minutes
echo   UNINSTALL_GUIDE.txt - Complete removal instructions
echo   TROUBLESHOOTING.txt - Common problems and solutions
echo   CHANGELOG.txt - Version history
echo   README.txt - Project overview
echo.
echo Feature Guides:
echo   Documentation\GPU_Memory_Guide.txt - VRAM management
echo   Documentation\GPU_Quick_Reference.txt - GPU optimization
echo   Documentation\Editable_File_Paths.txt - File path editing
echo   Documentation\Performance_Guide.txt - Speed optimization
echo   Documentation\Project_Overview.txt - Technical details
echo   Documentation\AI_Integration_Guide.txt - AI features
echo   Documentation\ProPainter_Guide.txt - Video inpainting
echo.
echo.
echo SYSTEM REQUIREMENTS
echo ===================
echo.
echo Minimum:
echo   - Windows 10 64-bit ^(version 1903+^)
echo   - Intel Core i5 / AMD Ryzen 5
echo   - 8 GB RAM
echo   - 2 GB free disk space
echo   - 1280×720 display
echo.
echo Recommended:
echo   - Windows 11 64-bit
echo   - Intel Core i7 / AMD Ryzen 7
echo   - 16 GB RAM
echo   - SSD with 10 GB free space
echo   - 1920×1080 display
echo.
echo For AI Features:
echo   - NVIDIA RTX 2060 or newer
echo   - 8 GB VRAM minimum ^(12 GB recommended^)
echo   - CUDA 11.8 or 12.1
echo.
echo.
echo REQUIRED PREREQUISITES
echo ======================
echo.
echo These are installed via FIRST_TIME_SETUP.bat:
echo.
echo 1. FFmpeg 6.0+
echo    - Video encoding and decoding
echo    - Size: ~100 MB
echo    - License: GPL/LGPL
echo.
echo 2. VapourSynth R65-R73
echo    - Video filtering framework
echo    - Size: ~50 MB
echo    - License: LGPL
echo.
echo 3. VapourSynth Plugins:
echo    - QTGMC ^(deinterlacing^)
echo    - BM3D ^(denoising^)
echo    - ZNEDI3 ^(scaling^)
echo    - havsfunc ^(helper functions^)
echo    - Size: ~30 MB combined
echo    - Licenses: Various open source
echo.
echo.
echo OPTIONAL COMPONENTS
echo ===================
echo.
echo PyTorch + CUDA ^(for AI features^):
echo    - PyTorch 2.0+
echo    - CUDA 11.8 or 12.1
echo    - Size: ~2.5 GB
echo    - License: BSD
echo    - Install: Setup\3_Install_GPU_Support.bat
echo.
echo.
echo FEATURES
echo ========
echo.
echo Core Restoration:
echo   √ QTGMC deinterlacing ^(7 quality presets^)
echo   √ BM3D denoising ^(CPU and GPU modes^)
echo   √ Artifact removal ^(TComb, Bifrost^)
echo   √ Debanding and stabilization
echo   √ Color correction
echo   √ Auto field-order detection
echo.
echo AI Enhancement ^(GPU required^):
echo   √ RealESRGAN 2x/4x upscaling
echo   √ RIFE frame interpolation ^(2x-4x^)
echo   √ ZNEDI3 fast upscaling
echo   √ ProPainter video inpainting
echo   √ Face restoration ^(GFPGAN^)
echo   √ B/W colorization ^(DeOldify^)
echo.
echo Performance:
echo   √ Real-time VRAM monitoring
echo   √ GPU memory management
echo   √ Adaptive batch sizing
echo   √ CPU/GPU utilization display
echo   √ FPS counter
echo   √ Temperature monitoring
echo.
echo Output Formats:
echo   √ H.264 ^(CPU/NVENC/AMF^)
echo   √ H.265 ^(HEVC^)
echo   √ ProRes 422/HQ
echo   √ FFV1 lossless
echo   √ VP9
echo.
echo User Interface:
echo   √ Editable file path fields
echo   √ Visual validation feedback
echo   √ Dark mode support
echo   √ Preset management
echo   √ Batch processing queue
echo   √ Live console log
echo.
echo.
echo CHANGE LOG HIGHLIGHTS
echo =====================
echo.
echo v3.3 ^(December 2025^):
echo   + GPU memory management ^(VRAM limits, pre-flight checks^)
echo   + Editable file path fields
echo   + Dark mode text visibility fix
echo   + Windows path separator normalization
echo   + Comprehensive documentation
echo.
echo v3.2 ^(November 2025^):
echo   + Performance optimizations
echo   + BM3D GPU support
echo   + Real-time GPU monitoring
echo   + FPS display
echo.
echo v3.0 ^(October 2025^):
echo   + AI model integration
echo   + ProPainter support
echo   + RealESRGAN upscaling
echo   + RIFE interpolation
echo.
echo See CHANGELOG.txt for complete history.
echo.
echo.
echo LICENSES
echo ========
echo.
echo Advanced Tape Restorer:
echo   [Your license] - Copyright ^(c^) 2025
echo.
echo Third-Party Components:
echo   - FFmpeg: GPL/LGPL
echo   - VapourSynth: LGPL
echo   - QTGMC: GPL
echo   - PyTorch: BSD
echo   - PySide6: LGPL
echo.
echo See individual component licenses in Documentation\Licenses\
echo.
echo.
echo SUPPORT
echo =======
echo.
echo Documentation:
echo   - Start with: QUICK_START.txt
echo   - Problems? See: TROUBLESHOOTING.txt
echo   - Advanced: Documentation\ folder
echo.
echo Online Resources:
echo   - Website: [Your URL]
echo   - GitHub: [Your repo]
echo   - Email: [Your email]
echo.
echo Community:
echo   - Discord: [Your server]
echo   - Reddit: [Your subreddit]
echo   - Forum: [Your forum]
echo.
echo.
echo ================================================================================
echo   Thank you for using Advanced Tape Restorer v%VERSION%!
echo ================================================================================
) > %DIST_DIR%\PACKAGE_INFO.txt
exit /b
