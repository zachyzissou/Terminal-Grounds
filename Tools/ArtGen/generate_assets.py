#!/usr/bin/env python3
"""
Terminal Grounds - Production Asset Generator
=============================================
Generates high-quality assets using your ComfyUI setup.
Optimized for FLUX and any additional models you have.
"""

import json
import urllib.request
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuration
COMFYUI_SERVER = "127.0.0.1:8000"
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")
OUTPUT_BASE = PROJECT_ROOT / "Content" / "TG"

# Terminal Grounds faction data
FACTIONS = {
    "Directorate": {
        "code": "DIR",
        "colors": "steel gray, tactical blue, gunmetal black",
        "style": "authoritarian military, geometric precision, brutalist",
        "emblem_prompt": "military chevron insignia with three stars, steel gray and tactical blue, authoritarian command emblem, sharp geometric design, metallic finish",
        "poster_prompt": "HOLD THE LINE propaganda poster, soldiers in formation, industrial military complex, stern commanding officer, directorate flag, wartime mobilization"
    },
    "VulturesUnion": {
        "code": "VLT", 
        "colors": "hazard yellow, oil black, rust orange",
        "style": "industrial salvage, makeshift, scavenger aesthetic",
        "emblem_prompt": "scavenger bird skull with crossed wrenches, hazard yellow stripes on black, salvage guild emblem, industrial decay, grunge texture",
        "poster_prompt": "SALVAGE FEEDS THE WAR poster, workers stripping destroyed mech, industrial salvage yard, sparks and welding, gritty workers"
    },
    "Free77": {
        "code": "F77",
        "colors": "tactical brown, khaki tan, olive drab", 
        "style": "mercenary contractor, practical military, worn equipment",
        "emblem_prompt": "stenciled number 77 with bullet holes, tactical brown and tan, mercenary badge, worn metal, practical minimalist design",
        "poster_prompt": "CONTRACT COMPLETE recruitment poster, battle-hardened mercenaries, payment in hand, professional soldiers for hire"
    },
    "CorporateCombine": {
        "code": "CCB",
        "colors": "corporate blue, chrome silver, sterile white",
        "style": "high-tech corporate, sleek futuristic, clean professional",
        "emblem_prompt": "hexagonal chrome shield with data streams, corporate blue accent, security corporation logo, holographic effect, pristine finish",
        "poster_prompt": "PUBLIC SAFETY IS OUR PRIORITY poster, corporate security forces, glass tower headquarters, surveillance drones, professional corporate aesthetic"
    },
    "NomadClans": {
        "code": "NMD",
        "colors": "rust red, leather brown, desert sand",
        "style": "convoy culture, road warrior, weathered vehicles",
        "emblem_prompt": "wheel hub with tribal patterns, rust and leather textures, convoy clan symbol, road warrior aesthetic, weathered metal",
        "poster_prompt": "THE CONVOY NEVER STOPS poster, vehicle column through wasteland, armed trucks and bikes, dust storm approaching, tribal banners"
    },
    "VaultedArchivists": {
        "code": "VAC",
        "colors": "deep purple, ancient gold, emerald green",
        "style": "techno-mysticism, occult technology, forbidden knowledge",
        "emblem_prompt": "mystical eye within circuit patterns, gold and purple, ancient technology sigil, arcane data streams, mysterious glow",
        "poster_prompt": "KNOWLEDGE IS POWER poster, hooded figure with alien artifact, purple energy, ancient vault entrance, techno-occult symbols"
    },
    "CivicWardens": {
        "code": "CWD",
        "colors": "safety orange, navy blue, concrete gray",
        "style": "community defense, neighborhood militia, makeshift fortification",
        "emblem_prompt": "fortress wall with crossed rifles, safety orange and navy, community defense badge, neighborhood watch symbol, protective shield",
        "poster_prompt": "DEFEND YOUR HOME poster, civilians building barricades, neighborhood militia, families protecting community, urban resistance"
    }
}

