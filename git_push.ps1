Set-Location "D:\Lab3_car_site"
git add .
git commit -m "Update project with repository improvements"
git pull origin main --rebase
git push origin main
Write-Host "Done" -ForegroundColor Green

