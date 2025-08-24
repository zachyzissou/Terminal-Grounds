@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ==========================================
echo  ComfyUI - Terminal Grounds (MINIMAL)
echo ==========================================
echo.
echo Configuration: Essential nodes only
echo Purpose: Stable FLUX workflow generation
echo Port: 8188
echo.
echo Starting minimal ComfyUI...
echo This should start successfully!
echo.

cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI stopped.
pause
