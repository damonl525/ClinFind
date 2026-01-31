@echo off
chcp 65001 >nul
echo ========================================
echo File Searcher V3 - Development Mode
echo ========================================
echo.

echo [1/2] Starting Backend Server...
cd /d "%~dp0backend"
start "FileSearcher Backend" cmd /k "python main.py"

echo [2/2] Waiting for backend to start...
timeout /t 3 >nul

echo [3/3] Starting Frontend (Electron)...
cd /d "%~dp0frontend"
npm run dev

pause
