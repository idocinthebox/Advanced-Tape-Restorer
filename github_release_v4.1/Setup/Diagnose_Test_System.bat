@echo off
REM ==============================================================================
REM  Diagnostic Script for Test System - Find Missing Dependencies
REM ==============================================================================

title Test System Diagnostics

cls
color 0E
echo.
echo ================================================================================
echo   ADVANCED TAPE RESTORER - TEST SYSTEM DIAGNOSTICS
echo ================================================================================
echo.
echo This script will check what's installed on your test system.
echo Run this on the test system where RealESRGAN is failing.
echo.
pause
echo.

echo ================================================================================
echo   STEP 1: CHECK SYSTEM PATH
echo ================================================================================
echo.
echo Current PATH:
echo %PATH%
echo.
pause
echo.

echo ================================================================================
echo   STEP 2: CHECK FFMPEG
echo ================================================================================
echo.
where ffmpeg 2>nul
if %errorLevel% equ 0 (
    echo [OK] FFmpeg found
    ffmpeg -version 2>nul | findstr "ffmpeg version"
) else (
    echo [ERROR] FFmpeg NOT found in PATH
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 3: CHECK VAPOURSYNTH
echo ================================================================================
echo.
where vspipe 2>nul
if %errorLevel% equ 0 (
    echo [OK] VapourSynth found
    vspipe --version 2>nul
) else (
    echo [ERROR] VapourSynth NOT found in PATH
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 4: CHECK PYTHON
echo ================================================================================
echo.
where python 2>nul
if %errorLevel% equ 0 (
    echo [OK] Python found
    python --version 2>nul
) else (
    echo [WARNING] Python NOT found
)
echo.

py -3.12 --version 2>nul
if %errorLevel% equ 0 (
    echo [OK] Python 3.12 found via launcher
) else (
    echo [WARNING] Python 3.12 NOT found
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 5: CHECK VAPOURSYNTH PLUGINS (via Python)
echo ================================================================================
echo.
python -c "import vapoursynth as vs; core = vs.core; print('[OK] VapourSynth Python module works'); print('Available plugins:', ', '.join([p.namespace for p in core.plugins()]))" 2>nul
if %errorLevel% neq 0 (
    echo [ERROR] VapourSynth Python module not accessible
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 6: CHECK SPECIFIC PLUGINS
echo ================================================================================
echo.
echo Checking ffms2...
python -c "import vapoursynth as vs; core = vs.core; print('ffms2:', hasattr(core, 'ffms2'))" 2>nul

echo Checking havsfunc...
python -c "import havsfunc; print('[OK] havsfunc installed')" 2>nul
if %errorLevel% neq 0 echo [ERROR] havsfunc NOT installed

echo Checking mvtools...
python -c "import vapoursynth as vs; core = vs.core; print('mvtools:', hasattr(core, 'mv'))" 2>nul

echo Checking vsrealesrgan...
python -c "import vsrealesrgan; print('[OK] vsrealesrgan plugin installed')" 2>nul
if %errorLevel% neq 0 echo [ERROR] vsrealesrgan NOT installed

echo.
pause
echo.

echo ================================================================================
echo   STEP 7: CHECK PYTORCH (if installed)
echo ================================================================================
echo.
python -c "import torch; print('[OK] PyTorch installed:', torch.__version__); print('CUDA available:', torch.cuda.is_available())" 2>nul
if %errorLevel% neq 0 (
    echo [INFO] PyTorch NOT installed - This is OKAY for vsrealesrgan plugin!
    echo        vsrealesrgan has bundled PyTorch inside the plugin DLL.
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 8: LOCATE VSREPO.PY
echo ================================================================================
echo.
if exist "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" (
    echo [OK] Found: %LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
    set VSREPO_PATH=%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
) else if exist "C:\Program Files\VapourSynth\vsrepo\vsrepo.py" (
    echo [OK] Found: C:\Program Files\VapourSynth\vsrepo\vsrepo.py
    set VSREPO_PATH=C:\Program Files\VapourSynth\vsrepo\vsrepo.py
) else (
    echo [ERROR] vsrepo.py NOT found!
    echo        vsrepo.py should be bundled with VapourSynth R73 installer.
    echo        You may have installed the portable version instead.
    set VSREPO_PATH=
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 9: LIST INSTALLED PLUGINS (via vsrepo)
echo ================================================================================
echo.
if defined VSREPO_PATH (
    echo Installed VapourSynth plugins:
    py -3.12 "%VSREPO_PATH%" installed 2>nul
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to run vsrepo - Python 3.12 may not be installed
    )
) else (
    echo [SKIP] Cannot check - vsrepo.py not found
)
echo.
pause
echo.

echo ================================================================================
echo   STEP 10: TEST VAPOURSYNTH SCRIPT EXECUTION
echo ================================================================================
echo.
echo Creating test VapourSynth script...
echo import vapoursynth as vs > test_vspy_diagnostic.vpy
echo core = vs.core >> test_vspy_diagnostic.vpy
echo print('VapourSynth version:', core.version()) >> test_vspy_diagnostic.vpy
echo print('Plugins:', [p.namespace for p in core.plugins()]) >> test_vspy_diagnostic.vpy

echo Running test script with vspipe...
vspipe --info test_vspy_diagnostic.vpy - 2>nul
if %errorLevel% equ 0 (
    echo [OK] VapourSynth script execution works
) else (
    echo [ERROR] VapourSynth script execution FAILED
)

del test_vspy_diagnostic.vpy 2>nul
echo.
pause
echo.

echo ================================================================================
echo   DIAGNOSTIC SUMMARY
echo ================================================================================
echo.
echo Copy the output above and provide it for troubleshooting.
echo.
echo Common issues on virgin installs:
echo   1. VapourSynth plugins not installed (run Install_VapourSynth_Plugins.bat)
echo   2. vsrepo.py not found (reinstall VapourSynth R73 installer, not portable)
echo   3. Python 3.12 not installed (needed for vsrepo)
echo   4. PATH not updated after installation (restart computer)
echo.
echo ================================================================================
echo.
pause