class TerminalGroundsGenerator:
    """Production-ready asset generator"""
    
    def __init__(self):
        self.server = COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.generated_count = 0
        
    def check_server(self) -> bool:
        """Verify ComfyUI is running"""
        try:
            with urllib.request.urlopen(f"{self.base_url}/system_stats", timeout=5) as response:
                return response.status == 200
        except:
            return False
    
    def queue_prompt(self, workflow: Dict) -> str:
        """Queue workflow for generation"""
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
                return result.get('prompt_id', '')
        except Exception as e:
            print(f"Queue error: {e}")
            return ""
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 120) -> List[str]:
        """Wait for generation with progress indicator"""
        start = time.time()
        
        sys.stdout.write("  Generating")
        sys.stdout.flush()
        
        while time.time() - start < timeout:
            try:
                url = f"{self.base_url}/history/{prompt_id}"
                with urllib.request.urlopen(url, timeout=10) as response:
                    history = json.loads(response.read())
                    
                if prompt_id in history:
                    outputs = history[prompt_id].get('outputs', {})
                    for node_output in outputs.values():
                        if 'images' in node_output:
                            sys.stdout.write(" Done!\n")
                            return [img['filename'] for img in node_output['images']]
            except:
                pass
            
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(2)
        
        sys.stdout.write(" Timeout!\n")
        return []
    
    def download_image(self, filename: str) -> bytes:
        """Download generated image"""
        url = f"{self.base_url}/view?filename={filename}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()
        except:
            return b""
    
    def create_workflow(self, prompt: str, width: int = 1024, height: int = 1024,
                       steps: int = 20, cfg: float = 7.5, seed: int = -1) -> Dict:
        """Create optimized workflow for current asset"""
        
        if seed < 0:
            seed = int(time.time() * 1000) % 1000000
        
        # FLUX-optimized workflow
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": f"{prompt}, high quality, professional game asset, detailed",
                    "clip": ["1", 1]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "low quality, blurry, amateur, placeholder",
                    "clip": ["1", 1]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
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
                    "filename_prefix": f"TG_{self.session_id}",
                    "images": ["6", 0]
                }
            }
        }
        
        return workflow
    
    def generate_asset(self, name: str, asset_type: str, prompt: str,
                      width: int = 1024, height: int = 1024) -> Optional[Path]:
        """Generate a single asset"""
        
        print(f"\n{name} ({asset_type})")
        
        # Asset-specific settings
        if asset_type == "emblem":
            width, height = 2048, 2048
            steps, cfg = 30, 8.5
        elif asset_type == "poster":
            width, height = 1024, 1536
            steps, cfg = 35, 9.0
        elif asset_type == "icon":
            width, height = 512, 512
            steps, cfg = 20, 7.0
        else:
            steps, cfg = 25, 7.5
        
        # Create workflow
        workflow = self.create_workflow(prompt, width, height, steps, cfg)
        
        # Queue generation
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            print("  ✗ Failed to queue")
            return None
        
        # Wait for completion
        images = self.wait_for_completion(prompt_id)
        if not images:
            print("  ✗ Generation failed")
            return None
        
        # Download and save
        image_data = self.download_image(images[0])
        if not image_data:
            print("  ✗ Download failed")
            return None
        
        # Determine output path
        if asset_type == "emblem":
            output_dir = OUTPUT_BASE / "Decals" / "Factions"
            filename = f"{name}_emblem_2K.png"
        elif asset_type == "poster":
            output_dir = OUTPUT_BASE / "Posters" / "Factions"
            filename = f"{name}_poster.png"
        elif asset_type == "icon":
            output_dir = OUTPUT_BASE / "UI" / "Icons"
            filename = f"{name}_icon.png"
        else:
            output_dir = OUTPUT_BASE / "Generated"
            filename = f"{name}_{asset_type}.png"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        output_path.write_bytes(image_data)
        
        self.generated_count += 1
        print(f"  ✓ Saved: {output_path.relative_to(PROJECT_ROOT)}")
        
        return output_path
    
    def generate_all_factions(self):
        """Generate complete asset set for all factions"""
        
        print("\n" + "=" * 60)
        print("GENERATING ALL FACTION ASSETS")
        print("=" * 60)
        
        for faction_name, faction_data in FACTIONS.items():
            print(f"\n{faction_name} ({faction_data['code']})")
            print(f"  Colors: {faction_data['colors']}")
            print(f"  Style: {faction_data['style']}")
            
            # Generate emblem
            self.generate_asset(
                name=faction_name,
                asset_type="emblem",
                prompt=faction_data['emblem_prompt']
            )
            
            # Generate poster
            self.generate_asset(
                name=faction_name,
                asset_type="poster",
                prompt=faction_data['poster_prompt']
            )
            
            # Small delay between factions
            time.sleep(2)
    
    def generate_ui_icons(self):
        """Generate UI icon set"""
        
        icons = [
            ("extraction_point", "military extraction point marker, green upward arrow, tactical HUD icon"),
            ("hostile_contact", "enemy contact warning, red crosshair target, combat alert icon"),
            ("objective_marker", "mission objective waypoint, yellow diamond marker, tactical navigation"),
            ("ammo_resupply", "ammunition crate icon, blue bullets, supply drop marker"),
            ("medical_station", "medical cross symbol, white health icon, emergency aid station"),
            ("vehicle_ready", "armored vehicle silhouette, orange highlight, transport available"),
            ("vault_detected", "alien vault entrance, purple geometric portal, mysterious energy"),
            ("faction_neutral", "neutral faction indicator, gray shield, non-hostile marker"),
            ("hazard_zone", "environmental hazard warning, yellow triangle, danger area"),
            ("intel_pickup", "data pad icon, blue information symbol, intelligence item")
        ]
        
        print("\n" + "=" * 60)
        print("GENERATING UI ICONS")
        print("=" * 60)
        
        for name, prompt in icons:
            full_prompt = f"{prompt}, clean UI icon design, high contrast, simple shapes, game HUD element"
            self.generate_asset(name, "icon", full_prompt)

