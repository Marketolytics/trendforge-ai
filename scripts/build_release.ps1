# Build a distributable TrendForge AI Windows release:
#   - embedded backend (PyInstaller onefile, no Python needed by users)
#   - Tauri desktop app + NSIS/MSI installer
#   - portable ZIP + SHA-256 checksums
#
# Prerequisites (build machine only):
#   - Python 3.12+ with backend deps + pyinstaller
#   - Node.js 20+
#   - Rust toolchain + Microsoft C++ Build Tools + WebView2
#
# Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1

param(
    [string]$Channel = "release"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# --- Version + build metadata ------------------------------------------------
$conf = Get-Content "$root\frontend\src-tauri\tauri.conf.json" -Raw | ConvertFrom-Json
$version = $conf.version
$buildDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$commit = ""
try { $commit = (git -C $root rev-parse --short HEAD).Trim() } catch { }

$buildInfo = [ordered]@{
    name       = "TrendForge AI"
    version    = $version
    build_date = $buildDate
    commit     = $commit
    channel    = $Channel
}
$buildInfo | ConvertTo-Json | Set-Content "$root\backend\build_info.json" -Encoding UTF8
Write-Host "==> Building TrendForge AI v$version ($Channel, $commit)"

# --- 1/4  Backend sidecar (embedded Python runtime) --------------------------
Write-Host "==> 1/4  Backend sidecar (PyInstaller)"
Push-Location "$root\backend"
& .\.venv\Scripts\python.exe -m pip install pyinstaller --quiet
& .\.venv\Scripts\python.exe -m PyInstaller trendforge-backend.spec --noconfirm
Pop-Location

$triple = (rustc -Vv | Select-String "host:").ToString().Split(":")[1].Trim()
$binDir = "$root\frontend\src-tauri\binaries"
New-Item -ItemType Directory -Force -Path $binDir | Out-Null
Copy-Item "$root\backend\dist\trendforge-backend.exe" "$binDir\trendforge-backend-$triple.exe" -Force
Write-Host "    sidecar -> trendforge-backend-$triple.exe"

# --- 2/4  Desktop app + installer -------------------------------------------
Write-Host "==> 2/4  Desktop app + installer (Tauri)"
Push-Location "$root\frontend"
npm install
npm run tauri build
Pop-Location

# --- 3/4  Collect artifacts --------------------------------------------------
Write-Host "==> 3/4  Collecting artifacts"
$releaseDir = "$root\dist\release\v$version"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$bundle = "$root\frontend\src-tauri\target\release\bundle"
$portableExe = "$root\frontend\src-tauri\target\release\TrendForge AI.exe"

Get-ChildItem -Path "$bundle\nsis\*.exe", "$bundle\msi\*.msi" -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName $releaseDir -Force }

# Portable ZIP: raw exe + sidecar + README.
if (Test-Path $portableExe) {
    $portableStage = "$releaseDir\portable"
    New-Item -ItemType Directory -Force -Path $portableStage | Out-Null
    Copy-Item $portableExe $portableStage -Force
    Copy-Item "$binDir\trendforge-backend-$triple.exe" $portableStage -Force
    Copy-Item "$root\docs\INSTALL.md" $portableStage -Force -ErrorAction SilentlyContinue
    Compress-Archive -Path "$portableStage\*" -DestinationPath "$releaseDir\TrendForge-AI-$version-portable.zip" -Force
    Remove-Item $portableStage -Recurse -Force
}

# --- 4/4  Checksums ----------------------------------------------------------
Write-Host "==> 4/4  SHA-256 checksums"
$sums = @()
Get-ChildItem -Path $releaseDir -File | Where-Object { $_.Extension -in ".exe", ".msi", ".zip" } | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    $sums += "$hash  $($_.Name)"
}
$sums | Set-Content "$releaseDir\SHA256SUMS.txt" -Encoding ASCII

Write-Host "`nDone. Release artifacts in: $releaseDir"
Get-ChildItem $releaseDir -File | Select-Object Name, Length | Format-Table -AutoSize
