@echo off
title Sync Saitual District Data
echo ============================================================
echo   Syncing fresh MGNREGA data for Saitual District...
echo ============================================================
echo.
python scraper.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Scraper encountered an error. Data was NOT modified.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Committing and pushing fresh data to GitHub Pages...
git add data/
git commit -m "Manual sync Saitual report data: %date% %time%"
git push origin main

echo.
echo ============================================================
echo   SUCCESS! Fresh data has been uploaded to GitHub Pages.
echo ============================================================
pause
