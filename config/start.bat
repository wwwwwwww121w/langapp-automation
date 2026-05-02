@echo off
chcp 65001 >nul 2>&1
echo.
echo   ArabicEngLearn — Web Dashboard
echo   http://localhost:5000
echo.

cd /d C:\langapp-automation

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Install from python.org
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet 2>nul

echo   Starting server...
echo.
start http://localhost:5000
python app.py
pause
