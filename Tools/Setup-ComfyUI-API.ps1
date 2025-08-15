# Terminal Grounds - ComfyUI API Setup Script
# =============================================
# This script sets up ComfyUI with API mode for reliable asset generation
# No more clunky desktop automation!

param(
    [string]$InstallPath = "C:\ComfyUI",
    [switch]$SkipModelDownload = $false
)

$ErrorActionPreference = "Stop"
Write-Host "Terminal Grounds - ComfyUI API Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Create API launcher
$apiLauncher = @'
@echo off
echo Starting ComfyUI in API mode for Terminal Grounds...
echo.
echo Server: http://127.0.0.1:8188
echo API: http://127.0.0.1:8188/prompt
echo.
cd /d "C:\ComfyUI\ComfyUI"
..\python_embeded\python.exe -s main.py --listen 127.0.0.1 --port 8188 --enable-cors-header
pause
'@

$launcherPath = "$InstallPath\run_comfyui_api.bat"
New-Item -ItemType Directory -Force -Path $InstallPath -ErrorAction SilentlyContinue | Out-Null
Set-Content -Path $launcherPath -Value $apiLauncher -Encoding ASCII

Write-Host "`nCreated API launcher at:" -ForegroundColor Green
Write-Host "  $launcherPath" -ForegroundColor White
Write-Host "`nRun this to start ComfyUI in API mode (no GUI interaction needed!)" -ForegroundColor Yellow
