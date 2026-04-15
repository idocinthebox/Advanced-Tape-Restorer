# Advanced Tape Restorer v4.1 - GitHub Release Build Script
# This script creates both EXE and ZIP distribution for GitHub release
# MIT Licensed Components Only

param(
    [switch]$Clean = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$VERSION = "4.1.0"
$PROJECT_NAME = "Advanced_Tape_Restorer"
$RELEASE_NAME = "${PROJECT_NAME}_v${VERSION}"
$DIST_DIR = "dist"
$BUILD_DIR = "build"
$RELEASE_DIR = "github_release"
$ZIP_NAME = "${RELEASE_NAME}_Windows.zip"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Advanced Tape Restorer v$VERSION" -ForegroundColor Cyan
Write-Host "GitHub Release Build (MIT Licensed)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous builds
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path $DIST_DIR) { Remove-Item -Recurse -Force $DIST_DIR }
    if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }
    if (Test-Path $RELEASE_DIR) { Remove-Item -Recurse -Force $RELEASE_DIR }
    if (Test-Path "*.spec") { Remove-Item -Force *.spec }
    Write-Host "Cleanup complete." -ForegroundColor Green
    Write-Host ""
}

# Step 1: Run tests (optional)
if (-not $SkipTests) {
    Write-Host "[1/6] Running tests..." -ForegroundColor Yellow
    python main.py --test
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Tests failed! Aborting build." -ForegroundColor Red
        exit 1
    }
    Write-Host "Tests passed!" -ForegroundColor Green
} else {
    Write-Host "[1/6] Skipping tests..." -ForegroundColor Gray
}
Write-Host ""

# Step 2: Check prerequisites
Write-Host "[2/6] Checking prerequisites..." -ForegroundColor Yellow

# Check if PyInstaller is installed
try {
    $pyinstallerVersion = & pyinstaller --version 2>&1
    Write-Host "  PyInstaller: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "  PyInstaller not found! Installing..." -ForegroundColor Red
    pip install pyinstaller
}

# Check required files
$requiredFiles = @(
    "main.py",
    "core.py",
    "capture.py",
    "LICENSE",
    "README.md",
    "restoration_presets.json",
    "restoration_settings.json"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "  ERROR: Required file missing: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  All required files present." -ForegroundColor Green
Write-Host ""

# Step 3: Build EXE with PyInstaller
Write-Host "[3/6] Building EXE with PyInstaller..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray

pyinstaller --noconfirm --clean main_v4.1.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "  PyInstaller build failed!" -ForegroundColor Red
    exit 1
}

# Check if EXE was created
$exePath = Join-Path $DIST_DIR "${PROJECT_NAME}_v${VERSION}.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "  ERROR: EXE not found at: $exePath" -ForegroundColor Red
    exit 1
}

$exeSize = (Get-Item $exePath).Length / 1MB
Write-Host "  EXE created successfully! Size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Green
Write-Host ""

# Step 4: Create release directory structure
Write-Host "[4/6] Creating release directory..." -ForegroundColor Yellow

# Create release folder
if (Test-Path $RELEASE_DIR) { Remove-Item -Recurse -Force $RELEASE_DIR }
New-Item -ItemType Directory -Path $RELEASE_DIR | Out-Null

# Copy EXE
Copy-Item $exePath $RELEASE_DIR
Write-Host "  Copied EXE" -ForegroundColor Green

# Copy documentation
$docs = @(
    "README.md",
    "LICENSE",
    "CHANGELOG.txt",
    "QUICK_START_GUIDE.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Copy-Item $doc $RELEASE_DIR
        Write-Host "  Copied $doc" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: $doc not found, skipping..." -ForegroundColor Yellow
    }
}

# Copy configuration files
Copy-Item "restoration_presets.json" $RELEASE_DIR
Copy-Item "restoration_settings.json" $RELEASE_DIR
Write-Host "  Copied configuration files" -ForegroundColor Green

# Create DOWNLOAD_INSTRUCTIONS.txt
$downloadInstructions = @"
ADVANCED TAPE RESTORER v$VERSION - INSTALLATION INSTRUCTIONS
================================================================

WINDOWS INSTALLATION
--------------------

1. Extract this ZIP file to a location of your choice
   (e.g., C:\Program Files\Advanced Tape Restorer\)

2. IMPORTANT: Before running, ensure you have installed:
   - FFmpeg (6.0+) - https://ffmpeg.org/download.html
   - VapourSynth (R65+) - https://www.vapoursynth.com/
   - Python 3.8+ (optional, for AI models)

3. Double-click: Advanced_Tape_Restorer_v$VERSION.exe

4. On first run:
   - Windows may show "Windows protected your PC"
   - Click "More info" → "Run anyway"
   - This is normal for unsigned applications

5. The application will perform prerequisite checks
   - If FFmpeg/VapourSynth are missing, you'll see warnings
   - Follow on-screen instructions to install missing components


PREREQUISITES INSTALLATION
---------------------------

