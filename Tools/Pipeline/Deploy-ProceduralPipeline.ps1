#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Terminal Grounds Procedural Pipeline Deployment Script
    Enterprise-grade DevOps deployment with comprehensive monitoring

.DESCRIPTION
    Deploys and configures the complete procedural generation pipeline:
    - ComfyUI service management
    - Territorial WebSocket server
    - Pipeline orchestrator
    - Monitoring dashboard
    - UE5 integration

.PARAMETER Action
    Deployment action: deploy, start, stop, status, monitor, restart

.PARAMETER Environment  
    Target environment: development, staging, production

.PARAMETER Force
    Force deployment even if services are running

.EXAMPLE
    .\Deploy-ProceduralPipeline.ps1 -Action deploy -Environment development

.EXAMPLE
    .\Deploy-ProceduralPipeline.ps1 -Action monitor
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "start", "stop", "status", "monitor", "restart", "health-check")]
    [string]$Action,
    
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [switch]$Force,
    
    [switch]$Verbose,
    
    [string]$LogLevel = "INFO"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Pipeline configuration
$PipelineConfig = @{
    ServiceName = "TGProceduralPipeline"
    ComfyUIPort = 8188
    WebSocketPort = 8765
    PipelinePort = 8766
    
    Directories = @{
        Root = "C:\Users\Zachg\Terminal-Grounds"
        Pipeline = "C:\Users\Zachg\Terminal-Grounds\Tools\Pipeline"
        ComfyUI = "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
        Database = "C:\Users\Zachg\Terminal-Grounds\Database"
        Logs = "C:\Users\Zachg\Terminal-Grounds\Logs\Pipeline"
        Output = "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output"
    }
    
    Services = @{
        ComfyUI = @{
            Name = "ComfyUI"
            Script = "main.py"
            Args = @("--listen", "127.0.0.1", "--port", "8188")
            HealthEndpoint = "http://127.0.0.1:8188/system_stats"
        }
        
        WebSocket = @{
            Name = "TerritorialWebSocket" 
            Script = "territorial_websocket_server.py"
            Args = @()
            HealthEndpoint = "ws://127.0.0.1:8765"
        }
        
        Orchestrator = @{
            Name = "ProceduralOrchestrator"
            Script = "procedural_generation_orchestrator.py" 
            Args = @()
            HealthEndpoint = "http://127.0.0.1:8766/health"
        }
    }
    
    Dependencies = @(
        "python",
        "pip", 
        "websockets",
        "asyncio",
        "sqlite3"
    )
}

# Logging functions
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO",
        [string]$Component = "DEPLOY"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] [$Component] $Message"
    
    # Color coding for console output
    $color = switch ($Level) {
        "INFO" { "Green" }
        "WARN" { "Yellow" } 
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
    }
    
    Write-Host $logMessage -ForegroundColor $color
    
    # Also log to file if logs directory exists
    $logFile = Join-Path $PipelineConfig.Directories.Logs "deployment.log"
    if (Test-Path (Split-Path $logFile -Parent)) {
        Add-Content -Path $logFile -Value $logMessage
    }
}

function Test-Dependencies {
    Write-Log "Checking pipeline dependencies..." -Component "DEPS"
    
    $missingDeps = @()
    
    foreach ($dep in $PipelineConfig.Dependencies) {
        try {
            $result = & $dep --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "✓ $dep available" -Level "DEBUG" -Component "DEPS"
            } else {
                $missingDeps += $dep
            }
        } catch {
            $missingDeps += $dep
        }
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Log "Missing dependencies: $($missingDeps -join ', ')" -Level "ERROR" -Component "DEPS"
        return $false
    }
    
    Write-Log "All dependencies satisfied" -Component "DEPS"
    return $true
}

