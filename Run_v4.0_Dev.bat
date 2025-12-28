@echo off
REM Advanced Tape Restorer v4.0 - Quick Launcher
REM ============================================

cd /d "%~dp0"

echo.
echo ========================================
echo   Advanced Tape Restorer v4.0-dev
echo ========================================
echo.
echo Starting application...
echo.

REM Activate virtual environment and run
call .venv\Scripts\activate.bat
python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application failed to start!
    echo Error code: %ERRORLEVEL%
    echo.
    echo Troubleshooting:
    echo   1. Check that virtual environment is set up
    echo   2. Run: .venv\Scripts\activate.bat
    echo   3. Verify dependencies: pip list
    echo.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
