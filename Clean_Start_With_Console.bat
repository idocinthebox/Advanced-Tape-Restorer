@echo off
REM Clean Start Script for Advanced Tape Restorer v4.0 (With Console)
REM Keeps console window open to view logs and errors

echo ================================================================
echo   Advanced Tape Restorer v4.0 - Clean Start (Debug Mode)
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

echo [4/4] Launching Advanced Tape Restorer with console output...
echo.
echo ================================================================
echo   Console output will appear below
echo   Keep this window open to see logs and errors
echo ================================================================
echo.

REM Launch with python.exe (not pythonw) to keep console visible
python main.py

echo.
echo ================================================================
echo   Application closed
echo ================================================================
echo.
pause
