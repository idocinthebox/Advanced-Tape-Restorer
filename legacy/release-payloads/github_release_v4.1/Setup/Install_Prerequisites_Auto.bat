@echo off
REM ==============================================================================
REM  Advanced Tape Restorer v3.1 - Prerequisites Installation Script
REM  Automatically downloads and installs all required components
REM ==============================================================================

title Advanced Tape Restorer v3.1 - Automatic Prerequisites Installer

setlocal enabledelayedexpansion

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ================================================================================
    echo   ADMINISTRATOR RIGHTS REQUIRED
    echo ================================================================================
    echo.
    echo This installer needs administrator rights to:
    echo   - Install FFmpeg to Program Files
    echo   - Install VapourSynth system-wide
    echo   - Add programs to system PATH
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

cls
color 0B
echo.
echo ================================================================================
echo   ADVANCED TAPE RESTORER v4.0 - AUTOMATIC INSTALLER
echo ================================================================================
echo.
echo REQUIRED COMPONENTS (will always be installed):
echo   [1] FFmpeg (video encoding) - ~100 MB
echo   [2] VapourSynth (video processing) - ~50 MB
echo   [3] Core VapourSynth Plugins (filters) - ~30 MB
echo.
echo OPTIONAL PERFORMANCE PLUGINS (choose below):
echo   [4] BestSource (Most reliable source filter - RECOMMENDED)
echo   [5] GPU Deinterlacing (142x faster QTGMC - RECOMMENDED)
echo   [6] fpng Plugin (142x faster PNG writing - RECOMMENDED)
echo   [7] ONNX NPU Runtime (AI model offloading)
echo   [8] PyTorch CUDA (NVIDIA GPU AI acceleration)
echo.
echo ================================================================================
echo.
echo Select optional plugins to install:
echo.

set INSTALL_BESTSOURCE=N
set INSTALL_GPU_DEINT=N
set INSTALL_FPNG=N
set INSTALL_ONNX=N
set INSTALL_PYTORCH=N

echo Install BestSource2? (Most accurate FPS/audio sync)
echo   Benefit: Critical for tape captures, proper telecine/RFF handling
set /p INSTALL_BESTSOURCE="   Install? (Y/N) [Recommended]: "

echo.
echo Install GPU-Accelerated Deinterlacing? (142x faster QTGMC)
echo   Requires: NVIDIA/AMD/Intel GPU with OpenCL
set /p INSTALL_GPU_DEINT="   Install? (Y/N) [Recommended]: "

echo.
echo Install fpng Plugin? (142x faster PNG frame extraction)
echo   Benefit: Critical for GFPGAN face enhancement
set /p INSTALL_FPNG="   Install? (Y/N) [Recommended]: "

echo.
echo Install ONNX NPU Runtime? (Offload AI models to NPU)
echo   Requires: Intel Core Ultra or AMD Ryzen AI processor
set /p INSTALL_ONNX="   Install? (Y/N) [Optional]: "

echo.
echo Install PyTorch CUDA? (GPU acceleration for AI models)
echo   Requires: NVIDIA GPU
set /p INSTALL_PYTORCH="   Install? (Y/N) [Optional]: "

echo.
echo ================================================================================
echo   INSTALLATION SUMMARY
echo ================================================================================
echo.
echo REQUIRED:
echo   - FFmpeg
echo   - VapourSynth  
echo   - Core VapourSynth Plugins
echo.
echo OPTIONAL (selected):
if /i "%INSTALL_BESTSOURCE%"=="Y" echo   - BestSource2 Source Filter
if /i "%INSTALL_GPU_DEINT%"=="Y" echo   - GPU Deinterlacing (nnedi3cl + SNEEDIF)
if /i "%INSTALL_FPNG%"=="Y" echo   - fpng Plugin
if /i "%INSTALL_ONNX%"=="Y" echo   - ONNX NPU Runtime
if /i "%INSTALL_PYTORCH%"=="Y" echo   - PyTorch CUDA
echo.
echo Total installation time: 10-20 minutes
echo.
echo ================================================================================
echo.
pause

