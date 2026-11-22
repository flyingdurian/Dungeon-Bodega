$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$needed = @('godot/project.godot', 'godot/scripts/Main.gd', 'backend/exodia.py', 'godot/assets/art_review/vn_master_chen_thinking.png', 'art/portrait_recovery_status_v124.json')
foreach ($f in $needed) { if (-not (Test-Path $f)) { throw "Missing required V1.2.4 file: $f" } }
Write-Host 'V1.2.4 files: PASS'
if (Test-Path '.venv/Scripts/python.exe') {
    & .\.venv\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Regression suite failed.' }
} else {
    Write-Host 'Regression suite: not run (install Python dependencies / launch backend first)'
}
Write-Host 'Art gate remains OPEN: 12 independent, approved states required for each rejected character.'
Write-Host 'Next: launch Godot, select Master Chen (F11), press F2 for review-only states.'
