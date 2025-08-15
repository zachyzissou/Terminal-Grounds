# Terminal Grounds - ComfyUI Auto-Setup Script
# Run this in PowerShell as Administrator

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Terminal Grounds - ComfyUI Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Function to download files
function Download-File {
    param(
        [string]$url,
        [string]$output
    )
    Write-Host "Downloading: $output" -ForegroundColor Yellow
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    $ProgressPreference = 'Continue'
}

# Check if ComfyUI directory exists
$comfyPath = "C:\ComfyUI"
if (Test-Path $comfyPath) {
    Write-Host "ComfyUI directory already exists at $comfyPath" -ForegroundColor Green
    $response = Read-Host "Do you want to continue with setup? (y/n)"
    if ($response -ne 'y') {
        exit
    }
} else {
    Write-Host "Creating ComfyUI directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $comfyPath -Force | Out-Null
}

# Download 7-Zip if not installed (for extracting .7z files)
$7zipPath = "$env:ProgramFiles\7-Zip\7z.exe"
if (-not (Test-Path $7zipPath)) {
    Write-Host "7-Zip not found. Installing..." -ForegroundColor Yellow
    $7zipInstaller = "$env:TEMP\7z-installer.exe"
    Download-File -url "https://www.7-zip.org/a/7z2301-x64.exe" -output $7zipInstaller
    Start-Process -FilePath $7zipInstaller -ArgumentList "/S" -Wait
    Write-Host "7-Zip installed." -ForegroundColor Green
}

# Download ComfyUI Portable
$comfyUIUrl = "https://github.com/comfyanonymous/ComfyUI/releases/download/latest/ComfyUI_windows_portable_nvidia_cu121_or_cpu.7z"
$comfyUIZip = "$comfyPath\ComfyUI_portable.7z"

if (-not (Test-Path "$comfyPath\ComfyUI\main.py")) {
    Write-Host "Downloading ComfyUI Portable (this may take a while)..." -ForegroundColor Yellow
    Download-File -url $comfyUIUrl -output $comfyUIZip
    
    Write-Host "Extracting ComfyUI..." -ForegroundColor Yellow
    & $7zipPath x $comfyUIZip -o"$comfyPath" -y
    
    # Clean up
    Remove-Item $comfyUIZip -Force
    Write-Host "ComfyUI extracted successfully!" -ForegroundColor Green
} else {
    Write-Host "ComfyUI already extracted." -ForegroundColor Green
}

# Create Terminal Grounds specific directories
$tgOutputPath = "C:\Users\Zachg\Terminal-Grounds-Generations"
if (-not (Test-Path $tgOutputPath)) {
    New-Item -ItemType Directory -Path $tgOutputPath -Force | Out-Null
    Write-Host "Created Terminal Grounds output directory." -ForegroundColor Green
}

# Create custom workflow directory
$workflowPath = "$comfyPath\ComfyUI\custom_workflows"
if (-not (Test-Path $workflowPath)) {
    New-Item -ItemType Directory -Path $workflowPath -Force | Out-Null
}

# Create Terminal Grounds workflow file
$workflowContent = @'
{
    "name": "Terminal Grounds Asset Generator",
    "description": "Workflow for generating game assets",
    "output_path": "C:\\Users\\Zachg\\Terminal-Grounds-Generations"
}
'@
$workflowContent | Out-File -FilePath "$workflowPath\terminal_grounds.json" -Encoding UTF8

# Create startup batch file for Terminal Grounds
$startupBatch = @"
@echo off
echo Starting ComfyUI for Terminal Grounds...
cd /d C:\ComfyUI\ComfyUI
python main.py --output-directory C:\Users\Zachg\Terminal-Grounds-Generations
"@
$startupBatch | Out-File -FilePath "$comfyPath\Start_ComfyUI_TerminalGrounds.bat" -Encoding ASCII

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Download a model from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0" -ForegroundColor White
Write-Host "2. Place it in: $comfyPath\ComfyUI\models\checkpoints\" -ForegroundColor White
Write-Host "3. Run: $comfyPath\Start_ComfyUI_TerminalGrounds.bat" -ForegroundColor White
Write-Host "4. Open browser to: http://127.0.0.1:8188" -ForegroundColor White
Write-Host ""
Write-Host "Images will save directly to: $tgOutputPath" -ForegroundColor Green
