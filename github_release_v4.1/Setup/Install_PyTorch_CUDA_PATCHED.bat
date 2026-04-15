@echo off
REM ==============================================================================
REM  Advanced Tape Restorer v3.1 - PyTorch CUDA Installer
REM  Installs PyTorch with CUDA support for external tools ONLY
REM ==============================================================================

title Advanced Tape Restorer v3.1 - PyTorch CUDA Installer (Optional)

setlocal enabledelayedexpansion

cls
color 0B
echo.
echo ================================================================================
echo   PYTORCH + CUDA INSTALLER (OPTIONAL) - Advanced Tape Restorer v3.1
echo ================================================================================
echo.
echo ================================================================================
echo   IMPORTANT: THIS IS OPTIONAL AND NOT REQUIRED FOR MOST USERS
echo ================================================================================
echo.
echo Advanced Tape Restorer AI features work WITHOUT this installer:
echo   - RealESRGAN AI upscaling (via VapourSynth plugin)
echo   - RIFE frame interpolation (via VapourSynth plugin)
echo   - BasicVSR++, SwinIR, ZNEDI3 (all built into VapourSynth)
echo.
echo This installer is ONLY needed if you want to use EXTERNAL tools:
echo   - Standalone ProPainter for video inpainting
echo   - Custom Python AI scripts outside the app
echo   - Advanced AI model development/testing
echo.
echo ================================================================================
echo.
pause
echo.
echo Do you want to continue installing PyTorch for external tools?
echo.
choice /C YN /M "Continue with optional PyTorch installation"
if %errorLevel% equ 2 (
    echo.
    echo Installation cancelled. Your app will work perfectly without this.
    echo.
    pause
    exit /b 0
)
echo.
echo ================================================================================
echo   PyTorch Features (for external tools only):
echo ================================================================================
echo.
echo   - ProPainter AI Inpainting (standalone tool)
echo   - GFPGAN face restoration (standalone)
echo   - Custom AI video processing scripts
echo.
echo REQUIREMENTS:
echo   - NVIDIA GPU (RTX 3060 or newer recommended)
echo   - 8+ GB VRAM for AI features
echo   - Python 3.9-3.12 (will be auto-installed if needed)
echo.
echo Download size: ~2.5 GB
echo Installation time: 10-15 minutes
echo.
echo ================================================================================
echo.

REM Check if Python is available (and not just Windows Store stub)
echo Checking for Python installation...
REM Prefer Python 3.11 via the Python Launcher if available (avoids PATH / Store alias issues)
set "PYTHON_CMD=python"
py -3.11 --version >nul 2>&1
if %errorLevel% equ 0 (
    set "PYTHON_CMD=py -3.11"
)
%PYTHON_CMD% --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Python not found on system
    echo.
    echo Would you like to automatically download and install Python 3.11?
    echo.
    choice /C YN /M "Auto-install Python 3.11 (64-bit)"
    if !errorLevel! equ 2 (
        echo.
        echo Installation cancelled.
        echo.
        echo To install Python manually:
        echo   1. Download from: https://www.python.org/downloads/
        echo   2. During installation, check "Add Python to PATH"
        echo   3. Disable Windows Store Python aliases (Settings ^> App execution aliases)
        echo   4. Re-run this script
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo Downloading Python 3.11 installer...
    set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe
    
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $webClient = New-Object System.Net.WebClient; $webClient.DownloadFile('%PYTHON_URL%', '%PYTHON_INSTALLER%'); $webClient.Dispose(); }"
    
    if not exist "%PYTHON_INSTALLER%" (
        echo [ERROR] Failed to download Python installer
        echo Please install manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo Running Python installer...
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    start /wait "" "%PYTHON_INSTALLER%" /passive PrependPath=1 Include_test=0
    
    if !errorLevel! neq 0 (
        echo [ERROR] Python installation failed
        pause
        exit /b 1
    )
    
    echo [OK] Python installed successfully
    echo.
    echo Refreshing PATH and continuing...
    echo.
    REM Refresh PATH by re-reading environment
    REM NOTE: 'refreshenv' is not guaranteed to exist. If PATH changes were made, open a NEW terminal after installation.
    set PYTHON_CMD=python
    goto :check_python_version
REM Get Python version robustly (handles: "Python 3.11.9" or just "3.11.9")
set "PY_VERSION="
for /f "tokens=1,2" %%a in ('%PYTHON_CMD% --version 2^>^&1') do (
    if /I "%%a"=="Python" (
        set "PY_VERSION=%%b"
    ) else (
        set "PY_VERSION=%%a"
    )
)

REM Validate version looks like a number (not a Windows Store stub message)
if not defined PY_VERSION goto :python_stub_detected
set "PY_FIRST=!PY_VERSION:~0,1!"
echo(!PY_FIRST!| findstr /R "^[0-9]$" >nul
if %errorLevel% neq 0 goto :python_stub_detected

echo [OK] Python %PY_VERSION% found
echo.

REM Check if Python version is supported by PyTorch
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)

if %PY_MAJOR% gtr 3 (
    goto :python_version_mismatch
)

if %PY_MAJOR% equ 3 if %PY_MINOR% gtr 12 (
    goto :python_version_mismatch
)

if %PY_MAJOR% equ 3 if %PY_MINOR% lss 9 (
    echo [ERROR] Python version too old for PyTorch
    echo.
    echo PyTorch requires Python 3.9 or newer
    echo You have Python %PY_VERSION% installed
    echo.
    echo Please install Python 3.11 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python version %PY_VERSION% is compatible with PyTorch
echo.

:gpu_check
REM Check for NVIDIA GPU
echo Checking for NVIDIA GPU...
where nvidia-smi >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [WARNING] NVIDIA drivers not found - nvidia-smi command not available
    echo.
    echo Do you have an NVIDIA graphics card installed?
    echo.
    choice /C YN /M "I have an NVIDIA GPU but drivers are not installed"
    if !errorLevel! equ 1 (
        echo.
        echo Opening NVIDIA Driver Download page...
        echo.
        echo INSTRUCTIONS:
        echo   1. Select your GPU model
        echo   2. Download the latest Game Ready or Studio Driver
        echo   3. Install the driver and restart your computer
        echo   4. Re-run this script after restart
        echo.
        start https://www.nvidia.com/Download/index.aspx
        echo.
        echo Press any key after installing drivers and restarting...
        pause
        exit /b 1
    )
    
    echo.
    echo [INFO] No NVIDIA GPU - will install CPU-only PyTorch
    echo       (Very slow for external AI tools, but app will work normally)
    echo.
    pause
    set CUDA_AVAILABLE=0
) else (
    echo [OK] NVIDIA drivers detected
    echo.
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv 2>nul
    echo.
    set CUDA_AVAILABLE=1
    pause
)

echo.
echo ================================================================================
echo   Installing PyTorch
echo ================================================================================
echo.

if "%CUDA_AVAILABLE%"=="1" (
    echo Installing with CUDA 12.4 support for GPU acceleration...
    echo This may take 10-15 minutes...
    echo.
    %PYTHON_CMD% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
) else (
    echo Installing CPU-only version (no GPU acceleration)...
    echo This may take 5-10 minutes...
    echo.
    %PYTHON_CMD% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] PyTorch installation failed
    echo.
    echo Try manual installation:
    echo   Visit: https://pytorch.org/get-started/locally/
    echo   Select: Stable, Windows, Pip, Python, CUDA 12.4
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] PyTorch installed
echo.

