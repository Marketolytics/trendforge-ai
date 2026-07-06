# Validate a built TrendForge AI release.
#   - the embedded backend launches, initializes the DB and creates the workspace
#   - expected installer / portable / checksum artifacts exist
#
# Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts\validate_release.ps1

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$fail = 0
function Check($name, $ok) {
    if ($ok) { Write-Host "  [PASS] $name" -ForegroundColor Green }
    else { Write-Host "  [FAIL] $name" -ForegroundColor Red; $script:fail++ }
}

Write-Host "==> Validating embedded backend"
$exe = Get-ChildItem "$root\frontend\src-tauri\binaries\trendforge-backend-*.exe" -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $exe) { $exe = Get-Item "$root\backend\dist\trendforge-backend.exe" -ErrorAction SilentlyContinue }
Check "Backend sidecar exists" ($null -ne $exe)

if ($exe) {
    $ws = Join-Path $env:TEMP "tf_validate_ws"
    if (Test-Path $ws) { Remove-Item $ws -Recurse -Force }
    $env:TRENDFORGE_DATA_DIR = $ws
    $port = 8799
    $proc = Start-Process -FilePath $exe.FullName -ArgumentList "--port", $port -PassThru -WindowStyle Hidden

    $up = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 500
        try { if ((Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$port/api/health").StatusCode -eq 200) { $up = $true; break } } catch { }
    }
    Check "Backend launches + responds to /api/health" $up

    if ($up) {
        $report = Invoke-RestMethod "http://127.0.0.1:$port/api/system/health-report"
        Check "Database initializes" ($report.database -eq "ok")
        Check "Workspace created" ($report.workspace -eq "ok")
        foreach ($d in @("projects", "exports", "cache", "logs", "backups", "settings", "temp")) {
            Check "Workspace folder: $d" (Test-Path (Join-Path $ws $d))
        }
    }
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Remove-Item Env:\TRENDFORGE_DATA_DIR -ErrorAction SilentlyContinue
}

Write-Host "==> Validating release artifacts"
$rel = Get-ChildItem "$root\dist\release" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
if ($rel) {
    Check "Installer (.exe/.msi) present" ((Get-ChildItem "$($rel.FullName)\*" -Include *.exe, *.msi -ErrorAction SilentlyContinue).Count -gt 0)
    Check "Portable ZIP present" ((Get-ChildItem "$($rel.FullName)\*portable*.zip" -ErrorAction SilentlyContinue).Count -gt 0)
    Check "SHA256SUMS present" (Test-Path "$($rel.FullName)\SHA256SUMS.txt")
} else {
    Write-Host "  (no dist\release found - run build_release.ps1 first)" -ForegroundColor Yellow
}

Write-Host ""
if ($fail -eq 0) { Write-Host "All checks passed." -ForegroundColor Green; exit 0 }
else { Write-Host "$fail check(s) failed." -ForegroundColor Red; exit 1 }
