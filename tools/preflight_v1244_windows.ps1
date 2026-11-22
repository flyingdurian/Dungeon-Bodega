# Owner review: native Godot + separate portrait QA for two visitors.
param([string]$GodotExe = '')
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$actors = @('master_chen', 'tarek_ashwood')
$states = @('neutral','thinking','amused','skeptical','annoyed')
foreach ($actor in $actors) {
    foreach ($state in $states) {
        $image = "godot/assets/vn_${actor}_${state}.png"
        if (-not (Test-Path $image)) { throw "Missing character portrait: $image" }
    }
}
Write-Host 'Ten native-size portrait assets found.'
if (Test-Path '.venv/Scripts/python.exe') {
    & .\.venv\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Backend / UI regression checks failed' }
    & .\.venv\Scripts\python.exe tools/validate_portraits_v123.py
    if ($LASTEXITCODE -ne 0) { throw 'Portrait report failed' }
} else { Write-Host 'Python suite not run (virtual environment missing).' }
if ($GodotExe -ne '') {
    & powershell -ExecutionPolicy Bypass -File .\tools\windows_godot_preflight.ps1 -GodotExe $GodotExe
    if ($LASTEXITCODE -ne 0) { throw 'Godot parser/import preflight failed' }
}
Write-Host 'Reminder: native Godot portrait acting still requires visual playtest.'
Write-Host 'Remaining 7 states per actor; strict art approval gate is intentionally open.'
