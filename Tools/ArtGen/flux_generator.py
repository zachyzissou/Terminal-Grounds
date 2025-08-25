#!/usr/bin/env python3
"""
Terminal Grounds - FLUX Asset Generator
========================================
Optimized for FLUX 1 Dev model (better quality than SDXL!)
"""

import json
import urllib.request
import time
from pathlib import Path
from typing import Dict, Any, List

# Configuration
COMFYUI_SERVER = "127.0.0.1:8000"
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")

class FluxGenerator:
    """FLUX-optimized asset generator for Terminal Grounds"""
    
    def __init__(self):
        self.server = COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        
    def check_server(self) -> bool:
        """Verify ComfyUI is running"""
        try:
            with urllib.request.urlopen(f"{self.base_url}/system_stats") as response:
                return response.status == 200
        except:
            return False
    
    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue workflow for generation"""
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                return result.get('prompt_id', '')
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def wait_for_image(self, prompt_id: str, timeout: int = 60) -> List[str]:
        """Wait for generation to complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                url = f"{self.base_url}/history/{prompt_id}"
                with urllib.request.urlopen(url) as response:
                    history = json.loads(response.read())
                    
                if prompt_id in history:
                    outputs = history[prompt_id].get('outputs', {})
                    for node_output in outputs.values():
                        if 'images' in node_output:
                            return [img['filename'] for img in node_output['images']]
            except:
                pass
            
            time.sleep(1)
        
        return []
    
    def download_image(self, filename: str) -> bytes:
        """Download generated image"""
        url = f"{self.base_url}/view?filename={filename}"
        try:
            with urllib.request.urlopen(url) as response:
                return response.read()
        except:
            return b""
    
    def create_flux_workflow(self, prompt: str, width: int = 1024, height: int = 1024) -> Dict:
        """Create FLUX-specific workflow"""
        
        # FLUX workflow structure
        workflow = {
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["11", 0]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["10", 0]
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "TG_Asset",
                    "images": ["8", 0]
                }
            },
            "10": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": "ae.safetensors"
                }
            },
            "11": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp16.safetensors",
                    "type": "flux"
                }
            },
            "12": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "FLUX1\\flux1-dev-fp8.safetensors",
                    "weight_dtype": "fp8_e4m3fn"
                }
            },
            "13": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["12", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "",
                    "clip": ["11", 0]
                }
            }
        }
        
        return workflow
    
    def generate_faction_emblem(self, name: str, description: str) -> Path:
        """Generate a single faction emblem"""
        
        prompt = f"{description}, military faction emblem, game asset, iconic symbol, high quality, centered composition, professional design"
        
        print(f"Generating {name}...", end=" ")
        
        # Create workflow
        workflow = self.create_flux_workflow(prompt, 2048, 2048)
        workflow["9"]["inputs"]["filename_prefix"] = f"TG_Emblem_{name}"
        
        # Queue generation
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            print("FAILED (queue error)")
            return None
        
        # Wait for completion
        images = self.wait_for_image(prompt_id, timeout=90)
        if not images:
            print("FAILED (timeout)")
            return None
        
        # Download and save
        image_data = self.download_image(images[0])
        if not image_data:
            print("FAILED (download error)")
            return None
        
        # Save to project
        output_dir = PROJECT_ROOT / "Content" / "TG" / "Decals" / "Factions"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{name}_2K.png"
        output_path.write_bytes(image_data)
        
        print(f"OK -> {output_path.name}")
        return output_path

def main():
    print("=" * 60)
    print("Terminal Grounds - FLUX Asset Generator")
    print("=" * 60)
    
    generator = FluxGenerator()
    
    # Check server
    print("\nChecking ComfyUI server...", end=" ")
    if not generator.check_server():
        print("NOT RUNNING!")
        print("Server should be at: http://127.0.0.1:8000")
        return 1
    print("OK")
    
    # Generate faction emblems
    print("\nGenerating Faction Emblems with FLUX")
    print("-" * 40)
    
    factions = [
        ("Directorate", "military chevron insignia, steel gray and blue, authoritative geometric design"),
        ("IronScavengers", "asymmetrical scrap-metal claw grasping mixed faction symbols, scavenger orange on gunmetal field with trophy gold, theft markers and salvage aesthetic"),
        ("Free77", "stenciled number 77, tactical brown and tan, mercenary contractor badge"),
        ("CorporateHegemony", "interlocked hexagonal corporate shields with holographic enhancement, corporate blue field with hologram cyan highlights, branding warfare aesthetic"),
        ("NomadClans", "hand-painted convoy culture symbol with adaptive camouflage elements, sun-bleached orange and weathered leather brown, mobile survival aesthetic"),
        ("ArchiveKeepers", "geometric data preservation patterns with glowing text elements, ancient purple and data gold, information archaeology aesthetic"),
        ("CivicWardens", "community-made urban militia stencil, safety green and warden teal, grassroots protection aesthetic")
    ]
    
    generated = []
    for name, description in factions:
        path = generator.generate_faction_emblem(name, description)
        if path:
            generated.append(path)
    
    print("\n" + "=" * 60)
    print(f"Generated {len(generated)}/{len(factions)} faction emblems")
    
    if generated:
        print("\nFiles saved to:")
        print("  Content/TG/Decals/Factions/")
        print("\nNext steps:")
        print("  1. Review generated emblems")
        print("  2. Import to UE5: python Tools/ArtGen/ue5_import_ui_icons.py")
        print("  3. Update manifest: python Tools/build_asset_manifest.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
