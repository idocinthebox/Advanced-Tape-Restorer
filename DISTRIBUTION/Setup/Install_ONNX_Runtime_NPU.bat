@echo off
REM ==============================================================================
REM  Advanced Tape Restorer v4.1 - ONNX Runtime + NPU Installer
REM  Installs ONNX Runtime with DirectML support for NPU acceleration
REM ==============================================================================

title Advanced Tape Restorer v4.1 - ONNX Runtime NPU Installer

setlocal enabledelayedexpansion

cls
color 0B
echo.
echo ================================================================================
echo   ONNX RUNTIME + NPU INSTALLER - Advanced Tape Restorer v4.1
echo ================================================================================
echo.
echo ================================================================================
echo   NEW: NPU ACCELERATION FOR AI MODELS
echo ================================================================================
echo.
echo This installer enables NPU (Neural Processing Unit) acceleration for:
echo   - RealESRGAN AI upscaling (98%% smaller models)
echo   - RIFE frame interpolation (99%% smaller models)
echo   - BasicVSR++ video restoration
echo   - SwinIR transformer upscaling
echo.
echo BENEFITS:
echo   - Offloads AI from GPU (frees 6-8GB VRAM)
echo   - Enables multiple AI models simultaneously
echo   - Works with models that failed due to VRAM limits
echo   - Lower power consumption (5-10W vs 100-200W GPU)
echo   - Can process 4K video that previously failed
echo.
echo ================================================================================
echo.
pause
echo.

REM ==============================================================================
REM Check Python Installation
REM ==============================================================================

echo Detecting Python installation...
echo.

set PYTHON_CMD=
set PYTHON_VERSION=

REM Try common Python commands in order of preference
for %%p in (py python python3) do (
    %%p --version >nul 2>&1
    if !errorLevel! equ 0 (
        set PYTHON_CMD=%%p
        goto :python_found
    )
)

:python_found
if not defined PYTHON_CMD (
    echo [ERROR] Python not found
    echo.
    echo Please install Python 3.9-3.13 from python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python found: %PYTHON_CMD%
echo.

REM Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM ==============================================================================
REM Check for NPU Support (AMD Ryzen AI, Intel Core Ultra)
REM ==============================================================================

echo Checking for NPU hardware...
echo.

set NPU_DETECTED=0

REM Check for AMD Ryzen AI NPU (XDNA)
wmic path Win32_PnPEntity where "Name like '%%IPU%%' or Name like '%%NPU%%'" get Name 2>nul | findstr /i "AMD" >nul
if %errorLevel% equ 0 (
    echo [OK] AMD Ryzen AI NPU detected
    set NPU_DETECTED=1
)

REM Check for Intel Core Ultra NPU
wmic path Win32_PnPEntity where "Name like '%%IPU%%' or Name like '%%NPU%%'" get Name 2>nul | findstr /i "Intel" >nul
if %errorLevel% equ 0 (
    echo [OK] Intel Core Ultra NPU detected
    set NPU_DETECTED=1
)

if %NPU_DETECTED% equ 0 (
    echo [INFO] No dedicated NPU detected
    echo.
    echo DirectML will still work and can use:
    echo   - NVIDIA GPU (via DirectML)
    echo   - AMD GPU (via DirectML)
    echo   - Intel GPU (via DirectML)
    echo   - CPU (fallback, slow)
    echo.
)
echo.

REM ==============================================================================
REM Check for GPU (Optional)
REM ==============================================================================

echo Checking for GPU support...
echo.

set GPU_AVAILABLE=0

REM Check NVIDIA GPU
nvidia-smi >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] NVIDIA GPU detected
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    set GPU_AVAILABLE=1
)

REM Check AMD GPU
where rocm-smi >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] AMD GPU detected
    set GPU_AVAILABLE=1
)

if %GPU_AVAILABLE% equ 0 (
    echo [INFO] No discrete GPU detected
    echo DirectML will use CPU for AI inference (slower)
)
echo.

REM ==============================================================================
REM Display Installation Plan
REM ==============================================================================

