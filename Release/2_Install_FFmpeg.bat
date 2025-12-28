@echo off
REM ============================================================================
REM  Advanced Tape Restorer v2.0 - FFmpeg Installation Helper
REM ============================================================================

echo.
echo ===============================================
echo  FFmpeg Installation Helper
echo ===============================================
echo.
echo This script will help you install FFmpeg (64-bit)
echo.
echo FFmpeg is used for video encoding and format conversion.
echo.
echo -----------------------------------------------
echo  OPTION 1: Automatic Setup (Recommended)
echo -----------------------------------------------
echo.
echo Press 'A' to download and configure FFmpeg automatically
echo This will:
echo   - Download FFmpeg essentials (small, 80MB)
echo   - Extract to C:\ffmpeg
echo   - Add to system PATH
echo.
echo -----------------------------------------------
echo  OPTION 2: Manual Installation
echo -----------------------------------------------
echo.
echo Press 'M' if you already have FFmpeg installed
echo or want to install it manually
echo.
echo Press 'Q' to quit
echo.

choice /C AMQ /N /M "Your choice (A/M/Q): "

if errorlevel 3 goto :quit
if errorlevel 2 goto :manual
if errorlevel 1 goto :auto

:auto
echo.
echo ===============================================
echo  Automatic FFmpeg Setup
echo ===============================================
echo.

REM Check if curl is available
where curl >nul 2>&1
if errorlevel 1 (
    echo ERROR: curl not found in your system.
    echo Using manual method instead.
    timeout /t 2 >nul
    goto :manual
)

REM Download FFmpeg essentials build
set DOWNLOAD_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
set ZIPFILE=%TEMP%\ffmpeg-essentials.zip
set INSTALL_DIR=C:\ffmpeg

echo Downloading FFmpeg essentials (~80MB)...
echo This may take a few minutes...
echo.

curl -L -o "%ZIPFILE%" "%DOWNLOAD_URL%"

if not exist "%ZIPFILE%" (
    echo.
    echo Download failed. Using manual method instead.
    timeout /t 2 >nul
    goto :manual
)

echo.
echo Download complete! Extracting...
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Extract using PowerShell (built into Windows 10+)
powershell -command "Expand-Archive -Path '%ZIPFILE%' -DestinationPath '%INSTALL_DIR%' -Force"

REM Find the extracted folder (it has version number in name)
for /d %%i in ("%INSTALL_DIR%\ffmpeg-*") do (
    REM Move bin folder contents to main directory
    if exist "%%i\bin" (
        xcopy "%%i\bin\*" "%INSTALL_DIR%\bin\" /E /I /Y >nul
        if not exist "%INSTALL_DIR%\bin\ffmpeg.exe" (
            mkdir "%INSTALL_DIR%\bin" >nul 2>&1
            move "%%i\bin\ffmpeg.exe" "%INSTALL_DIR%\bin\" >nul
            move "%%i\bin\ffprobe.exe" "%INSTALL_DIR%\bin\" >nul
            move "%%i\bin\ffplay.exe" "%INSTALL_DIR%\bin\" >nul
        )
    )
)

REM Clean up
del "%ZIPFILE%" >nul 2>&1

echo.
echo Extraction complete!
echo.

REM Add to PATH
echo Adding FFmpeg to system PATH...
echo.
echo NOTE: This requires administrator privileges.
echo If you see "Access Denied", please run this script as Administrator.
echo.

setx /M PATH "%PATH%;%INSTALL_DIR%\bin" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Could not add to system PATH automatically.
    echo This is usually because the script is not run as Administrator.
    echo.
    echo MANUAL STEPS:
    echo   1. Press Win + Pause/Break to open System Properties
    echo   2. Click "Advanced system settings"
    echo   3. Click "Environment Variables"
    echo   4. Under "System variables", select "Path" and click "Edit"
    echo   5. Click "New" and add: %INSTALL_DIR%\bin
    echo   6. Click OK on all dialogs
    echo   7. Restart this command prompt
    echo.
    pause
) else (
    echo.
    echo FFmpeg added to PATH successfully!
    echo.
    echo IMPORTANT: You must restart this command prompt for changes to take effect.
    echo Close this window and open a new one to verify installation.
    echo.
)

goto :verify

:manual
echo.
echo ===============================================
echo  Manual Installation Instructions
echo ===============================================
echo.
echo If you already have FFmpeg installed:
echo   - Make sure ffmpeg.exe is in your system PATH
echo   - Restart command prompt after adding to PATH
echo   - Run "3_Check_Prerequisites.bat" to verify
echo.
echo If you need to install FFmpeg manually:
echo.
echo 1. Download FFmpeg from:
echo    https://www.gyan.dev/ffmpeg/builds/
echo.
echo 2. Choose: "ffmpeg-release-essentials.zip"
echo.
echo 3. Extract to C:\ffmpeg (or your preferred location)
echo.
echo 4. Add to PATH:
echo    - Right-click "This PC" ^> Properties
echo    - Advanced system settings ^> Environment Variables
echo    - Edit "Path" under System variables
echo    - Add: C:\ffmpeg\bin
echo    - Restart command prompt
echo.
echo Opening download page in browser...
start https://www.gyan.dev/ffmpeg/builds/
echo.
echo Press any key after completing installation...
pause >nul

:verify
echo.
echo ===============================================
echo  Verifying Installation...
echo ===============================================
echo.

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg not found in PATH
    echo.
    echo Please:
    echo   1. Restart this command prompt
    echo   2. Run "3_Check_Prerequisites.bat" to verify
    echo.
    echo If still not found, FFmpeg may not be installed correctly.
    echo Review the manual installation instructions above.
    echo.
) else (
    echo SUCCESS: FFmpeg found!
    echo.
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo FFmpeg is ready to use!
    echo.
)

:quit
echo.
echo ===============================================
echo.
echo Next step: Run "3_Check_Prerequisites.bat"
echo.
echo ===============================================
echo.
pause
exit /b 0
