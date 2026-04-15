# GitHub Release Upload Script for v4.0
# Uses GitHub CLI (gh) to create release and upload files

Write-Host "`n=== Creating GitHub Release v4.0.0 ===" -ForegroundColor Cyan

# Check if gh CLI installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] GitHub CLI not installed!" -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "OR use GitHub web interface instead" -ForegroundColor Yellow
    exit 1
}

# Navigate to v4.0 directory
cd "C:\Advanced Tape Restorer v4.0"

# Create release
Write-Host "`nCreating release..." -ForegroundColor Yellow
gh release create v4.0.0 `
    --title "Advanced Tape Restorer v4.0 - Community Edition (FREE)" `
    --notes-file "GITHUB_RELEASE_NOTES_V4.0.md" `
    --repo idocinthebox/Advanced-Tape-Restorer `
    "Advanced_Tape_Restorer_v4.0_Community_Edition_with_Setup.zip#v4.0 Community Edition (45.65 MB)" `
    "Advanced_Tape_Restorer_v4.0_SHA256_with_Setup.txt#SHA256 Checksums"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Release created!" -ForegroundColor Green
    Write-Host "View at: https://github.com/idocinthebox/Advanced-Tape-Restorer/releases/tag/v4.0.0" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] Release creation failed!" -ForegroundColor Red
    Write-Host "Try using GitHub web interface instead" -ForegroundColor Yellow
}