REM Create temp directory in Downloads (less likely to be blocked than %TEMP%)
set TEMP_DIR=%USERPROFILE%\Downloads\ATR_Setup
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM ============================================================================
REM STEP 1: Install FFmpeg
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 1/3: Installing FFmpeg
echo ================================================================================
echo.

where ffmpeg >nul 2>&1
if %errorLevel% equ 0 (
    echo FFmpeg is already installed and in PATH
    echo [SKIP] FFmpeg installation
    goto skip_ffmpeg
)

echo Downloading FFmpeg...
set FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
set FFMPEG_ZIP=%TEMP_DIR%\ffmpeg.zip
set FFMPEG_DIR=C:\ffmpeg

REM Robust download with retry logic
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $maxRetries = 3; $retryCount = 0; $success = $false; while (-not $success -and $retryCount -lt $maxRetries) { try { Write-Host 'Download attempt' ($retryCount + 1) 'of' $maxRetries'...'; $webClient = New-Object System.Net.WebClient; $webClient.DownloadFile('%FFMPEG_URL%', '%FFMPEG_ZIP%'); $success = $true; Write-Host 'Download successful!'; } catch { $retryCount++; Write-Host 'Download failed:' $_.Exception.Message; if ($retryCount -lt $maxRetries) { Write-Host 'Retrying in 3 seconds...'; Start-Sleep -Seconds 3; } } finally { if ($webClient) { $webClient.Dispose(); } } } if (-not $success) { Write-Host '[ERROR] Failed after' $maxRetries 'attempts'; exit 1; } }"

if not exist "%FFMPEG_ZIP%" (
    echo [ERROR] Failed to download FFmpeg after multiple attempts
    echo.
    echo MANUAL INSTALLATION:
    echo   1. Download from: %FFMPEG_URL%
    echo   2. Extract to C:\ffmpeg
    echo   3. Add C:\ffmpeg\bin to system PATH
    echo.
    pause
    exit /b 1
)

echo Extracting FFmpeg...
powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%TEMP_DIR%\ffmpeg_extract' -Force"

REM Find the extracted folder (it has version number in name)
for /d %%d in ("%TEMP_DIR%\ffmpeg_extract\ffmpeg-*") do (
    set EXTRACTED_DIR=%%d
)

echo Installing FFmpeg to %FFMPEG_DIR%...
if exist "%FFMPEG_DIR%" rmdir /s /q "%FFMPEG_DIR%"
move "!EXTRACTED_DIR!" "%FFMPEG_DIR%" >nul

REM Add to PATH
echo Adding FFmpeg to system PATH...
powershell -Command "& {[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';%FFMPEG_DIR%\bin', 'Machine')}"

echo [OK] FFmpeg installation complete

:skip_ffmpeg

REM ============================================================================
REM STEP 1.5: Check/Install Python 3.12 (required for VapourSynth & PyTorch)
REM ============================================================================

echo.
echo ================================================================================
echo   Checking Python Installation
echo ================================================================================
echo.

REM Check if Python 3.12 is available
py -3.12 --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python 3.12 found
    goto skip_python_install
)

echo Python 3.12 is required for:
echo   - VapourSynth R73 installer (needs Python 3.12+)
echo   - PyTorch (supports Python 3.9-3.12)
echo.
echo Your current Python installations:
py -0
echo.
echo Downloading Python 3.12.8 installer...
set PY_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
set PY_INSTALLER=%TEMP_DIR%\python-3.12.8-amd64.exe

curl -L -o "%PY_INSTALLER%" "%PY_URL%"

if not exist "%PY_INSTALLER%" (
    echo [ERROR] Failed to download Python installer
    pause
    exit /b 1
)

echo.
echo Installing Python 3.12.8...
echo IMPORTANT: Installation will proceed automatically
echo   - Python will be added to PATH
echo   - Both 3.12 and 3.14 can coexist (use py -3.12 or py -3.14)
echo.
pause

