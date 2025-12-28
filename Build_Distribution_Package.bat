@echo off
REM ==================================================================
REM Build Distribution Package
REM Advanced Tape Restorer v2.0
REM ==================================================================

setlocal EnableDelayedExpansion

echo.
echo ================================================================
echo  Building Distribution Package - Advanced Tape Restorer v2.0
echo ================================================================
echo.

REM Get version and date
set VERSION=2.0.0
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set DATE=%datetime:~0,8%
set PACKAGE_NAME=Advanced_Tape_Restorer_v2.0_Distribution_%DATE%

echo Version: %VERSION%
echo Date: %DATE%
echo Package: %PACKAGE_NAME%.zip
echo.

REM Check if DISTRIBUTION folder exists
if not exist "DISTRIBUTION\" (
    echo [ERROR] DISTRIBUTION folder not found!
    echo Please ensure DISTRIBUTION folder exists with all files.
    pause
    exit /b 1
)

REM Check if EXE exists in DISTRIBUTION
if not exist "DISTRIBUTION\Advanced_Tape_Restorer_v2.exe" (
    echo [WARN] EXE not found in DISTRIBUTION folder!
    echo Copying EXE from dist folder...
    copy "dist\Advanced_Tape_Restorer_v2.exe" "DISTRIBUTION\" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to copy EXE! Build the application first.
        pause
        exit /b 1
    )
    echo [OK] EXE copied successfully
)

REM Verify critical files
echo.
echo Verifying distribution contents...
echo.

set MISSING=0

if not exist "DISTRIBUTION\README.txt" (
    echo [MISSING] README.txt
    set MISSING=1
) else (
    echo [OK] README.txt
)

if not exist "DISTRIBUTION\Setup\Install_Prerequisites.bat" (
    echo [MISSING] Setup\Install_Prerequisites.bat
    set MISSING=1
) else (
    echo [OK] Setup\Install_Prerequisites.bat
)

if not exist "DISTRIBUTION\Setup\Install_PyTorch_CUDA.bat" (
    echo [MISSING] Setup\Install_PyTorch_CUDA.bat
    set MISSING=1
) else (
    echo [OK] Setup\Install_PyTorch_CUDA.bat
)

if not exist "DISTRIBUTION\Setup\Check_Prerequisites.bat" (
    echo [MISSING] Setup\Check_Prerequisites.bat
    set MISSING=1
) else (
    echo [OK] Setup\Check_Prerequisites.bat
)

if not exist "DISTRIBUTION\Documentation\QUICK_START_GUIDE.md" (
    echo [MISSING] Documentation\QUICK_START_GUIDE.md
    set MISSING=1
) else (
    echo [OK] Documentation\QUICK_START_GUIDE.md
)

if not exist "DISTRIBUTION\Documentation\TIPS_AND_TRICKS.md" (
    echo [MISSING] Documentation\TIPS_AND_TRICKS.md
    set MISSING=1
) else (
    echo [OK] Documentation\TIPS_AND_TRICKS.md
)

if not exist "DISTRIBUTION\Documentation\TROUBLESHOOTING.md" (
    echo [MISSING] Documentation\TROUBLESHOOTING.md
    set MISSING=1
) else (
    echo [OK] Documentation\TROUBLESHOOTING.md
)

if not exist "DISTRIBUTION\Documentation\CODEC_GUIDE.md" (
    echo [MISSING] Documentation\CODEC_GUIDE.md
    set MISSING=1
) else (
    echo [OK] Documentation\CODEC_GUIDE.md
)

if not exist "DISTRIBUTION\Advanced_Tape_Restorer_v2.exe" (
    echo [MISSING] Advanced_Tape_Restorer_v2.exe
    set MISSING=1
) else (
    echo [OK] Advanced_Tape_Restorer_v2.exe
)

echo.

if %MISSING%==1 (
    echo [ERROR] Some required files are missing!
    echo Cannot build distribution package.
    pause
    exit /b 1
)

echo All critical files present!
echo.

REM Get file size of EXE
for %%A in ("DISTRIBUTION\Advanced_Tape_Restorer_v2.exe") do (
    set SIZE=%%~zA
    set /A SIZE_MB=!SIZE! / 1048576
)
echo EXE Size: !SIZE_MB! MB
echo.

REM Build ZIP package
echo Building ZIP package...
echo.

REM Delete old ZIP if exists
if exist "%PACKAGE_NAME%.zip" (
    echo Removing old package...
    del "%PACKAGE_NAME%.zip" >nul 2>&1
)

REM Check if 7-Zip is available (better compression)
where 7z >nul 2>&1
if %errorlevel%==0 (
    echo Using 7-Zip for compression...
    7z a -tzip "%PACKAGE_NAME%.zip" ".\DISTRIBUTION\*" -mx9 >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] 7-Zip compression failed!
        goto POWERSHELL_ZIP
    )
    echo [OK] ZIP created with 7-Zip
    goto ZIP_DONE
)

:POWERSHELL_ZIP
echo Using PowerShell for compression...
powershell -Command "Compress-Archive -Path 'DISTRIBUTION\*' -DestinationPath '%PACKAGE_NAME%.zip' -CompressionLevel Optimal -Force"
if errorlevel 1 (
    echo [ERROR] PowerShell compression failed!
    pause
    exit /b 1
)
echo [OK] ZIP created with PowerShell

:ZIP_DONE

REM Get ZIP file size
if exist "%PACKAGE_NAME%.zip" (
    for %%A in ("%PACKAGE_NAME%.zip") do (
        set ZIP_SIZE=%%~zA
        set /A ZIP_SIZE_MB=!ZIP_SIZE! / 1048576
    )
    echo.
    echo ================================================================
    echo  DISTRIBUTION PACKAGE CREATED SUCCESSFULLY!
    echo ================================================================
    echo.
    echo Package: %PACKAGE_NAME%.zip
    echo Size: !ZIP_SIZE_MB! MB
    echo Location: %CD%\%PACKAGE_NAME%.zip
    echo.
    echo Contents:
    echo   - Advanced_Tape_Restorer_v2.exe (!SIZE_MB! MB)
    echo   - README.txt (comprehensive user guide)
    echo   - Setup scripts (3 batch files)
    echo   - Documentation (4 guides)
    echo.
    echo READY FOR DISTRIBUTION!
    echo.
) else (
    echo [ERROR] ZIP file not created!
    echo Something went wrong during packaging.
    pause
    exit /b 1
)

echo Press any key to open the folder containing the package...
pause >nul
explorer /select,"%CD%\%PACKAGE_NAME%.zip"

endlocal
exit /b 0
