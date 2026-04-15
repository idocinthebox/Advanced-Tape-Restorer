@echo off
REM ==============================================================================
REM  Advanced Tape Restorer v3.1 - VapourSynth Plugins Installer
REM  Installs essential VapourSynth plugins for video restoration
REM ==============================================================================

title Advanced Tape Restorer v3.1 - VapourSynth Plugins Installer

setlocal enabledelayedexpansion

cls
color 0B
echo.
echo ================================================================================
echo   VAPOURSYNTH PLUGINS INSTALLER - Advanced Tape Restorer v3.1
echo ================================================================================
echo.
echo This will install essential VapourSynth plugins:
echo.
echo   REQUIRED:
echo   - havsfunc (QTGMC deinterlacing)
echo   - ffms2 (video source)
echo   - mvtools (motion compensation)
echo.
echo   RECOMMENDED:
echo   - bm3d (GPU denoising)
echo   - znedi3 (AI upscaling)
echo   - tcomb (artifact removal)
echo.
echo ================================================================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo VapourSynth plugins require Python for installation.
    echo.
    echo Please install Python first:
    echo   1. Download from: https://www.python.org/downloads/
    echo   2. During installation, check "Add Python to PATH"
    echo   3. Re-run this script
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if VapourSynth is installed
where vspipe >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] VapourSynth not found!
    echo.
    echo Please install VapourSynth first:
    echo   Run: Setup\Install_Prerequisites_Auto.bat
    echo.
    pause
    exit /b 1
)

echo [OK] VapourSynth found
echo.

pause

echo.
echo ================================================================================
echo   LOCATING VSREPO.PY
echo ================================================================================
echo.

echo vsrepo.py is bundled with VapourSynth installer (not on PyPI)
echo Searching for vsrepo.py in VapourSynth installation...
echo.

set VSREPO_PATH=

REM Check user-level install
if exist "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" (
    set VSREPO_PATH=%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
    echo [OK] Found: %LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
)

REM Check system-level install
if not defined VSREPO_PATH (
    if exist "C:\Program Files\VapourSynth\vsrepo\vsrepo.py" (
        set VSREPO_PATH=C:\Program Files\VapourSynth\vsrepo\vsrepo.py
        echo [OK] Found: C:\Program Files\VapourSynth\vsrepo\vsrepo.py
    )
)

if not defined VSREPO_PATH (
    echo [ERROR] vsrepo.py not found!
    echo.
    echo vsrepo.py should be in VapourSynth installation directory.
    echo Please reinstall VapourSynth R73 installer (not portable version).
    echo.
    pause
    exit /b 1
)

echo.

REM Check Python 3.12
py -3.12 --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 3.12 not found!
    echo Please install Python 3.12 first.
    pause
    exit /b 1
)

echo [OK] Python 3.12 found
echo.

pause

echo.
echo ================================================================================
echo   UPDATING PLUGIN DATABASE
echo ================================================================================
echo.

py -3.12 "%VSREPO_PATH%" update

echo.
echo ================================================================================
echo   INSTALLING VAPOURSYNTH PLUGINS
echo ================================================================================
echo.

echo Installing required plugins (this may take a few minutes)...
echo.

REM Install core plugins
echo [1/6] Installing vsutil (utility functions - required by havsfunc)...
py -3.12 "%VSREPO_PATH%" install vsutil

echo [2/6] Installing havsfunc (QTGMC deinterlacing)...
py -3.12 "%VSREPO_PATH%" install havsfunc

echo [3/6] Installing ffms2 (video source)...
py -3.12 "%VSREPO_PATH%" install ffms2

echo [4/6] Installing mvtools (motion compensation)...
py -3.12 "%VSREPO_PATH%" install mvtools

echo [5/6] Installing bm3d (GPU denoising)...
py -3.12 "%VSREPO_PATH%" install bm3d

echo [6/6] Installing znedi3 (AI upscaling)...
py -3.12 "%VSREPO_PATH%" install znedi3

echo.
echo ================================================================================
echo   INSTALLATION COMPLETE
echo ================================================================================
echo.

echo VapourSynth plugins have been installed.
echo.
echo To verify everything works:
echo   1. Run: Setup\Check_Prerequisites.bat
echo   2. Launch Advanced_Tape_Restorer_v3.1.exe
echo   3. Try processing a test video
echo.
echo If you encounter missing plugins, install manually:
echo   python -m vsrepo install [plugin_name]
echo.

pause
