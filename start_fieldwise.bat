@echo off
title Fieldwise Outdoor Intelligence Launcher
echo =======================================================
echo   Launching Fieldwise - Outdoor Spatio-Temporal AI
echo =======================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend API Server on http://localhost:8000 ...
start "Fieldwise Backend (Port 8000)" cmd /k "set PYTHONPATH=backend&& cd backend&& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Web Interface on http://localhost:3000 ...
start "Fieldwise Frontend (Port 3000)" cmd /k "cd frontend&& npm.cmd run dev"

timeout /t 4 /nobreak >nul

echo [3/3] Opening browser at http://localhost:3000 ...
start http://localhost:3000

echo.
echo =======================================================
echo   Fieldwise is now running!
echo   - Web UI: http://localhost:3000
echo   - Backend API Docs: http://localhost:8000/docs
echo   - Presentation Deck: docs\presentation.html
echo =======================================================
