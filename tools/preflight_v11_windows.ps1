$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
Write-Host 'Living Counter V1.1.0 — QA preflight'
$python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Python/API regression failed.' }
Write-Host 'Art status (strict production gate):'
& $python .\tools\validate_visual_art_v11.py
Write-Host 'Godot parser check:'
$godot = Get-Command godot -ErrorAction SilentlyContinue
if (-not $godot) { $godot = Get-Command godot4 -ErrorAction SilentlyContinue }
if ($godot) {
    & $godot.Source --headless --path .\godot --editor --quit
    if ($LASTEXITCODE -ne 0) { throw 'Godot parser/import failed.' }
} else { Write-Warning 'Godot command not found in PATH; run Godot editor manually and inspect debugger.' }
