@echo off
REM ============================================================================
REM  Advanced Tape Restorer v2.0 - Release Package Builder
REM ============================================================================

echo.
echo ===============================================
echo  Advanced Tape Restorer v2.0
echo  Release Package Builder
echo ===============================================
echo.

REM Set version
set VERSION=2.0.0

REM Set directories
set BUILD_DIR=dist
set RELEASE_DIR=Release
set PACKAGE_NAME=Advanced_Tape_Restorer_v2.0.0_Release

echo Building release package: %PACKAGE_NAME%.zip
echo.

REM Check if EXE exists
if not exist "%BUILD_DIR%\Advanced_Tape_Restorer_v2.exe" (
    echo ERROR: Advanced_Tape_Restorer_v2.exe not found in dist folder!
    echo Please build the application first using: build.bat
    echo.
    pause
    exit /b 1
)

REM Create Release directory if it doesn't exist
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

echo [1/5] Copying executable...
copy "%BUILD_DIR%\Advanced_Tape_Restorer_v2.exe" "%RELEASE_DIR%\" >nul

echo [2/5] Copying documentation...
REM Documentation files already in Release folder

echo [3/5] Copying configuration...
if exist "config\default_settings.json" (
    if not exist "%RELEASE_DIR%\config" mkdir "%RELEASE_DIR%\config"
    copy "config\default_settings.json" "%RELEASE_DIR%\config\" >nul
)

echo [4/5] Copying additional documentation...
if exist "docs\ARCHITECTURE.md" copy "docs\ARCHITECTURE.md" "%RELEASE_DIR%\" >nul
if exist "docs\CAPTURE_GUIDE.md" copy "docs\CAPTURE_GUIDE.md" "%RELEASE_DIR%\" >nul
if exist "docs\THIRD_PARTY_LICENSES.md" copy "docs\THIRD_PARTY_LICENSES.md" "%RELEASE_DIR%\" >nul

echo [5/5] Creating ZIP archive...

REM Create ZIP using PowerShell
powershell -command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

if exist "%PACKAGE_NAME%.zip" (
    echo.
    echo ===============================================
    echo  SUCCESS!
    echo ===============================================
    echo.
    echo Release package created: %PACKAGE_NAME%.zip
    echo.
    
    REM Show file size
    for %%F in ("%PACKAGE_NAME%.zip") do (
        set /a "size=%%~zF / 1048576"
        echo Package size: !size! MB
    )
    
    echo.
    echo Package contents:
    echo   - Advanced_Tape_Restorer_v2.exe
    echo   - Setup scripts (VapourSynth, FFmpeg, Prerequisites)
    echo   - Quick start guide
    echo   - Troubleshooting guide
    echo   - Complete documentation
    echo   - Configuration files
    echo.
    echo This package is ready for distribution!
    echo.
) else (
    echo.
    echo ERROR: Failed to create ZIP archive
    echo.
)

pause
