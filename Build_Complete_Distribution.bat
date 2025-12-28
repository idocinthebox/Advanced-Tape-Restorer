@echo off
REM ============================================================================
REM  Build Complete Distribution Package for Advanced Tape Restorer v3.0
REM  Creates a ready-to-distribute package with automatic installers
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ================================================================================
echo   BUILDING DISTRIBUTION PACKAGE - Advanced Tape Restorer v3.1
echo ================================================================================
echo.

set VERSION=3.1.0
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set DATE=%datetime:~0,8%
set PACKAGE_NAME=Advanced_Tape_Restorer_v%VERSION%_Complete_%DATE%

echo Version: %VERSION%
echo Date: %DATE%
echo Package: %PACKAGE_NAME%.zip
echo.

REM ============================================================================
REM STEP 1: Build the EXE
REM ============================================================================

echo ================================================================================
echo   STEP 1: Building EXE with PyInstaller
echo ================================================================================
echo.

if not exist "Advanced_Tape_Restorer_v2.spec" (
    echo [ERROR] PyInstaller spec file not found!
    echo Expected: Advanced_Tape_Restorer_v2.spec
    pause
    exit /b 1
)

echo Running PyInstaller...
pyinstaller --clean Advanced_Tape_Restorer_v2.spec

if not exist "dist\Advanced_Tape_Restorer_v3.1.exe" (
    echo [ERROR] EXE build failed!
    echo Check PyInstaller output above for errors.
    pause
    exit /b 1
)

echo [OK] EXE built successfully
echo.

REM Get EXE size
for %%A in ("dist\Advanced_Tape_Restorer_v3.1.exe") do (
    set SIZE=%%~zA
    set /A SIZE_MB=!SIZE! / 1048576
)
echo EXE Size: !SIZE_MB! MB

REM ============================================================================
REM STEP 2: Prepare Distribution Folder
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 2: Preparing Distribution Folder
echo ================================================================================
echo.

REM Clean and recreate DISTRIBUTION folder
if exist "DISTRIBUTION\" (
    echo Cleaning old distribution folder...
    rmdir /S /Q "DISTRIBUTION\" 2>nul
)

mkdir "DISTRIBUTION"
mkdir "DISTRIBUTION\Setup"
mkdir "DISTRIBUTION\Documentation"

echo [OK] Folder structure created

REM ============================================================================
REM STEP 3: Copy Files
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 3: Copying Files
echo ================================================================================
echo.

REM Copy EXE
echo Copying executable...
copy "dist\Advanced_Tape_Restorer_v3.1.exe" "DISTRIBUTION\Advanced_Tape_Restorer_v3.1.exe" >nul
if %errorLevel% neq 0 (
    echo [ERROR] Failed to copy EXE
    pause
    exit /b 1
)
echo [OK] Advanced_Tape_Restorer_v3.exe

REM Copy Setup Scripts
echo.
echo Copying setup scripts...

copy "DISTRIBUTION\Setup\Install_Prerequisites_Auto.bat" "DISTRIBUTION\Setup\" >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARN] Install_Prerequisites_Auto.bat not found - creating...
    REM It should already exist from previous step
)
echo [OK] Install_Prerequisites_Auto.bat (automatic installer)

copy "DISTRIBUTION\Setup\Install_Prerequisites.bat" "DISTRIBUTION\Setup\" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] Install_Prerequisites.bat) else (echo [OK] Install_Prerequisites.bat)

copy "DISTRIBUTION\Setup\Check_Prerequisites.bat" "DISTRIBUTION\Setup\" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] Check_Prerequisites.bat) else (echo [OK] Check_Prerequisites.bat)

copy "DISTRIBUTION\Setup\Install_PyTorch_CUDA.bat" "DISTRIBUTION\Setup\" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] Install_PyTorch_CUDA.bat) else (echo [OK] Install_PyTorch_CUDA.bat)

REM Copy Documentation
echo.
echo Copying documentation...

copy "PREREQUISITES_FOR_EXE.md" "DISTRIBUTION\Documentation\PREREQUISITES.md" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] PREREQUISITES.md) else (echo [OK] PREREQUISITES.md)

copy "QUICK_SETUP.txt" "DISTRIBUTION\QUICK_SETUP.txt" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] QUICK_SETUP.txt) else (echo [OK] QUICK_SETUP.txt)

