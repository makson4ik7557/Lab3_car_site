# PowerShell script for committing changes
Write-Host "Changing directory..." -ForegroundColor Cyan
Set-Location "D:\Lab3_car_site"

Write-Host "`nChecking git status..." -ForegroundColor Cyan
git status

Write-Host "`nAdding all changes..." -ForegroundColor Cyan
git add .

Write-Host "`nCommitting changes..." -ForegroundColor Cyan
git commit -m "Add car data and repository improvements"

Write-Host "`nPulling from GitHub..." -ForegroundColor Cyan
git pull origin main --rebase

Write-Host "`nPushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`nDone!" -ForegroundColor Green
Read-Host "Press Enter to exit"

