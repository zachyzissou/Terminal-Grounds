param(
    [switch]$NoComfyUI,
    [switch]$NoTerritorial,
    [switch]$NoBridge,
    [switch]$TestMode,
    [int]$Timeout = 120
)

Write-Host "=== TERMINAL GROUNDS PROCEDURAL SERVICES LAUNCHER ===" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$processes = @()

try {
    # Change to Terminal Grounds root directory
    $rootDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Set-Location $rootDir
    Write-Host "Working directory: $rootDir" -ForegroundColor Yellow
    Write-Host ""

    # 1. Start ComfyUI (if not disabled)
    if (-not $NoComfyUI) {
        Write-Host "Starting ComfyUI..." -ForegroundColor Green
        
        $comfyuiPath = "Tools\Comfy\ComfyUI-API"
        if (Test-Path $comfyuiPath) {
            $comfyuiProcess = Start-Process -FilePath "python" -ArgumentList @("main.py", "--listen", "127.0.0.1", "--port", "8188") -WorkingDirectory $comfyuiPath -PassThru -WindowStyle Minimized
            $processes += $comfyuiProcess
            Write-Host "  ComfyUI process started (PID: $($comfyuiProcess.Id))" -ForegroundColor Green
            
            # Wait for ComfyUI to be ready
            Write-Host "  Waiting for ComfyUI to initialize..." -ForegroundColor Gray
            $waitStart = Get-Date
            do {
                Start-Sleep -Seconds 2
                try {
                    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8188/system_stats" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        Write-Host "  ComfyUI is ready!" -ForegroundColor Green
                        break
                    }
                } catch {
                    # Continue waiting
                }
                
                if ((Get-Date) - $waitStart -gt [TimeSpan]::FromSeconds($Timeout)) {
                    throw "ComfyUI failed to start within $Timeout seconds"
                }
            } while ($true)
        } else {
            Write-Warning "ComfyUI path not found: $comfyuiPath"
        }
    } else {
        Write-Host "ComfyUI startup skipped" -ForegroundColor Yellow
    }

    # 2. Start Territorial WebSocket Server (if not disabled)
    if (-not $NoTerritorial) {
        Write-Host ""
        Write-Host "Starting Territorial WebSocket Server..." -ForegroundColor Green
        
        $territorialScript = "Tools\TerritorialSystem\territorial_websocket_server.py"
        if (Test-Path $territorialScript) {
            $territorialProcess = Start-Process -FilePath "python" -ArgumentList @($territorialScript) -PassThru -WindowStyle Minimized
            $processes += $territorialProcess
            Write-Host "  Territorial server process started (PID: $($territorialProcess.Id))" -ForegroundColor Green
            
            # Wait a moment for server to initialize
            Start-Sleep -Seconds 3
            Write-Host "  Territorial WebSocket server should be running on port 8765" -ForegroundColor Green
        } else {
            Write-Warning "Territorial server script not found: $territorialScript"
        }
    } else {
        Write-Host "Territorial server startup skipped" -ForegroundColor Yellow
    }

    # 3. Start Procedural Generation Bridge (if not disabled)
    if (-not $NoBridge) {
        Write-Host ""
        Write-Host "Starting Procedural Generation Bridge..." -ForegroundColor Green
        
        $bridgeScript = "Tools\ProceduralBridge\procedural_generation_bridge.py"
        if (Test-Path $bridgeScript) {
            $bridgeProcess = Start-Process -FilePath "python" -ArgumentList @($bridgeScript) -PassThru -WindowStyle Minimized
            $processes += $bridgeProcess
            Write-Host "  Bridge process started (PID: $($bridgeProcess.Id))" -ForegroundColor Green
            
            # Wait for bridge to initialize
            Start-Sleep -Seconds 5
            Write-Host "  Procedural bridge should be running on port 8766" -ForegroundColor Green
        } else {
            Write-Warning "Bridge script not found: $bridgeScript"
        }
    } else {
        Write-Host "Procedural bridge startup skipped" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "=== ALL SERVICES STARTED ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service Status:" -ForegroundColor White
    Write-Host "  ComfyUI:           http://127.0.0.1:8188" -ForegroundColor $(if ($NoComfyUI) { "Yellow" } else { "Green" })
    Write-Host "  Territorial:       ws://127.0.0.1:8765" -ForegroundColor $(if ($NoTerritorial) { "Yellow" } else { "Green" })
    Write-Host "  Procedural Bridge: ws://127.0.0.1:8766" -ForegroundColor $(if ($NoBridge) { "Yellow" } else { "Green" })
    Write-Host ""

    # Test mode - validate all services
    if ($TestMode) {
        Write-Host "Running service validation tests..." -ForegroundColor Cyan
        Write-Host ""
        
        $allGood = $true
        
        # Test ComfyUI
        if (-not $NoComfyUI) {
            try {
                $response = Invoke-WebRequest -Uri "http://127.0.0.1:8188/system_stats" -UseBasicParsing -TimeoutSec 10
                Write-Host "  ComfyUI: OK (Status: $($response.StatusCode))" -ForegroundColor Green
            } catch {
                Write-Host "  ComfyUI: FAILED ($($_.Exception.Message))" -ForegroundColor Red
                $allGood = $false
            }
        }
        
        # Test Territorial (basic port check)
        if (-not $NoTerritorial) {
            try {
                $tcpClient = New-Object System.Net.Sockets.TcpClient
                $tcpClient.ConnectAsync("127.0.0.1", 8765).Wait(5000)
                if ($tcpClient.Connected) {
                    Write-Host "  Territorial: OK (Port 8765 responding)" -ForegroundColor Green
                    $tcpClient.Close()
                } else {
                    Write-Host "  Territorial: FAILED (Connection timeout)" -ForegroundColor Red
                    $allGood = $false
                }
            } catch {
                Write-Host "  Territorial: FAILED ($($_.Exception.Message))" -ForegroundColor Red
                $allGood = $false
            }
        }
        
        # Test Procedural Bridge (basic port check)
        if (-not $NoBridge) {
            try {
                $tcpClient = New-Object System.Net.Sockets.TcpClient
                $tcpClient.ConnectAsync("127.0.0.1", 8766).Wait(5000)
                if ($tcpClient.Connected) {
                    Write-Host "  Procedural Bridge: OK (Port 8766 responding)" -ForegroundColor Green
                    $tcpClient.Close()
                } else {
                    Write-Host "  Procedural Bridge: FAILED (Connection timeout)" -ForegroundColor Red
                    $allGood = $false
                }
            } catch {
                Write-Host "  Procedural Bridge: FAILED ($($_.Exception.Message))" -ForegroundColor Red
                $allGood = $false
            }
        }
        
        Write-Host ""
        if ($allGood) {
            Write-Host "ALL SERVICES VALIDATED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host "The procedural generation pipeline is ready for use." -ForegroundColor Green
        } else {
            Write-Host "SOME SERVICES FAILED VALIDATION" -ForegroundColor Red
            Write-Host "Check the error messages above and verify service configurations." -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "Usage Instructions:" -ForegroundColor White
    Write-Host "1. Open UE5 Editor with Terminal Grounds project" -ForegroundColor Gray
    Write-Host "2. In Blueprint/C++, use UTGProceduralWorldSubsystem for generation requests" -ForegroundColor Gray
    Write-Host "3. Assets will be generated via ComfyUI and cached automatically" -ForegroundColor Gray
    Write-Host "4. Territorial changes will trigger automatic regeneration" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
    Write-Host ""

    # Keep script running and monitor processes
    if (-not $TestMode) {
        while ($true) {
            Start-Sleep -Seconds 10
            
            # Check if any processes have died
            $deadProcesses = @()
            foreach ($process in $processes) {
                if ($process.HasExited) {
                    $deadProcesses += $process
                    Write-Warning "Process $($process.Id) has exited with code $($process.ExitCode)"
                }
            }
            
            # Remove dead processes from monitoring
            foreach ($deadProcess in $deadProcesses) {
                $processes = $processes | Where-Object { $_.Id -ne $deadProcess.Id }
            }
            
            # If all processes are dead, exit
            if ($processes.Count -eq 0) {
                Write-Host "All processes have exited. Stopping launcher." -ForegroundColor Red
                break
            }
        }
    }

} catch {
    Write-Error "Error starting services: $($_.Exception.Message)"
    Write-Host "Attempting to clean up processes..." -ForegroundColor Yellow
    
    # Clean up any started processes
    foreach ($process in $processes) {
        try {
            if (-not $process.HasExited) {
                $process.Kill()
                Write-Host "Killed process $($process.Id)" -ForegroundColor Yellow
            }
        } catch {
            Write-Warning "Could not kill process $($process.Id): $($_.Exception.Message)"
        }
    }
    
    exit 1
} finally {
    # Cleanup on normal exit (Ctrl+C)
    if (-not $TestMode) {
        Write-Host ""
        Write-Host "Shutting down all services..." -ForegroundColor Yellow
        
        foreach ($process in $processes) {
            try {
                if (-not $process.HasExited) {
                    $process.Kill()
                    Write-Host "Stopped process $($process.Id)" -ForegroundColor Green
                }
            } catch {
                Write-Warning "Could not stop process $($process.Id): $($_.Exception.Message)"
            }
        }
        
        Write-Host "All services stopped." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Procedural services launcher finished." -ForegroundColor Cyan