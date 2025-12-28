@echo off
REM Create Desktop Shortcut for Advanced Tape Restorer v4.0

echo ================================================================
echo   Creating Desktop Shortcut
echo ================================================================
echo.

REM Get desktop path
set DESKTOP=%USERPROFILE%\Desktop

REM Get current directory (where the batch file is)
set CURRENT_DIR=%~dp0

REM Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Advanced Tape Restorer v4.0.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%CURRENT_DIR%Clean_Start.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Advanced Tape Restorer v4.0 - Professional Video Restoration" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%CURRENT_DIR%icon.ico,0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

REM Run VBS script
cscript //nologo "%TEMP%\CreateShortcut.vbs"

REM Clean up
del "%TEMP%\CreateShortcut.vbs"

echo.
echo ================================================================
echo   ✓ Desktop shortcut created!
echo ================================================================
echo.
echo You can now launch the app from your desktop.
echo Double-click: "Advanced Tape Restorer v4.0"
echo.

pause