def main():
    print("=" * 60)
    print("TERMINAL GROUNDS - Production Asset Generator")
    print("=" * 60)
    print(f"Server: http://{COMFYUI_SERVER}")
    print(f"Output: {OUTPUT_BASE}")
    
    generator = TerminalGroundsGenerator()
    
    # Check server
    print("\nChecking ComfyUI...", end=" ")
    if not generator.check_server():
        print("NOT RUNNING!")
        print(f"\nPlease ensure ComfyUI is running on {COMFYUI_SERVER}")
        return 1
    print("OK")
    
    # Menu
    print("\n" + "=" * 60)
    print("ASSET GENERATION MENU")
    print("=" * 60)
    print("  1. Generate ALL faction assets (emblems + posters)")
    print("  2. Generate faction emblems only")
    print("  3. Generate faction posters only")
    print("  4. Generate UI icons")
    print("  5. Generate single test asset")
    print("  6. Exit")
    print("=" * 60)
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == "1":
        generator.generate_all_factions()
    
    elif choice == "2":
        print("\nGenerating faction emblems...")
        for faction_name, faction_data in FACTIONS.items():
            generator.generate_asset(
                faction_name, "emblem", 
                faction_data['emblem_prompt']
            )
    
    elif choice == "3":
        print("\nGenerating faction posters...")
        for faction_name, faction_data in FACTIONS.items():
            generator.generate_asset(
                faction_name, "poster",
                faction_data['poster_prompt']
            )
    
    elif choice == "4":
        generator.generate_ui_icons()
    
    elif choice == "5":
        print("\nGenerating test asset...")
        generator.generate_asset(
            "test_directorate",
            "emblem",
            "military chevron emblem, steel gray and blue, high quality test"
        )
    
    elif choice == "6":
        print("\nExiting...")
        return 0
    
    else:
        print("\nInvalid option")
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"GENERATION COMPLETE")
    print(f"Total assets generated: {generator.generated_count}")
    print(f"Session ID: {generator.session_id}")
    print("=" * 60)
    
    if generator.generated_count > 0:
        print("\nNext steps:")
        print("  1. Review generated assets in Content/TG/")
        print("  2. Import to UE5: python Tools/ArtGen/ue5_import_ui_icons.py")
        print("  3. Update manifest: python Tools/build_asset_manifest.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
