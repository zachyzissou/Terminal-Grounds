# Terminal Grounds - Style Baseline Explorer (PowerShell Version)
# Generates style comparisons using your 168 LoRAs

$global:ComfyServer = "http://127.0.0.1:8000"
$global:ProjectRoot = "C:\Users\Zachg\Terminal-Grounds"
$global:StagingBase = "$global:ProjectRoot\Style_Staging"
$global:SessionID = Get-Date -Format "yyyyMMdd_HHmm"

# Style Presets with LoRA combinations
$global:StylePresets = @{
    "Gritty_Realism" = @{
        Name = "Gritty Realism"
        Description = "Photorealistic military with heavy weathering"
        LoRAs = @(
            @{Name="battlefield 2042 style.safetensors"; Strength=0.8},
            @{Name="Detailed Skin&Textures Flux V3.safetensors"; Strength=0.6},
            @{Name="Reactive armour style.safetensors"; Strength=0.7}
        )
        PromptStyle = "photorealistic, gritty, weathered, battle-worn, realistic military"
        CFG = 7.5
        Steps = 35
    }
    
    "Stylized_Military" = @{
        Name = "Stylized Military" 
        Description = "Semi-realistic with artistic flair"
        LoRAs = @(
            @{Name="Future_Warfare_SDXL.safetensors"; Strength=0.7},
            @{Name="StylizedTexture_v2.safetensors"; Strength=0.6}
        )
        PromptStyle = "stylized military art, concept art style, semi-realistic, professional game art"
        CFG = 8.0
        Steps = 30
    }
    
    "Cyberpunk_Military" = @{
        Name = "Cyberpunk Military"
        Description = "High-tech neon-infused military"
        LoRAs = @(
            @{Name="CyberPunk.safetensors"; Strength=0.7},
            @{Name="Neon_Noir_FLUX.safetensors"; Strength=0.6},
            @{Name="Future_Warfare_SDXL.safetensors"; Strength=0.5}
        )
        PromptStyle = "cyberpunk military, neon accents, high-tech warfare, futuristic combat"
        CFG = 8.5
        Steps = 30
    }
    
    "Post_Apocalyptic" = @{
        Name = "Post-Apocalyptic"
        Description = "Wasteland survivor aesthetic"
        LoRAs = @(
            @{Name="Reactive armour style.safetensors"; Strength=0.8},
            @{Name="war_t.safetensors"; Strength=0.7}
        )
        PromptStyle = "post-apocalyptic, makeshift armor, wasteland warrior, survival gear"
        CFG = 7.0
        Steps = 32
    }
    
    "Clean_SciFi" = @{
        Name = "Clean Sci-Fi"
        Description = "Pristine futuristic military"
        LoRAs = @(
            @{Name="SCIFI_Concept_Art_Landscapes.safetensors"; Strength=0.7},
            @{Name="Sci-fi_env_flux.safetensors"; Strength=0.6}
        )
        PromptStyle = "clean sci-fi, pristine technology, advanced military, sleek futuristic"
        CFG = 8.0
        Steps = 28
    }
}

# Test subjects
$global:TestSubjects = @{
    "faction_emblem" = @{
        Prompt = "military faction emblem, insignia, badge, symbol"
        Width = 1024
        Height = 1024
    }
    "soldier_portrait" = @{
        Prompt = "military soldier portrait, combat gear, tactical equipment"
        Width = 1024
        Height = 1024
    }
    "weapon_concept" = @{
        Prompt = "assault rifle weapon, military firearm, tactical weapon"
        Width = 1536
        Height = 1024
    }
}

function Initialize-StagingFolders {
    Write-Host "`nCreating staging folder structure..." -ForegroundColor Cyan
    
    # Create main staging folder
    New-Item -ItemType Directory -Force -Path $global:StagingBase | Out-Null
    
    # Create style folders
    foreach ($styleKey in $global:StylePresets.Keys) {
        $stylePath = Join-Path $global:StagingBase $styleKey
        New-Item -ItemType Directory -Force -Path $stylePath | Out-Null
        
        # Create subject subfolders
        foreach ($subjectKey in $global:TestSubjects.Keys) {
            $subjectPath = Join-Path $stylePath $subjectKey
            New-Item -ItemType Directory -Force -Path $subjectPath | Out-Null
        }
    }
    
    # Create comparison and favorites folders
    New-Item -ItemType Directory -Force -Path "$global:StagingBase\_Comparisons" | Out-Null
    New-Item -ItemType Directory -Force -Path "$global:StagingBase\_Favorites" | Out-Null
    
    Write-Host "  Created staging structure at: $global:StagingBase" -ForegroundColor Green
}

