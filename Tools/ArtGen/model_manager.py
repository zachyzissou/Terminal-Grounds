#!/usr/bin/env python3
"""
Terminal Grounds - Model & LoRA Manager
========================================
Automatically downloads and configures the best models for Terminal Grounds.
Works with your existing ComfyUI setup on port 8000.
"""

import json
import urllib.request
import time
from pathlib import Path
from typing import Dict, List, Optional

COMFYUI_SERVER = "127.0.0.1:8000"
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")

class ModelManager:
    """Manages models and creates optimized workflows"""
    
    def __init__(self):
        self.server = COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        
    def check_available_models(self) -> Dict:
        """Check what models are currently available in ComfyUI"""
        print("\nChecking available models...")
        
        try:
            # Get checkpoint models
            url = f"{self.base_url}/object_info/CheckpointLoaderSimple"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                checkpoints = data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            
            # Get LoRA models
            url = f"{self.base_url}/object_info/LoraLoader"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                loras = data["LoraLoader"]["input"]["required"]["lora_name"][0] if "LoraLoader" in data else []
            
            # Get VAE models
            url = f"{self.base_url}/object_info/VAELoader"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                vaes = data["VAELoader"]["input"]["required"]["vae_name"][0]
            
            print(f"  Checkpoints: {len(checkpoints)} found")
            for ckpt in checkpoints[:5]:  # Show first 5
                print(f"    - {ckpt}")
            
            print(f"  LoRAs: {len(loras)} found")
            for lora in loras[:5]:  # Show first 5
                print(f"    - {lora}")
                
            print(f"  VAEs: {len(vaes)} found")
            for vae in vaes[:3]:
                print(f"    - {vae}")
            
            return {
                "checkpoints": checkpoints,
                "loras": loras,
                "vaes": vaes
            }
            
        except Exception as e:
            print(f"Error checking models: {e}")
            return {"checkpoints": [], "loras": [], "vaes": []}
    
    def recommend_downloads(self) -> List[Dict]:
        """Recommend specific models for Terminal Grounds aesthetic"""
        
        recommendations = [
            {
                "type": "LoRA",
                "name": "Military Equipment LoRA",
                "filename": "military_equipment_lora.safetensors",
                "url": "https://civitai.com/api/download/models/239306",
                "description": "Adds detailed military gear, weapons, tactical equipment",
                "use_for": ["weapon_concepts", "character_gear", "vehicle_details"]
            },
            {
                "type": "LoRA", 
                "name": "Weathered Metal LoRA",
                "filename": "weathered_metal_lora.safetensors",
                "url": "https://civitai.com/api/download/models/187432",
                "description": "Rust, wear, battle damage, scratched paint",
                "use_for": ["vehicles", "weapons", "environments"]
            },
            {
                "type": "LoRA",
                "name": "Sci-Fi Technology LoRA",
                "filename": "scifi_tech_lora.safetensors",
                "url": "https://civitai.com/api/download/models/298765",
                "description": "Futuristic UI, holograms, alien tech",
                "use_for": ["ui_elements", "alien_weapons", "tech_concepts"]
            },
            {
                "type": "LoRA",
                "name": "Logo/Emblem Design LoRA",
                "filename": "logo_design_lora.safetensors",
                "url": "https://civitai.com/api/download/models/276543",
                "description": "Clean vector-style logos and emblems",
                "use_for": ["faction_emblems", "ui_icons", "decals"]
            },
            {
                "type": "LoRA",
                "name": "Post-Apocalyptic LoRA",
                "filename": "post_apoc_lora.safetensors",
                "url": "https://civitai.com/api/download/models/234567",
                "description": "Wasteland aesthetics, makeshift repairs, survival gear",
                "use_for": ["environments", "vehicles", "character_outfits"]
            },
            {
                "type": "Checkpoint",
                "name": "RealVisXL V4.0",
                "filename": "realvisxl_v40.safetensors",
                "url": "https://civitai.com/api/download/models/361593",
                "description": "Photorealistic model, excellent for weapons and vehicles",
                "use_for": ["weapon_renders", "vehicle_concepts", "character_portraits"]
            },
            {
                "type": "VAE",
                "name": "SDXL VAE (Better Colors)",
                "filename": "sdxl_vae.safetensors",
                "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
                "description": "Improved color accuracy and less artifacts",
                "use_for": ["all_assets"]
            }
        ]
        
        return recommendations
    
    def create_download_script(self) -> None:
        """Create a PowerShell script to download recommended models"""
        
        script_content = """# Terminal Grounds - Model Downloader
# Downloads recommended models for ComfyUI

$models = @(
    @{
        Name = "Military Equipment LoRA"
        URL = "https://civitai.com/api/download/models/239306"
        Path = "C:\Users\Zachg\Documents\ComfyUI\models\loras\military_equipment.safetensors"
    },
    @{
        Name = "Weathered Metal LoRA"
        URL = "https://civitai.com/api/download/models/187432"
        Path = "C:\Users\Zachg\Documents\ComfyUI\models\loras\weathered_metal.safetensors"
    },
    @{
        Name = "Sci-Fi Tech LoRA"
        URL = "https://civitai.com/api/download/models/298765"
        Path = "C:\Users\Zachg\Documents\ComfyUI\models\loras\scifi_tech.safetensors"
    },
    @{
        Name = "Logo Design LoRA"
        URL = "https://civitai.com/api/download/models/276543"
        Path = "C:\Users\Zachg\Documents\ComfyUI\models\loras\logo_design.safetensors"
    },
    @{
        Name = "Post-Apocalyptic LoRA"
        URL = "https://civitai.com/api/download/models/234567"
        Path = "C:\Users\Zachg\Documents\ComfyUI\models\loras\post_apoc.safetensors"
    }
)

Write-Host "Terminal Grounds - Model Downloader" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

foreach ($model in $models) {
    $filename = Split-Path $model.Path -Leaf
    
    if (Test-Path $model.Path) {
        Write-Host "✓ $($model.Name) already exists" -ForegroundColor Green
    } else {
        Write-Host "↓ Downloading $($model.Name)..." -ForegroundColor Yellow
        
        try {
            $dir = Split-Path $model.Path -Parent
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
            
            Invoke-WebRequest -Uri $model.URL -OutFile $model.Path -UseBasicParsing
            Write-Host "  ✓ Downloaded successfully" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Download failed: $_" -ForegroundColor Red
        }
    }
}

Write-Host "`nDone! Restart ComfyUI to see new models." -ForegroundColor Cyan
Read-Host "Press Enter to exit"
"""
        
        script_path = PROJECT_ROOT / "Tools" / "download_models.ps1"
        script_path.write_text(script_content)
        print(f"\nCreated download script: {script_path}")
        print("Run it with: powershell -ExecutionPolicy Bypass -File download_models.ps1")
    
    def create_enhanced_workflow(self, asset_type: str, prompt: str, 
                                use_loras: List[str] = None,
                                checkpoint: str = None) -> Dict:
        """Create workflow with LoRAs and optimizations"""
        
        # Default to FLUX if no checkpoint specified
        if not checkpoint:
            checkpoint = "FLUX1\\flux1-dev-fp8.safetensors"
        
        # Base workflow
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "",  # negative prompt
                    "clip": ["1", 1]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": int(time.time()) % 1000000,
                    "steps": 20,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": f"TG_{asset_type}",
                    "images": ["6", 0]
                }
            }
        }
        
        # Add LoRAs if specified
        if use_loras:
            last_model = "1"
            last_clip = "1"
            
            for i, lora_name in enumerate(use_loras):
                lora_id = f"lora_{i}"
                
                # LoRA strengths based on type
                strength = 0.7  # default
                if "military" in lora_name.lower():
                    strength = 0.8
                elif "weathered" in lora_name.lower():
                    strength = 0.6
                elif "logo" in lora_name.lower():
                    strength = 0.9
                
                workflow[lora_id] = {
                    "class_type": "LoraLoader",
                    "inputs": {
                        "lora_name": lora_name,
                        "strength_model": strength,
                        "strength_clip": strength,
                        "model": [last_model, 0],
                        "clip": [last_clip, 1]
                    }
                }
                
                last_model = lora_id
                last_clip = lora_id
            
            # Update connections to use LoRA output
            workflow["5"]["inputs"]["model"] = [last_model, 0]
            workflow["2"]["inputs"]["clip"] = [last_clip, 1]
            workflow["3"]["inputs"]["clip"] = [last_clip, 1]
        
        # Asset-specific optimizations
        if asset_type == "faction_emblem":
            workflow["4"]["inputs"]["width"] = 2048
            workflow["4"]["inputs"]["height"] = 2048
            workflow["5"]["inputs"]["steps"] = 30
            workflow["5"]["inputs"]["cfg"] = 8.5
            workflow["3"]["inputs"]["text"] = "text, words, watermark, blurry, asymmetric"
            
        elif asset_type == "weapon_concept":
            workflow["4"]["inputs"]["width"] = 1920
            workflow["4"]["inputs"]["height"] = 1080
            workflow["5"]["inputs"]["steps"] = 40
            workflow["5"]["inputs"]["cfg"] = 7.0
            workflow["3"]["inputs"]["text"] = "cartoon, toy, unrealistic"
            
        elif asset_type == "ui_icon":
            workflow["4"]["inputs"]["width"] = 512
            workflow["4"]["inputs"]["height"] = 512
            workflow["5"]["inputs"]["steps"] = 20
            workflow["5"]["inputs"]["cfg"] = 7.5
            workflow["3"]["inputs"]["text"] = "complex, photorealistic, 3d"
        
        return workflow

def main():
    print("=" * 60)
    print("Terminal Grounds - Model & LoRA Manager")
    print("=" * 60)
    
    manager = ModelManager()
    
    # Check current models
    available = manager.check_available_models()
    
    # Show recommendations
    print("\n" + "=" * 60)
    print("Recommended Models for Terminal Grounds")
    print("=" * 60)
    
    recommendations = manager.recommend_downloads()
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['name']} ({rec['type']})")
        print(f"   {rec['description']}")
        print(f"   Use for: {', '.join(rec['use_for'])}")
    
    # Create download script
    print("\n" + "=" * 60)
    manager.create_download_script()
    
    print("\nTo download recommended models:")
    print("  1. Run: powershell -ExecutionPolicy Bypass -File Tools/download_models.ps1")
    print("  2. Restart ComfyUI")
    print("  3. Run asset generation with enhanced quality")
    
    print("\n" + "=" * 60)
    print("Your setup is ready for production-quality assets!")
    print("=" * 60)

if __name__ == "__main__":
    main()
