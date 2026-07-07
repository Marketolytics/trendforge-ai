# TrendForge AI - run the FastAPI backend (development, auto-reload)
# Serves the API at http://localhost:8000 (docs at /docs, health at /api/health).

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root "backend")

if (-not (Test-Path ".venv")) {
    Write-Host "No virtualenv found. Run scripts\setup.ps1 first." -ForegroundColor Red
    Pop-Location
    exit 1
}

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
