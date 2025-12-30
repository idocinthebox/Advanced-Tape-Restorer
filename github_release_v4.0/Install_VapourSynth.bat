@echo off
REM Advanced Tape Restorer v4.0 - VapourSynth Installer
REM Installs VapourSynth for video filtering (QTGMC deinterlacing)
echo ========================================
echo Advanced Tape Restorer v4.0
echo VapourSynth Installation
echo ========================================
echo.

REM Check if already installed
where vspipe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] VapourSynth is already installed!
    vspipe --version
    echo.
    echo To install plugins, run: Install_VS_Plugins.bat
    pause
    exit /b 0
)

echo VapourSynth is required for:
echo   - QTGMC deinterlacing (VHS/Hi8 tapes)
echo   - Denoise filters (BM3D, FFT3D)
echo   - Color correction and sharpening
echo.
echo IMPORTANT: VapourSynth R73 recommended
echo   (R73 is the last version with Windows 7 support)
echo.

echo Opening VapourSynth download page...
echo.
echo Download: VapourSynth64-Portable-R73.7z
echo Extract to: C:\VapourSynth\
echo.
echo After extraction, add to PATH:
echo   C:\VapourSynth
echo.
echo Then restart terminal and run: Install_VS_Plugins.bat
echo.

start https://github.com/vapoursynth/vapoursynth/releases/tag/R73

echo.
echo ========================================
echo Download Started
echo ========================================
echo.
echo After installation:
echo   1. Extract VapourSynth to C:\VapourSynth\
echo   2. Add C:\VapourSynth to PATH
echo   3. Restart terminal
echo   4. Run: Install_VS_Plugins.bat
echo.
pause
