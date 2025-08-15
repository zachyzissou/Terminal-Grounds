@echo off
title Installing ComfyUI Custom Nodes for Terminal Grounds
color 0A

echo ============================================================
echo    INSTALLING COMFYUI CUSTOM NODES FOR TERMINAL GROUNDS
echo ============================================================
echo.

set COMFYUI_PATH=C:\Users\Zachg\Documents\ComfyUI
set CUSTOM_NODES=%COMFYUI_PATH%\custom_nodes

echo ComfyUI Path: %COMFYUI_PATH%
echo Custom Nodes Path: %CUSTOM_NODES%
echo.

if not exist "%CUSTOM_NODES%" (
    echo ERROR: ComfyUI custom_nodes folder not found!
    echo Please check your ComfyUI installation path.
    pause
    exit /b 1
)

cd /d "%CUSTOM_NODES%"

echo ============================================================
echo 1. Installing ComfyUI-Manager (Essential for node management)
echo ============================================================
if exist "ComfyUI-Manager" (
    echo ComfyUI-Manager already installed, updating...
    cd ComfyUI-Manager
    git pull
    cd ..
) else (
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
)
echo.

echo ============================================================
echo 2. Installing rgthree-comfy (Better workflow organization)
echo ============================================================
if exist "rgthree-comfy" (
    echo rgthree-comfy already installed, updating...
    cd rgthree-comfy
    git pull
    cd ..
) else (
    git clone https://github.com/rgthree/rgthree-comfy.git
)
echo.

echo ============================================================
echo 3. Installing ComfyUI-KJNodes (Math ops, batch processing)
echo ============================================================
if exist "ComfyUI-KJNodes" (
    echo ComfyUI-KJNodes already installed, updating...
    cd ComfyUI-KJNodes
    git pull
    cd ..
) else (
    git clone https://github.com/kijai/ComfyUI-KJNodes.git
)
echo.

echo ============================================================
echo 4. Installing ComfyUI-Impact-Pack (Detailers, face fixing)
echo ============================================================
if exist "ComfyUI-Impact-Pack" (
    echo ComfyUI-Impact-Pack already installed, updating...
    cd ComfyUI-Impact-Pack
    git pull
    cd ..
) else (
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
)
echo.

echo ============================================================
echo 5. Installing efficiency-nodes-comfyui (Efficient workflows)
echo ============================================================
if exist "efficiency-nodes-comfyui" (
    echo efficiency-nodes-comfyui already installed, updating...
    cd efficiency-nodes-comfyui
    git pull
    cd ..
) else (
    git clone https://github.com/jags111/efficiency-nodes-comfyui.git
)
echo.

echo ============================================================
echo 6. Installing ComfyUI-Inspire-Pack (Advanced prompting)
echo ============================================================
if exist "ComfyUI-Inspire-Pack" (
    echo ComfyUI-Inspire-Pack already installed, updating...
    cd ComfyUI-Inspire-Pack
    git pull
    cd ..
) else (
    git clone https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git
)
echo.

echo ============================================================
echo           INSTALLATION COMPLETE!
echo ============================================================
echo.
echo Installed nodes for Terminal Grounds:
echo   ✓ ComfyUI-Manager - Node management
echo   ✓ rgthree-comfy - Better workflows  
echo   ✓ ComfyUI-KJNodes - Math and batch processing
echo   ✓ ComfyUI-Impact-Pack - Image enhancement
echo   ✓ efficiency-nodes-comfyui - Efficient workflows
echo   ✓ ComfyUI-Inspire-Pack - Advanced prompting
echo.
echo IMPORTANT: Restart ComfyUI to load the new nodes!
echo.
echo Benefits for Terminal Grounds:
echo   • Better faction workflow management
echo   • Batch generation with variations
echo   • Enhanced emblem/logo quality
echo   • Automated asset organization
echo   • Advanced style control
echo.

pause