echo ================================================================================
echo   Installation Plan
echo ================================================================================
echo.
echo Will install:
echo   1. onnxruntime-directml (ONNX Runtime with NPU/GPU support)
echo   2. ONNX model converter tools (already included)
echo.
echo This replaces the CPU-only onnxruntime if installed.
echo.
if %NPU_DETECTED% equ 1 (
    echo Primary execution: NPU (Ryzen AI / Core Ultra)
    echo Fallback: GPU or CPU
) else if %GPU_AVAILABLE% equ 1 (
    echo Primary execution: GPU (via DirectML)
    echo Fallback: CPU
) else (
    echo Primary execution: CPU only
)
echo.
echo Download size: ~100 MB
echo Installation time: 2-3 minutes
echo.
pause
echo.

REM ==============================================================================
REM Install ONNX Runtime with DirectML
REM ==============================================================================

echo ================================================================================
echo   Installing ONNX Runtime with DirectML...
echo ================================================================================
echo.

REM Uninstall CPU-only version if present
echo Checking for existing onnxruntime installation...
%PYTHON_CMD% -m pip show onnxruntime >nul 2>&1
if %errorLevel% equ 0 (
    echo Uninstalling CPU-only onnxruntime...
    %PYTHON_CMD% -m pip uninstall onnxruntime -y
    echo.
)

REM Uninstall GPU version if present (conflicts with DirectML)
%PYTHON_CMD% -m pip show onnxruntime-gpu >nul 2>&1
if %errorLevel% equ 0 (
    echo Uninstalling onnxruntime-gpu (replaced by DirectML)...
    %PYTHON_CMD% -m pip uninstall onnxruntime-gpu -y
    echo.
)

echo Installing onnxruntime-directml...
echo This may take 2-3 minutes...
echo.
%PYTHON_CMD% -m pip install onnxruntime-directml

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Installation failed
    echo.
    echo Try manual installation:
    echo   python -m pip install onnxruntime-directml
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] ONNX Runtime with DirectML installed
echo.

REM ==============================================================================
REM Verify Installation
REM ==============================================================================

echo ================================================================================
echo   Verifying Installation
echo ================================================================================
echo.

echo Checking available execution providers...
echo.
%PYTHON_CMD% -c "import onnxruntime as ort; print('ONNX Runtime version:', ort.__version__); print('Available providers:', ort.get_available_providers())"

echo.
echo.

REM Check if DirectML provider is available
%PYTHON_CMD% -c "import onnxruntime as ort; exit(0 if 'DmlExecutionProvider' in ort.get_available_providers() else 1)" 2>nul

if %errorLevel% equ 0 goto :directml_success
goto :directml_not_found

:directml_success
echo [OK] DirectML provider is available!
echo.
if %NPU_DETECTED% equ 1 (
    echo Your NPU is ready for AI inference!
) else (
    echo Your GPU/CPU is ready for DirectML acceleration!
)
echo.
echo ONNX models will automatically use:
echo   1. NPU (if available) - Lowest power, frees GPU VRAM
echo   2. GPU (if available) - Fastest inference
echo   3. CPU (fallback) - Slowest but always works
echo.
goto :installation_complete

:directml_not_found
echo [WARNING] DirectML provider not found
echo.
echo Available providers: CPU only
echo.
echo Possible causes:
echo   - Windows version too old (requires Windows 10 1903+)
echo   - Graphics driver outdated
echo   - DirectX 12 not supported
echo.
echo Solutions:
echo   - Update Windows to latest version
echo   - Update GPU drivers
echo   - Restart computer
echo.
echo AI models will still work but only on CPU (slower).
echo.

:installation_complete
echo ================================================================================
echo   INSTALLATION COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Run Advanced Tape Restorer
echo   2. Go to Output tab
echo   3. Set "Inference Mode" to "ONNX" or "Auto"
echo   4. Process a video with AI upscaling/interpolation
echo.
echo Your converted ONNX models are located at:
echo   %LOCALAPPDATA%\Advanced_Tape_Restorer\onnx_models\
echo.
if %NPU_DETECTED% equ 1 (
    echo Benefits you'll see:
    echo   - GPU VRAM freed up (6-8GB saved)
    echo   - Can run RealESRGAN 4x + RIFE 2x together
    echo   - 4K video processing now possible
    echo   - Lower GPU temperature and power usage
    echo.
)
echo For more information, see:
echo   - ONNX_CONVERSION_COMPLETE.md
echo   - NPU_VS_CUDA_COMPATIBILITY.md
echo   - ENABLE_NPU_QUICK_START.md
echo.
pause
exit /b 0
