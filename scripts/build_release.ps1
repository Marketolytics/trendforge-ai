# Build a portable TrendForge AI Windows release.
#
# Prerequisites (on the build machine):
#   - Python 3.12+ with backend deps installed (+ pyinstaller)
#   - Node.js 20+
#   - Rust toolchain + Microsoft C++ Build Tools + WebView2
#
# Run from the repo root:  powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "==> 1/3  Building backend sidecar (PyInstaller)"
Push-Location "$root\backend"
& .\.venv\Scripts\python.exe -m pip install pyinstaller --quiet
& .\.venv\Scripts\python.exe -m PyInstaller trendforge-backend.spec --noconfirm
Pop-Location

# Tauri sidecars must carry the Rust target-triple suffix.
$triple = (rustc -Vv | Select-String "host:").ToString().Split(":")[1].Trim()
$binDir = "$root\frontend\src-tauri\binaries"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
Copy-Item "$root\backend\dist\trendforge-backend.exe" "$binDir\trendforge-backend-$triple.exe" -Force
Write-Host "    sidecar -> binaries\trendforge-backend-$triple.exe"

Write-Host "==> 2/3  Installing frontend deps"
Push-Location "$root\frontend"
npm install

Write-Host "==> 3/3  Building the desktop app + installer (Tauri)"
npm run tauri build
Pop-Location

Write-Host "`nDone. Installer + portable exe are in:"
Write-Host "  frontend\src-tauri\target\release\bundle\"
