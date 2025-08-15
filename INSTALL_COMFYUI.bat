@echo off
echo ================================================
echo   COMFYUI AUTOMATED INSTALLER
echo   Terminal Grounds Asset Generation Setup
echo ================================================
echo.

set INSTALL_DIR=C:\Users\Zachg\Terminal-Grounds\ComfyUI
set OUTPUT_DIR=C:\Users\Zachg\Terminal-Grounds\Generations

echo Creating directories...
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%OUTPUT_DIR%" 2>nul

echo.
echo This script will help you install ComfyUI.
echo.
echo Please follow these steps:
echo.
echo 1. DOWNLOAD ComfyUI Portable (includes Python and everything):
echo    https://github.com/comfyanonymous/ComfyUI/releases
echo    
echo    Download: "ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z"
echo    Size: ~1.5 GB
echo.
echo 2. EXTRACT the .7z file to:
echo    %INSTALL_DIR%
echo.
echo 3. DOWNLOAD a model (SDXL recommended for your 3090 Ti):
echo    https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
echo    Size: ~6.9 GB
echo    
echo    Save to: %INSTALL_DIR%\ComfyUI\models\checkpoints\
echo.
echo 4. After extraction, run:
echo    %INSTALL_DIR%\run_nvidia_gpu.bat
echo.
pause

echo.
echo Opening download pages in your browser...
start https://github.com/comfyanonymous/ComfyUI/releases
timeout /t 3 >nul
start https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main

echo.
echo Once downloaded and extracted, ComfyUI will be ready!
echo.
pause
