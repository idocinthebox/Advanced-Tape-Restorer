@echo off
REM ========================================
REM Install fpng VapourSynth Plugin
REM Ultra-fast PNG writing (142x faster)
REM ========================================

echo.
echo ================================================================================
echo   fpng - Ultra-Fast PNG Plugin for VapourSynth
echo ================================================================================
echo.
echo   Performance: 142x faster than standard PNG writing
echo   Benchmark:   871 fps vs 6 fps (standard imwri)
echo   Use case:    GFPGAN frame extraction
echo.
echo   Source: https://github.com/Mikewando/vsfpng
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

echo [2/3] Installing fpng plugin via vsrepo...
echo.
echo Note: This plugin is optional but highly recommended for GFPGAN performance
echo.

REM Install via vsrepo (VapourSynth plugin repository)
vsrepo install fpng

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo   SUCCESS! fpng plugin installed
    echo ================================================================================
    echo.
    echo   GFPGAN frame extraction will now be 142x faster!
    echo.
    echo   Performance comparison for 35,000 frame video:
    echo   - Without fpng: ~5660 seconds (94 minutes)
    echo   - With fpng:    ~40 seconds (less than 1 minute)
    echo.
    echo   The application will automatically use fpng when available.
    echo.
) else (
    echo.
    echo ================================================================================
    echo   Manual Installation Required
    echo ================================================================================
    echo.
    echo   vsrepo not available or fpng not in repository.
    echo.
    echo   Manual installation steps:
    echo   1. Download fpng from: https://github.com/Mikewando/vsfpng/releases
    echo   2. Extract vsfpng.dll to VapourSynth plugins folder
    echo   3. Typical location: C:\Program Files\VapourSynth\plugins64\
    echo.
    echo   The application will fallback to FFmpeg if fpng is not found.
    echo.
)

echo [3/3] Verifying installation...
echo.
python -c "import vapoursynth as vs; core = vs.core; print('fpng available:', hasattr(core, 'fpng'))" 2>nul
if %errorlevel% neq 0 (
    echo Unable to verify - Python import failed
    echo This is normal for PyInstaller builds
)

echo.
echo ================================================================================
pause
