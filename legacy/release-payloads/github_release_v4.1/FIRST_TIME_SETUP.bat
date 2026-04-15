@echo off
REM ================================================================================
REM  Advanced Tape Restorer v3.1 - One-Click Setup Wizard
REM  Installs all required prerequisites automatically
REM ================================================================================

title Advanced Tape Restorer v3.1 - First Time Setup

color 0B
cls
echo.
echo ================================================================================
echo   ADVANCED TAPE RESTORER v3.1 - FIRST TIME SETUP
echo ================================================================================
echo.
echo This wizard will automatically download and install all required components:
echo.
echo   [1] FFmpeg (video encoding) - ~100 MB
echo   [2] VapourSynth (video processing) - ~50 MB  
echo   [3] VapourSynth Plugins (QTGMC, filters) - ~30 MB
echo.
echo Total download size: ~180 MB
echo Installation time: 5-10 minutes
echo.
echo ================================================================================
echo.
pause

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the automatic installer from the script's directory
if exist "%SCRIPT_DIR%Setup\Install_Prerequisites_Auto.bat" (
    call "%SCRIPT_DIR%Setup\Install_Prerequisites_Auto.bat"
) else (
    echo [ERROR] Setup scripts not found!
    echo.
    echo Expected location: %SCRIPT_DIR%Setup\Install_Prerequisites_Auto.bat
    echo Current directory: %CD%
    echo.
    echo Please ensure Setup folder exists in the same directory as this script.
    pause
    exit /b 1
)

cls
echo.
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo   1. RESTART YOUR COMPUTER (required for PATH changes)
echo   2. After restart, double-click: Advanced_Tape_Restorer_v3.1.exe
echo   3. Start restoring your videos!
echo.
echo For advanced features (AI upscaling):
echo   - Requires NVIDIA RTX GPU (3060 or newer)
echo   - Run %SCRIPT_DIR%Setup\Install_PyTorch_CUDA.bat
echo.
echo ================================================================================
pause