function Initialize-Directories {
    Write-Log "Initializing pipeline directories..." -Component "INIT"
    
    foreach ($dirName in $PipelineConfig.Directories.Keys) {
        $dirPath = $PipelineConfig.Directories[$dirName]
        
        if (-not (Test-Path $dirPath)) {
            Write-Log "Creating directory: $dirPath" -Component "INIT"
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        } else {
            Write-Log "✓ Directory exists: $dirName" -Level "DEBUG" -Component "INIT"
        }
    }
    
    # Create service-specific log directories
    foreach ($service in $PipelineConfig.Services.Keys) {
        $serviceLogDir = Join-Path $PipelineConfig.Directories.Logs $service
        if (-not (Test-Path $serviceLogDir)) {
            New-Item -ItemType Directory -Path $serviceLogDir -Force | Out-Null
        }
    }
    
    Write-Log "Directory initialization complete" -Component "INIT"
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$HealthEndpoint,
        [int]$TimeoutSeconds = 10
    )
    
    Write-Log "Checking health: $ServiceName" -Level "DEBUG" -Component "HEALTH"
    
    try {
        if ($HealthEndpoint.StartsWith("http")) {
            # HTTP health check
            $response = Invoke-WebRequest -Uri $HealthEndpoint -UseBasicParsing -TimeoutSec $TimeoutSeconds
            return $response.StatusCode -eq 200
        } elseif ($HealthEndpoint.StartsWith("ws")) {
            # WebSocket health check (simplified - just check port)
            $uri = [System.Uri]$HealthEndpoint
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $connect = $tcpClient.ConnectAsync($uri.Host, $uri.Port)
            $result = $connect.Wait($TimeoutSeconds * 1000)
            $tcpClient.Close()
            return $result
        } else {
            Write-Log "Unknown endpoint type: $HealthEndpoint" -Level "WARN" -Component "HEALTH"
            return $false
        }
    } catch {
        Write-Log "Health check failed for $ServiceName`: $($_.Exception.Message)" -Level "DEBUG" -Component "HEALTH"
        return $false
    }
}

function Start-PipelineService {
    param(
        [string]$ServiceName,
        [hashtable]$ServiceConfig
    )
    
    Write-Log "Starting service: $ServiceName" -Component "SERVICE"
    
    # Determine script path
    $scriptPath = ""
    if ($ServiceName -eq "ComfyUI") {
        $scriptPath = Join-Path $PipelineConfig.Directories.ComfyUI $ServiceConfig.Script
    } elseif ($ServiceName -eq "TerritorialWebSocket") {
        $scriptPath = Join-Path $PipelineConfig.Directories.Root "Tools\TerritorialSystem\$($ServiceConfig.Script)"
    } else {
        $scriptPath = Join-Path $PipelineConfig.Directories.Pipeline $ServiceConfig.Script
    }
    
    if (-not (Test-Path $scriptPath)) {
        Write-Log "Service script not found: $scriptPath" -Level "ERROR" -Component "SERVICE"
        return $false
    }
    
    # Check if service is already running
    if (Test-ServiceHealth -ServiceName $ServiceName -HealthEndpoint $ServiceConfig.HealthEndpoint -TimeoutSeconds 2) {
        Write-Log "Service $ServiceName is already running" -Level "WARN" -Component "SERVICE"
        return $true
    }
    
    # Create log file path
    $logFile = Join-Path $PipelineConfig.Directories.Logs "$ServiceName\service.log"
    
    # Start service as background process
    try {
        $arguments = @($scriptPath) + $ServiceConfig.Args
        
        Write-Log "Starting: python $($arguments -join ' ')" -Level "DEBUG" -Component "SERVICE"
        
        $processInfo = @{
            FilePath = "python"
            ArgumentList = $arguments
            WindowStyle = "Hidden"
            RedirectStandardOutput = $logFile
            RedirectStandardError = $logFile
            UseNewEnvironment = $false
        }
        
        $process = Start-Process @processInfo -PassThru
        
        if ($process) {
            Write-Log "Service $ServiceName started (PID: $($process.Id))" -Component "SERVICE"
            
            # Wait for service to become healthy
            $maxWait = 30
            $waited = 0
            
            do {
                Start-Sleep -Seconds 2
                $waited += 2
                $healthy = Test-ServiceHealth -ServiceName $ServiceName -HealthEndpoint $ServiceConfig.HealthEndpoint
            } while (-not $healthy -and $waited -lt $maxWait)
            
            if ($healthy) {
                Write-Log "✓ Service $ServiceName is healthy" -Component "SERVICE"
                return $true
            } else {
                Write-Log "Service $ServiceName failed to become healthy within ${maxWait}s" -Level "WARN" -Component "SERVICE"
                return $false
            }
        }
    } catch {
        Write-Log "Failed to start service $ServiceName`: $($_.Exception.Message)" -Level "ERROR" -Component "SERVICE"
        return $false
    }
    
    return $false
}

function Stop-PipelineService {
    param(
        [string]$ServiceName
    )
    
    Write-Log "Stopping service: $ServiceName" -Component "SERVICE"
    
    # Find processes by script name
    $scriptName = $PipelineConfig.Services[$ServiceName].Script
    $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*$scriptName*"
    }
    
    if ($processes) {
        foreach ($process in $processes) {
            try {
                Write-Log "Terminating process PID: $($process.Id)" -Level "DEBUG" -Component "SERVICE"
                $process.Kill()
                $process.WaitForExit(5000)
                Write-Log "✓ Service $ServiceName stopped" -Component "SERVICE"
            } catch {
                Write-Log "Failed to stop process $($process.Id): $($_.Exception.Message)" -Level "WARN" -Component "SERVICE"
            }
        }
    } else {
        Write-Log "No running processes found for $ServiceName" -Level "DEBUG" -Component "SERVICE"
    }
}

