@echo off
echo =========================================================
echo Starting ComfyUI for Chief Art Director Implementation
echo =========================================================
echo.
cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
echo Starting server on http://127.0.0.1:8188
echo Please wait ~90 seconds for full startup...
echo.
python main.py --listen 127.0.0.1 --port 8188
pause