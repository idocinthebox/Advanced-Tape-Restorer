@echo off
REM Advanced Tape Restorer v4.0 - FFmpeg Installer
REM Installs FFmpeg for video encoding and capture
echo ========================================
echo Advanced Tape Restorer v4.0
echo FFmpeg Installation
echo ========================================
echo.

REM Check if already installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] FFmpeg is already installed!
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo No installation needed.
    pause
    exit /b 0
)

echo FFmpeg is required for:
echo   - Video encoding (H.264, H.265, ProRes, etc.)
echo   - Hardware capture (DirectShow devices)
echo   - Audio processing
echo.
echo Installation options:
echo   1. Winget (recommended - automatic)
echo   2. Manual download
echo.

choice /C 12 /N /M "Choose option (1 or 2): "
set choice=%ERRORLEVEL%

if %choice%==1 goto :winget
if %choice%==2 goto :manual

:winget
echo.
echo Installing FFmpeg via Winget...
winget install --id Gyan.FFmpeg --source winget --accept-source-agreements --accept-package-agreements

where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Installation failed!
    echo Please restart your terminal or computer, then try again.
    echo.
    echo Or try manual installation: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

echo.
echo [SUCCESS] FFmpeg installed successfully!
ffmpeg -version | findstr "ffmpeg version"
goto :end

:manual
echo.
echo Manual Installation Steps:
echo.
echo 1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
echo    (Choose: ffmpeg-release-essentials.zip)
echo.
echo 2. Extract to: C:\ffmpeg\
echo.
echo 3. Add to PATH:
echo    - Right-click This PC ^> Properties
echo    - Advanced system settings ^> Environment Variables
echo    - Edit "Path" under System variables
echo    - Add: C:\ffmpeg\bin
echo.
echo 4. Restart your terminal/computer
echo.
echo 5. Verify: ffmpeg -version
echo.
start https://www.gyan.dev/ffmpeg/builds/

:end
echo.
echo ========================================
echo Installation Complete
echo ========================================
pause
