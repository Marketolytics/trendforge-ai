# TrendForge AI - run the React + Vite dev server
# Serves the UI at http://localhost:5173 and proxies /api to the backend.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root "frontend")

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev
Pop-Location
