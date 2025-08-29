@echo off
REM Start Procedural Generation Services for Terminal Grounds
REM This launches all components needed for AI-driven procedural generation

echo ============================================
echo Terminal Grounds Procedural Generation Stack
echo ============================================
echo.

REM Check if ComfyUI is running
echo [1/4] Checking ComfyUI status...
curl -s http://127.0.0.1:8188/system_stats >nul 2>&1
if %errorlevel% neq 0 (
    echo ComfyUI not running - starting...
    start "ComfyUI" cmd /k "cd /d C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API && python main.py --listen 127.0.0.1 --port 8188"
    echo Waiting for ComfyUI to initialize (90 seconds)...
    timeout /t 90 /nobreak >nul
) else (
    echo ComfyUI already running on port 8188
)

REM Start Territorial WebSocket Server
echo [2/4] Starting Territorial WebSocket Server...
start "Territorial Server" cmd /k "cd /d C:\Users\Zachg\Terminal-Grounds && python Tools\TerritorialSystem\territorial_websocket_server.py"
echo Territorial server starting on port 8765...
timeout /t 3 /nobreak >nul

REM Start Procedural Generation Bridge
echo [3/4] Starting Procedural Generation Bridge...
start "Generation Bridge" cmd /k "cd /d C:\Users\Zachg\Terminal-Grounds && python Tools\ProceduralBridge\procedural_generation_bridge.py"
echo Generation bridge starting on port 8766...
timeout /t 3 /nobreak >nul

REM Start Asset Import Monitor
echo [4/4] Starting Asset Import Monitor...
start "Import Monitor" cmd /k "cd /d C:\Users\Zachg\Terminal-Grounds && python Tools\ProceduralBridge\asset_import_monitor.py"
echo Import monitor watching ComfyUI output directory...
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo All procedural services started successfully!
echo ============================================
echo.
echo Services running:
echo - ComfyUI:              http://127.0.0.1:8188
echo - Territorial Server:   ws://127.0.0.1:8765
echo - Generation Bridge:    ws://127.0.0.1:8766
echo - Asset Import Monitor: Watching output directory
echo.
echo Press any key to open service dashboard...
pause >nul

REM Open monitoring dashboard (future implementation)
echo Dashboard not yet implemented. Use individual service windows to monitor.
pause