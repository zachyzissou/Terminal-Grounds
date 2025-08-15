@echo off
color 0A
title Terminal Grounds - One-Click Asset Generator

echo ===========================================================
echo    TERMINAL GROUNDS - AUTOMATED ASSET PIPELINE
echo    RTX 3090 Ti Edition - Maximum Quality
echo ===========================================================
echo.

:: Check if ComfyUI is installed
if not exist "C:\ComfyUI\ComfyUI\main.py" (
    echo [ERROR] ComfyUI not found!
    echo.
    echo Please run Setup-ComfyUI-Advanced.ps1 first
    echo.
    pause
    exit /b 1
)

echo [1/3] Starting ComfyUI Server...
echo ----------------------------------------
start "ComfyUI Server" /MIN cmd /c "cd /d C:\ComfyUI\ComfyUI && python main.py --highvram --output-directory C:\Users\Zachg\Terminal-Grounds-Generations"

:: Wait for ComfyUI to start
echo Waiting for ComfyUI to initialize...
timeout /t 10 /nobreak > nul

:: Check if ComfyUI is running
curl -s http://127.0.0.1:8188/system_stats > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] ComfyUI failed to start
    pause
    exit /b 1
)

echo.
echo [2/3] ComfyUI Started Successfully!
echo ----------------------------------------
echo Server running at: http://127.0.0.1:8188
echo.

:: Open browser
echo [3/3] Opening ComfyUI in browser...
start http://127.0.0.1:8188

echo.
echo ===========================================================
echo    READY TO GENERATE!
echo ===========================================================
echo.
echo OPTIONS:
echo   [1] Run batch generation (all assets)
echo   [2] Open ComfyUI for manual generation
echo   [3] Exit
echo.
choice /c 123 /n /m "Select option: "

if %errorlevel%==1 goto batch_generate
if %errorlevel%==2 goto manual_mode
if %errorlevel%==3 goto exit_script

:batch_generate
echo.
echo Starting batch generation...
echo This will generate:
echo   - 7 Faction Logos (5 variants each = 35 images)
echo   - 16 UI Icons (3 variants each = 48 images)  
echo   - 18 Weapon Concepts
echo   Total: ~100 images
echo.
echo Estimated time with RTX 3090 Ti: 5-10 minutes
echo.
pause

cd /d C:\Users\Zachg\Terminal-Grounds\Tools
python batch_generate_assets.py

echo.
echo Generation complete! Check:
echo C:\Users\Zachg\Terminal-Grounds-Generations\
echo.
pause
goto end

:manual_mode
echo.
echo ComfyUI is now open in your browser.
echo.
echo Quick tips:
echo   - Load workflow: TerminalGrounds_Advanced.json
echo   - Drag and drop images for img2img refinement
echo   - Use batch size 8 for UI icons
echo   - Stack multiple LoRAs for unique styles
echo.
echo Output directory: C:\Users\Zachg\Terminal-Grounds-Generations\
echo.
pause
goto end

:exit_script
echo Shutting down ComfyUI...
taskkill /F /FI "WindowTitle eq ComfyUI Server*" > nul 2>&1
echo Done!
goto end

:end
exit /b 0
