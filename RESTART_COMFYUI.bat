@echo off
echo Restarting ComfyUI to fix tqdm error...
echo.

:: Kill any existing ComfyUI processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im python3.exe >nul 2>&1

echo Waiting for processes to terminate...
timeout /t 3 >nul

echo Starting ComfyUI fresh...
cd /d "C:\Users\Zachg\Documents\ComfyUI"
start "ComfyUI" python main.py --listen 127.0.0.1 --port 8000

echo ComfyUI is restarting...
echo Wait 30 seconds then test generation again.
pause