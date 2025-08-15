@echo off
title Terminal Grounds - Advanced Asset Generator
color 0A
cls

echo ============================================================
echo     TERMINAL GROUNDS - ADVANCED ASSET GENERATOR v2.0
echo ============================================================
echo.
echo This system provides:
echo   - Optimized workflows for faction assets
echo   - Real-time output monitoring
echo   - Review dashboard for asset approval
echo   - Automatic organization of generated files
echo.
echo ============================================================
echo.

:: Check if ComfyUI is running (probe 8000 then 8188)
echo Checking ComfyUI status...
powershell -Command "function Test-Port($u){ try { Invoke-WebRequest -Uri $u -UseBasicParsing | Out-Null; return $true } catch { return $false } }; if (Test-Port 'http://127.0.0.1:8000/system_stats' -or Test-Port 'http://127.0.0.1:8188/system_stats') { Write-Host '  [OK] ComfyUI is running' -ForegroundColor Green } else { Write-Host '  [ERROR] ComfyUI is not running!' -ForegroundColor Red; Write-Host '  Please start ComfyUI first' -ForegroundColor Yellow }"

echo.
echo ============================================================
echo.

:: Run the main generator
python "%~dp0ArtGen\terminal_grounds_generator.py"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Python script failed to run
    echo Make sure Python is installed with required packages
    echo ============================================================
    echo.
)

pause
