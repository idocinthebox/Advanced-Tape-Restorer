@echo off
REM Build Distribution Package for Advanced Tape Restorer v3.0
REM This script builds the EXE and prepares the distribution folder

setlocal
set DIST_DIR=dist_package\Advanced_Tape_Restorer_v3.0_Release
set SRC_DIR=%~dp0

REM Clean previous build
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%

REM Build EXE
pyinstaller --onefile --windowed main.py

REM Create distribution folder
mkdir %DIST_DIR%

REM Copy EXE
copy dist\main.exe %DIST_DIR%\Advanced_Tape_Restorer_v3.0.exe

REM Copy essential files
copy restoration_presets.json %DIST_DIR%\
copy restoration_settings.json %DIST_DIR%\
copy README.md %DIST_DIR%\
copy QUICK_START_GUIDE.md %DIST_DIR%\
copy LICENSE.txt %DIST_DIR%\

REM Copy model and config folders
xcopy ai_models %DIST_DIR%\ai_models /E /I /Y
xcopy config %DIST_DIR%\config /E /I /Y
xcopy core %DIST_DIR%\core /E /I /Y
xcopy capture %DIST_DIR%\capture /E /I /Y

REM Copy documentation
xcopy docs %DIST_DIR%\docs /E /I /Y

REM Done
@echo Distribution package created at %DIST_DIR%
endlocal
