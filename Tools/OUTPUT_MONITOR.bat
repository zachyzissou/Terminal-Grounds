@echo off
title Terminal Grounds - Output Monitor
color 0E
cls

echo ============================================================
echo       TERMINAL GROUNDS - OUTPUT MONITOR
echo ============================================================
echo.
echo This tool watches ComfyUI output and organizes assets
echo for review and approval.
echo.
echo Features:
echo   - Auto-detect new generated assets
echo   - Organize by type (Emblems, Posters, Icons)
echo   - Web dashboard for review
echo   - Auto-refresh every 5 seconds
echo.
echo ============================================================
echo.

python "%~dp0output_monitor.py"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Failed to run monitor
    echo Make sure Python is installed
    echo ============================================================
    echo.
)

pause
