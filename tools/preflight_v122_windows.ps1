$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
Write-Host 'V1.2.2 — Python/API tests'
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'PYTHON REGRESSION FAILED' }
Write-Host 'V1.2.2 — Offline Godot sanity check'
& $python tools\check_gdscript_static_v11.py
if ($LASTEXITCODE -ne 0) { throw 'OFFLINE GDSCRIPT SANITY FAILED' }
Write-Host 'Art-bible audit (rejected characters are NOT approved)'
& $python tools\validate_visual_art_v12.py
if ($LASTEXITCODE -ne 0) { throw 'ART CHECK COULD NOT RUN' }
$godot = Get-Command godot4 -ErrorAction SilentlyContinue
if (-not $godot) { $godot = Get-Command godot -ErrorAction SilentlyContinue }
if (-not $godot) { Write-Warning 'Godot CLI not found. You MUST launch Godot editor and check errors before treating this build as verified.'; exit 0 }
Write-Host 'Godot native parser check'
& $godot.Source --headless --path '.\godot' --editor --quit
if ($LASTEXITCODE -ne 0) { throw 'GODOT PARSER FAILED' }
Write-Host 'ENGINEERING CHECKS PASS. Character-art acceptance remains OPEN.'
