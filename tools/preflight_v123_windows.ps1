$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
Write-Host 'V1.2.3 — Python/API / UI regressions'
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Regression suite FAILED' }
Write-Host 'V1.2.3 — Offline Godot script sanity check'
& $python tools\check_gdscript_static_v11.py
if ($LASTEXITCODE -ne 0) { throw 'GDScript static sanity FAILED' }
Write-Host 'V1.2.3 — Art approval readiness (intentionally NOT passing)'
& $python tools\validate_portraits_v123.py
if ($LASTEXITCODE -ne 0) { throw 'Art audit script failed to run' }
Write-Warning 'PRODUCTION ART GATE remains OPEN: seven rejected visitors still require 12 full-resolution illustrated portraits each.'
$godot = Get-Command godot4 -ErrorAction SilentlyContinue
if (-not $godot) { $godot = Get-Command godot -ErrorAction SilentlyContinue }
if ($godot) {
    Write-Host 'Native Godot parser/import check'
    & $godot.Source --headless --path '.\godot' --editor --quit
    if ($LASTEXITCODE -ne 0) { throw 'GODOT PARSER FAILED — do not accept build' }
} else {
    Write-Warning 'Godot CLI not found; you MUST open Godot editor and check Debugger/Output for errors before acceptance.'
}
Write-Host 'V1.2.3 engineering preflight completed; visual/art approval still required.'
