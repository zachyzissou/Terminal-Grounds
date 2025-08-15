@echo off
title Terminal Grounds - Asset Generation (API Mode)
color 0A

echo ============================================================
echo      TERMINAL GROUNDS - ASSET GENERATION (API MODE)
echo ============================================================
echo.
echo This replaces the clunky desktop automation approach!
echo.
echo Steps:
echo   1. Start ComfyUI in API mode (no GUI control needed)
echo   2. Test the API connection
echo   3. Generate assets programmatically
echo.
echo ============================================================
echo.

:menu
echo What would you like to do?
echo.
echo   1. Create ComfyUI API launcher
echo   2. Test API connection
echo   3. Generate Faction Emblems
echo   4. Generate ALL assets
echo   5. Open ComfyUI web interface
echo   6. Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" goto create_launcher
if "%choice%"=="2" goto test_api
if "%choice%"=="3" goto gen_emblems
if "%choice%"=="4" goto gen_all
if "%choice%"=="5" goto open_web
if "%choice%"=="6" exit

goto menu

:create_launcher
echo.
echo Creating API launcher...
powershell -ExecutionPolicy Bypass -File "%~dp0Setup-ComfyUI-API.ps1"
echo.
echo Launcher created! Now start ComfyUI:
echo   Run: C:\ComfyUI\run_comfyui_api.bat
echo.
pause
goto menu

:test_api
echo.
echo Testing ComfyUI API connection...
echo.
python "%~dp0test_comfyui_api.py"
echo.
pause
goto menu

:gen_emblems
echo.
echo Generating faction emblems via API...
echo.
python "%~dp0ArtGen\comfyui_api_client.py" --type emblems
echo.
pause
goto menu

:gen_all
echo.
echo Generating ALL assets via API...
echo.
python "%~dp0ArtGen\comfyui_api_client.py" --all
echo.
pause
goto menu

:open_web
echo.
echo Opening ComfyUI web interface...
start http://127.0.0.1:8188
goto menu