function Generate-StyleTest {
    param(
        [string]$StyleKey,
        [string]$SubjectKey,
        [int]$Seed = 42
    )
    
    $style = $global:StylePresets[$StyleKey]
    $subject = $global:TestSubjects[$SubjectKey]
    
    Write-Host "`n  Testing: $($style.Name) - $SubjectKey" -ForegroundColor Yellow
    
    # Build full prompt
    $fullPrompt = "$($subject.Prompt), $($style.PromptStyle), high quality, professional game asset"
    
    # Create workflow
    $workflow = @{
        "1" = @{
            class_type = "CheckpointLoaderSimple"
            inputs = @{ckpt_name = "FLUX1\flux1-dev-fp8.safetensors"}
        }
        "positive" = @{
            class_type = "CLIPTextEncode"
            inputs = @{
                text = $fullPrompt
                clip = @("1", 1)
            }
        }
        "negative" = @{
            class_type = "CLIPTextEncode"
            inputs = @{
                text = "low quality, amateur, placeholder, watermark"
                clip = @("1", 1)
            }
        }
        "latent" = @{
            class_type = "EmptyLatentImage"
            inputs = @{
                width = $subject.Width
                height = $subject.Height
                batch_size = 1
            }
        }
    }
    
    # Add LoRAs
    $lastModel = "1"
    $lastClip = "1"
    $loraIndex = 0
    
    if ($style.LoRAs) {
        Write-Host "    Using LoRAs:" -ForegroundColor Gray
        foreach ($lora in $style.LoRAs) {
            Write-Host "      - $($lora.Name) @ $($lora.Strength)" -ForegroundColor DarkGray
            
            $loraId = "lora_$loraIndex"
            $workflow[$loraId] = @{
                class_type = "LoraLoader"
                inputs = @{
                    lora_name = $lora.Name
                    strength_model = $lora.Strength
                    strength_clip = $lora.Strength * 0.8
                    model = @($lastModel, 0)
                    clip = @($lastClip, 1)
                }
            }
            
            $lastModel = $loraId
            $lastClip = $loraId
            $loraIndex++
        }
    }
    
    # Update CLIP connections
    $workflow["positive"]["inputs"]["clip"] = @($lastClip, 1)
    $workflow["negative"]["inputs"]["clip"] = @($lastClip, 1)
    
    # Add sampler
    $workflow["sampler"] = @{
        class_type = "KSampler"
        inputs = @{
            seed = $Seed
            steps = $style.Steps
            cfg = $style.CFG
            sampler_name = "dpmpp_2m"
            scheduler = "karras"
            denoise = 1.0
            model = @($lastModel, 0)
            positive = @("positive", 0)
            negative = @("negative", 0)
            latent_image = @("latent", 0)
        }
    }
    
    # Add decode and save
    $workflow["decode"] = @{
        class_type = "VAEDecode"
        inputs = @{
            samples = @("sampler", 0)
            vae = @("1", 2)
        }
    }
    
    $workflow["save"] = @{
        class_type = "SaveImage"
        inputs = @{
            filename_prefix = "TG_Style_${StyleKey}_${SubjectKey}"
            images = @("decode", 0)
        }
    }
    
    # Queue the generation
    Write-Host "    Queueing generation..." -ForegroundColor Gray
    
    $body = @{prompt = $workflow} | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-RestMethod -Uri "$global:ComfyServer/prompt" -Method Post -Body $body -ContentType "application/json"
        $promptId = $response.prompt_id
        Write-Host "    Queued: $promptId" -ForegroundColor Green
        
        # Wait for completion
        Write-Host "    Generating" -NoNewline
        $timeout = 120
        $start = Get-Date
        
        while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($timeout)) {
            Start-Sleep -Seconds 3
            Write-Host "." -NoNewline
            
            try {
                $history = Invoke-RestMethod -Uri "$global:ComfyServer/history/$promptId"
                if ($history.$promptId) {
                    Write-Host " Done!" -ForegroundColor Green
                    
                    # Get filename
                    $outputs = $history.$promptId.outputs
                    foreach ($output in $outputs.PSObject.Properties.Value) {
                        if ($output.images) {
                            $filename = $output.images[0].filename
                            Write-Host "    Generated: $filename" -ForegroundColor Cyan
                            
                            # Download and save
                            $imageUrl = "$global:ComfyServer/view?filename=$filename"
                            $outputPath = Join-Path $global:StagingBase "$StyleKey\$SubjectKey\${StyleKey}_${SubjectKey}_${Seed}.png"
                            
                            Write-Host "    Downloading to staging folder..." -ForegroundColor Gray
                            Invoke-WebRequest -Uri $imageUrl -OutFile $outputPath
                            Write-Host "    Saved: $outputPath" -ForegroundColor Green
                            
                            return $outputPath
                        }
                    }
                }
            } catch {
                # Still processing
            }
        }
        
        Write-Host " Timeout!" -ForegroundColor Red
        
    } catch {
        Write-Host "    Error: $_" -ForegroundColor Red
    }
    
    return $null
}

