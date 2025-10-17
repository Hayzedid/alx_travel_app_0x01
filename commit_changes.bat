@echo off
echo Committing and pushing changes...
cd /d "c:\Users\USER\Documents\Alx Projects\alx_travel_app_0x01"

echo.
echo Committing restructured files...
git commit -m "Restructure project into alx_travel_app directory"

echo.
echo Pushing changes to GitHub...
git push origin main

echo.
echo Done! Changes pushed to: https://github.com/Hayzedid/alx_travel_app_0x01
pause
