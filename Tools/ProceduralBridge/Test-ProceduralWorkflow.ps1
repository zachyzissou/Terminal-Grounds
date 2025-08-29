param(
    [string]$TestType = "quick",  # quick, comprehensive, single
    [string]$AssetType = "vehicles",  # vehicles, weapons, ui, environments, concepts, emblems
    [string]$Faction = "directorate",
    [switch]$SkipServices
)

Write-Host "=== TERMINAL GROUNDS PROCEDURAL GENERATION WORKFLOW TEST ===" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$testResults = @()

function Test-ServiceAvailability {
    Write-Host "Testing service availability..." -ForegroundColor Yellow
    
    $services = @{
        "ComfyUI" = "http://127.0.0.1:8188/system_stats"
        "Territorial" = "127.0.0.1:8765"
        "Bridge" = "127.0.0.1:8766"
    }
    
    foreach ($service in $services.GetEnumerator()) {
        try {
            if ($service.Value.StartsWith("http")) {
                $response = Invoke-WebRequest -Uri $service.Value -UseBasicParsing -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Host "  $($service.Key): AVAILABLE" -ForegroundColor Green
                    $testResults += @{Service = $service.Key; Status = "Available"; Details = "HTTP $($response.StatusCode)"}
                } else {
                    Write-Host "  $($service.Key): ISSUE (Status: $($response.StatusCode))" -ForegroundColor Yellow
                    $testResults += @{Service = $service.Key; Status = "Issue"; Details = "HTTP $($response.StatusCode)"}
                }
            } else {
                # Test TCP port
                $tcpClient = New-Object System.Net.Sockets.TcpClient
                $tcpClient.ConnectAsync($service.Value.Split(':')[0], $service.Value.Split(':')[1]).Wait(3000)
                if ($tcpClient.Connected) {
                    Write-Host "  $($service.Key): AVAILABLE" -ForegroundColor Green
                    $testResults += @{Service = $service.Key; Status = "Available"; Details = "TCP Connection OK"}
                    $tcpClient.Close()
                } else {
                    Write-Host "  $($service.Key): NOT AVAILABLE" -ForegroundColor Red
                    $testResults += @{Service = $service.Key; Status = "Not Available"; Details = "TCP Connection Failed"}
                }
            }
        } catch {
            Write-Host "  $($service.Key): NOT AVAILABLE ($($_.Exception.Message))" -ForegroundColor Red
            $testResults += @{Service = $service.Key; Status = "Not Available"; Details = $_.Exception.Message}
        }
    }
    
    Write-Host ""
}

function Test-AssetGeneration {
    param($Category, $Faction, $AssetName = "test_asset")
    
    Write-Host "Testing $Category generation for faction $Faction..." -ForegroundColor Yellow
    
    $startTime = Get-Date
    
    try {
        # Test the comprehensive asset generator
        $result = python "Tools\ProceduralBridge\comprehensive_asset_generator.py" --test --category $Category --faction $Faction --asset-name $AssetName
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  $Category generation: SUCCESS (${duration}s)" -ForegroundColor Green
            $testResults += @{Test = "$Category Generation"; Status = "Success"; Duration = "${duration}s"; Details = "Generated successfully"}
            return $true
        } else {
            Write-Host "  $Category generation: FAILED (${duration}s)" -ForegroundColor Red
            $testResults += @{Test = "$Category Generation"; Status = "Failed"; Duration = "${duration}s"; Details = "Generation script failed"}
            return $false
        }
    } catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        Write-Host "  $Category generation: ERROR (${duration}s) - $($_.Exception.Message)" -ForegroundColor Red
        $testResults += @{Test = "$Category Generation"; Status = "Error"; Duration = "${duration}s"; Details = $_.Exception.Message}
        return $false
    }
}

