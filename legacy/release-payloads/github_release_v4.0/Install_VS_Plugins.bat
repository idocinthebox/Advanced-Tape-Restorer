@echo off
REM Advanced Tape Restorer v4.0 - VapourSynth Plugins Installer
REM Installs required VapourSynth plugins for v4.0
echo ========================================
echo Advanced Tape Restorer v4.0
echo VapourSynth Plugins Installation
echo ========================================
echo.

REM Check if VapourSynth installed
where vspipe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] VapourSynth not found!
    echo Please install VapourSynth first: Install_VapourSynth.bat
    pause
    exit /b 1
)

echo [OK] VapourSynth found:
vspipe --version
echo.

REM Check if vsrepo exists
where vsrepo >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] vsrepo not found!
    echo vsrepo is VapourSynth's plugin manager.
    echo.
    echo It should be included with VapourSynth installation.
    echo Please reinstall VapourSynth from: https://github.com/vapoursynth/vapoursynth/releases
    pause
    exit /b 1
)

echo Installing required plugins...
echo.

echo [1/5] QTGMC (deinterlacing - REQUIRED)
vsrepo install havsfunc
vsrepo install mvtools
vsrepo install nnedi3
vsrepo install eedi3
vsrepo install fftw3

echo.
echo [2/5] Denoise plugins
vsrepo install bm3d
vsrepo install fft3dfilter
vsrepo install knlmeanscl

echo.
echo [3/5] Essential filters
vsrepo install descale
vsrepo install bilateral
vsrepo install tcanny

echo.
echo [4/5] Frame manipulation
vsrepo install misc
vsrepo install resize

echo.
echo [5/5] Optional enhancement plugins
vsrepo install cas
vsrepo install ttmpsm

echo.
echo ========================================
echo Installation Complete
echo ========================================
echo.
echo Installed plugins:
vsrepo installed
echo.
echo You can now run Advanced_Tape_Restorer_v4.0.exe
echo.
pause
