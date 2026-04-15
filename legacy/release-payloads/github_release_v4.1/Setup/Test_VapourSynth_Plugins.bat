@echo off
REM ==============================================================================
REM  Test VapourSynth Plugin Installation
REM  Verifies that essential plugins are accessible
REM ==============================================================================

title Test VapourSynth Plugins

setlocal enabledelayedexpansion

cls
echo.
echo ================================================================================
echo   VAPOURSYNTH PLUGIN TEST
echo ================================================================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.12+ and add to PATH
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
    echo Please install VapourSynth first
    pause
    exit /b 1
)

echo [OK] VapourSynth found
vspipe --version
echo.

REM Locate vsrepo.py
set VSREPO_PATH=
if exist "%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py" (
    set VSREPO_PATH=%LOCALAPPDATA%\Programs\VapourSynth\vsrepo\vsrepo.py
)
if not defined VSREPO_PATH (
    if exist "C:\Program Files\VapourSynth\vsrepo\vsrepo.py" (
        set VSREPO_PATH=C:\Program Files\VapourSynth\vsrepo\vsrepo.py
    )
)

if defined VSREPO_PATH (
    echo [OK] vsrepo.py found at: %VSREPO_PATH%
    echo.
) else (
    echo [WARNING] vsrepo.py not found (should be bundled with VapourSynth)
    echo.
)

echo ================================================================================
echo   CHECKING INSTALLED PLUGINS
echo ================================================================================
echo.

REM Try to list installed plugins using vsrepo
if defined VSREPO_PATH (
    py -3.12 "%VSREPO_PATH%" installed 2>nul
    if %errorLevel% neq 0 (
        echo [INFO] Could not list plugins, testing directly via VapourSynth...
        echo.
    )
) else (
    echo [INFO] vsrepo.py not available, testing plugins directly...
    echo.
)

echo ================================================================================
echo   TESTING PLUGIN LOADING (via VapourSynth Python API)
echo ================================================================================
echo.

REM Create a test script to check if plugins can be loaded
echo Testing critical plugins...
echo.

REM Test ffms2 (CRITICAL - without this, can't read video files)
echo [1/5] Testing ffms2 (video source)...
python -c "import vapoursynth as vs; core = vs.core; print('      ffms2:', 'OK' if hasattr(core, 'ffms2') else 'MISSING')"

REM Test havsfunc (needed for QTGMC)
echo [2/5] Testing havsfunc (QTGMC deinterlacing)...
python -c "try: import havsfunc; print('      havsfunc: OK')" "except: print('      havsfunc: MISSING')" 2>nul

REM Test mvtools (needed for motion compensation)
echo [3/5] Testing mvtools (motion compensation)...
python -c "import vapoursynth as vs; core = vs.core; print('      mvtools:', 'OK' if hasattr(core, 'mv') else 'MISSING')"

REM Test bm3d (recommended for denoising) - has multiple variants
echo [4/5] Testing bm3d (denoising)...
python -c "import vapoursynth as vs; core = vs.core; variants = [attr for attr in dir(core) if 'bm3d' in attr.lower()]; print('      bm3d:', 'OK (' + ', '.join(variants) + ')' if variants else 'MISSING')"

REM Test znedi3 (recommended for upscaling)
echo [5/5] Testing znedi3 (AI upscaling)...
python -c "import vapoursynth as vs; core = vs.core; print('      znedi3:', 'OK' if hasattr(core, 'znedi3') else 'MISSING')"

echo.
echo ================================================================================
echo   ALL LOADED PLUGINS
echo ================================================================================
echo.
echo Listing all VapourSynth plugins currently loaded:
python -c "import vapoursynth as vs; core = vs.core; plugins = [attr for attr in dir(core) if not attr.startswith('_') and attr not in ['num_threads', 'max_cache_size', 'add_cache']]; print('\n'.join(sorted(plugins)) if plugins else 'No plugins loaded')"

echo.
echo ================================================================================
echo   TEST COMPLETE
echo ================================================================================
echo.

echo If any plugins show as MISSING, install them with:
echo   python -m pip install vsrepo
echo   vsrepo.py install [plugin_name]
echo.
echo Required plugins: ffms2, havsfunc, mvtools
echo Recommended plugins: bm3d, znedi3
echo.

pause
