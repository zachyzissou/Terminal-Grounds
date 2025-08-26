@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ==========================================
echo  ComfyUI - Terminal Grounds (ADVANCED)
echo ==========================================
echo.
echo Configuration: Essential + Advanced workflow nodes
echo Purpose: Full Terminal Grounds workflow compatibility
echo Port: 8188
echo.
echo Starting ComfyUI with advanced nodes...
echo This includes workflow-specific nodes for:
echo - Ultimate SD Upscale
echo - Impact Pack (ImageSharpen, etc.)
echo - ControlNet preprocessing
echo - Additional workflow utilities
echo.

cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI stopped.
pause
