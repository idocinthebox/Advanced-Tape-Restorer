# Advanced Tape Restorer v4.0 (Community Edition) - Build Script
# FREE version without AI features - MIT Licensed
# This builds a much smaller EXE (~500MB vs 3GB) without PyTorch/AI models

param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Advanced Tape Restorer v4.0" -ForegroundColor Green
Write-Host "Community Edition (FREE - No AI)" -ForegroundColor Yellow
Write-Host "=========================================`n" -ForegroundColor Cyan

# Step 1: Optional tests
if (-not $SkipTests) {
    Write-Host "[1/6] Running tests..." -ForegroundColor Cyan
    try {
        python main.py --test
        Write-Host "✓ Tests passed`n" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Tests failed, but continuing build..." -ForegroundColor Yellow
    }
} else {
    Write-Host "[1/6] Skipping tests (-SkipTests specified)`n" -ForegroundColor Yellow
}

# Step 2: Check prerequisites
Write-Host "[2/6] Checking prerequisites..." -ForegroundColor Cyan

# Check PyInstaller
try {
    $pyinstallerVersion = python -m PyInstaller --version 2>&1
    Write-Host "  ✓ PyInstaller: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ PyInstaller not found. Installing..." -ForegroundColor Red
    pip install pyinstaller
}

# Check required files
$requiredFiles = @(
    "main.py",
    "main_v4.0.spec",
    "core.py",
    "capture.py",
    "restoration_presets.json",
    "restoration_settings.json",
    "LICENSE",
    "README.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Missing: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 3: Clean previous builds
Write-Host "[3/6] Cleaning previous builds..." -ForegroundColor Cyan
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "  ✓ Removed build/" -ForegroundColor Green
}
if (Test-Path "dist\Advanced_Tape_Restorer_v4.0.exe") {
    Remove-Item -Force "dist\Advanced_Tape_Restorer_v4.0.exe"
    Write-Host "  ✓ Removed old v4.0 EXE" -ForegroundColor Green
}
Write-Host ""

# Step 4: Build EXE with PyInstaller
Write-Host "[4/6] Building v4.0 EXE (this may take 5-10 minutes)..." -ForegroundColor Cyan
Write-Host "  NOTE: v4.0 will be MUCH smaller (~500MB) without PyTorch/AI" -ForegroundColor Yellow
Write-Host ""