FFmpeg:
  1. Download from: https://www.gyan.dev/ffmpeg/builds/
  2. Extract to C:\ffmpeg\
  3. Add C:\ffmpeg\bin to your PATH environment variable

VapourSynth:
  1. Download from: https://github.com/vapoursynth/vapoursynth/releases
  2. Run installer (VapourSynth64-R##.exe)
  3. Install recommended plugins via vsrepo

AI Models (Optional):
  - Models download automatically when first used
  - Requires ~2-10 GB disk space per model
  - NVIDIA GPU recommended for best performance


FIRST-TIME SETUP
-----------------

1. Go to "Restoration" tab
2. Select a test video file
3. Choose output location
4. Click "Start Restoration"
5. Wait for processing to complete

For detailed usage instructions, see QUICK_START_GUIDE.md


PORTABLE INSTALLATION
---------------------

This is a portable application - no installation required!
- Run directly from any folder
- Settings saved to %LOCALAPPDATA%\Advanced_Tape_Restorer\
- Move the folder anywhere without breaking functionality


LICENSE
-------

This software is licensed under the MIT License.
See LICENSE file for full license text.

Version $VERSION is completely FREE and open source.


SUPPORT
-------

- GitHub Issues: https://github.com/[your-username]/advanced-tape-restorer/issues
- Documentation: See README.md and QUICK_START_GUIDE.md
- Community: [Discord/Forum link if available]


TROUBLESHOOTING
---------------

Application won't start:
  - Check Windows Event Viewer for errors
  - Run from command line to see error messages:
    cmd /c Advanced_Tape_Restorer_v$VERSION.exe

"FFmpeg not found" error:
  - Install FFmpeg and add to PATH
  - Restart application

"VapourSynth not found" error:
  - Install VapourSynth
  - Restart application

Video processing fails:
  - Check that input video is valid
  - Ensure enough disk space for output
  - Review log messages in application


WHAT'S NEW IN v$VERSION
------------------------

See CHANGELOG.txt for complete version history.


================================================================
Advanced Tape Restorer v$VERSION
Released: December 2025
MIT Licensed - Free and Open Source
================================================================
"@

Set-Content -Path (Join-Path $RELEASE_DIR "DOWNLOAD_INSTRUCTIONS.txt") -Value $downloadInstructions
Write-Host "  Created DOWNLOAD_INSTRUCTIONS.txt" -ForegroundColor Green
Write-Host ""

# Step 5: Create ZIP distribution
Write-Host "[5/6] Creating ZIP distribution..." -ForegroundColor Yellow

$zipPath = Join-Path (Get-Location) $ZIP_NAME

# Remove existing ZIP if present
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

# Create ZIP
Compress-Archive -Path "$RELEASE_DIR\*" -DestinationPath $zipPath -CompressionLevel Optimal

$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "  ZIP created: $ZIP_NAME ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Step 6: Generate checksums
Write-Host "[6/6] Generating checksums..." -ForegroundColor Yellow

$sha256 = Get-FileHash -Path $zipPath -Algorithm SHA256
$checksumFile = "${RELEASE_NAME}_SHA256.txt"

$checksumContent = @"
Advanced Tape Restorer v$VERSION - SHA256 Checksums
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

$ZIP_NAME
SHA256: $($sha256.Hash)

Verify the integrity of your download:
1. Open PowerShell in the download folder
2. Run: Get-FileHash -Path "$ZIP_NAME" -Algorithm SHA256
3. Compare the hash with the one above
"@

Set-Content -Path $checksumFile -Value $checksumContent
Write-Host "  Checksums saved to: $checksumFile" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Release files ready for GitHub:" -ForegroundColor White
Write-Host "  1. $ZIP_NAME ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Yellow
Write-Host "  2. $checksumFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Upload instructions:" -ForegroundColor White
Write-Host "  1. Go to: https://github.com/[your-username]/advanced-tape-restorer/releases" -ForegroundColor Gray
Write-Host "  2. Click 'Draft a new release'" -ForegroundColor Gray
Write-Host "  3. Tag: v$VERSION" -ForegroundColor Gray
Write-Host "  4. Title: Advanced Tape Restorer v$VERSION" -ForegroundColor Gray
Write-Host "  5. Attach: $ZIP_NAME" -ForegroundColor Gray
Write-Host "  6. Paste checksums from: $checksumFile" -ForegroundColor Gray
Write-Host "  7. Click 'Publish release'" -ForegroundColor Gray
Write-Host ""
Write-Host "Optional: Also attach the standalone EXE" -ForegroundColor White
Write-Host "  Location: $RELEASE_DIR\${PROJECT_NAME}_v${VERSION}.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "Build artifacts:" -ForegroundColor White
Write-Host "  - EXE: $RELEASE_DIR\${PROJECT_NAME}_v${VERSION}.exe" -ForegroundColor Gray
Write-Host "  - ZIP: $ZIP_NAME" -ForegroundColor Gray
Write-Host "  - Checksums: $checksumFile" -ForegroundColor Gray
Write-Host ""
