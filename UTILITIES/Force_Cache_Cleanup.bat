@echo off
REM Force cleanup of all caches and temporary files
REM Use this if the app is acting strange or hanging

echo ========================================
echo Advanced Tape Restorer v4.0
echo Force Cache Cleanup Utility
echo ========================================
echo.

echo [Step 1/4] Stopping any running instances...
taskkill /F /IM Advanced_Tape_Restorer_v4.0.exe 2>nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul

echo [Step 2/4] Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo [Step 3/4] Clearing PyInstaller temp folders...
del /s /q "%TEMP%\_MEI*" 2>nul

echo [Step 4/4] Clearing VapourSynth temp scripts...
del /s /q "%TEMP%\tape_restorer_*.vpy" 2>nul

echo.
echo ========================================
echo Cleanup Complete!
echo You can now launch the application.
echo ========================================
pause