function Get-PipelineStatus {
    Write-Log "Checking pipeline status..." -Component "STATUS"
    
    $status = @{
        Overall = $true
        Services = @{}
        Directories = @{}
        Dependencies = Test-Dependencies
    }
    
    # Check directories
    foreach ($dirName in $PipelineConfig.Directories.Keys) {
        $dirPath = $PipelineConfig.Directories[$dirName]
        $status.Directories[$dirName] = Test-Path $dirPath
        if (-not $status.Directories[$dirName]) {
            $status.Overall = $false
        }
    }
    
    # Check services
    foreach ($serviceName in $PipelineConfig.Services.Keys) {
        $serviceConfig = $PipelineConfig.Services[$serviceName]
        $isHealthy = Test-ServiceHealth -ServiceName $serviceName -HealthEndpoint $serviceConfig.HealthEndpoint
        $status.Services[$serviceName] = $isHealthy
        
        if (-not $isHealthy) {
            $status.Overall = $false
        }
    }
    
    return $status
}

function Show-PipelineStatus {
    $status = Get-PipelineStatus
    
    Write-Host ""
    Write-Host "=== TERMINAL GROUNDS PROCEDURAL PIPELINE STATUS ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Overall status
    $overallColor = if ($status.Overall) { "Green" } else { "Red" }
    $overallText = if ($status.Overall) { "HEALTHY" } else { "DEGRADED" }
    Write-Host "Overall Status: $overallText" -ForegroundColor $overallColor
    Write-Host ""
    
    # Services status
    Write-Host "Services:" -ForegroundColor Yellow
    foreach ($serviceName in $status.Services.Keys) {
        $serviceStatus = $status.Services[$serviceName]
        $statusColor = if ($serviceStatus) { "Green" } else { "Red" }
        $statusText = if ($serviceStatus) { "RUNNING" } else { "STOPPED" }
        Write-Host "  $serviceName`: $statusText" -ForegroundColor $statusColor
    }
    Write-Host ""
    
    # Dependencies
    $depsColor = if ($status.Dependencies) { "Green" } else { "Red" }
    $depsText = if ($status.Dependencies) { "OK" } else { "MISSING" }
    Write-Host "Dependencies: $depsText" -ForegroundColor $depsColor
    Write-Host ""
    
    # Directories
    Write-Host "Directories:" -ForegroundColor Yellow
    foreach ($dirName in $status.Directories.Keys) {
        $dirStatus = $status.Directories[$dirName]
        $statusColor = if ($dirStatus) { "Green" } else { "Red" }
        $statusText = if ($dirStatus) { "EXISTS" } else { "MISSING" }
        Write-Host "  $dirName`: $statusText" -ForegroundColor $statusColor
    }
    Write-Host ""
}

function Start-PipelineMonitor {
    Write-Log "Starting pipeline monitor..." -Component "MONITOR"
    
    $monitorScript = Join-Path $PipelineConfig.Directories.Pipeline "pipeline_monitor.py"
    
    if (-not (Test-Path $monitorScript)) {
        Write-Log "Monitor script not found: $monitorScript" -Level "ERROR" -Component "MONITOR"
        return
    }
    
    try {
        & python $monitorScript monitor --refresh 5
    } catch {
        Write-Log "Monitor failed: $($_.Exception.Message)" -Level "ERROR" -Component "MONITOR"
    }
}

