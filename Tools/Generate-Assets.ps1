# Terminal Grounds Asset Generator - PowerShell Version
# Works with your ComfyUI at http://127.0.0.1:8000

$global:ComfyServer = "http://127.0.0.1:8000"
$global:OutputPath = "C:\Users\Zachg\Terminal-Grounds\Generated_Assets"

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $global:OutputPath | Out-Null

function Generate-Asset {
    param(
        [string]$Name,
        [string]$Type,
        [string]$Prompt,
        [int]$Width = 1024,
        [int]$Height = 1024,
        [int]$Steps = 20,
        [float]$CFG = 7.5
    )
    
    Write-Host "`n=== Generating: $Name ($Type) ===" -ForegroundColor Cyan
    Write-Host "Prompt: $Prompt" -ForegroundColor Gray
    
    # Create workflow
    $workflow = @{
        "1" = @{
            "class_type" = "CheckpointLoaderSimple"
            "inputs" = @{
                "ckpt_name" = "FLUX1\flux1-dev-fp8.safetensors"
            }
        }
        "2" = @{
            "class_type" = "CLIPTextEncode"
            "inputs" = @{
                "text" = $Prompt
                "clip" = @("1", 1)
            }
        }
        "3" = @{
            "class_type" = "CLIPTextEncode"
            "inputs" = @{
                "text" = "low quality, blurry, text, watermark"
                "clip" = @("1", 1)
            }
        }
        "4" = @{
            "class_type" = "EmptyLatentImage"
            "inputs" = @{
                "width" = $Width
                "height" = $Height
                "batch_size" = 1
            }
        }
        "5" = @{
            "class_type" = "KSampler"
            "inputs" = @{
                "seed" = Get-Random -Maximum 1000000
                "steps" = $Steps
                "cfg" = $CFG
                "sampler_name" = "euler"
                "scheduler" = "normal"
                "denoise" = 1.0
                "model" = @("1", 0)
                "positive" = @("2", 0)
                "negative" = @("3", 0)
                "latent_image" = @("4", 0)
            }
        }
        "6" = @{
            "class_type" = "VAEDecode"
            "inputs" = @{
                "samples" = @("5", 0)
                "vae" = @("1", 2)
            }
        }
        "7" = @{
            "class_type" = "SaveImage"
            "inputs" = @{
                "filename_prefix" = "TG_${Name}_${Type}"
                "images" = @("6", 0)
            }
        }
    }
    
    # Queue generation
    $body = @{
        "prompt" = $workflow
    } | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri "$global:ComfyServer/prompt" -Method Post -Body $body -ContentType "application/json"
        $promptId = $response.prompt_id
        Write-Host "Queued: $promptId" -ForegroundColor Green
        
        # Wait for completion
        Write-Host "Generating" -NoNewline
        $timeout = 120
        $start = Get-Date
        
        while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($timeout)) {
            Start-Sleep -Seconds 2
            Write-Host "." -NoNewline
            
            try {
                $history = Invoke-RestMethod -Uri "$global:ComfyServer/history/$promptId"
                if ($history.$promptId) {
                    Write-Host " Done!" -ForegroundColor Green
                    
                    # Get generated files
                    $outputs = $history.$promptId.outputs
                    foreach ($output in $outputs.PSObject.Properties.Value) {
                        if ($output.images) {
                            foreach ($img in $output.images) {
                                Write-Host "  Generated: $($img.filename)" -ForegroundColor Yellow
                                
                                # Download image
                                $imageUrl = "$global:ComfyServer/view?filename=$($img.filename)"
                                $localPath = Join-Path $global:OutputPath "$Name_$Type.png"
                                Invoke-WebRequest -Uri $imageUrl -OutFile $localPath
                                Write-Host "  Saved to: $localPath" -ForegroundColor Green
                            }
                        }
                    }
                    return $true
                }
            } catch {
                # Still processing
            }
        }
        
        Write-Host " Timeout!" -ForegroundColor Red
        return $false
        
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
        return $false
    }
}

# Main menu
function Show-Menu {
    Clear-Host
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "     TERMINAL GROUNDS - ASSET GENERATOR (POWERSHELL)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Generate Single Test Asset" -ForegroundColor White
    Write-Host "  2. Generate All Faction Emblems" -ForegroundColor White
    Write-Host "  3. Generate All Faction Posters" -ForegroundColor White
    Write-Host "  4. Generate UI Icons" -ForegroundColor White
    Write-Host "  5. Generate Everything" -ForegroundColor Yellow
    Write-Host "  6. Exit" -ForegroundColor Gray
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
}

