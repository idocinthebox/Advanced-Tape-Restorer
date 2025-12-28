# Emergency Cleanup Script
# Use this if the app is completely stuck and won't respond

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Emergency Cleanup - Advanced Tape Restorer" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kill all Python processes
Write-Host "[1/3] Terminating Python processes..." -ForegroundColor Yellow
$pythonProcs = Get-Process -Name python* -ErrorAction SilentlyContinue
if ($pythonProcs) {
    $pythonProcs | ForEach-Object {
        Write-Host "  Killing PID $($_.Id): $($_.Name)" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Done" -ForegroundColor Green
} else {
    Write-Host "  No Python processes running" -ForegroundColor Gray
}

# 2. Clear all cache
Write-Host ""
Write-Host "[2/3] Clearing Python cache..." -ForegroundColor Yellow
$cacheRemoved = 0
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  Removing: $($_.FullName)" -ForegroundColor Gray
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cacheRemoved++
}
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
    $cacheRemoved++
}
Write-Host "  ✓ Removed $cacheRemoved cache items" -ForegroundColor Green

# 3. Check for lock files
Write-Host ""
Write-Host "[3/3] Checking for lock files..." -ForegroundColor Yellow
$lockFiles = Get-ChildItem -Path . -Recurse -File -Filter "*.lock" -ErrorAction SilentlyContinue
if ($lockFiles) {
    $lockFiles | ForEach-Object {
        Write-Host "  Found: $($_.Name)" -ForegroundColor Gray
        Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ Removed lock files" -ForegroundColor Green
} else {
    Write-Host "  No lock files found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✓ Cleanup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now safely restart the app:" -ForegroundColor White
Write-Host "  - Double-click Clean_Start.bat" -ForegroundColor Yellow
Write-Host "  - Or run: python main.py" -ForegroundColor Yellow
Write-Host ""

# Pause
Read-Host "Press Enter to exit"
