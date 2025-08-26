@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ==========================================
echo  ComfyUI - Terminal Grounds (STABLE)
echo ==========================================
echo.
echo Status: Problematic nodes disabled
echo Encoding: UTF-8 
echo Port: 8188
echo.
echo Starting ComfyUI...
echo Wait for "Starting server" message
echo.

cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI stopped.
pause
