$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Missing .venv. Run: python -m venv .venv"
}

if (-not $env:DOWNLOAD_KEY) {
    throw "Set DOWNLOAD_KEY before running this script"
}

if (-not $env:DISCORD_WEBHOOK_URL) {
    throw "Set DISCORD_WEBHOOK_URL before running this script"
}

& $python -m pip install -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Backend dependency installation failed"
}

& $python backend\server.py
