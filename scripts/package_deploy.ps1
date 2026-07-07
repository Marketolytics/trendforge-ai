# TrendForge AI - assemble a deployable package for Hostinger shared hosting.
# Builds the frontend and stages backend + build + config into dist/deploy/,
# then zips it. Upload the zip contents to your Hostinger application root.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stage = Join-Path $root "dist\deploy"
$backendSrc = Join-Path $root "backend"
$backendDst = Join-Path $stage "backend"
$frontendDist = Join-Path $root "frontend\dist"

Write-Host "==> Building frontend" -ForegroundColor Cyan
Push-Location (Join-Path $root "frontend")
npm ci
npm run build
Pop-Location

Write-Host "==> Staging package at $stage" -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Path $backendDst | Out-Null

# Backend source (exclude local/dev artifacts).
$exclude = @(".venv", "data", "build", "dist", "__pycache__", ".pytest_cache", ".ruff_cache", ".env")
Get-ChildItem -Path $backendSrc -Force | Where-Object { $exclude -notcontains $_.Name } | ForEach-Object {
    Copy-Item $_.FullName -Destination $backendDst -Recurse -Force
}
# Prune any nested __pycache__ that slipped through.
Get-ChildItem -Path $backendDst -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Frontend build.
if (-not (Test-Path $frontendDist)) { throw "frontend/dist not found — build failed?" }
$frontendDst = Join-Path $stage "frontend\dist"
New-Item -ItemType Directory -Path $frontendDst -Force | Out-Null
Copy-Item (Join-Path $frontendDist "*") -Destination $frontendDst -Recurse -Force

# Docs.
Copy-Item (Join-Path $root "docs\DEPLOYMENT_HOSTINGER.md") -Destination $stage -Force

# Zip it.
$zip = Join-Path $root "dist\trendforge-hostinger.zip"
if (Test-Path $zip) { Remove-Item -Force $zip }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip

Write-Host "`nPackage ready:" -ForegroundColor Green
Write-Host "  Folder: $stage"
Write-Host "  Zip:    $zip"
Write-Host "Next: upload contents, set backend/.env, then run 'python manage.py initdb'." -ForegroundColor Yellow