echo.
echo ================================================================================
echo   Verifying Installation
echo ================================================================================
echo.

echo Checking PyTorch installation...
%PYTHON_CMD% -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('Device count:', torch.cuda.device_count() if torch.cuda.is_available() else 0); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')" 2>nul

echo.
echo.
echo ================================================================================
echo   INSTALLATION COMPLETE
echo ================================================================================
echo.

%PYTHON_CMD% -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
if %errorLevel% equ 0 (
    echo [OK] GPU acceleration is working!
    echo.
    echo You can now use these EXTERNAL tools with GPU acceleration:
    echo   - Standalone ProPainter for video inpainting
    echo   - GFPGAN for face restoration
    echo   - Custom PyTorch-based video scripts
    echo.
    echo NOTE: The main app's AI features (RealESRGAN, RIFE, etc.) work
    echo       via VapourSynth plugins and don't require this installation.
    echo.
) else (
    echo [INFO] CPU-only PyTorch installed
    echo.
    if "%CUDA_AVAILABLE%"=="1" (
        echo [WARNING] NVIDIA drivers detected but CUDA not working in PyTorch
        echo.
        echo Your configuration:
        nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>nul
        echo.
        echo Possible causes:
        echo   - Python version incompatibility (PyTorch requires Python 3.9-3.12)
        echo   - Driver version too old for CUDA 12.4 (requires 525.60.13+)
        echo   - GPU architecture not supported
        echo.
        echo Solutions:
        echo   - Use Python 3.11 instead of Python 3.14+ (see instructions below)
        echo   - Update drivers from nvidia.com/drivers
        echo   - Restart computer after driver update
        echo.
    ) else (
        echo External AI tools will run on CPU only (very slow^)
        echo.
    )
    echo The main app's AI features will still work normally via VapourSynth.
    echo.
)

echo.
echo Your Advanced Tape Restorer app is fully functional with or without PyTorch.
echo Launch Advanced_Tape_Restorer_v3.1.exe to use built-in AI features!
echo.

pause
exit /b 0

:python_version_mismatch
echo [ERROR] Python version too new for PyTorch
echo.
echo PyTorch currently supports Python 3.9 - 3.12 only
echo You have Python %PY_VERSION% installed
echo.

REM Check if Python 3.11 is already installed via Python Launcher
echo Checking for Python 3.11 installation...
py -3.11 --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python 3.11 found via Python Launcher
    echo Using py -3.11 for PyTorch installation
    set PYTHON_CMD=py -3.11
    goto :gpu_check
)

echo Would you like to automatically install Python 3.11 alongside Python %PY_VERSION%?
echo (Both versions can coexist - you can use py -3.11 to access it)
echo.
choice /C YN /M "Install Python 3.11 for PyTorch compatibility"
if %errorLevel% equ 2 (
    echo.
    echo Installation cancelled.
    echo.
    echo To install manually:
    echo   1. Download Python 3.11.9: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo   2. During install, check "Add Python to PATH"
    echo   3. Use "py -3.11" command to run Python 3.11
    echo   4. Run: py -3.11 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    echo.
    pause
    exit /b 1
)

echo.
echo Downloading Python 3.11 installer...
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $webClient = New-Object System.Net.WebClient; $webClient.DownloadFile('%PYTHON_URL%', '%PYTHON_INSTALLER%'); $webClient.Dispose(); }"

if not exist "%PYTHON_INSTALLER%" (
    echo [ERROR] Failed to download Python installer
    pause
    exit /b 1
)

echo Running Python 3.11 installer...
echo.
start /wait "" "%PYTHON_INSTALLER%" /passive PrependPath=1 Include_test=0

if !errorLevel! neq 0 (
    echo [ERROR] Python installation failed
    pause
    exit /b 1
)

echo [OK] Python 3.11 installed
echo.
echo Continuing installation with Python 3.11...
set PYTHON_CMD=py -3.11
echo.
goto :gpu_check