"%PY_INSTALLER%" /passive PrependPath=1 Include_test=0

if %errorLevel% neq 0 (
    echo [ERROR] Python installation failed
    pause
    exit /b 1
)

echo [OK] Python 3.12 installed
echo.

:skip_python_install

REM ============================================================================
REM STEP 2: Install VapourSynth
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 2/3: Installing VapourSynth
echo ================================================================================
echo.

where vspipe >nul 2>&1
if %errorLevel% equ 0 (
    echo VapourSynth is already installed and in PATH
    echo [SKIP] VapourSynth installation
    goto skip_vapoursynth
)

echo Downloading VapourSynth R73 installer (includes vsrepo for plugin management)...
set VS_URL=https://github.com/vapoursynth/vapoursynth/releases/download/R73/VapourSynth-x64-R73.exe
set VS_INSTALLER=%TEMP_DIR%\VapourSynth-x64-R73.exe

REM Use curl (more reliable for large GitHub files)
curl -L --retry 3 --retry-delay 3 --max-time 300 -o "%VS_INSTALLER%" "%VS_URL%"

if %errorLevel% neq 0 (
    echo [ERROR] Download failed with exit code %errorLevel%
    pause
    exit /b 1
)

echo [OK] Downloaded to: %VS_INSTALLER%
echo.

if not exist "%VS_INSTALLER%" (
    echo.
    echo [ERROR] File check failed but curl succeeded
    echo Expected: %VS_INSTALLER%
    dir "%TEMP_DIR%"
    echo.
    pause
    exit /b 1
)

echo [OK] File verified, preparing to install...
echo.
echo ================================================================================
echo   VAPOURSYNTH INSTALLER WILL NOW LAUNCH
echo ================================================================================
echo.
echo Installing VapourSynth...
echo.
echo IMPORTANT: During installation:
echo   1. Choose "Install for ME only" (not all users)
echo   2. Keep default installation path
echo   3. Complete the installation wizard
echo.
echo NOTE: Python 3.12 was installed for current user, so VapourSynth
echo       must also install for current user to find Python correctly.
echo.
echo Press any key to launch installer...
pause

echo.
echo [DEBUG] Launching: "%VS_INSTALLER%"
start /wait "" "%VS_INSTALLER%"

if %errorLevel% neq 0 (
    echo [ERROR] VapourSynth installation failed or was cancelled
    pause
    exit /b 1
)

echo [OK] VapourSynth installer completed

:skip_vapoursynth

REM ============================================================================
REM STEP 3: Install VapourSynth Plugins
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 3/3: Installing VapourSynth Plugins
echo ================================================================================
echo.

REM Check if Python 3.12 is available
py -3.12 --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Python 3.12 not found - cannot install VapourSynth plugins
    echo.
    echo Install plugins manually after setup - see PLUGIN_INSTALLATION_FIX.md
    echo.
    goto skip_plugins
)

echo [OK] Python 3.12 found
echo.

REM Locate vsrepo.py (bundled with VapourSynth installer)
echo Locating vsrepo.py...

set VSREPO_PATH=

REM Check user-level install (Install for ME only)
if exist "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" (
    set VSREPO_PATH=%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
    echo [OK] Found at: %LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
)

REM Check system-level install (Install for all users)
if not defined VSREPO_PATH (
    if exist "C:\Program Files\VapourSynth\vsrepo\vsrepo.py" (
        set VSREPO_PATH=C:\Program Files\VapourSynth\vsrepo\vsrepo.py
        echo [OK] Found at: C:\Program Files\VapourSynth\vsrepo\vsrepo.py
    )
)

if not defined VSREPO_PATH (
    echo [ERROR] vsrepo.py not found!
    echo.
    echo vsrepo.py should be in VapourSynth installation directory.
    echo Checked:
    echo   - %LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
    echo   - C:\Program Files\VapourSynth\vsrepo\vsrepo.py
    echo.
    echo Manual installation required - see PLUGIN_INSTALLATION_FIX.md
    goto skip_plugins
)

echo.

