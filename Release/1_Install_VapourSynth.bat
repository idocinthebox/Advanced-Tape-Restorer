@echo off
REM ============================================================================
REM  Advanced Tape Restorer v2.0 - VapourSynth Installation Helper
REM ============================================================================

echo.
echo ===============================================
echo  VapourSynth Installation Helper
echo ===============================================
echo.
echo This script will help you install VapourSynth R68+ (64-bit)
echo.
echo VapourSynth is the core video processing framework used by
echo Advanced Tape Restorer for deinterlacing and restoration.
echo.
echo -----------------------------------------------
echo  OPTION 1: Automatic Download (Recommended)
echo -----------------------------------------------
echo.
echo Press 'A' to automatically download and install VapourSynth
echo.
echo -----------------------------------------------
echo  OPTION 2: Manual Installation
echo -----------------------------------------------
echo.
echo Press 'M' to open download page in browser
echo Then run the installer manually
echo.
echo Press 'Q' to quit
echo.

choice /C AMQ /N /M "Your choice (A/M/Q): "

if errorlevel 3 goto :quit
if errorlevel 2 goto :manual
if errorlevel 1 goto :auto

:auto
echo.
echo Attempting to download VapourSynth installer...
echo.

REM Check if curl is available
where curl >nul 2>&1
if errorlevel 1 (
    echo ERROR: curl not found. Using manual method instead.
    timeout /t 2 >nul
    goto :manual
)

REM Download latest VapourSynth installer
set DOWNLOAD_URL=https://github.com/vapoursynth/vapoursynth/releases/download/R68/VapourSynth64-R68.exe
set INSTALLER=VapourSynth64-R68.exe

echo Downloading from GitHub releases...
curl -L -o "%TEMP%\%INSTALLER%" "%DOWNLOAD_URL%"

if not exist "%TEMP%\%INSTALLER%" (
    echo.
    echo Download failed. Using manual method instead.
    timeout /t 2 >nul
    goto :manual
)

echo.
echo Download complete! Starting installer...
echo.
echo IMPORTANT: During installation:
echo   1. Choose "Install for all users" if prompted
echo   2. Keep default installation path
echo   3. Complete the installation wizard
echo.
pause

start /wait "%TEMP%\%INSTALLER%"

echo.
echo Installation complete!
echo.
goto :verify

:manual
echo.
echo Opening VapourSynth download page in browser...
start https://github.com/vapoursynth/vapoursynth/releases
echo.
echo Please download: VapourSynth64-R68.exe (or newer)
echo Run the installer after downloading.
echo.
echo IMPORTANT: During installation:
echo   1. Choose "Install for all users" if prompted
echo   2. Keep default installation path
echo   3. Complete the installation wizard
echo.
echo Press any key after installation completes...
pause >nul
goto :verify

:verify
echo.
echo -----------------------------------------------
echo  Verifying Installation...
echo -----------------------------------------------
echo.

REM Check if vspipe is in PATH
where vspipe >nul 2>&1
if errorlevel 1 (
    echo WARNING: vspipe not found in PATH
    echo.
    echo VapourSynth may not be installed correctly.
    echo Try restarting your computer and run this script again.
    echo.
    echo If problem persists:
    echo   1. Reinstall VapourSynth
    echo   2. Ensure you chose "Install for all users"
    echo   3. Restart Windows
    echo.
) else (
    echo SUCCESS: VapourSynth found!
    echo.
    vspipe --version
    echo.
    echo VapourSynth is ready to use!
    echo.
)

echo -----------------------------------------------
echo  Installing Required Plugins...
echo -----------------------------------------------
echo.
echo VapourSynth requires additional plugins for restoration.
echo These will be installed via vsrepo (VapourSynth plugin manager).
echo.
echo Essential plugins:
echo   - havsfunc (QTGMC deinterlacing)
echo   - ffms2 (video source filter)
echo   - bm3d (denoising - optional but recommended)
echo.
echo Press any key to install plugins now...
pause >nul

REM Try to install essential plugins
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python not found. Cannot install plugins automatically.
    echo Please install plugins manually using vsrepo.
    echo See USER_GUIDE.pdf for instructions.
    echo.
) else (
    echo.
    echo Installing essential plugins...
    echo.
    
    python -m pip install vsrepo >nul 2>&1
    vsrepo.py install havsfunc
    vsrepo.py install ffms2
    vsrepo.py install bm3d
    
    echo.
    echo Plugin installation complete (core plugins)!
    echo.
    echo Now installing optional AI enhancement plugins (RealESRGAN, RIFE)...
    echo These provide AI upscaling and frame interpolation but may require
    echo large model weights to be downloaded separately. Follow prompts.
    echo.
    vsrepo.py install rife
    vsrepo.py install realesrgan
    echo.
    echo NOTE: RealESRGAN and RIFE may require model weights that are not
    echo automatically downloaded by vsrepo on all systems. If a plugin
    echo reports "model not found" after installation, see
    echo "%~dp0..\docs\AI_ENHANCEMENT_GUIDE.md" for manual model download
    echo instructions and recommended models.
    echo.
    echo AI plugin installation finished (if no errors reported).
    echo.
)

echo.
echo -----------------------------------------------
echo  OPTIONAL MODULES
echo -----------------------------------------------
echo.
echo  1) ProPainter Installation Guide (README + GitHub)
echo  2) Open ProPainter GitHub Page
echo  Q) Continue (skip optional modules)
echo.
choice /C 12Q /N /M "Select optional module or Q to continue: "

if errorlevel 3 goto :quit
if errorlevel 2 goto :open_propainter_github
if errorlevel 1 goto :show_propainter_readme

:show_propainter_readme
echo.
if exist "%~dp0PROPAINTER_README.txt" (
    type "%~dp0PROPAINTER_README.txt"
) else (
    echo ProPainter README not found in Release folder.
)
echo.
set /p accept="Do you accept ProPainter's license terms and want to open the ProPainter page? (Y/N): "
if /I "%accept%"=="Y" (
    start https://github.com/sczhou/ProPainter
) else (
    echo Skipping ProPainter external install guidance.
)
echo.
goto :verify_optional_done

:open_propainter_github
start https://github.com/sczhou/ProPainter
goto :verify_optional_done

:verify_optional_done
echo.
echo Returning to main installer flow...
echo.

:quit
echo.
echo ===============================================
echo.
echo Next step: Run "2_Install_FFmpeg.bat"
echo.
echo ===============================================
echo.
pause
exit /b 0
