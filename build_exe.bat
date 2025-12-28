@echo off
REM ============================================
REM Advanced Tape Restorer v3.0 - Build Script
REM ============================================

echo.
echo ========================================
echo Advanced Tape Restorer v3.0 - Builder
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo [1/4] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment found
    echo Make sure all dependencies are installed globally
)

echo.
echo [2/4] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Advanced_Tape_Restorer_v3.1.spec.bak del Advanced_Tape_Restorer_v3.1.spec.bak

echo.
echo [3/4] Building executable with PyInstaller...
echo This may take 3-5 minutes...
echo.
pyinstaller Advanced_Tape_Restorer_v2.spec --clean --noconfirm

echo.
echo [4/4] Checking build result...
if exist "dist\Advanced_Tape_Restorer_v3.1.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created at:
    echo   dist\Advanced_Tape_Restorer_v3.1.exe
    echo.
    echo File size:
    dir "dist\Advanced_Tape_Restorer_v3.1.exe" | find "Advanced_Tape_Restorer"
    echo.
    echo You can now distribute this single .exe file!
    echo.
    echo IMPORTANT NOTES:
    echo - VapourSynth must be installed on target system
    echo - FFmpeg must be in PATH or same directory
    echo - Python NOT required on target system
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Check the error messages above.
    echo Common issues:
    echo   - Missing dependencies
    echo   - Antivirus blocking PyInstaller
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)
