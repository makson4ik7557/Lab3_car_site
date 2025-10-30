Set-Location "D:\Lab3_car_site"
git rm --cached commit_changes.bat commit_changes.ps1 push_changes.ps1
git add .
git commit -m "Add car data and repository improvements"
git pull origin main --rebase
git push origin main
Write-Host "Done" -ForegroundColor Green