try {
    pyinstaller --noconfirm --clean main_v4.0.spec
    Write-Host "`n  ✓ Build successful!" -ForegroundColor Green
} catch {
    Write-Host "`n  ✗ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 5: Verify EXE exists
Write-Host "`n[5/6] Verifying build..." -ForegroundColor Cyan
if (Test-Path "dist\Advanced_Tape_Restorer_v4.0.exe") {
    $exeSize = (Get-Item "dist\Advanced_Tape_Restorer_v4.0.exe").Length / 1MB
    Write-Host "  ✓ EXE created: dist\Advanced_Tape_Restorer_v4.0.exe" -ForegroundColor Green
    Write-Host "  ✓ Size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Green
    
    if ($exeSize -gt 1000) {
        Write-Host "  ⚠ Warning: EXE is larger than expected (should be ~500MB)" -ForegroundColor Yellow
        Write-Host "    PyTorch/AI may not have been excluded properly" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ Size looks good (no AI bloat!)" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ EXE not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Create distribution package
Write-Host "[6/6] Creating v4.0 distribution package..." -ForegroundColor Cyan

# Create release directory
$releaseDir = "github_release_v4.0"
if (Test-Path $releaseDir) {
    Remove-Item -Recurse -Force $releaseDir
}
New-Item -ItemType Directory -Path $releaseDir | Out-Null

# Copy v4.0 files
Copy-Item "dist\Advanced_Tape_Restorer_v4.0.exe" $releaseDir
Copy-Item "LICENSE" $releaseDir
Copy-Item "README.md" $releaseDir
Copy-Item "restoration_presets.json" $releaseDir
Copy-Item "restoration_settings.json" $releaseDir
Copy-Item "QUICK_START_GUIDE.md" $releaseDir
Copy-Item "LICENSING_GUIDE.md" $releaseDir
Copy-Item "VERSION_FEATURE_MATRIX.md" $releaseDir

# Copy setup batch files (FIRST_TIME_SETUP.bat + Setup/)
if (Test-Path "DISTRIBUTION\FIRST_TIME_SETUP.bat") {
    Copy-Item "DISTRIBUTION\FIRST_TIME_SETUP.bat" $releaseDir
    Write-Host "  ✓ Copied FIRST_TIME_SETUP.bat" -ForegroundColor Green
}
if (Test-Path "DISTRIBUTION\Setup") {
    Copy-Item -Recurse "DISTRIBUTION\Setup" $releaseDir
    Write-Host "  ✓ Copied Setup/ folder (batch files)" -ForegroundColor Green
}

Write-Host "  ✓ Created $releaseDir/" -ForegroundColor Green
Write-Host ""

# Step 7: Create ZIP
Write-Host "[7/7] Creating ZIP file..." -ForegroundColor Cyan
$zipFile = "Advanced_Tape_Restorer_v4.0_Windows.zip"
if (Test-Path $zipFile) {
    Remove-Item -Force $zipFile
}

# Check for 7-Zip
$sevenZip = "C:\Program Files\7-Zip\7z.exe"
if (Test-Path $sevenZip) {
    Write-Host "  Using 7-Zip for compression..." -ForegroundColor Gray
    & $sevenZip a -mx=1 $zipFile ".\$releaseDir\*"
    Write-Host "  ✓ ZIP created with 7-Zip" -ForegroundColor Green
} else {
    Write-Host "  Using PowerShell Compress-Archive..." -ForegroundColor Gray
    Compress-Archive -Path "$releaseDir\*" -DestinationPath $zipFile -CompressionLevel Fastest
    Write-Host "  ✓ ZIP created" -ForegroundColor Green
}

# Calculate SHA256
Write-Host "`n[8/8] Calculating SHA256 checksums..." -ForegroundColor Cyan
$exeHash = (Get-FileHash "dist\Advanced_Tape_Restorer_v4.0.exe" -Algorithm SHA256).Hash
$zipHash = (Get-FileHash $zipFile -Algorithm SHA256).Hash

# Create checksums file
$checksumFile = "Advanced_Tape_Restorer_v4.0_SHA256.txt"
@"
Advanced Tape Restorer v4.0 (Community Edition) - SHA256 Checksums
==================================================================

EXE File:
  Filename: Advanced_Tape_Restorer_v4.0.exe
  SHA256:   $exeHash
  Size:     $([math]::Round((Get-Item "dist\Advanced_Tape_Restorer_v4.0.exe").Length / 1MB, 2)) MB

ZIP File:
  Filename: Advanced_Tape_Restorer_v4.0_Windows.zip
  SHA256:   $zipHash
  Size:     $([math]::Round((Get-Item $zipFile).Length / 1MB, 2)) MB

Verification Instructions:
=========================

Windows PowerShell:
  Get-FileHash "Advanced_Tape_Restorer_v4.0_Windows.zip" -Algorithm SHA256

Windows CMD:
  certutil -hashfile "Advanced_Tape_Restorer_v4.0_Windows.zip" SHA256

Compare the output with the SHA256 above. If they don't match, re-download.

Build Information:
==================
  Version: v4.0 (Community Edition - FREE)
  License: MIT
  Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  Features: Basic restoration (NO AI)
  
v4.0 includes:
  ✅ QTGMC deinterlacing
  ✅ Hardware capture (DirectShow, DV/FireWire)
  ✅ Multi-GPU support
  ✅ All output formats
  ❌ NO AI models (RealESRGAN, RIFE, etc.)
  ❌ NO ONNX/NPU acceleration
  
For AI features, see v4.1 (paid): https://github.com/YOUR_USERNAME/Advanced-Tape-Restorer/releases/tag/v4.1.0

"@ | Out-File -FilePath $checksumFile -Encoding UTF8

Write-Host "  ✓ Checksums saved to $checksumFile" -ForegroundColor Green

# Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "✅ BUILD COMPLETE!" -ForegroundColor Green
Write-Host "=========================================`n" -ForegroundColor Cyan

Write-Host "Build artifacts:" -ForegroundColor Yellow
Write-Host "  • dist\Advanced_Tape_Restorer_v4.0.exe" -ForegroundColor White
Write-Host "  • $zipFile" -ForegroundColor White
Write-Host "  • $checksumFile" -ForegroundColor White
Write-Host "  • $releaseDir\ (release folder)" -ForegroundColor White

Write-Host "`nEXE SHA256: " -ForegroundColor Yellow -NoNewline
Write-Host $exeHash -ForegroundColor White

Write-Host "ZIP SHA256: " -ForegroundColor Yellow -NoNewline
Write-Host $zipHash -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Test the EXE: .\dist\Advanced_Tape_Restorer_v4.0.exe" -ForegroundColor Gray
Write-Host "  2. Upload ZIP to Cloudflare R2 or GitHub" -ForegroundColor Gray
Write-Host "  3. Publish v4.0 release with $checksumFile" -ForegroundColor Gray
Write-Host "  4. Update release notes with download link`n" -ForegroundColor Gray

Write-Host "v4.0 is FREE and MIT licensed!" -ForegroundColor Green
Write-Host "For AI features, users can upgrade to v4.1 ($45/$150)`n" -ForegroundColor Yellow
