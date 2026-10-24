@echo off
title Fieldwise GeoAI - Starter
echo ========================================================
echo   Fieldwise - Outdoor Intelligence Assistant
echo   CSRE, IIT Bombay GeoAI Hackathon 2026
echo ========================================================
echo.

echo [1/3] Clearing old processes on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000...
start "Fieldwise Backend (Port 8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Starting Next.js Frontend on http://localhost:3000...
start "Fieldwise Frontend (Port 3000)" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo ========================================================
echo   Fieldwise GeoAI is starting up!
echo   - Web UI:    http://localhost:3000
echo   - API Docs:  http://127.0.0.1:8000/docs
echo ========================================================
timeout /t 5 >nul
start http://localhost:3000
