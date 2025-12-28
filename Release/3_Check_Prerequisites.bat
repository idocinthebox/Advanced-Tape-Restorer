@echo off
REM ============================================================================
REM  Advanced Tape Restorer v2.0 - Prerequisites Checker
REM ============================================================================

echo.
echo ===============================================
echo  Advanced Tape Restorer v2.0
echo  Prerequisites Verification
echo ===============================================
echo.
echo Checking required dependencies...
echo.

set ALL_OK=1

REM Check FFmpeg
echo [1/3] Checking FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] FFmpeg not found in PATH
    echo          Run "2_Install_FFmpeg.bat" to install
    set ALL_OK=0
) else (
    echo   [OK]   FFmpeg found
    for /f "tokens=*" %%i in ('ffmpeg -version ^| findstr "ffmpeg version"') do echo          %%i
)

echo.

REM Check FFprobe
echo [2/3] Checking FFprobe...
where ffprobe >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] FFprobe not found in PATH
    echo          This is usually installed with FFmpeg
    set ALL_OK=0
) else (
    echo   [OK]   FFprobe found
)

echo.

REM Check VapourSynth
echo [3/3] Checking VapourSynth...
where vspipe >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] vspipe not found in PATH
    echo          Run "1_Install_VapourSynth.bat" to install
    set ALL_OK=0
) else (
    echo   [OK]   VapourSynth found
    for /f "tokens=*" %%i in ('vspipe --version 2^>^&1 ^| findstr "VapourSynth"') do echo          %%i
)

echo.
echo ===============================================

if %ALL_OK%==1 (
    echo.
    echo  SUCCESS: All prerequisites are installed!
    echo.
    echo  You can now run:
    echo    Advanced_Tape_Restorer_v2.exe
    echo.
    echo ===============================================
    echo.
    
    REM Offer to launch the application
    echo Would you like to launch Advanced Tape Restorer now?
    echo.
    choice /C YN /N /M "Launch application? (Y/N): "
    if not errorlevel 2 (
        echo.
        echo Starting Advanced Tape Restorer v2.0...
        start "" "Advanced_Tape_Restorer_v2.exe"
    )
) else (
    echo.
    echo  WARNING: Some prerequisites are missing!
    echo.
    echo  Please install missing dependencies:
    echo    1. Run "1_Install_VapourSynth.bat" if needed
    echo    2. Run "2_Install_FFmpeg.bat" if needed
    echo    3. Run this script again to verify
    echo.
    echo  NOTE: After installing, you may need to:
    echo    - Restart this command prompt
    echo    - Log out and log back in (Windows)
    echo    - Restart your computer
    echo.
    echo ===============================================
    echo.
)

pause
exit /b 0
