$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
Write-Host 'V1.2 — Python/API regression suite'
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Python/API regression check FAILED' }
Write-Host 'V1.2 — Character-art readiness report (incomplete sets are expected and NOT approved)'
& $python tools\validate_visual_art_v12.py
if ($LASTEXITCODE -ne 0) { throw 'Art report could not run' }
$godot = Get-Command godot4 -ErrorAction SilentlyContinue
if (-not $godot) { $godot = Get-Command godot -ErrorAction SilentlyContinue }
if ($godot) {
    Write-Host 'Godot parser check (headless editor)'
    & $godot.Source --headless --path '.\godot' --editor --quit
    if ($LASTEXITCODE -ne 0) { throw 'GODOT PARSER FAILED: do not install this build' }
} else {
    Write-Host 'GODOT NOT FOUND: launch Godot editor and inspect Output/Debugger before acceptance'
}
Write-Host 'Engineering preflight complete. Production art approval is NOT implied.'
