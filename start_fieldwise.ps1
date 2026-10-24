# Fieldwise PowerShell Launcher
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "  Launching Fieldwise - Outdoor Spatio-Temporal AI" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""

$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

Write-Host "[1/3] Starting Backend API Server (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='backend'; cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/3] Starting Frontend Web Interface (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm.cmd run dev"

Start-Sleep -Seconds 4

Write-Host "[3/3] Opening browser at http://localhost:3000..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Fieldwise is now running!" -ForegroundColor Green
Write-Host " - Web UI: http://localhost:3000" -ForegroundColor Yellow
Write-Host " - Backend API: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host " - Presentation Deck: docs\presentation.html" -ForegroundColor Yellow
