@echo off
REM Clean Start Script for Advanced Tape Restorer v4.0
REM Kills stuck processes, clears cache, and launches app

echo ================================================================
echo   Advanced Tape Restorer v4.0 - Clean Start
echo ================================================================
echo.

echo [1/4] Killing any running Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
timeout /t 1 >nul
echo       Done.

echo [2/4] Clearing Python cache files...
if exist "__pycache__" rd /s /q "__pycache__" >nul 2>&1
if exist "gui\__pycache__" rd /s /q "gui\__pycache__" >nul 2>&1
if exist "core\__pycache__" rd /s /q "core\__pycache__" >nul 2>&1
if exist "ai_models\__pycache__" rd /s /q "ai_models\__pycache__" >nul 2>&1
echo       Done.

echo [3/4] Clearing .pyc files...
del /s /q *.pyc >nul 2>&1
echo       Done.

echo [4/4] Launching Advanced Tape Restorer...
echo.
echo Starting application in separate window...
echo You can safely close this window - the app will stay open.
echo.

REM Launch Python in a detached process (stays open after batch closes)
start "Advanced Tape Restorer v4.0" pythonw main.py

REM Wait a moment to check if it started
timeout /t 2 >nul

echo.
echo ================================================================
echo   Application launched!
echo ================================================================
echo.
echo The app is now running in a separate window.
echo You can close this command prompt safely.
echo.
echo If the app didn't start, check for errors in the console.
echo.

pause