function Deploy-Pipeline {
    Write-Log "=== DEPLOYING TERMINAL GROUNDS PROCEDURAL PIPELINE ===" -Component "DEPLOY"
    Write-Log "Environment: $Environment" -Component "DEPLOY"
    Write-Log "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Component "DEPLOY"
    Write-Host ""
    
    # Check if force deployment is needed
    if (-not $Force) {
        $currentStatus = Get-PipelineStatus
        if ($currentStatus.Overall) {
            Write-Log "Pipeline is already running. Use -Force to redeploy." -Level "WARN" -Component "DEPLOY"
            return
        }
    }
    
    # Step 1: Check dependencies
    Write-Log "Step 1: Checking dependencies" -Component "DEPLOY"
    if (-not (Test-Dependencies)) {
        Write-Log "Dependency check failed. Aborting deployment." -Level "ERROR" -Component "DEPLOY"
        return
    }
    
    # Step 2: Initialize directories
    Write-Log "Step 2: Initializing directories" -Component "DEPLOY"
    Initialize-Directories
    
    # Step 3: Stop existing services if force deployment
    if ($Force) {
        Write-Log "Step 3: Stopping existing services (force mode)" -Component "DEPLOY"
        foreach ($serviceName in $PipelineConfig.Services.Keys) {
            Stop-PipelineService -ServiceName $serviceName
        }
        Start-Sleep -Seconds 5
    }
    
    # Step 4: Start services in order
    Write-Log "Step 4: Starting pipeline services" -Component "DEPLOY"
    
    $startOrder = @("ComfyUI", "TerritorialWebSocket", "ProceduralOrchestrator")
    $failedServices = @()
    
    foreach ($serviceName in $startOrder) {
        if ($PipelineConfig.Services.ContainsKey($serviceName)) {
            $success = Start-PipelineService -ServiceName $serviceName -ServiceConfig $PipelineConfig.Services[$serviceName]
            if (-not $success) {
                $failedServices += $serviceName
            }
            Start-Sleep -Seconds 3  # Brief delay between service starts
        }
    }
    
    # Step 5: Verify deployment
    Write-Log "Step 5: Verifying deployment" -Component "DEPLOY"
    
    $finalStatus = Get-PipelineStatus
    
    if ($finalStatus.Overall) {
        Write-Log "=== DEPLOYMENT SUCCESSFUL ===" -Level "INFO" -Component "DEPLOY"
        Write-Log "All services are running and healthy" -Component "DEPLOY"
        
        Write-Host ""
        Write-Host "Access URLs:" -ForegroundColor Cyan
        Write-Host "  ComfyUI: http://127.0.0.1:8188" -ForegroundColor Green
        Write-Host "  WebSocket: ws://127.0.0.1:8765" -ForegroundColor Green
        Write-Host "  Pipeline Monitor: python Tools\Pipeline\pipeline_monitor.py monitor" -ForegroundColor Green
        Write-Host ""
        
    } else {
        Write-Log "=== DEPLOYMENT COMPLETED WITH WARNINGS ===" -Level "WARN" -Component "DEPLOY"
        if ($failedServices.Count -gt 0) {
            Write-Log "Failed services: $($failedServices -join ', ')" -Level "WARN" -Component "DEPLOY"
        }
        
        Write-Host ""
        Write-Host "Check service logs in: $($PipelineConfig.Directories.Logs)" -ForegroundColor Yellow
    }
    
    # Show final status
    Show-PipelineStatus
}

function Restart-Pipeline {
    Write-Log "Restarting pipeline..." -Component "RESTART"
    
    # Stop all services
    foreach ($serviceName in $PipelineConfig.Services.Keys) {
        Stop-PipelineService -ServiceName $serviceName
    }
    
    Write-Log "Waiting for services to stop..." -Component "RESTART"
    Start-Sleep -Seconds 10
    
    # Start all services
    Deploy-Pipeline
}

# Main execution logic
function Main {
    # Ensure log directory exists
    if (-not (Test-Path $PipelineConfig.Directories.Logs)) {
        New-Item -ItemType Directory -Path $PipelineConfig.Directories.Logs -Force | Out-Null
    }
    
    Write-Log "Terminal Grounds Procedural Pipeline Deployment" -Component "MAIN"
    Write-Log "Action: $Action, Environment: $Environment" -Component "MAIN"
    
    switch ($Action.ToLower()) {
        "deploy" {
            Deploy-Pipeline
        }
        
        "start" {
            Write-Log "Starting pipeline services..." -Component "START"
            foreach ($serviceName in $PipelineConfig.Services.Keys) {
                Start-PipelineService -ServiceName $serviceName -ServiceConfig $PipelineConfig.Services[$serviceName]
            }
            Show-PipelineStatus
        }
        
        "stop" {
            Write-Log "Stopping pipeline services..." -Component "STOP"
            foreach ($serviceName in $PipelineConfig.Services.Keys) {
                Stop-PipelineService -ServiceName $serviceName
            }
            Show-PipelineStatus
        }
        
        "restart" {
            Restart-Pipeline
        }
        
        "status" {
            Show-PipelineStatus
        }
        
        "monitor" {
            Start-PipelineMonitor
        }
        
        "health-check" {
            $status = Get-PipelineStatus
            if ($status.Overall) {
                Write-Log "Pipeline is healthy" -Level "INFO" -Component "HEALTH"
                exit 0
            } else {
                Write-Log "Pipeline is not healthy" -Level "ERROR" -Component "HEALTH"
                Show-PipelineStatus
                exit 1
            }
        }
        
        default {
            Write-Log "Unknown action: $Action" -Level "ERROR" -Component "MAIN"
            exit 1
        }
    }
}

# Execute main function
try {
    Main
} catch {
    Write-Log "Deployment failed: $($_.Exception.Message)" -Level "ERROR" -Component "MAIN"
    Write-Log $_.ScriptStackTrace -Level "DEBUG" -Component "MAIN"
    exit 1
}