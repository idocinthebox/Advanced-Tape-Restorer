@echo off
REM Build complete distribution package for Advanced Tape Restorer v4.0
REM Creates installer-ready folder structure with EXE and documentation

setlocal enabledelayedexpansion

echo ========================================
echo Advanced Tape Restorer v4.0
echo Distribution Package Builder
echo ========================================
echo.

REM Configuration
set "VERSION=4.0"
set "RELEASE_DIR=Advanced_Tape_Restorer_v%VERSION%_Release"
set "DIST_DIR=dist"
set "EXE_NAME=Advanced_Tape_Restorer_v4.0.exe"

REM Step 1: Clean previous builds
echo [Step 1/6] Cleaning previous builds...
if exist "%RELEASE_DIR%" (
    echo Removing old release folder...
    rd /s /q "%RELEASE_DIR%"
)
if exist "%DIST_DIR%" (
    echo Removing old dist folder...
    rd /s /q "%DIST_DIR%"
)
if exist "build" (
    echo Removing old build folder...
    rd /s /q "build"
)
echo.

REM Step 2: Build executable with PyInstaller
echo [Step 2/6] Building executable with PyInstaller...
if not exist "main.spec" (
    echo ERROR: main.spec not found!
    echo Please ensure main.spec exists in the current directory.
    pause
    exit /b 1
)

pyinstaller --noconfirm --clean main.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

if not exist "%DIST_DIR%\%EXE_NAME%" (
    echo ERROR: Executable not found at %DIST_DIR%\%EXE_NAME%
    pause
    exit /b 1
)
echo Build successful!
echo.

REM Step 3: Create release directory structure
echo [Step 3/6] Creating release directory structure...
mkdir "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%\UTILITIES"
mkdir "%RELEASE_DIR%\DOCUMENTATION"
echo.

REM Step 4: Copy executable
echo [Step 4/6] Copying executable...
copy "%DIST_DIR%\%EXE_NAME%" "%RELEASE_DIR%\"
if errorlevel 1 (
    echo ERROR: Failed to copy executable!
    pause
    exit /b 1
)
echo.

REM Step 5: Copy configuration files
echo [Step 5/6] Copying configuration and documentation files...

REM Copy config files if they exist
if exist "restoration_presets.json" copy "restoration_presets.json" "%RELEASE_DIR%\"
if exist "restoration_settings.json" copy "restoration_settings.json" "%RELEASE_DIR%\"

REM Copy utilities
if exist "UTILITIES\Force_Cache_Cleanup.bat" copy "UTILITIES\Force_Cache_Cleanup.bat" "%RELEASE_DIR%\UTILITIES\"
if exist "UTILITIES\Launch_With_Console.bat" copy "UTILITIES\Launch_With_Console.bat" "%RELEASE_DIR%\UTILITIES\"
if exist "UTILITIES\README_UTILITIES.md" copy "UTILITIES\README_UTILITIES.md" "%RELEASE_DIR%\UTILITIES\"
if exist "Emergency_Cleanup.ps1" copy "Emergency_Cleanup.ps1" "%RELEASE_DIR%\UTILITIES\"

REM Copy documentation
if exist "QUICK_START_GUIDE.md" copy "QUICK_START_GUIDE.md" "%RELEASE_DIR%\"
if exist "README.md" copy "README.md" "%RELEASE_DIR%\DOCUMENTATION\"
if exist "REAL_CAPTURE_HARDWARE_GUIDE.md" copy "REAL_CAPTURE_HARDWARE_GUIDE.md" "%RELEASE_DIR%\DOCUMENTATION\"
if exist "CAPTURE_IMPLEMENTATION_SUMMARY.md" copy "CAPTURE_IMPLEMENTATION_SUMMARY.md" "%RELEASE_DIR%\DOCUMENTATION\"
if exist "START_HERE.md" copy "START_HERE.md" "%RELEASE_DIR%\DOCUMENTATION\"
if exist "CHANGELOG.txt" copy "CHANGELOG.txt" "%RELEASE_DIR%\DOCUMENTATION\"

echo.

REM Step 6: Create quick start readme
echo [Step 6/6] Creating distribution README...
(
echo # Advanced Tape Restorer v4.0
echo.
echo ## Quick Start
echo.
echo 1. **Double-click `Advanced_Tape_Restorer_v4.0.exe`** to launch
echo 2. Install prerequisites:
echo    - FFmpeg ^(required^)
echo    - VapourSynth R73 ^(required^)
echo    - CUDA 11.8/12.1 ^(optional, for AI features^)
echo 3. Check QUICK_START_GUIDE.md for detailed setup
echo.
echo ## What's New in v4.0
echo.
echo - **Real Capture Hardware Support**
echo   - DirectShow device detection
echo   - Analog capture ^(VHS, Hi8, S-Video, Component^)
echo   - DV/FireWire capture
echo   - Crossbar input selection
echo - **Lazy device loading** - Faster startup
echo - **Built-in cleanup** - No manual cache clearing needed
echo.
echo ## Troubleshooting
echo.
echo If the app hangs or behaves strangely:
echo 1. Run `UTILITIES\Force_Cache_Cleanup.bat`
echo 2. Restart the application
echo 3. Check DOCUMENTATION folder for detailed guides
echo.
echo For debug mode with console output:
echo - Run `UTILITIES\Launch_With_Console.bat`
echo.
echo ## System Requirements
echo.
echo **Required:**
echo - Windows 7/10/11 ^(64-bit^)
echo - FFmpeg 6.0+
echo - VapourSynth R73 ^(R65+ compatible^)
echo.
echo **Optional ^(for AI features^):**
echo - CUDA 11.8 or 12.1
echo - 8GB+ RAM ^(16GB recommended for AI upscaling^)
echo - NVIDIA GPU with 6GB+ VRAM
echo.
echo ## Documentation
echo.
echo - `QUICK_START_GUIDE.md` - Initial setup instructions
echo - `DOCUMENTATION/README.md` - Full user manual
echo - `DOCUMENTATION/REAL_CAPTURE_HARDWARE_GUIDE.md` - Capture device setup
echo - `UTILITIES/README_UTILITIES.md` - Troubleshooting utilities
echo.
echo ## Support
echo.
echo - GitHub: [Your GitHub URL]
echo - Issues: [Your Issues URL]
echo - Wiki: [Your Wiki URL]
) > "%RELEASE_DIR%\README.txt"

echo.
echo ========================================
echo Distribution package created successfully!
echo ========================================
echo.
echo Location: %RELEASE_DIR%\
echo.
echo Contents:
dir /b "%RELEASE_DIR%"
echo.
echo Next steps:
echo 1. Test the executable in the release folder
echo 2. Create installer with NSIS or Inno Setup
echo 3. Distribute!
echo.
pause
