@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════╗
echo ║     Backend Server Only - Port 8000   ║
echo ╚════════════════════════════════════════╝
echo.

cd /d "%~dp0backend"

echo 🚀 Starting backend server...
echo.
echo 📍 Server will run on: http://localhost:8000
echo 🔍 Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