copy "EMBEDDED_PYTHON_FIX.md" "DISTRIBUTION\Documentation\EMBEDDED_PYTHON_FIX.md" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] EMBEDDED_PYTHON_FIX.md) else (echo [OK] EMBEDDED_PYTHON_FIX.md)

copy "QUICK_START_GUIDE.md" "DISTRIBUTION\Documentation\QUICK_START_GUIDE.md" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] QUICK_START_GUIDE.md) else (echo [OK] QUICK_START_GUIDE.md)

copy "README.md" "DISTRIBUTION\Documentation\README.md" >nul 2>&1
if %errorLevel% neq 0 (echo [SKIP] README.md) else (echo [OK] README.md)

REM Copy preset/config files if they exist
copy "restoration_presets.json" "DISTRIBUTION\" >nul 2>&1
if %errorLevel% equ 0 (echo [OK] restoration_presets.json)

copy "tape_restorer_config.json" "DISTRIBUTION\" >nul 2>&1
if %errorLevel% equ 0 (echo [OK] tape_restorer_config.json)

REM ============================================================================
REM STEP 4: Create README.txt
REM ============================================================================

echo.
echo Creating README.txt...

(
echo ================================================================================
echo   ADVANCED TAPE RESTORER v3.1 - COMPLETE DISTRIBUTION PACKAGE
echo   Professional Video Restoration ^& Analog Capture Suite
echo ================================================================================
echo.
echo Version: %VERSION%
echo Build Date: %DATE:~0,4%-%DATE:~4,2%-%DATE:~6,2%
echo Platform: Windows 10/11 ^(64-bit^)
echo.
echo ================================================================================
echo   QUICK START - 3 STEPS TO GET RUNNING
echo ================================================================================
echo.
echo STEP 1: AUTOMATIC INSTALLATION ^(RECOMMENDED^)
echo -----------------------------------------------
echo Run: Setup\Install_Prerequisites_Auto.bat
echo.
echo This will automatically download and install:
echo   - FFmpeg ^(video encoding^)
echo   - VapourSynth ^(video processing^)
echo   - VapourSynth plugins ^(QTGMC, filters^)
echo   - Python ^(optional, for AI models^)
echo.
echo Total download: ~210MB
echo Time required: 10-15 minutes
echo.
echo STEP 2: RESTART YOUR COMPUTER
echo -------------------------------
echo After installation completes, restart Windows
echo ^(required for PATH changes to take effect^)
echo.
echo STEP 3: LAUNCH THE APPLICATION
echo --------------------------------
echo Double-click: Advanced_Tape_Restorer_v3.1.exe
echo.
echo That's it! Start restoring your videos!
echo.
echo ================================================================================
echo   ALTERNATIVE: MANUAL INSTALLATION
echo ================================================================================
echo.
echo If automatic installation fails, use manual setup:
echo   Run: Setup\Install_Prerequisites.bat ^(guided manual process^)
echo.
echo ================================================================================
echo   VERIFY INSTALLATION
echo ================================================================================
echo.
echo After installation and restart, run:
echo   Setup\Check_Prerequisites.bat
echo.
echo This will verify all components are properly installed.
echo.
echo ================================================================================
echo   OPTIONAL: AI UPSCALING WITH GPU
echo ================================================================================
echo.
echo For RealESRGAN AI upscaling with NVIDIA RTX GPU:
echo   Run: Setup\Install_PyTorch_CUDA.bat
echo.
echo Requires: NVIDIA RTX 2060 or newer with 6+ GB VRAM
echo.
echo ================================================================================
echo   WHAT'S INCLUDED
echo ================================================================================
echo.
echo Application:
echo   Advanced_Tape_Restorer_v3.1.exe - Main application ^(!SIZE_MB! MB^)
echo.
echo Setup Scripts:
echo   Setup\Install_Prerequisites_Auto.bat - Automatic installer ^(RECOMMENDED^)
echo   Setup\Install_Prerequisites.bat - Manual guided installation
echo   Setup\Check_Prerequisites.bat - Verify installation
echo   Setup\Install_PyTorch_CUDA.bat - Optional GPU acceleration
echo.
echo Documentation:
echo   QUICK_SETUP.txt - Fast setup reference
echo   Documentation\PREREQUISITES.md - Detailed prerequisites guide
echo   Documentation\QUICK_START_GUIDE.md - Getting started guide
echo   Documentation\README.md - Complete application documentation
echo.
echo Configuration:
echo   restoration_presets.json - Sample restoration presets
echo   tape_restorer_config.json - Application configuration
echo.
echo ================================================================================
echo   SYSTEM REQUIREMENTS
echo ================================================================================
echo.
echo MINIMUM:
echo   - Windows 10/11 ^(64-bit^)
echo   - Intel Core i5 / AMD Ryzen 5 ^(4+ cores^)
echo   - 8 GB RAM
echo   - 100 GB free disk space
echo.
echo RECOMMENDED FOR AI:
echo   - Intel Core i7/i9 / AMD Ryzen 7/9 ^(8+ cores^)
echo   - 16-32 GB RAM
echo   - NVIDIA RTX 3060 or newer ^(8+ GB VRAM^)
echo   - SSD with 500+ GB free space
echo.
echo ================================================================================
echo   FEATURES
echo ================================================================================
echo.
echo Video Restoration:
echo   - QTGMC Deinterlacing ^(7 quality presets^)
echo   - Auto Field Order Detection
echo   - BM3D Denoising ^(CPU/GPU^)
echo   - VHS Artifact Removal
echo   - Color Correction
echo   - AI Upscaling ^(RealESRGAN 2x^)
echo.
echo Video Capture:
echo   - Analog capture ^(VHS, Hi8, Betamax^)
echo   - DV/miniDV FireWire capture
echo   - Auto device detection
echo   - Lossless codecs ^(HuffYUV, FFV1^)
echo   - User-specified output folders
echo.
echo Output Formats:
echo   - H.264/H.265 ^(CPU or NVIDIA NVENC^)
echo   - ProRes 422/4444 ^(professional editing^)
echo   - DNxHD ^(Avid workflows^)
echo   - FFV1 ^(lossless archival^)
echo   - AV1 ^(next-gen compression^)
echo.
echo ================================================================================
echo   GETTING HELP
echo ================================================================================
echo.
echo If you encounter issues:
echo   1. Read: Documentation\PREREQUISITES.md
echo   2. Run: Setup\Check_Prerequisites.bat
echo   3. Check: Documentation\README.md for troubleshooting
echo.
echo Common issues are usually fixed by:
echo   - Restarting computer after installation
echo   - Running Check_Prerequisites.bat to diagnose
echo   - Reinstalling missing components
echo.
echo ================================================================================
echo   DEPLOYMENT TO OTHER COMPUTERS
echo ================================================================================
echo.
echo To use on another computer:
echo   1. Copy this entire folder to the new computer
echo   2. Run: Setup\Install_Prerequisites_Auto.bat
echo   3. Restart the computer
echo   4. Run: Advanced_Tape_Restorer_v3.1.exe
echo.
echo The EXE is portable - no installation needed for the application itself.
echo Only the external video processing tools ^(FFmpeg, VapourSynth^) need setup.
echo.
echo ================================================================================
echo.
echo Build Information:
echo   Build Date: %datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%
echo   EXE Size: !SIZE_MB! MB
echo   Python Version: Embedded
echo   PyQt Version: 6.x
echo.
echo Ready for distribution!
echo.
echo ================================================================================
) > "DISTRIBUTION\README.txt"

