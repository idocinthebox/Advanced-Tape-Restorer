@echo off
REM Launch Advanced Tape Restorer with console output visible
REM Useful for debugging and seeing error messages

echo ========================================
echo Advanced Tape Restorer v4.0
echo Debug Mode (Console Output Visible)
echo ========================================
echo.
echo Starting application with console logging...
echo Press Ctrl+C to stop the application.
echo.

REM Build from spec with console enabled
if exist "main.spec" (
    echo Building debug version with console...
    pyinstaller --noconfirm --clean main.spec --console
    echo.
    echo Launching debug build...
    "dist\Advanced_Tape_Restorer_v4.0.exe"
) else (
    echo ERROR: main.spec not found!
    echo This script must be run from the project root directory.
    pause
    exit /b 1
)

pause
