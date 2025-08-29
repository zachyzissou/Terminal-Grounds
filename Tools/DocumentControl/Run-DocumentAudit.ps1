# Terminal Grounds - Document Control Specialist PowerShell Wrapper
# Provides convenient access to documentation governance features

param(
    [switch]$Audit,
    [switch]$Fix,
    [string]$Report = "governance_report.md",
    [switch]$Summary,
    [switch]$Help
)

# Set up paths
$ScriptRoot = $PSScriptRoot
$ProjectRoot = Split-Path (Split-Path $ScriptRoot -Parent) -Parent
$PythonScript = Join-Path $ScriptRoot "document_control_specialist.py"

if ($Help) {
    Write-Host @"
Terminal Grounds - Document Control Specialist

USAGE:
    .\Run-DocumentAudit.ps1 [OPTIONS]

OPTIONS:
    -Audit          Perform comprehensive documentation audit
    -Fix            Auto-fix issues that can be resolved automatically  
    -Report <path>  Generate governance report to specified file (default: governance_report.md)
    -Summary        Show quick summary of documentation health
    -Help           Show this help message

EXAMPLES:
    # Quick health check
    .\Run-DocumentAudit.ps1 -Summary

    # Full audit with auto-fixes
    .\Run-DocumentAudit.ps1 -Audit -Fix

    # Generate detailed report
    .\Run-DocumentAudit.ps1 -Audit -Report "docs\governance\monthly_report.md"

INTEGRATION WITH CLAUDE CODE:
    This tool integrates with Claude's agent system. You can invoke the 
    document-control-specialist agent for advanced governance tasks:
    
    - Documentation consolidation
    - Content architecture optimization
    - Quality assurance enforcement
    - Metadata standardization
"@
    return
}

# Verify Python script exists
if (-not (Test-Path $PythonScript)) {
    Write-Error "Document Control Specialist not found at: $PythonScript"
    Write-Host "Please ensure the document control system is properly installed."
    return
}

# Change to project root for proper path resolution
Push-Location $ProjectRoot

try {
    if ($Summary) {
        Write-Host "Terminal Grounds - Documentation Health Summary" -ForegroundColor Cyan
        Write-Host "=" * 50
        
        # Quick file count
        $MarkdownFiles = Get-ChildItem -Path . -Filter "*.md" -Recurse | Where-Object {
            $_.FullName -notmatch "\.git|node_modules|__pycache__|\.venv"
        }
        
        Write-Host "Total Markdown Files: $($MarkdownFiles.Count)" -ForegroundColor Green
        
        # Category breakdown
        $Categories = @{
            "docs/" = 0
            "Tools/" = 0  
            "Content/" = 0
            "Root" = 0
        }
        
        foreach ($file in $MarkdownFiles) {
            $relativePath = $file.FullName.Replace($PWD.Path, "").TrimStart("\")
            if ($relativePath.StartsWith("docs\")) { $Categories["docs/"]++ }
            elseif ($relativePath.StartsWith("Tools\")) { $Categories["Tools/"]++ }
            elseif ($relativePath.StartsWith("Content\")) { $Categories["Content/"]++ }
            else { $Categories["Root"]++ }
        }
        
        Write-Host "`nCategory Breakdown:" -ForegroundColor Yellow
        foreach ($category in $Categories.GetEnumerator()) {
            Write-Host "  $($category.Key): $($category.Value) files" -ForegroundColor White
        }
        
        # Check for registry
        $RegistryPath = Join-Path $ScriptRoot "document_registry.json"
        if (Test-Path $RegistryPath) {
            Write-Host "`nDocument Registry: Present" -ForegroundColor Green
            $RegistryData = Get-Content $RegistryPath | ConvertFrom-Json
            Write-Host "  Tracked Documents: $($RegistryData.PSObject.Properties.Count)" -ForegroundColor White
        } else {
            Write-Host "`nDocument Registry: Missing" -ForegroundColor Red
            Write-Host "  Run full audit to initialize registry" -ForegroundColor Yellow
        }
        
        Write-Host "`nRecommendation: Run '.\Run-DocumentAudit.ps1 -Audit' for detailed analysis" -ForegroundColor Cyan
    }
    else {
        # Build Python command arguments
        $PythonArgs = @("$PythonScript")
        
        if ($Audit) {
            $PythonArgs += "--audit"
        }
        
        if ($Fix) {
            $PythonArgs += "--fix"  
        }
        
        if ($Report -and $Audit) {
            $PythonArgs += "--report", $Report
        }
        
        $PythonArgs += "--project-root", "."
        
        # Execute Python script
        Write-Host "Executing Document Control Specialist..." -ForegroundColor Cyan
        & python @PythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nDocument control operation completed successfully!" -ForegroundColor Green
            
            if ($Report -and $Audit -and (Test-Path $Report)) {
                Write-Host "Governance report generated: $Report" -ForegroundColor Yellow
            }
        } else {
            Write-Error "Document control operation failed with exit code: $LASTEXITCODE"
        }
    }
}
catch {
    Write-Error "Error executing document control specialist: $($_.Exception.Message)"
}
finally {
    Pop-Location
}