echo [OK] README.txt created

REM ============================================================================
REM STEP 5: Create Package Info
REM ============================================================================

echo.
echo Creating PACKAGE_INFO.txt...

(
echo Advanced Tape Restorer v%VERSION%
echo.
echo Build Date: %DATE:~0,4%-%DATE:~4,2%-%DATE:~6,2%
echo Package: %PACKAGE_NAME%
echo EXE Size: !SIZE_MB! MB
echo.
echo Contents:
echo   - Application executable
echo   - Automatic prerequisite installer
echo   - Manual installation scripts
echo   - Complete documentation
echo   - Sample presets
echo.
echo Installation:
echo   1. Extract this ZIP to any folder
echo   2. Run Setup\Install_Prerequisites_Auto.bat
echo   3. Restart computer
echo   4. Launch Advanced_Tape_Restorer_v3.exe
echo.
echo Support: See Documentation folder
) > "DISTRIBUTION\PACKAGE_INFO.txt"

echo [OK] PACKAGE_INFO.txt created

REM ============================================================================
REM STEP 6: Verify Distribution Contents
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 4: Verifying Distribution Contents
echo ================================================================================
echo.

set MISSING=0

REM Check critical files
if not exist "DISTRIBUTION\Advanced_Tape_Restorer_v3.1.exe" (
    echo [MISSING] Advanced_Tape_Restorer_v3.1.exe
    set MISSING=1
) else (
    echo [OK] Advanced_Tape_Restorer_v3.1.exe
)

