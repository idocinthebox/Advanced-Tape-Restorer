# Advanced Tape Restorer v4.0 - Quick Launcher (PowerShell)
# =========================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host "  Advanced Tape Restorer v4.0-dev"
Write-Host "========================================"
Write-Host ""
Write-Host "Starting application..."
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment and run
& ".\.venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Setup required:"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\.venv\Scripts\pip.exe install -r requirements.txt"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Application failed to start!" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE"
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Check that virtual environment is set up"
    Write-Host "  2. Run: .\.venv\Scripts\Activate.ps1"
    Write-Host "  3. Verify dependencies: pip list"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}

exit 0
