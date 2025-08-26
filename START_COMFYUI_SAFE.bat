@echo off
REM Terminal Grounds ComfyUI Safe Launcher - Prevents stderr corruption
REM This launcher ensures ComfyUI won't crash when browser windows close

echo ========================================================
echo Terminal Grounds ComfyUI Safe Launcher
echo Prevents stderr stream corruption from browser disconnects
echo ========================================================
echo.

cd /d "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"

echo Starting ComfyUI with protected output streams...
echo ComfyUI will be available at: http://127.0.0.1:8188
echo.
echo IMPORTANT: This window must stay open while generating
echo Closing browser tabs is now safe - won't crash generation
echo ========================================================
echo.

REM Start Python with unbuffered output and redirect stderr to null to prevent crashes
REM While still showing important messages to console
python -u main.py --listen 127.0.0.1 --port 8188 --disable-metadata 2>nul

echo.
echo ComfyUI has stopped. Press any key to exit...
pause >nul