$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "ไม่พบ .venv กรุณารัน: python -m venv .venv"
}

if (-not $env:DOWNLOAD_KEY) {
    throw "กรุณาตั้งค่า DOWNLOAD_KEY ใน PowerShell ก่อนรัน"
}

if (-not $env:DISCORD_WEBHOOK_URL) {
    throw "กรุณาตั้งค่า DISCORD_WEBHOOK_URL ใน PowerShell ก่อนรัน"
}

& $python -m pip install -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "ติดตั้ง Backend dependency ไม่สำเร็จ"
}

& $python backend\server.py
