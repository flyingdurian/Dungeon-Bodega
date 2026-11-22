# Optional Godot 4 preflight after extracting the project on Windows.
# Usage: powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe 'C:\path\to\Godot_v4.4-stable_win64.exe'
param([string]$GodotExe = 'godot')
$ErrorActionPreference = 'Stop'
$game = (Resolve-Path (Join-Path $PSScriptRoot '..\godot')).Path
$log = Join-Path $PSScriptRoot '..\godot-preflight.log'
Write-Host "Checking Godot project: $game"
$lines = @(& $GodotExe --headless --editor --path $game --quit 2>&1 | Out-String)
$lines | Set-Content -Path $log -Encoding UTF8
$failure = ($LASTEXITCODE -ne 0) -or ($lines -match '(?i)SCRIPT ERROR|Parse Error|Parser Error|Failed to load script|Invalid access to property')
if ($failure) {
    Write-Host "Godot preflight FAILED. Inspect: $log" -ForegroundColor Red
    exit 1
}
Write-Host "Godot preflight PASSED. Log: $log" -ForegroundColor Green
