@echo off
cd /d D:\Lab3_car_site
echo Checking git status...
git status
echo.
echo Adding README.md...
git add README.md
echo.
echo Committing changes...
git commit -m "Update README with Repository pattern description"
echo.
echo Pushing to GitHub...
git push origin main
echo.
echo Done!
pause

