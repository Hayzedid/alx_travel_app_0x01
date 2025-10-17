@echo off
echo Pushing ALX Travel App API v0x01 to GitHub...
cd /d "c:\Users\USER\Documents\Alx Projects\alx_travel_app_0x01"

echo.
echo Committing files...
git commit -m "Add ALX Travel App API v0x01 with Django REST Framework"

echo.
echo Adding remote origin...
git remote add origin https://github.com/Hayzedid/alx_travel_app_0x01.git

echo.
echo Setting main branch...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo Done! Check your repository at: https://github.com/Hayzedid/alx_travel_app_0x01
pause
