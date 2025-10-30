# PowerShell script for committing changes
Write-Host "Changing directory..." -ForegroundColor Cyan
Set-Location "D:\Lab3_car_site"

Write-Host "`nChecking git status..." -ForegroundColor Cyan
git status

Write-Host "`nAdding README.md..." -ForegroundColor Cyan
git add README.md

Write-Host "`nCommitting changes..." -ForegroundColor Cyan
git commit -m "Update README with Repository pattern description"

Write-Host "`nPushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`nDone!" -ForegroundColor Green
Read-Host "Press Enter to exit"

