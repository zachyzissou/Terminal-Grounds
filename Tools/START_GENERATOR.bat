@echo off
title Terminal Grounds - Asset Generator
color 0A
cls

echo ============================================================
echo      TERMINAL GROUNDS - PRODUCTION ASSET GENERATOR
echo ============================================================
echo.
echo Your Setup:
echo   ComfyUI: http://127.0.0.1:8000 (Running)
echo   Model: FLUX1-dev-fp8
echo   GPU: RTX 3090 Ti (24GB VRAM)
echo.
echo This will generate game-ready assets using the API.
echo No desktop automation needed!
echo.
echo ============================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0Generate-Assets.ps1"

pause
