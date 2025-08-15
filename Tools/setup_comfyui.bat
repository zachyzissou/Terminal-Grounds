@echo off
echo ========================================
echo Terminal Grounds - ComfyUI Setup Script
echo ========================================
echo.

:: Check if ComfyUI folder exists
if exist "C:\ComfyUI" (
    echo ComfyUI folder already exists!
    echo Starting ComfyUI...
    cd /d C:\ComfyUI
    if exist "run_nvidia_gpu.bat" (
        call run_nvidia_gpu.bat
    ) else if exist "run_cpu.bat" (
        call run_cpu.bat
    )
    exit /b
)

echo This script will download and set up ComfyUI for local image generation.
echo.
echo Requirements:
echo - ~10GB disk space
echo - NVIDIA GPU with 4GB+ VRAM (recommended) or CPU mode
echo - Windows 10/11
echo.
pause

:: Create ComfyUI directory
echo Creating ComfyUI directory...
mkdir C:\ComfyUI 2>nul
cd /d C:\ComfyUI

:: Download ComfyUI Portable
echo.
echo Downloading ComfyUI Portable...
echo Please download from: https://github.com/comfyanonymous/ComfyUI/releases
echo.
echo Download the file: ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z
echo Extract it to C:\ComfyUI\
echo.
pause

:: Once extracted, create custom workflow for Terminal Grounds
echo.
echo After extraction, run:
echo - For NVIDIA GPU: run_nvidia_gpu.bat
echo - For CPU only: run_cpu.bat
echo.
echo ComfyUI will open in your browser at http://127.0.0.1:8188
echo.
pause
