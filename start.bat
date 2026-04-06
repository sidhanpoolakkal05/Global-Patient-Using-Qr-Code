@echo off
echo ============================================
echo   MediScan HMS - Django Template Server
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Django backend + frontend...
echo       http://127.0.0.1:8000
echo.
start python manage.py runserver

timeout /t 2 /nobreak > nul
echo [2/2] Opening browser...
start http://127.0.0.1:8000

echo.
echo MediScan is running at http://127.0.0.1:8000
echo Press Ctrl+C in the Django window to stop.
pause
