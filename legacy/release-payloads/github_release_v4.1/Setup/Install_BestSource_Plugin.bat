@echo off
REM ============================================================
REM BestSource2 Plugin Installer - Advanced Tape Restorer v4.0
REM ============================================================
REM 
REM BestSource2: The most reliable VapourSynth source filter
REM - Most accurate FPS detection (critical for VFR/telecine)
REM - Superior audio sync (frame-perfect timestamps)
REM - Proper RFF (Repeat Field Flag) handling for DVD/analog
REM - Hardware decode support (DXVA2/D3D11VA)
REM 
REM Trade-off: Slower initial indexing (one-time cost)
REM ============================================================

title BestSource2 Plugin Installer
color 0B

echo.
echo ========================================================
echo   BestSource2 Plugin Installer
echo   Advanced Tape Restorer v4.0
echo ========================================================
echo.
echo BestSource2 is the MOST RELIABLE source filter for:
echo   - VHS, Hi8, Betamax tape captures (accurate sync)
echo   - DVD and LaserDisc sources (proper RFF handling)
echo   - VFR/telecine content (accurate FPS detection)
echo   - Problematic audio sync issues (frame-perfect)
echo.
echo PERFORMANCE:
echo   - First load: Slower (indexes entire file)
echo   - Subsequent: Fast (cached index)
echo   - Worth it: Maximum reliability for archival work
echo.

REM Check if Python 3.12+ is installed
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo.
    echo BestSource2 requires Python 3.12 or newer.
    echo Please run Install_Prerequisites_Auto.bat first.
    echo.
    pause
    exit /b 1
)

REM Check if VapourSynth is installed
where vspipe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] VapourSynth not found!
    echo.
    echo BestSource2 requires VapourSynth to be installed.
    echo Please run Install_Prerequisites_Auto.bat first.
    echo.
    pause
    exit /b 1
)

echo.
echo Checking VapourSynth plugin manager (vsrepo)...
echo.

REM Try to find vsrepo in common locations
set VSREPO_PATH=
if exist "%APPDATA%\VapourSynth\vsrepo\vsrepo.py" (
    set VSREPO_PATH=%APPDATA%\VapourSynth\vsrepo\vsrepo.py
) else if exist "C:\Program Files\VapourSynth\vsrepo\vsrepo.py" (
    set VSREPO_PATH=C:\Program Files\VapourSynth\vsrepo\vsrepo.py
) else (
    echo [WARNING] vsrepo not found in standard locations
    echo Trying direct vsrepo command...
    where vsrepo >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Found vsrepo in PATH
        goto :install_plugin
    )
)

if defined VSREPO_PATH (
    echo [OK] Found vsrepo at: %VSREPO_PATH%
) else (
    echo [ERROR] Could not locate vsrepo!
    echo.
    echo Please install VapourSynth properly, then try again.
    echo.
    pause
    exit /b 1
)

:install_plugin
echo.
echo ========================================================
echo   Installing BestSource2 Plugin
echo ========================================================
echo.
echo This will download and install BestSource2 from the
echo official VapourSynth plugin repository.
echo.
pause

echo.
echo Installing BestSource2...
echo.

REM Install BestSource2 using vsrepo
if defined VSREPO_PATH (
    py -3.12 "%VSREPO_PATH%" install bestsource
) else (
    vsrepo install bestsource
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS - BestSource2 Installed!
    echo ========================================================
    echo.
    echo BestSource2 is now available in VapourSynth.
    echo.
    echo USAGE IN ADVANCED TAPE RESTORER:
    echo   1. Go to Restoration tab ^> Input Settings
    echo   2. Source Filter: Select "BestSource (Best - Most Reliable)"
    echo   3. Process your video
    echo.
    echo FIRST USE:
    echo   - Initial indexing may take 1-5 minutes per hour of video
    echo   - Index is cached for instant subsequent loads
    echo   - Worth it: Maximum reliability for tape preservation
    echo.
    echo BENEFITS:
    echo   - Most accurate FPS detection (no sync drift)
    echo   - Proper telecine/RFF handling (DVD sources)
    echo   - Frame-perfect audio sync (critical for long captures)
    echo   - Hardware decode support (GPU acceleration)
    echo.
) else (
    echo.
    echo ========================================================
    echo   ERROR - Installation Failed
    echo ========================================================
    echo.
    echo BestSource2 could not be installed automatically.
    echo.
    echo MANUAL INSTALLATION:
    echo   1. Download from: https://github.com/vapoursynth/bestsource/releases
    echo   2. Extract bestsource.dll to VapourSynth plugins folder:
    echo      %APPDATA%\VapourSynth\plugins64\
    echo   3. Restart Advanced Tape Restorer
    echo.
)

echo.
pause