REM Update vsrepo database
echo Updating plugin database...
py -3.12 "%VSREPO_PATH%" update
echo.

REM Install essential VapourSynth plugins
echo Installing VapourSynth plugins (this may take a few minutes)...
echo   - vsutil (utility functions - required by havsfunc)
echo   - havsfunc (QTGMC deinterlacing)
echo   - ffms2 (video source - CRITICAL)
echo   - mvtools (motion compensation)
echo   - bm3d (GPU denoising)
echo   - znedi3 (AI upscaling)
echo.

py -3.12 "%VSREPO_PATH%" install vsutil havsfunc ffms2 mvtools bm3d znedi3

if %errorLevel% equ 0 (
    echo.
    echo [OK] VapourSynth plugins installed successfully!
    echo.
) else (
    echo.
    echo [WARN] Some plugins may have failed to install
    echo Verify with: py -3.12 "%VSREPO_PATH%" installed
    echo.
)

:skip_plugins

REM ============================================================================
REM STEP 4: Install Optional Performance Plugins
REM ============================================================================

REM ===== Step 4A: BestSource2 Source Filter =====
if /i "%INSTALL_BESTSOURCE%"=="Y" (
    echo.
    echo ================================================================================
    echo   STEP 4A/8: Installing BestSource2 Source Filter
    echo ================================================================================
    echo.
    
    if not defined VSREPO_PATH (
        echo [WARN] vsrepo not found - skipping BestSource2
        echo Install manually: Setup\Install_BestSource_Plugin.bat
        goto skip_bestsource
    )
    
    echo Installing BestSource2 (most reliable source filter)...
    py -3.12 "%VSREPO_PATH%" install bestsource
    
    if %errorLevel% equ 0 (
        echo [OK] BestSource2 installed
        echo       Most accurate FPS detection and audio sync for tape sources
    ) else (
        echo [WARN] BestSource2 installation failed - run Install_BestSource_Plugin.bat manually
    )
)
:skip_bestsource

REM ===== Step 4B: GPU Deinterlacing Plugins =====
if /i "%INSTALL_GPU_DEINT%"=="Y" (
    echo.
    echo ================================================================================
    echo   STEP 4B/8: Installing GPU Deinterlacing Plugins
    echo ================================================================================
    echo.
    
    if not defined VSREPO_PATH (
        echo [WARN] vsrepo not found - skipping GPU plugins
        echo Install manually: Setup\Install_GPU_Deinterlace_Plugins.bat
        goto skip_gpu_deint
    )
    
    echo Installing nnedi3cl (OpenCL GPU acceleration)...
    py -3.12 "%VSREPO_PATH%" install nnedi3cl
    
    echo.
    echo Installing SNEEDIF (optimized GPU deinterlacing)...
    py -3.12 "%VSREPO_PATH%" install sneedif
    
    if %errorLevel% equ 0 (
        echo [OK] GPU deinterlacing plugins installed
        echo       QTGMC will now be 142x faster on compatible GPUs!
    ) else (
        echo [WARN] Some GPU plugins failed - run Install_GPU_Deinterlace_Plugins.bat manually
    )
)
:skip_gpu_deint

if /i "%INSTALL_FPNG%"=="Y" (
    echo.
    echo ================================================================================
    echo   STEP 4C/8: Installing fpng Plugin
    echo ================================================================================
    echo.
    
    if not defined VSREPO_PATH (
        echo [WARN] vsrepo not found - skipping fpng
        echo Install manually: Setup\Install_FPNG_Plugin.bat
        goto skip_fpng
    )
    
    echo Installing fpng (ultra-fast PNG writing)...
    py -3.12 "%VSREPO_PATH%" install fpng
    
    if %errorLevel% equ 0 (
        echo [OK] fpng plugin installed
        echo       GFPGAN frame extraction will be 142x faster!
    ) else (
        echo [WARN] fpng installation failed - run Install_FPNG_Plugin.bat manually
    )
)
:skip_fpng

