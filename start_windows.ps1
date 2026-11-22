# Dungeon Bodega v1.2.4.4 — Windows developer launcher.
# Run in PowerShell: powershell -ExecutionPolicy Bypass -File .\start_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    & py -3.11 --version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Python 3.11 is required. Install Python 3.11, then run this script again.'
    }
    & py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python 3.11 virtual environment' }
}
$version = & $python -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)'
if ($version -ne '311') {
    throw "Existing .venv uses Python $version, expected 3.11. Remove it with Remove-Item -Recurse -Force .venv and rerun."
}
if (Test-Path '.env') {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
}
& $python -c 'import fastapi, httpx, uvicorn'
if ($LASTEXITCODE -ne 0) {
    & $python -m pip install -r requirements-game.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
}
# Local Whisper microphone recognition is installed separately from the small
# game dependency set. Install once if enabled; no cloud API key is required.
if (-not $env:STT_PREWARM) { $env:STT_PREWARM = '1' }
if ($env:STT_PREWARM -in @('1', 'true', 'yes')) {
    # pip exits quickly when requirements are already installed. Using pip here
    # avoids an error-prone PowerShell-to-Python quoted -c import check.
    Write-Host 'Checking local Whisper microphone dependencies...' -ForegroundColor Cyan
    & $python -m pip install --disable-pip-version-check -q -r requirements-stt-windows.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'Local Whisper STT was not installed. Typed play still works; run pip install -r requirements-stt-windows.txt when ready.'
    }
}
Write-Host 'Open mic is OFF on launch. Enable it explicitly in the game.'
Write-Host 'Dungeon Bodega v1.2.4.4: http://127.0.0.1:8010/docs'
Write-Host "Exodia: $env:EXODIA_URL ($env:EXODIA_PROVIDER); Hermes: $env:HERMES_URL"
& $python -m uvicorn backend.app:app --host 127.0.0.1 --port 8010 --workers 1
