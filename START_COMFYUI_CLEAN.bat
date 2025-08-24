@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo =====================================
echo  ComfyUI - Terminal Grounds (Repaired)
echo =====================================
echo.
echo Environment: UTF-8 encoding enabled
echo Port: 8188
echo.

cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"

echo Starting ComfyUI server...
echo Wait for "Starting server" message (~90 seconds)
echo.

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI has stopped. Press any key to close.
pause >nul
