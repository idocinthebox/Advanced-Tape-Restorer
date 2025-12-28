@echo off
REM ============================================================
REM Build Distribution Package for Advanced Tape Restorer v3.2
REM ============================================================
REM This script:
REM 1. Builds the EXE with PyInstaller
REM 2. Creates distribution folder structure
REM 3. Copies all necessary files
REM 4. Packages setup scripts and documentation
REM ============================================================

setlocal EnableDelayedExpansion
set VERSION=3.2
set DIST_DIR=dist_package\Advanced_Tape_Restorer_v3.2_Release
set SRC_DIR=%~dp0

echo.
echo ============================================================
echo   Advanced Tape Restorer v3.2 - Distribution Builder
echo ============================================================
echo.

REM Clean previous build
echo [1/7] Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist dist_package\Advanced_Tape_Restorer_v3.2_Release.zip del /q dist_package\Advanced_Tape_Restorer_v3.2_Release.zip

REM Build EXE with PyInstaller
echo.
echo [2/7] Building EXE with PyInstaller...
echo.
pyinstaller main.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

REM Create distribution folder structure
echo.
echo [3/7] Creating distribution folder structure...
mkdir %DIST_DIR%
mkdir %DIST_DIR%\DISTRIBUTION
mkdir %DIST_DIR%\DISTRIBUTION\Setup
mkdir %DIST_DIR%\DISTRIBUTION\Documentation

REM Copy EXE
echo.
echo [4/7] Copying executable...
copy dist\Advanced_Tape_Restorer_v3.2.exe %DIST_DIR%\Advanced_Tape_Restorer_v3.2.exe
if errorlevel 1 (
    echo ERROR: Failed to copy EXE!
    pause
    exit /b 1
)

REM Copy essential configuration files
echo.
echo [5/7] Copying configuration files...
copy restoration_presets.json %DIST_DIR%\
copy restoration_settings.json %DIST_DIR%\
if exist tape_restorer_config.json copy tape_restorer_config.json %DIST_DIR%\

REM Copy setup scripts
echo.
echo [6/7] Copying setup scripts and documentation...
copy DISTRIBUTION\Setup\*.bat %DIST_DIR%\DISTRIBUTION\Setup\
copy DISTRIBUTION\FIRST_TIME_SETUP.bat %DIST_DIR%\
copy DISTRIBUTION\README.txt %DIST_DIR%\
copy DISTRIBUTION\Quick_Start.txt %DIST_DIR%\
copy DISTRIBUTION\QUICK_SETUP.txt %DIST_DIR%\
if exist DISTRIBUTION\PACKAGE_INFO.txt copy DISTRIBUTION\PACKAGE_INFO.txt %DIST_DIR%\
if exist DISTRIBUTION\PLUGIN_INSTALLATION_FIX.md copy DISTRIBUTION\PLUGIN_INSTALLATION_FIX.md %DIST_DIR%\

REM Copy documentation
if exist README.md copy README.md %DIST_DIR%\DISTRIBUTION\Documentation\
if exist QUICK_START_GUIDE.md copy QUICK_START_GUIDE.md %DIST_DIR%\DISTRIBUTION\Documentation\
if exist CHANGELOG_V3.2.md copy CHANGELOG_V3.2.md %DIST_DIR%\DISTRIBUTION\Documentation\
if exist README_V3.2.md copy README_V3.2.md %DIST_DIR%\DISTRIBUTION\Documentation\
if exist V3.2_DEVELOPMENT_COMPLETE.md copy V3.2_DEVELOPMENT_COMPLETE.md %DIST_DIR%\DISTRIBUTION\Documentation\

REM Create release info file
echo.
echo [7/7] Creating release info...
(
echo Advanced Tape Restorer v3.2.0
echo =============================
echo.
echo Build Date: %date% %time%
echo.
echo CRITICAL FIXES IN v3.2:
echo - Direct VapourSynth plugin usage ^(no Python package dependencies^)
echo - Fixed virgin install dependency cascade errors
echo - QComboBox dropdown visibility improvements
echo - Improved splash screen text visibility
echo - RealESRGAN tile parameter fix
echo.
echo CONTENTS:
echo - Advanced_Tape_Restorer_v3.2.exe
echo - restoration_presets.json
echo - restoration_settings.json
echo - DISTRIBUTION/Setup/ ^(installation batch files^)
echo - DISTRIBUTION/Documentation/ ^(user guides^)
echo.
echo INSTALLATION:
echo 1. Run FIRST_TIME_SETUP.bat
echo 2. Follow the on-screen instructions
echo 3. Launch Advanced_Tape_Restorer_v3.2.exe
echo.
echo For detailed setup instructions, see Quick_Start.txt
echo.
) > %DIST_DIR%\RELEASE_NOTES_v3.2.txt

echo.
echo ============================================================
echo   BUILD COMPLETE!
echo ============================================================
echo.
echo Distribution package created at:
echo %DIST_DIR%
echo.
echo Files included:
dir /b %DIST_DIR%
echo.
echo Setup scripts:
dir /b %DIST_DIR%\DISTRIBUTION\Setup
echo.
echo.
echo To create ZIP archive, run:
echo cd dist_package
echo tar -a -c -f Advanced_Tape_Restorer_v3.2_Release.zip Advanced_Tape_Restorer_v3.2_Release
echo.
pause
endlocal
