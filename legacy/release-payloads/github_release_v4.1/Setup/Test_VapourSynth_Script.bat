@echo off
REM ==============================================================================
REM  Test VapourSynth Script Execution
REM  Diagnoses why vspipe returns 0 frames
REM ==============================================================================

title Test VapourSynth Script

setlocal enabledelayedexpansion

cls
echo.
echo ================================================================================
echo   VAPOURSYNTH SCRIPT EXECUTION TEST
echo ================================================================================
echo.

REM Check if vspipe exists
where vspipe >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] vspipe not found in PATH!
    pause
    exit /b 1
)

echo [OK] vspipe found
vspipe --version
echo.

REM Check if the generated script exists
set SCRIPT_PATH=%~dp0last_generated_script.vpy

if not exist "%SCRIPT_PATH%" (
    echo [ERROR] Test script not found!
    echo Expected: %SCRIPT_PATH%
    echo.
    echo Run the app first to generate a script, then run this test.
    pause
    exit /b 1
)

echo [OK] Found test script: %SCRIPT_PATH%
echo.

echo ================================================================================
echo   TESTING SCRIPT WITH VSPIPE --INFO
echo ================================================================================
echo.
echo This will show the actual error if VapourSynth can't execute the script...
echo.

REM Run vspipe --info to get frame count (this is what the app does)
echo Command: vspipe --info "%SCRIPT_PATH%" -
echo.
echo --- Output Start ---
vspipe --info "%SCRIPT_PATH%" -
set VSPIPE_EXIT=%errorLevel%
echo --- Output End ---
echo.

if %VSPIPE_EXIT% equ 0 (
    echo [SUCCESS] Script executed successfully!
    echo.
) else (
    echo [ERROR] Script failed with exit code %VSPIPE_EXIT%
    echo.
    echo Common causes:
    echo   - ffms2 plugin not installed: py -3.12 "path\to\vsrepo.py" install ffms2
    echo   - havsfunc not installed: py -3.12 "path\to\vsrepo.py" install havsfunc
    echo   - mvtools not installed: py -3.12 "path\to\vsrepo.py" install mvtools
    echo   - Wrong Python environment (VapourSynth can't find packages)
    echo.
)

echo ================================================================================
echo   MANUAL PLUGIN TEST
echo ================================================================================
echo.
echo Testing if VapourSynth can load plugins directly...
echo.

REM Create a minimal test script
set TEST_SCRIPT=%TEMP%\vstest.vpy

echo import vapoursynth as vs > "%TEST_SCRIPT%"
echo core = vs.core >> "%TEST_SCRIPT%"
echo print('Core:', core) >> "%TEST_SCRIPT%"
echo print('Plugins:', [attr for attr in dir(core) if not attr.startswith('_')]) >> "%TEST_SCRIPT%"
echo # Test ffms2 >> "%TEST_SCRIPT%"
echo try: >> "%TEST_SCRIPT%"
echo     test = core.ffms2 >> "%TEST_SCRIPT%"
echo     print('ffms2: OK') >> "%TEST_SCRIPT%"
echo except AttributeError: >> "%TEST_SCRIPT%"
echo     print('ffms2: MISSING') >> "%TEST_SCRIPT%"
echo # Test havsfunc import >> "%TEST_SCRIPT%"
echo try: >> "%TEST_SCRIPT%"
echo     import havsfunc as haf >> "%TEST_SCRIPT%"
echo     print('havsfunc: OK') >> "%TEST_SCRIPT%"
echo except ImportError: >> "%TEST_SCRIPT%"
echo     print('havsfunc: MISSING') >> "%TEST_SCRIPT%"

echo Running minimal VapourSynth test...
echo.
vspipe --info "%TEST_SCRIPT%" - 2>&1
echo.

del "%TEST_SCRIPT%" 2>nul

echo ================================================================================
echo   PLUGIN LOCATION CHECK
echo ================================================================================
echo.

echo Checking plugin directories...
echo.

REM Check user-level plugins
if exist "%APPDATA%\VapourSynth\plugins64\" (
    echo [OK] User plugins folder exists: %APPDATA%\VapourSynth\plugins64\
    echo     Contents:
    dir /b "%APPDATA%\VapourSynth\plugins64\*.dll" 2>nul
    echo.
) else (
    echo [INFO] User plugins folder not found: %APPDATA%\VapourSynth\plugins64\
)

REM Check system-level plugins
if exist "C:\Program Files\VapourSynth\plugins64\" (
    echo [OK] System plugins folder exists: C:\Program Files\VapourSynth\plugins64\
    echo     Contents:
    dir /b "C:\Program Files\VapourSynth\plugins64\*.dll" 2>nul
    echo.
) else (
    echo [INFO] System plugins folder not found: C:\Program Files\VapourSynth\plugins64\
)

REM Check local install plugins
if exist "%LOCALAPPDATA%\Programs\VapourSynth\plugins64\" (
    echo [OK] Local plugins folder exists: %LOCALAPPDATA%\Programs\VapourSynth\plugins64\
    echo     Contents:
    dir /b "%LOCALAPPDATA%\Programs\VapourSynth\plugins64\*.dll" 2>nul
    echo.
) else (
    echo [INFO] Local plugins folder not found: %LOCALAPPDATA%\Programs\VapourSynth\plugins64\
)

echo ================================================================================
echo   PYTHON ENVIRONMENT CHECK
echo ================================================================================
echo.

echo VapourSynth uses the Python it was installed with (Python 3.12).
echo Checking if Python 3.12 can import vapoursynth and havsfunc...
echo.

py -3.12 -c "import vapoursynth; print('[OK] vapoursynth module found'); print('Version:', vapoursynth.__version__)" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 3.12 cannot import vapoursynth module
    echo This means VapourSynth and Python 3.12 are not properly linked.
)
echo.

py -3.12 -c "import havsfunc; print('[OK] havsfunc module found')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 3.12 cannot import havsfunc
    echo Install with: py -3.12 "path\to\vsrepo.py" install havsfunc
)
echo.

echo ================================================================================
echo   DIAGNOSTIC COMPLETE
echo ================================================================================
echo.
echo If script execution failed above, the error message should indicate
echo which plugin or module is missing.
echo.

pause
