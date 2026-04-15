@echo off
REM ========================================
REM Install GPU-Accelerated NNEDI3 Plugins
REM 142x faster QTGMC deinterlacing
REM ========================================

echo.
echo ================================================================================
echo   GPU-Accelerated Deinterlacing Plugins
echo ================================================================================
echo.
echo   Performance: Up to 142x faster than CPU-based deinterlacing
echo   Plugins: nnedi3cl (OpenCL) or SNEEDIF (OpenCL/CUDA)
echo.
echo   Based on: https://forum.doom9.org/showthread.php?t=186657
echo.
echo ================================================================================
echo.

REM Check if VapourSynth is installed
where vspipe >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] VapourSynth not found!
    echo.
    echo Please install VapourSynth first using Install_VapourSynth.bat
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking VapourSynth installation...
vspipe --version
echo.

echo [2/3] Installing GPU-accelerated NNEDI3 plugins...
echo.

REM Try installing nnedi3cl (OpenCL - works with NVIDIA, AMD, Intel)
echo Installing nnedi3cl (OpenCL)...
vsrepo install nnedi3cl
if %errorlevel% equ 0 (
    echo [OK] nnedi3cl installed successfully
) else (
    echo [WARN] nnedi3cl installation failed or not in repository
)

echo.

REM Try installing SNEEDIF (newer, faster)
echo Installing SNEEDIF (OpenCL/CUDA)...
vsrepo install sneedif
if %errorlevel% equ 0 (
    echo [OK] SNEEDIF installed successfully
) else (
    echo [WARN] SNEEDIF installation failed or not in repository
)

echo.
echo ================================================================================
echo   Installation Complete
echo ================================================================================
echo.
echo   Benefits:
echo   - QTGMC deinterlacing will automatically use GPU acceleration
echo   - Up to 142x faster frame processing (871 fps vs 6 fps CPU)
echo   - Reduces CPU load during restoration
echo.
echo   Compatibility:
echo   - nnedi3cl: Works with NVIDIA, AMD (ROCm/OpenCL), Intel GPUs
echo   - SNEEDIF: Optimized for NVIDIA CUDA and AMD OpenCL
echo.
echo   The application will automatically detect and use these plugins.
echo   If not available, it will fall back to CPU processing.
echo.
echo [3/3] Verifying GPU support...
echo.

REM Check for CUDA
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] NVIDIA GPU detected - CUDA available
    nvidia-smi --query-gpu=name --format=csv,noheader
) else (
    echo [INFO] NVIDIA GPU not detected
)

REM Check for OpenCL
where clinfo >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] OpenCL detected
    clinfo -l 2>nul
) else (
    echo [INFO] clinfo not found - install GPU drivers for OpenCL support
)

echo.
echo ================================================================================
echo.
echo Manual installation (if vsrepo failed):
echo.
echo   nnedi3cl: https://github.com/HomeOfVapourSynthEvolution/VapourSynth-NNEDI3CL
echo   SNEEDIF:  https://github.com/Jaded-Encoding-Thaumaturgy/vs-sneedif
echo.
echo   Extract DLLs to: C:\Program Files\VapourSynth\plugins64\
echo.
echo ================================================================================
pause