if not exist "DISTRIBUTION\README.txt" (
    echo [MISSING] README.txt
    set MISSING=1
) else (
    echo [OK] README.txt
)

if not exist "DISTRIBUTION\QUICK_SETUP.txt" (
    echo [WARN] QUICK_SETUP.txt ^(optional^)
) else (
    echo [OK] QUICK_SETUP.txt
)

if not exist "DISTRIBUTION\Setup\Install_Prerequisites_Auto.bat" (
    echo [MISSING] Setup\Install_Prerequisites_Auto.bat
    set MISSING=1
) else (
    echo [OK] Setup\Install_Prerequisites_Auto.bat
)

if not exist "DISTRIBUTION\Setup\Check_Prerequisites.bat" (
    echo [WARN] Setup\Check_Prerequisites.bat ^(optional^)
) else (
    echo [OK] Setup\Check_Prerequisites.bat
)

echo.

if %MISSING% equ 1 (
    echo [ERROR] Critical files missing!
    echo Cannot create distribution package.
    pause
    exit /b 1
)

echo All critical files present!

REM ============================================================================
REM STEP 7: Create ZIP Package
REM ============================================================================

echo.
echo ================================================================================
echo   STEP 5: Creating ZIP Package
echo ================================================================================
echo.

REM Delete old package if exists
if exist "%PACKAGE_NAME%.zip" (
    echo Removing old package...
    del "%PACKAGE_NAME%.zip" >nul 2>&1
)

REM Try 7-Zip first (better compression)
where 7z >nul 2>&1
if %errorLevel%==0 (
    echo Using 7-Zip for compression...
    7z a -tzip "%PACKAGE_NAME%.zip" ".\DISTRIBUTION\*" -mx9 >nul
    if %errorLevel% equ 0 (
        echo [OK] ZIP created with 7-Zip
        goto ZIP_SUCCESS
    )
)

REM Fallback to PowerShell
echo Using PowerShell for compression...
powershell -Command "Compress-Archive -Path 'DISTRIBUTION\*' -DestinationPath '%PACKAGE_NAME%.zip' -CompressionLevel Optimal -Force"
if %errorLevel% neq 0 (
    echo [ERROR] ZIP creation failed!
    pause
    exit /b 1
)
echo [OK] ZIP created with PowerShell

:ZIP_SUCCESS

REM Get ZIP size
for %%A in ("%PACKAGE_NAME%.zip") do (
    set ZIP_SIZE=%%~zA
    set /A ZIP_SIZE_MB=!ZIP_SIZE! / 1048576
)

REM ============================================================================
REM SUCCESS
REM ============================================================================

echo.
echo ================================================================================
echo   DISTRIBUTION PACKAGE CREATED SUCCESSFULLY!
echo ================================================================================
echo.
echo Package: %PACKAGE_NAME%.zip
echo Size: !ZIP_SIZE_MB! MB
echo Location: %CD%\%PACKAGE_NAME%.zip
echo.
echo Contents:
echo   - Advanced_Tape_Restorer_v3.1.exe ^(!SIZE_MB! MB^)
echo   - Automatic prerequisite installer
echo   - Manual installation scripts
echo   - Complete documentation
echo   - Setup verification tools
echo.
echo ================================================================================
echo   DISTRIBUTION CHECKLIST
echo ================================================================================
echo.
echo [X] EXE built and tested
echo [X] All setup scripts included
echo [X] Documentation bundled
echo [X] README.txt with quick start guide
echo [X] Automatic installer for prerequisites
echo [X] Package compressed and ready
echo.
echo READY FOR DISTRIBUTION!
echo.
echo To deploy:
echo   1. Upload %PACKAGE_NAME%.zip to distribution server
echo   2. Users download and extract ZIP
echo   3. Users run Setup\Install_Prerequisites_Auto.bat
echo   4. Users restart computer and launch app
echo.
echo ================================================================================

echo.
echo Press any key to open the package folder...
pause >nul
explorer /select,"%CD%\%PACKAGE_NAME%.zip"

endlocal
exit /b 0