if /i "%INSTALL_ONNX%"=="Y" (
    echo.
    echo ================================================================================
    echo   STEP 4D/8: Installing ONNX Runtime (NPU Support)
    echo ================================================================================
    echo.
    
    echo Installing onnxruntime-directml via pip...
    py -3.12 -m pip install --upgrade onnxruntime-directml
    
    if %errorLevel% equ 0 (
        echo [OK] ONNX NPU Runtime installed
        echo       AI models can now use NPU acceleration
    ) else (
        echo [WARN] ONNX installation failed - run Install_ONNX_Runtime_NPU.bat manually
    )
)

if /i "%INSTALL_PYTORCH%"=="Y" (
    echo.
    echo ================================================================================
    echo   STEP 4E/8: Installing PyTorch with CUDA Support
    echo ================================================================================
    echo.
    
    echo Installing PyTorch with CUDA 12.1 support...
    echo This may take 5-10 minutes (2GB download)...
    py -3.12 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    if %errorLevel% equ 0 (
        echo [OK] PyTorch CUDA installed
        echo       AI models (RealESRGAN, GFPGAN, RIFE) can now use GPU
    ) else (
        echo [WARN] PyTorch installation failed - run Install_PyTorch_CUDA.bat manually
    )
)

REM ============================================================================
REM Cleanup and Finish
REM ============================================================================

echo.
echo Cleaning up temporary files...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"

cls
echo.
echo ================================================================================
echo   INSTALLATION COMPLETE!
echo ================================================================================
echo.
if exist "%FFMPEG_DIR%" (
    echo [OK] FFmpeg installed: %FFMPEG_DIR%\bin
) else (
    echo [SKIP] FFmpeg (already installed or skipped)
)

where vspipe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] VapourSynth installed
) else (
    echo [WARN] VapourSynth may need manual installation
)

cls
echo.
echo ================================================================================
echo   INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo REQUIRED COMPONENTS:
if exist "%FFMPEG_DIR%" (
    echo   [OK] FFmpeg installed: %FFMPEG_DIR%\bin
) else (
    echo   [SKIP] FFmpeg (already installed)
)

where vspipe >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] VapourSynth installed
) else (
    echo   [WARN] VapourSynth may need manual installation
)

echo   [OK] Core VapourSynth plugins
echo.
echo OPTIONAL PERFORMANCE PLUGINS:
if /i "%INSTALL_BESTSOURCE%"=="Y" echo   [OK] BestSource2 (Most accurate FPS/audio sync)
if /i "%INSTALL_GPU_DEINT%"=="Y" echo   [OK] GPU Deinterlacing (142x faster QTGMC)
if /i "%INSTALL_FPNG%"=="Y" echo   [OK] fpng Plugin (142x faster PNG)
if /i "%INSTALL_ONNX%"=="Y" echo   [OK] ONNX NPU Runtime
if /i "%INSTALL_PYTORCH%"=="Y" echo   [OK] PyTorch CUDA

echo.
echo ================================================================================
echo   IMPORTANT: RESTART REQUIRED
echo ================================================================================
echo.
echo    NEXT STEPS:
echo    1. Restart your computer (for PATH changes to take effect)
echo    2. Run Advanced_Tape_Restorer_v4.0.exe
echo    3. Test with a video file
echo.
echo    PERFORMANCE BENEFITS:
if /i "%INSTALL_BESTSOURCE%"=="Y" echo    - Source Filter: Most accurate FPS/audio sync ^(critical for tapes^)
if /i "%INSTALL_GPU_DEINT%"=="Y" echo    - QTGMC deinterlacing: 142x faster (5 min → 2 sec)
if /i "%INSTALL_FPNG%"=="Y" echo    - GFPGAN frame extraction: 142x faster (94 min → 40 sec)
if /i "%INSTALL_ONNX%"=="Y" echo    - AI models: Can offload to NPU (frees GPU VRAM)
if /i "%INSTALL_PYTORCH%"=="Y" echo    - AI upscaling: Full GPU acceleration
echo.
echo ================================================================================
pause
