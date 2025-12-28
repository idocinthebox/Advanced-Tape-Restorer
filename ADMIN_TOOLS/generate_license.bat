@echo off
REM Generate activation code for Advanced Tape Restorer
REM Usage: generate_license.bat

echo ============================================================
echo ADVANCED TAPE RESTORER - LICENSE GENERATOR
echo ============================================================
echo.

set /p LICENSE_TYPE="License type (trial/personal/professional/enterprise): "
set /p HARDWARE_ID="Hardware ID (get from user's activation dialog): "
set /p TESTER_ID="Tester ID (email or identifier): "
set /p EXPIRY_DAYS="Expiry days (leave empty for permanent): "

echo.
echo Generating activation code...
echo.

if "%EXPIRY_DAYS%"=="" (
    python -m licensing.generate_keys --type %LICENSE_TYPE% --hardware %HARDWARE_ID% --tester %TESTER_ID% --validate
) else (
    python -m licensing.generate_keys --type %LICENSE_TYPE% --hardware %HARDWARE_ID% --tester %TESTER_ID% --days %EXPIRY_DAYS% --validate
)

echo.
pause
