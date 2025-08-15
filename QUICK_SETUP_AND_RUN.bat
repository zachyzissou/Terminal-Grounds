@echo off
color 0A
title Terminal Grounds - Quick ComfyUI Setup & Asset Generation

echo ===========================================================
echo    TERMINAL GROUNDS - EMERGENCY SETUP
echo    Let's get you generating assets RIGHT NOW!
echo ===========================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [STEP 1/4] Installing ComfyUI...
echo ----------------------------------------

:: Create directories
if not exist "C:\ComfyUI" mkdir "C:\ComfyUI"
cd /d C:\ComfyUI

:: Clone ComfyUI if not exists
if not exist "ComfyUI\.git" (
    echo Downloading ComfyUI...
    git clone https://github.com/comfyanonymous/ComfyUI.git
    if %errorlevel% neq 0 (
        echo [ERROR] Git not installed! Installing via winget...
        winget install --id Git.Git -e --silent
        echo Please restart this script after Git installs
        pause
        exit /b 1
    )
)

cd ComfyUI

echo.
echo [STEP 2/4] Installing dependencies...
echo ----------------------------------------
python -m pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

echo.
echo [STEP 3/4] Installing ComfyUI Manager...
echo ----------------------------------------
if not exist "custom_nodes\ComfyUI-Manager" (
    cd custom_nodes
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    cd ..
)

echo.
echo [STEP 4/4] Setting up for quick generation...
echo ----------------------------------------
if not exist "models\checkpoints" mkdir "models\checkpoints"

echo.
echo ===========================================================
echo    SETUP COMPLETE! Starting ComfyUI...
echo ===========================================================
echo.

echo Launching ComfyUI with your RTX 3090 Ti optimizations...
start "ComfyUI Server" cmd /c "python main.py --listen --port 8188 --highvram"

timeout /t 10 /nobreak > nul

echo.
echo ===========================================================
echo    🎉 SUCCESS! ComfyUI is now running!
echo ===========================================================
echo.
echo Next steps:
echo 1. Opening your browser to: http://127.0.0.1:8188
echo 2. Use ComfyUI Manager to install models (Manager button)
echo 3. Install "SDXL Base 1.0" or "FLUX" from the Manager
echo 4. Start generating your Terminal Grounds assets!
echo.
echo Your generated images will be in:
echo C:\ComfyUI\ComfyUI\output\
echo.

start http://127.0.0.1:8188

echo ComfyUI is running in the background.
echo Keep this window open while generating.
pause