function Show-Menu {
    Clear-Host
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "     TERMINAL GROUNDS - STYLE BASELINE EXPLORER" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available Style Presets:" -ForegroundColor Yellow
    $i = 1
    foreach ($key in $global:StylePresets.Keys) {
        $style = $global:StylePresets[$key]
        Write-Host "  $i. $($style.Name) - $($style.Description)" -ForegroundColor White
        $i++
    }
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Quick Test (1 style, 1 subject)" -ForegroundColor White
    Write-Host "  2. Compare All Styles (single subject)" -ForegroundColor White
    Write-Host "  3. Test Single Style (all subjects)" -ForegroundColor White
    Write-Host "  4. Generate Comparison Report" -ForegroundColor White
    Write-Host "  5. Exit" -ForegroundColor Gray
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
}

# Main execution
Initialize-StagingFolders

Show-Menu
$choice = Read-Host "Select option (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`nQuick Test - Generating Gritty Realism faction emblem..." -ForegroundColor Yellow
        Generate-StyleTest -StyleKey "Gritty_Realism" -SubjectKey "faction_emblem" -Seed 42
    }
    
    "2" {
        Write-Host "`nSelect subject to compare across all styles:" -ForegroundColor Yellow
        $subjects = @("faction_emblem", "soldier_portrait", "weapon_concept")
        for ($i = 0; $i -lt $subjects.Count; $i++) {
            Write-Host "  $($i+1). $($subjects[$i])" -ForegroundColor White
        }
        
        $subjectChoice = [int](Read-Host "Select subject (1-3)") - 1
        $selectedSubject = $subjects[$subjectChoice]
        
        Write-Host "`nGenerating $selectedSubject in all styles..." -ForegroundColor Yellow
        
        foreach ($styleKey in $global:StylePresets.Keys) {
            Generate-StyleTest -StyleKey $styleKey -SubjectKey $selectedSubject -Seed 42
            Start-Sleep -Seconds 2
        }
    }
    
    "3" {
        Write-Host "`nSelect style to test all subjects:" -ForegroundColor Yellow
        $styleKeys = @($global:StylePresets.Keys)
        for ($i = 0; $i -lt $styleKeys.Count; $i++) {
            Write-Host "  $($i+1). $($global:StylePresets[$styleKeys[$i]].Name)" -ForegroundColor White
        }
        
        $styleChoice = [int](Read-Host "Select style (1-$($styleKeys.Count))") - 1
        $selectedStyle = $styleKeys[$styleChoice]
        
        Write-Host "`nGenerating all subjects in $($global:StylePresets[$selectedStyle].Name) style..." -ForegroundColor Yellow
        
        foreach ($subjectKey in $global:TestSubjects.Keys) {
            Generate-StyleTest -StyleKey $selectedStyle -SubjectKey $subjectKey -Seed 42
            Start-Sleep -Seconds 2
        }
    }
    
    "4" {
        Write-Host "`nGenerating comparison report..." -ForegroundColor Yellow
        $reportPath = Join-Path $global:StagingBase "style_comparison_$global:SessionID.txt"
        
        $report = @"
TERMINAL GROUNDS - STYLE BASELINE COMPARISON
Generated: $(Get-Date)
Session: $global:SessionID

STYLE PRESETS TESTED:
"@
        
        foreach ($styleKey in $global:StylePresets.Keys) {
            $style = $global:StylePresets[$styleKey]
            $report += "`n`n$($style.Name):"
            $report += "`n  Description: $($style.Description)"
            $report += "`n  LoRAs: $($style.LoRAs.Count)"
            $report += "`n  CFG: $($style.CFG) | Steps: $($style.Steps)"
        }
        
        $report += "`n`nResults saved in: $global:StagingBase"
        $report | Out-File -FilePath $reportPath
        
        Write-Host "  Report saved: $reportPath" -ForegroundColor Green
    }
    
    "5" {
        Write-Host "`nExiting..." -ForegroundColor Gray
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Results saved to: $global:StagingBase" -ForegroundColor Green
Write-Host "Review generated styles and copy favorites to _Favorites folder" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
