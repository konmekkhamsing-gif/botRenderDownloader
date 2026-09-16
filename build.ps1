$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Missing .venv. Run: python -m venv .venv"
}

& $python -m pip install -r requirements.txt pyinstaller
if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed"
}

Remove-Item -LiteralPath (Join-Path $root "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $root "dist") -Recurse -Force -ErrorAction SilentlyContinue

$args = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "MapleXDDownloader",
    "--icon", "MapleXD.ico",
    "--add-data", "MapleXD.jpg;.",
    "app.py"
)

if (Test-Path (Join-Path $root "ffmpeg\ffmpeg.exe")) {
    $args += @("--add-binary", "ffmpeg\ffmpeg.exe;ffmpeg")
} else {
    Write-Warning "ffmpeg\ffmpeg.exe was not found; FFmpeg will not be bundled"
}

& $python -m PyInstaller @args
if ($LASTEXITCODE -ne 0) {
    throw "Executable build failed"
}

Write-Host ""
Write-Host "Build complete: dist\MapleXDDownloader.exe"
Write-Host "Run it directly or compile installer.iss with Inno Setup"