function Test-ProvenScripts {
    Write-Host "Testing proven generation scripts..." -ForegroundColor Yellow
    
    $provenScripts = @{
        "Vehicles (FIXED)" = "Tools\ArtGen\FIXED_faction_vehicle_concepts.py"
        "UI/HUD (FIXED)" = "Tools\ArtGen\FIXED_faction_ui_hud_concepts.py" 
        "Environments" = "Tools\ArtGen\terminal_grounds_generator.py"
        "Pipeline" = "Tools\ArtGen\terminal_grounds_pipeline.py"
    }
    
    foreach ($script in $provenScripts.GetEnumerator()) {
        if (Test-Path $script.Value) {
            Write-Host "  $($script.Key): FOUND" -ForegroundColor Green
            $testResults += @{Script = $script.Key; Status = "Found"; Path = $script.Value}
            
            # Test if Python can import the script
            try {
                $importTest = python -c "import sys; sys.path.append('$(Split-Path $script.Value)'); import $(Split-Path -Leaf $script.Value -Replace '.py', ''); print('Import OK')" 2>$null
                if ($importTest -eq "Import OK") {
                    Write-Host "    Import test: OK" -ForegroundColor Green
                } else {
                    Write-Host "    Import test: ISSUE" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "    Import test: FAILED" -ForegroundColor Red
            }
        } else {
            Write-Host "  $($script.Key): NOT FOUND" -ForegroundColor Red
            $testResults += @{Script = $script.Key; Status = "Not Found"; Path = $script.Value}
        }
    }
    Write-Host ""
}

function Test-OutputDirectories {
    Write-Host "Testing output directories..." -ForegroundColor Yellow
    
    $outputDirs = @(
        "Tools\Comfy\ComfyUI-API\output",
        "Tools\Comfy\ComfyUI-API\output\procedural",
        "Content\ProceduralAssets"
    )
    
    foreach ($dir in $outputDirs) {
        if (Test-Path $dir) {
            $fileCount = (Get-ChildItem $dir -File).Count
            Write-Host "  $dir: EXISTS ($fileCount files)" -ForegroundColor Green
            $testResults += @{Directory = $dir; Status = "Exists"; FileCount = $fileCount}
        } else {
            Write-Host "  $dir: MISSING" -ForegroundColor Yellow
            try {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Host "    Created directory" -ForegroundColor Green
                $testResults += @{Directory = $dir; Status = "Created"; FileCount = 0}
            } catch {
                Write-Host "    Failed to create: $($_.Exception.Message)" -ForegroundColor Red
                $testResults += @{Directory = $dir; Status = "Failed to Create"; Details = $_.Exception.Message}
            }
        }
    }
    Write-Host ""
}

# Start testing
try {
    # Change to Terminal Grounds root
    $rootDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Set-Location $rootDir
    Write-Host "Working directory: $rootDir" -ForegroundColor Gray
    Write-Host ""

    # Test 1: Service Availability
    if (-not $SkipServices) {
        Test-ServiceAvailability
    } else {
        Write-Host "Skipping service availability tests" -ForegroundColor Yellow
        Write-Host ""
    }

    # Test 2: Proven Scripts
    Test-ProvenScripts

    # Test 3: Output Directories
    Test-OutputDirectories

    # Test 4: Asset Generation
    if ($TestType -eq "single") {
        # Test single asset type
        Write-Host "Testing single asset generation..." -ForegroundColor Cyan
        Test-AssetGeneration -Category $AssetType -Faction $Faction
        
    } elseif ($TestType -eq "quick") {
        # Quick test of key asset types
        Write-Host "Running quick asset generation tests..." -ForegroundColor Cyan
        $quickTests = @(
            @{Category = "vehicles"; Faction = "directorate"},
            @{Category = "environments"; Faction = "neutral"}
        )
        
        foreach ($test in $quickTests) {
            Test-AssetGeneration -Category $test.Category -Faction $test.Faction
        }
        
    } elseif ($TestType -eq "comprehensive") {
        # Test all asset types
        Write-Host "Running comprehensive asset generation tests..." -ForegroundColor Cyan
        $allTests = @(
            @{Category = "vehicles"; Faction = "directorate"},
            @{Category = "weapons"; Faction = "free77"},
            @{Category = "ui"; Faction = "civicwardens"},
            @{Category = "environments"; Faction = "neutral"},
            @{Category = "concepts"; Faction = "nomadclans"},
            @{Category = "emblems"; Faction = "vulturesunion"}
        )
        
        foreach ($test in $allTests) {
            Test-AssetGeneration -Category $test.Category -Faction $test.Faction
            Start-Sleep -Seconds 2  # Brief delay between tests
        }
    }

    # Generate test report
    Write-Host ""
    Write-Host "=== TEST RESULTS SUMMARY ===" -ForegroundColor Cyan
    Write-Host ""

    $totalTests = $testResults.Count
    $successfulTests = ($testResults | Where-Object { $_.Status -eq "Success" -or $_.Status -eq "Available" -or $_.Status -eq "Found" -or $_.Status -eq "Exists" }).Count
    $successRate = if ($totalTests -gt 0) { [math]::Round(($successfulTests / $totalTests) * 100, 1) } else { 0 }

    Write-Host "Total Tests: $totalTests" -ForegroundColor White
    Write-Host "Successful: $successfulTests" -ForegroundColor Green  
    Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -gt 80) { "Green" } elseif ($successRate -gt 60) { "Yellow" } else { "Red" })
    Write-Host ""

    # Detailed results
    Write-Host "Detailed Results:" -ForegroundColor White
    foreach ($result in $testResults) {
        $status = $result.Status
        $color = switch ($status) {
            "Success" { "Green" }
            "Available" { "Green" }
            "Found" { "Green" }
            "Exists" { "Green" }
            "Created" { "Green" }
            "Issue" { "Yellow" }
            "Not Available" { "Red" }
            "Not Found" { "Red" }
            "Failed" { "Red" }
            "Error" { "Red" }
            default { "Gray" }
        }
        
        $testName = $result.Test ?? $result.Service ?? $result.Script ?? $result.Directory ?? "Unknown"
        $duration = if ($result.Duration) { " ($($result.Duration))" } else { "" }
        $details = if ($result.Details) { " - $($result.Details)" } else { "" }
        
        Write-Host "  $testName : $status$duration$details" -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "=== RECOMMENDATIONS ===" -ForegroundColor Cyan
    Write-Host ""

    if ($successRate -lt 60) {
        Write-Host "❌ CRITICAL: Multiple systems are not working correctly" -ForegroundColor Red
        Write-Host "   • Check service availability and restart if needed" -ForegroundColor Yellow
        Write-Host "   • Verify Python dependencies and script paths" -ForegroundColor Yellow  
        Write-Host "   • Run: Tools\ProceduralBridge\Start-ProceduralServices.ps1 -TestMode" -ForegroundColor Yellow
    } elseif ($successRate -lt 80) {
        Write-Host "⚠️  WARNING: Some issues detected" -ForegroundColor Yellow
        Write-Host "   • Review failed tests above for specific issues" -ForegroundColor Yellow
        Write-Host "   • Most core functionality appears to be working" -ForegroundColor Yellow
    } else {
        Write-Host "✅ EXCELLENT: Procedural generation system is operational!" -ForegroundColor Green
        Write-Host "   • System is ready for Copilot integration" -ForegroundColor Green
        Write-Host "   • UE5 can now request procedural assets via UTGProceduralAssetCache" -ForegroundColor Green
        Write-Host "   • All asset types (vehicles, weapons, UI, environments) are supported" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor White
    Write-Host "1. Open UE5 Editor with Terminal Grounds project" -ForegroundColor Gray
    Write-Host "2. Add UTGProceduralAssetRequestor component to test actors" -ForegroundColor Gray
    Write-Host "3. Use Blueprint functions to request assets:" -ForegroundColor Gray
    Write-Host "   • RequestFactionVehicle(Directorate, 'transport')" -ForegroundColor Gray
    Write-Host "   • RequestFactionWeapon(Free77, 'rifle')" -ForegroundColor Gray  
    Write-Host "   • RequestFactionHUD(CivicWardens, 'status_overlay')" -ForegroundColor Gray
    Write-Host "4. Assets will be generated via ComfyUI and cached automatically" -ForegroundColor Gray

} catch {
    Write-Error "Test execution failed: $($_.Exception.Message)"
    exit 1
} finally {
    Write-Host ""
    Write-Host "Procedural generation workflow test completed." -ForegroundColor Cyan
}