# Faction data
$factions = @(
    @{
        Name = "Directorate"
        EmblemPrompt = "military chevron emblem with three stars, steel gray and tactical blue, authoritarian insignia, sharp geometric design, game asset"
        PosterPrompt = "HOLD THE LINE propaganda poster, military soldiers in formation, industrial complex, directorate flag, wartime mobilization"
    },
    @{
        Name = "VulturesUnion"
        EmblemPrompt = "scavenger bird skull with wrenches, hazard yellow on black, salvage guild emblem, industrial grunge texture, game asset"
        PosterPrompt = "SALVAGE FEEDS THE WAR poster, workers stripping mech, industrial salvage yard, sparks and welding"
    },
    @{
        Name = "Free77"
        EmblemPrompt = "stenciled number 77 with bullet holes, tactical brown, mercenary badge, worn metal, minimalist military design, game asset"
        PosterPrompt = "CONTRACT COMPLETE recruitment poster, battle-hardened mercenaries, professional soldiers for hire"
    },
    @{
        Name = "CorporateCombine"
        EmblemPrompt = "hexagonal chrome shield, corporate blue, security corporation logo, holographic effect, pristine finish, game asset"
        PosterPrompt = "PUBLIC SAFETY PRIORITY poster, corporate security forces, glass tower, surveillance drones"
    },
    @{
        Name = "NomadClans"
        EmblemPrompt = "wheel hub with tribal patterns, rust and leather, convoy clan symbol, road warrior aesthetic, game asset"
        PosterPrompt = "THE CONVOY NEVER STOPS poster, vehicle column through wasteland, armed trucks, dust storm"
    },
    @{
        Name = "VaultedArchivists"
        EmblemPrompt = "mystical eye in circuit patterns, gold and purple, ancient technology sigil, arcane glow, game asset"
        PosterPrompt = "KNOWLEDGE IS POWER poster, hooded figure with artifact, purple energy, techno-occult symbols"
    },
    @{
        Name = "CivicWardens"
        EmblemPrompt = "fortress wall with rifles, safety orange and navy, community defense badge, protective shield, game asset"
        PosterPrompt = "DEFEND YOUR HOME poster, civilians building barricades, neighborhood militia, urban resistance"
    }
)

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Select option (1-6)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nGenerating test asset..." -ForegroundColor Yellow
            Generate-Asset -Name "Test_Directorate" -Type "emblem" `
                -Prompt "military faction emblem, chevron design, steel blue and gray, high quality game asset" `
                -Width 1024 -Height 1024 -Steps 20
        }
        
        "2" {
            Write-Host "`nGenerating all faction emblems..." -ForegroundColor Yellow
            foreach ($faction in $factions) {
                Generate-Asset -Name $faction.Name -Type "emblem" `
                    -Prompt $faction.EmblemPrompt `
                    -Width 2048 -Height 2048 -Steps 30 -CFG 8.5
            }
        }
        
        "3" {
            Write-Host "`nGenerating all faction posters..." -ForegroundColor Yellow
            foreach ($faction in $factions) {
                Generate-Asset -Name $faction.Name -Type "poster" `
                    -Prompt $faction.PosterPrompt `
                    -Width 1024 -Height 1536 -Steps 35 -CFG 9.0
            }
        }
        
        "4" {
            Write-Host "`nGenerating UI icons..." -ForegroundColor Yellow
            $icons = @(
                @{Name="extraction"; Prompt="extraction point icon, green arrow up, military HUD"},
                @{Name="hostile"; Prompt="enemy contact icon, red crosshair, combat alert"},
                @{Name="objective"; Prompt="objective marker, yellow diamond, waypoint icon"},
                @{Name="ammo"; Prompt="ammunition icon, blue bullets, supply marker"},
                @{Name="medical"; Prompt="medical cross, white health icon, aid station"}
            )
            
            foreach ($icon in $icons) {
                Generate-Asset -Name $icon.Name -Type "icon" `
                    -Prompt "$($icon.Prompt), clean UI design, high contrast, game HUD element" `
                    -Width 512 -Height 512 -Steps 20 -CFG 7.0
            }
        }
        
        "5" {
            Write-Host "`nGenerating EVERYTHING..." -ForegroundColor Yellow
            Write-Host "This will take approximately 30-45 minutes." -ForegroundColor Gray
            
            # Generate all emblems
            foreach ($faction in $factions) {
                Generate-Asset -Name $faction.Name -Type "emblem" `
                    -Prompt $faction.EmblemPrompt `
                    -Width 2048 -Height 2048 -Steps 30 -CFG 8.5
            }
            
            # Generate all posters
            foreach ($faction in $factions) {
                Generate-Asset -Name $faction.Name -Type "poster" `
                    -Prompt $faction.PosterPrompt `
                    -Width 1024 -Height 1536 -Steps 35 -CFG 9.0
            }
        }
        
        "6" {
            Write-Host "`nExiting..." -ForegroundColor Gray
            break
        }
        
        default {
            Write-Host "`nInvalid option!" -ForegroundColor Red
        }
    }
    
    if ($choice -ne "6") {
        Write-Host "`nPress any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
} while ($choice -ne "6")

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Assets saved to: $global:OutputPath" -ForegroundColor Green
Write-Host "ComfyUI output: C:\Users\Zachg\Documents\ComfyUI\output\" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
