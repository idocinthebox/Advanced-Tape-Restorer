@echo off
setlocal enabledelayedexpansion
REM Build script for Advanced Tape Restorer v3.1
REM Usage: build.bat [--debug]

echo ===============================================
echo  Advanced Tape Restorer v3.1 - Build Script
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.9+ and add to PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Determine build mode
set BUILD_MODE=onefile
set DEBUG_FLAG=

if "%1"=="--debug" set DEBUG_FLAG=--debug
if "%2"=="--debug" set DEBUG_FLAG=--debug

echo.
echo Building Advanced Tape Restorer v3.1...
echo Mode: Single-file EXE
if defined DEBUG_FLAG echo Debug: Enabled
echo.

REM Run PyInstaller with the v3.1 spec file
python -m PyInstaller Advanced_Tape_Restorer_v2.spec %DEBUG_FLAG%

if errorlevel 1 (
    echo.
    echo ===============================================
    echo  BUILD FAILED
    echo ===============================================
    pause
    exit /b 1
)

echo.
echo ===============================================
echo  BUILD SUCCESSFUL
echo ===============================================
echo.
echo Output: dist\Advanced_Tape_Restorer_v3.1.exe
echo.

REM Show file size
for %%F in (dist\Advanced_Tape_Restorer_v3.1.exe) do (
    set /a "size=%%~zF / 1048576"
    echo File size: !size! MB
)

echo.
pause
