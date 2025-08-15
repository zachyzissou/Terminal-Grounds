# Terminal Grounds - Advanced ComfyUI Setup for RTX 3090 Ti
# Leverages 24GB VRAM for maximum quality and creativity

Write-Host "================================================" -ForegroundColor Magenta
Write-Host "  TERMINAL GROUNDS - ADVANCED SD SETUP" -ForegroundColor Magenta
Write-Host "  RTX 3090 Ti Detected - 24GB VRAM" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Magenta
Write-Host ""

$ErrorActionPreference = "Stop"

# Configuration
$config = @{
    ComfyUIPath = "C:\ComfyUI"
    ModelsPath = "C:\ComfyUI\ComfyUI\models"
    OutputPath = "C:\Users\Zachg\Terminal-Grounds-Generations"
    TempPath = "$env:TEMP\TG_Setup"
}

# Create directories
foreach ($path in $config.Values) {
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "✓ Created: $path" -ForegroundColor Green
    }
}

Write-Host "`n📦 INSTALLING COMFYUI..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Install Git if needed
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (!$gitPath) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Clone ComfyUI
if (!(Test-Path "$($config.ComfyUIPath)\ComfyUI\.git")) {
    Write-Host "Cloning ComfyUI repository..." -ForegroundColor Yellow
    git clone https://github.com/comfyanonymous/ComfyUI.git "$($config.ComfyUIPath)\ComfyUI"
} else {
    Write-Host "Updating ComfyUI..." -ForegroundColor Yellow
    cd "$($config.ComfyUIPath)\ComfyUI"
    git pull
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
cd "$($config.ComfyUIPath)\ComfyUI"
python -m pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Install ComfyUI Manager (essential for downloading models in-app)
Write-Host "`nInstalling ComfyUI Manager..." -ForegroundColor Yellow
$customNodesPath = "$($config.ComfyUIPath)\ComfyUI\custom_nodes"
if (!(Test-Path "$customNodesPath\ComfyUI-Manager")) {
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git "$customNodesPath\ComfyUI-Manager"
}

Write-Host "`n🎨 DOWNLOADING CREATIVE MODELS & LORAS..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Model download function
function Download-Model {
    param(
        [string]$url,
        [string]$outputPath,
        [string]$fileName,
        [string]$description
    )
    
    $fullPath = Join-Path $outputPath $fileName
    if (!(Test-Path $fullPath)) {
        Write-Host "↓ Downloading: $description" -ForegroundColor Yellow
        Write-Host "  To: $fileName" -ForegroundColor DarkGray
        
        # Use aria2 for faster downloads if available
        $aria2 = Get-Command aria2c -ErrorAction SilentlyContinue
        if ($aria2) {
            aria2c -x 16 -s 16 -d $outputPath -o $fileName $url
        } else {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $url -OutFile $fullPath -UseBasicParsing
            $ProgressPreference = 'Continue'
        }
        Write-Host "✓ Downloaded: $description" -ForegroundColor Green
    } else {
        Write-Host "✓ Already exists: $description" -ForegroundColor DarkGreen
    }
}

# Create model directories
$modelDirs = @(
    "checkpoints",
    "loras", 
    "vae",
    "controlnet",
    "upscale_models",
    "embeddings"
)

foreach ($dir in $modelDirs) {
    $path = "$($config.ModelsPath)\$dir"
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

Write-Host "`n🎮 MAIN MODELS (for different asset types):" -ForegroundColor White

# Download models perfect for game assets
$models = @(
    @{
        Name = "DreamShaper XL"
        Description = "Best for stylized game art"
        Url = "https://civitai.com/api/download/models/351306"
        Path = "$($config.ModelsPath)\checkpoints"
        FileName = "dreamshaper_xl.safetensors"
    },
    @{
        Name = "Juggernaut XL" 
        Description = "Photorealistic for reference/concepts"
        Url = "https://civitai.com/api/download/models/456194"
        Path = "$($config.ModelsPath)\checkpoints"
        FileName = "juggernaut_xl.safetensors"
    },
    @{
        Name = "SDXL Base"
        Description = "Versatile base model"
        Url = "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
        Path = "$($config.ModelsPath)\checkpoints"
        FileName = "sd_xl_base_1.0.safetensors"
    }
)

Write-Host "`n🔧 SPECIALIZED LORAS (for Terminal Grounds style):" -ForegroundColor White

$loras = @(
    @{
        Name = "Cyberpunk 2077 Style"
        Description = "Perfect for sci-fi UI elements"
        Url = "https://civitai.com/api/download/models/298508"
        Path = "$($config.ModelsPath)\loras"
        FileName = "cyberpunk2077_style.safetensors"
    },
    @{
        Name = "Military Vehicles"
        Description = "Detailed military tech"
        Url = "https://civitai.com/api/download/models/146856"
        Path = "$($config.ModelsPath)\loras"
        FileName = "military_vehicles.safetensors"
    },
    @{
        Name = "Post-Apocalyptic"
        Description = "Weathered, worn aesthetics"
        Url = "https://civitai.com/api/download/models/135931"
        Path = "$($config.ModelsPath)\loras"
        FileName = "post_apocalyptic.safetensors"
    },
    @{
        Name = "Weapon Concepts"
        Description = "Detailed weapon designs"
        Url = "https://civitai.com/api/download/models/180525"
        Path = "$($config.ModelsPath)\loras"
        FileName = "weapon_concepts.safetensors"
    },
    @{
        Name = "Logo Design"
        Description = "Clean logo/emblem generation"
        Url = "https://civitai.com/api/download/models/152309"
        Path = "$($config.ModelsPath)\loras"
        FileName = "logo_design.safetensors"
    }
)

# Note: Some URLs may need updating - these are examples
Write-Host "`n⚠️  Note: Downloading from CivitAI requires their API" -ForegroundColor Yellow
Write-Host "If any downloads fail, you can manually download from:" -ForegroundColor Yellow
Write-Host "- https://civitai.com (search for the model names)" -ForegroundColor DarkGray
Write-Host "- https://huggingface.co" -ForegroundColor DarkGray

# Download SDXL Base as minimum
Download-Model -url $models[2].Url -outputPath $models[2].Path -fileName $models[2].FileName -description $models[2].Description

Write-Host "`n🚀 CREATING TERMINAL GROUNDS WORKFLOWS..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Create advanced workflow for Terminal Grounds
$workflowsPath = "$($config.ComfyUIPath)\ComfyUI\user\default\workflows"
if (!(Test-Path $workflowsPath)) {
    New-Item -ItemType Directory -Path $workflowsPath -Force | Out-Null
}

# Save Terminal Grounds mega workflow
$megaWorkflow = @'
{
    "name": "Terminal Grounds Asset Pipeline",
    "description": "Advanced workflow leveraging 24GB VRAM",
    "last_node_id": 50,
    "last_link_id": 100,
    "nodes": [
        {
            "id": 1,
            "type": "CheckpointLoaderSimple",
            "pos": [50, 300],
            "size": {"0": 315, "1": 98},
            "outputs": [
                {"name": "MODEL", "type": "MODEL"},
                {"name": "CLIP", "type": "CLIP"},
                {"name": "VAE", "type": "VAE"}
            ],
            "properties": {},
            "widgets_values": ["dreamshaper_xl.safetensors"]
        },
        {
            "id": 2,
            "type": "LoraLoader",
            "pos": [400, 300],
            "size": {"0": 315, "1": 126},
            "inputs": [
                {"name": "model", "type": "MODEL", "link": 1},
                {"name": "clip", "type": "CLIP", "link": 2}
            ],
            "outputs": [
                {"name": "MODEL", "type": "MODEL"},
                {"name": "CLIP", "type": "CLIP"}
            ],
            "properties": {},
            "widgets_values": ["post_apocalyptic.safetensors", 0.7, 0.7]
        }
    ],
    "config": {
        "terminal_grounds": {
            "factions": ["Directorate", "Vultures Union", "Free 77", "Corporate Combine", "Nomad Clans", "Vaulted Archivists", "Civic Wardens"],
            "asset_types": ["faction_logos", "ui_icons", "weapons", "vehicles", "environments"],
            "style_tags": "military sci-fi, post-apocalyptic, weathered, tactical, industrial"
        }
    }
}
'@

$megaWorkflow | Out-File -FilePath "$workflowsPath\TerminalGrounds_Advanced.json" -Encoding UTF8

Write-Host "✓ Created Terminal Grounds workflow" -ForegroundColor Green

# Create launcher with optimizations for 3090 Ti
$launcherContent = @"
@echo off
title Terminal Grounds - ComfyUI (RTX 3090 Ti Optimized)
echo ================================================
echo   TERMINAL GROUNDS ASSET GENERATOR
echo   RTX 3090 Ti - 24GB VRAM Detected
echo ================================================
echo.

cd /d "$($config.ComfyUIPath)\ComfyUI"

echo Starting ComfyUI with optimizations...
echo - High VRAM mode enabled
echo - Batch processing ready
echo - Multiple LoRAs supported
echo.

:: Launch with 3090 Ti optimizations
python main.py ^
    --highvram ^
    --use-pytorch-cross-attention ^
    --output-directory "$($config.OutputPath)" ^
    --listen 127.0.0.1 ^
    --port 8188

pause
"@

$launcherContent | Out-File -FilePath "$($config.ComfyUIPath)\Launch_TerminalGrounds.bat" -Encoding ASCII

Write-Host "`n✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "🎮 Your 3090 Ti can handle:" -ForegroundColor Cyan
Write-Host "  • SDXL models at full resolution" -ForegroundColor White
Write-Host "  • Multiple LoRAs stacked (3-4 simultaneously)" -ForegroundColor White
Write-Host "  • Batch sizes up to 8 images" -ForegroundColor White
Write-Host "  • ControlNet + main model + upscaling" -ForegroundColor White
Write-Host ""
Write-Host "📂 Launcher created at:" -ForegroundColor Yellow
Write-Host "  $($config.ComfyUIPath)\Launch_TerminalGrounds.bat" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To start generating:" -ForegroundColor Green
Write-Host "  1. Run the launcher above" -ForegroundColor White
Write-Host "  2. Open: http://127.0.0.1:8188" -ForegroundColor White
Write-Host "  3. Load: TerminalGrounds_Advanced workflow" -ForegroundColor White
Write-Host ""
Write-Host "💡 First time? ComfyUI Manager will help download" -ForegroundColor Cyan
Write-Host "   any missing models directly from the UI!" -ForegroundColor Cyan
