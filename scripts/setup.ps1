# TrendForge AI - one-time development setup (Windows / PowerShell)
# Installs backend (Python) and frontend (Node) dependencies.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Setting up backend" -ForegroundColor Cyan
Push-Location (Join-Path $root "backend")
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend/.env (edit it to add your Gemini API key)." -ForegroundColor Yellow
}
Pop-Location

Write-Host "==> Setting up frontend" -ForegroundColor Cyan
Push-Location (Join-Path $root "frontend")
npm install
Pop-Location

Write-Host "`nSetup complete." -ForegroundColor Green
Write-Host "Start the backend:  scripts\backend.ps1"
Write-Host "Start the frontend: scripts\frontend.ps1"
