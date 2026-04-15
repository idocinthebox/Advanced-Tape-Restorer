@echo off
REM ==============================================================================
REM  Advanced Tape Restorer v3.1 - Prerequisites Checker
REM  Verifies all required components are installed correctly
REM ==============================================================================

title Advanced Tape Restorer v3.1 - Prerequisites Check

setlocal enabledelayedexpansion

cls
color 0B
echo.
echo ================================================================================
echo   ADVANCED TAPE RESTORER v3.1 - PREREQUISITES CHECK
echo ================================================================================
echo.
echo Checking required components...
echo.

set ALL_OK=1

REM ============================================================================
REM Check FFmpeg
REM ============================================================================

echo Checking FFmpeg...
where ffmpeg >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] FFmpeg found in PATH
    for /f "delims=" %%i in ('where ffmpeg') do echo       Location: %%i
    for /f "tokens=3" %%v in ('ffmpeg -version 2^>^&1 ^| findstr "ffmpeg version"') do echo       Version: %%v
) else (
    echo   [MISSING] FFmpeg not found
    echo   Install with: Setup\Install_Prerequisites_Auto.bat
    set ALL_OK=0
)
echo.

REM ============================================================================
REM Check VapourSynth
REM ============================================================================

echo Checking VapourSynth...
where vspipe >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] VapourSynth found in PATH
    for /f "delims=" %%i in ('where vspipe') do echo       Location: %%i
    vspipe --version 2>nul
) else (
    echo   [MISSING] VapourSynth not found
    echo   Install with: Setup\Install_Prerequisites_Auto.bat
    set ALL_OK=0
)
echo.

REM ============================================================================
REM Check Python (Optional)
REM ============================================================================

echo Checking Python (optional for AI features)...
where python >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] Python found in PATH
    for /f "delims=" %%i in ('where python') do echo       Location: %%i
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo       Version: %%v
) else (
    echo   [INFO] Python not found (optional)
    echo   Not required for basic features
    echo   Needed only for: AI model installation, plugin management
)
echo.

REM ============================================================================
REM Check VapourSynth Plugins (Optional)
REM ============================================================================

echo Checking VapourSynth Plugins (optional)...
if exist "%APPDATA%\VapourSynth\plugins64" (
    echo   [INFO] Plugin directory exists: %APPDATA%\VapourSynth\plugins64
    dir /b "%APPDATA%\VapourSynth\plugins64\*.dll" 2>nul | find /c /v "" > nul
    if !errorLevel! equ 0 (
        echo   [OK] Plugins found
    ) else (
        echo   [INFO] No plugins installed yet
    )
) else (
    echo   [INFO] Plugin directory not found (will be created on first use)
)
echo.

REM ============================================================================
REM Check NVIDIA GPU (Optional for AI)
REM ============================================================================

echo Checking NVIDIA GPU (optional for AI features)...
where nvidia-smi >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] NVIDIA GPU driver detected
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>nul
) else (
    echo   [INFO] NVIDIA GPU not detected
    echo   AI features require NVIDIA RTX GPU (3060 or newer)
)
echo.

REM ============================================================================
REM Summary
REM ============================================================================

echo ================================================================================
echo   SUMMARY
echo ================================================================================
echo.

if !ALL_OK! equ 1 (
    echo   RESULT: ALL REQUIRED COMPONENTS INSTALLED
    echo ================================================================================
    echo.
    echo You're ready to use Advanced Tape Restorer v3.1!
    echo.
    echo Next steps:
        echo   1. Launch Advanced_Tape_Restorer_v3.1.exe
        echo   2. Try File ^> Select Input to process a video
        echo   3. Check Documentation\ folder for guides
    echo.
) else (
    echo   RESULT: SOME COMPONENTS MISSING
    echo ================================================================================
    echo.
    echo To install missing components:
    echo   Run: Setup\Install_Prerequisites_Auto.bat
    echo.
    echo Or install manually:
    echo   - FFmpeg: https://ffmpeg.org/download.html
    echo   - VapourSynth: https://github.com/vapoursynth/vapoursynth/releases
    echo.
)

echo ================================================================================
pause
