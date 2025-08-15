#!/usr/bin/env python3
"""
Terminal Grounds - Style Baseline Explorer
===========================================
Generates style comparison grids to establish the perfect aesthetic.
Creates organized staging folders with different style combinations.
"""

import json
import urllib.request
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configuration
COMFYUI_SERVER = "127.0.0.1:8000"
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")
STAGING_BASE = PROJECT_ROOT / "Style_Staging"

# Style Presets - Different aesthetic approaches for Terminal Grounds
STYLE_PRESETS = {
    "Gritty_Realism": {
        "name": "Gritty Realism",
        "description": "Photorealistic military with heavy weathering",
        "loras": [
            ("battlefield 2042 style.safetensors", 0.8),
            ("Detailed Skin&Textures Flux V3.safetensors", 0.6),
            ("Reactive armour style.safetensors", 0.7),
            ("war_t.safetensors", 0.5)
        ],
        "prompt_style": "photorealistic, gritty, weathered, battle-worn, realistic military",
        "cfg": 7.5,
        "steps": 35
    },
    
    "Stylized_Military": {
        "name": "Stylized Military",
        "description": "Semi-realistic with artistic flair",
        "loras": [
            ("Future_Warfare_SDXL.safetensors", 0.7),
            ("StylizedTexture_v2.safetensors", 0.6),
            ("military tactics combined arms formation.safetensors", 0.5)
        ],
        "prompt_style": "stylized military art, concept art style, semi-realistic, professional game art",
        "cfg": 8.0,
        "steps": 30
    },
    
    "Cyberpunk_Military": {
        "name": "Cyberpunk Military",
        "description": "High-tech neon-infused military aesthetic",
        "loras": [
            ("CyberPunk.safetensors", 0.7),
            ("Neon_Noir_FLUX.safetensors", 0.6),
            ("Future_Warfare_SDXL.safetensors", 0.5),
            ("scifi_buildings_sdxl_lora.safetensors", 0.4)
        ],
        "prompt_style": "cyberpunk military, neon accents, high-tech warfare, futuristic combat",
        "cfg": 8.5,
        "steps": 30
    },
    
    "Post_Apocalyptic": {
        "name": "Post-Apocalyptic",
        "description": "Wasteland survivor aesthetic",
        "loras": [
            ("Reactive armour style.safetensors", 0.8),
            ("war_t.safetensors", 0.7),
            ("Hand-Painted_2d_Seamless_Textures-000007.safetensors", 0.4)
        ],
        "prompt_style": "post-apocalyptic, makeshift armor, wasteland warrior, survival gear",
        "cfg": 7.0,
        "steps": 32
    },
    
    "Clean_SciFi": {
        "name": "Clean Sci-Fi",
        "description": "Pristine futuristic military",
        "loras": [
            ("SCIFI_Concept_Art_Landscapes.safetensors", 0.7),
            ("Sci-fi_env_flux.safetensors", 0.6),
            ("futuristic_interior_composer.safetensors", 0.5)
        ],
        "prompt_style": "clean sci-fi, pristine technology, advanced military, sleek futuristic",
        "cfg": 8.0,
        "steps": 28
    },
    
    "Painted_Concept": {
        "name": "Painted Concept Art",
        "description": "Hand-painted concept art style",
        "loras": [
            ("Hand-Painted_2d_Seamless_Textures-000007.safetensors", 0.7),
            ("ck-Sommo-Concept-Art-000015.safetensors", 0.6),
            ("StylizedTexture_v2.safetensors", 0.5)
        ],
        "prompt_style": "concept art, hand-painted, artistic rendering, painterly style",
        "cfg": 9.0,
        "steps": 25
    },
    
    "Hybrid_Tech": {
        "name": "Hybrid Human-Alien Tech",
        "description": "Mix of human military and alien technology",
        "loras": [
            ("Future_Warfare_SDXL.safetensors", 0.6),
            ("SCIFI_Concept_Art_Landscapes.safetensors", 0.6),
            ("Synthetic_Breed.safetensors", 0.5),
            ("Enhanced_Lighting_and_Textures_flux_lora.safetensors", 0.4)
        ],
        "prompt_style": "hybrid technology, human-alien fusion, advanced xenotech, exotic materials",
        "cfg": 8.5,
        "steps": 35
    },
    
    "Comic_Military": {
        "name": "Comic Book Military",
        "description": "Bold comic book/graphic novel style",
        "loras": [
            ("Graffiti_Logo_Style_Flux.safetensors", 0.6),
            ("Ink_poster-000004.safetensors", 0.7),
            ("battlefield 2042 style.safetensors", 0.4)
        ],
        "prompt_style": "comic book style, bold lines, graphic novel aesthetic, high contrast",
        "cfg": 9.5,
        "steps": 25
    },
    
    "Soviet_Retro": {
        "name": "Soviet Retrofuturism",
        "description": "Cold War era military aesthetic",
        "loras": [
            ("USSRART.safetensors", 0.8),
            ("soldart.safetensors", 0.6),
            ("military tactics combined arms formation.safetensors", 0.5)
        ],
        "prompt_style": "soviet military aesthetic, cold war era, brutalist design, propaganda style",
        "cfg": 8.0,
        "steps": 30
    },
    
    "Minimal_Tactical": {
        "name": "Minimal Tactical",
        "description": "Clean, minimalist military design",
        "loras": [
            ("HMSG-LOGO-XL-000001.safetensors", 0.7),
            ("ui_interface.safetensors", 0.6),
            ("Future_Warfare_SDXL.safetensors", 0.4)
        ],
        "prompt_style": "minimalist design, clean tactical, simple military iconography, modern warfare",
        "cfg": 7.0,
        "steps": 20
    }
}

# Test subjects for each style
TEST_SUBJECTS = {
    "faction_emblem": {
        "base_prompt": "military faction emblem, insignia, badge, symbol",
        "size": (1024, 1024)
    },
    "soldier_portrait": {
        "base_prompt": "military soldier portrait, combat gear, tactical equipment",
        "size": (1024, 1024)
    },
    "weapon_concept": {
        "base_prompt": "assault rifle weapon, military firearm, tactical weapon",
        "size": (1536, 1024)
    },
    "environment_scene": {
        "base_prompt": "military base, combat zone, warfare environment",
        "size": (1920, 1080)
    },
    "vehicle_design": {
        "base_prompt": "military vehicle, armored transport, combat vehicle",
        "size": (1536, 1024)
    }
}

class StyleBaselineExplorer:
    """Generates comparison grids for style exploration"""
    
    def __init__(self):
        self.server = COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M")
        self.results = {}
        
    def create_staging_structure(self):
        """Create organized folder structure for style exploration"""
        
        print("\nCreating staging folder structure...")
        
        # Main staging folder
        STAGING_BASE.mkdir(parents=True, exist_ok=True)
        
        # Create folders for each style preset
        for style_key, style_data in STYLE_PRESETS.items():
            style_folder = STAGING_BASE / style_key
            style_folder.mkdir(exist_ok=True)
            
            # Create subfolders for each test subject
            for subject_key in TEST_SUBJECTS.keys():
                subject_folder = style_folder / subject_key
                subject_folder.mkdir(exist_ok=True)
        
        # Create comparison folder
        comparison_folder = STAGING_BASE / "_Comparisons"
        comparison_folder.mkdir(exist_ok=True)
        
        # Create favorites folder
        favorites_folder = STAGING_BASE / "_Favorites"
        favorites_folder.mkdir(exist_ok=True)
        
        print(f"  Created staging structure at: {STAGING_BASE}")
        
    def create_workflow(self, prompt: str, style_preset: Dict, 
                       width: int = 1024, height: int = 1024,
                       seed: int = 42) -> Dict:
        """Create workflow with specific style preset"""
        
        # Build full prompt
        full_prompt = f"{prompt}, {style_preset['prompt_style']}, high quality, professional game asset"
        
        print(f"    Using {len(style_preset.get('loras', []))} LoRAs")
        print(f"    Steps: {style_preset.get('steps', 30)}, CFG: {style_preset.get('cfg', 8.0)}")
        
        # Base workflow for FLUX
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
            },
            "positive": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": full_prompt,
                    "clip": ["1", 1]
                }
            },
            "negative": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "low quality, amateur, placeholder, watermark",
                    "clip": ["1", 1]
                }
            },
            "latent": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            }
        }
        
        # Add LoRA chain
        last_model = "1"
        last_clip = "1"
        
        for i, (lora_name, strength) in enumerate(style_preset.get("loras", [])):
            lora_id = f"lora_{i}"
            
            workflow[lora_id] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": strength,
                    "strength_clip": strength * 0.8,
                    "model": [last_model, 0],
                    "clip": [last_clip, 1]
                }
            }
            
            last_model = lora_id
            last_clip = lora_id
        
        # Update CLIP connections
        workflow["positive"]["inputs"]["clip"] = [last_clip, 1]
        workflow["negative"]["inputs"]["clip"] = [last_clip, 1]
        
        # Sampler
        workflow["sampler"] = {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": style_preset.get("steps", 30),
                "cfg": style_preset.get("cfg", 8.0),
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": [last_model, 0],
                "positive": ["positive", 0],
                "negative": ["negative", 0],
                "latent_image": ["latent", 0]
            }
        }
        
        # Decode and save
        workflow["decode"] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["sampler", 0],
                "vae": ["1", 2]
            }
        }
        
        workflow["save"] = {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"TG_Style_{self.session_id}",
                "images": ["decode", 0]
            }
        }
        
        return workflow
    
    def queue_and_wait(self, workflow: Dict, timeout: int = 120) -> Optional[str]:
        """Queue workflow and wait for completion"""
        
        # Queue
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                prompt_id = result.get('prompt_id', '')
        except:
            return None
        
        if not prompt_id:
            return None
        
        # Wait for completion
        print("    Generating", end="")
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
                            print(" ✓")
                            return node_output['images'][0]['filename']
            except:
                pass
            
            print(".", end="", flush=True)
            time.sleep(2)
        
        print(" ✗")
        return None
    
    def download_and_save(self, filename: str, output_path: Path) -> bool:
        """Download generated image and save to staging folder"""
        
        # Method 1: Try downloading from ComfyUI API
        url = f"{self.base_url}/view?filename={filename}"
        
        try:
            with urllib.request.urlopen(url) as response:
                image_data = response.read()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_data)
            print(f"    Saved to: {output_path.relative_to(STAGING_BASE)}")
            return True
        except Exception as e:
            print(f"    API download failed: {e}")
            
            # Method 2: Try copying from ComfyUI output folder
            comfyui_output = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
            source_file = comfyui_output / filename
            
            if source_file.exists():
                import shutil
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, output_path)
                print(f"    Copied to: {output_path.relative_to(STAGING_BASE)}")
                return True
            else:
                print(f"    File not found in ComfyUI output: {filename}")
                
        return False
    
    def generate_style_test(self, style_key: str, subject_key: str, 
                           seed: int = 42) -> Optional[Path]:
        """Generate a single style test"""
        
        style_preset = STYLE_PRESETS[style_key]
        test_subject = TEST_SUBJECTS[subject_key]
        
        print(f"  {style_preset['name']} - {subject_key}")
        
        # Create workflow
        workflow = self.create_workflow(
            prompt=test_subject["base_prompt"],
            style_preset=style_preset,
            width=test_subject["size"][0],
            height=test_subject["size"][1],
            seed=seed
        )
        
        # Generate
        filename = self.queue_and_wait(workflow)
        if not filename:
            return None
        
        # Save to staging folder
        output_path = STAGING_BASE / style_key / subject_key / f"{style_key}_{subject_key}_{seed}.png"
        
        if self.download_and_save(filename, output_path):
            return output_path
        
        return None
    
    def generate_style_grid(self, subject_key: str, seed: int = 42):
        """Generate the same subject in all styles for comparison"""
        
        print(f"\nGenerating comparison grid for: {subject_key}")
        print("-" * 50)
        
        results = []
        
        for style_key in STYLE_PRESETS.keys():
            output_path = self.generate_style_test(style_key, subject_key, seed)
            if output_path:
                results.append((style_key, output_path))
        
        # Save results summary
        if results:
            summary_path = STAGING_BASE / "_Comparisons" / f"{subject_key}_comparison_{self.session_id}.txt"
            summary_path.parent.mkdir(exist_ok=True)
            
            with open(summary_path, 'w') as f:
                f.write(f"Style Comparison: {subject_key}\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"Seed: {seed}\n\n")
                
                for style_key, path in results:
                    f.write(f"{style_key}: {path.relative_to(STAGING_BASE)}\n")
            
            print(f"\n  Comparison saved to: {summary_path.name}")
        
        return results
    
    def generate_full_baseline(self):
        """Generate complete baseline with all styles and subjects"""
        
        print("\n" + "=" * 60)
        print("GENERATING COMPLETE STYLE BASELINE")
        print("=" * 60)
        
        total_combinations = len(STYLE_PRESETS) * len(TEST_SUBJECTS)
        print(f"This will generate {total_combinations} images")
        print(f"Estimated time: {total_combinations * 30 // 60} minutes")
        
        confirm = input("\nProceed? (y/n): ")
        if confirm.lower() != 'y':
            return
        
        # Use consistent seed for fair comparison
        seed = 42
        
        for subject_key in TEST_SUBJECTS.keys():
            self.generate_style_grid(subject_key, seed)
            time.sleep(2)  # Brief pause between subjects
        
        print("\n" + "=" * 60)
        print("BASELINE GENERATION COMPLETE!")
        print(f"Results saved to: {STAGING_BASE}")
        print("=" * 60)
    
    def create_style_report(self):
        """Create an HTML report for easy style comparison"""
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Terminal Grounds - Style Baseline Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #fff;
            padding: 20px;
        }
        h1 { color: #00ff88; text-align: center; }
        h2 { color: #0088ff; border-bottom: 2px solid #0088ff; padding-bottom: 10px; }
        .style-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .style-card {
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 15px;
        }
        .style-card h3 {
            color: #ffaa00;
            margin-top: 0;
        }
        .style-card img {
            width: 100%;
            border-radius: 4px;
        }
        .style-info {
            font-size: 12px;
            color: #888;
            margin-top: 10px;
        }
        .comparison-section {
            margin: 40px 0;
        }
    </style>
</head>
<body>
    <h1>Terminal Grounds - Style Baseline Report</h1>
    <p style="text-align: center;">Generated: {timestamp}</p>
"""
        
        # Add sections for each test subject
        for subject_key, subject_data in TEST_SUBJECTS.items():
            html_content += f"""
    <div class="comparison-section">
        <h2>{subject_key.replace('_', ' ').title()}</h2>
        <div class="style-grid">
"""
            
            # Add each style for this subject
            for style_key, style_data in STYLE_PRESETS.items():
                image_path = f"{style_key}/{subject_key}/{style_key}_{subject_key}_42.png"
                
                html_content += f"""
            <div class="style-card">
                <h3>{style_data['name']}</h3>
                <img src="{image_path}" alt="{style_data['name']}">
                <p>{style_data['description']}</p>
                <div class="style-info">
                    CFG: {style_data['cfg']} | Steps: {style_data['steps']}<br>
                    LoRAs: {len(style_data['loras'])} active
                </div>
            </div>
"""
            
            html_content += """
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # Save report
        report_path = STAGING_BASE / "style_baseline_report.html"
        report_path.write_text(html_content.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")))
        
        print(f"\nHTML report created: {report_path}")
        print("Open in browser to compare all styles side-by-side")

def main():
    while True:  # Main loop to keep program running
        print("\n" + "=" * 60)
        print("TERMINAL GROUNDS - STYLE BASELINE EXPLORER")
        print("=" * 60)
        print("\nThis tool will help you find the perfect visual style")
        print("by generating the same subjects in multiple styles.")
        
        explorer = StyleBaselineExplorer()
        
        # Create folder structure
        explorer.create_staging_structure()
        
        # Menu
        print("\n" + "=" * 60)
        print("BASELINE GENERATION OPTIONS")
        print("=" * 60)
        print("  1. Quick Test (1 style, 1 subject)")
        print("  2. Single Subject (all styles)")
        print("  3. Single Style (all subjects)")
        print("  4. Full Baseline (all combinations)")
        print("  5. Generate HTML Report")
        print("  6. Open Staging Folder")
        print("  7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            print("\nQuick Test - Generating Gritty Realism emblem...")
            result = explorer.generate_style_test("Gritty_Realism", "faction_emblem", seed=42)
            if result:
                print(f"\nGenerated: {result}")
            
        elif choice == "2":
            print("\nAvailable subjects:")
            for i, key in enumerate(TEST_SUBJECTS.keys(), 1):
                print(f"  {i}. {key}")
            
            try:
                subject_idx = int(input("Select subject (number): ")) - 1
                subject_key = list(TEST_SUBJECTS.keys())[subject_idx]
                explorer.generate_style_grid(subject_key, seed=42)
            except (ValueError, IndexError):
                print("Invalid selection")
            
        elif choice == "3":
            print("\nAvailable styles:")
            for i, key in enumerate(STYLE_PRESETS.keys(), 1):
                print(f"  {i}. {key} - {STYLE_PRESETS[key]['name']}")
            
            try:
                style_idx = int(input("Select style (number): ")) - 1
                style_key = list(STYLE_PRESETS.keys())[style_idx]
                
                print(f"\nGenerating all subjects in {STYLE_PRESETS[style_key]['name']} style...")
                for subject_key in TEST_SUBJECTS.keys():
                    explorer.generate_style_test(style_key, subject_key, seed=42)
            except (ValueError, IndexError):
                print("Invalid selection")
            
        elif choice == "4":
            explorer.generate_full_baseline()
            
        elif choice == "5":
            explorer.create_style_report()
            
        elif choice == "6":
            # Open staging folder in Windows Explorer
            import subprocess
            subprocess.Popen(f'explorer "{STAGING_BASE}"')
            print(f"\nOpened: {STAGING_BASE}")
            
        elif choice == "7":
            print("\nExiting...")
            break
        else:
            print("\nInvalid option")
        
        # Post-action menu
        if choice not in ["7"]:
            print("\n" + "=" * 60)
            print("GENERATION COMPLETE")
            print(f"Results saved to: {STAGING_BASE}")
            print("=" * 60)
            print("\nWhat would you like to do?")
            print("  1. Return to main menu")
            print("  2. Open staging folder")
            print("  3. Exit")
            
            post_choice = input("\nSelect option (1-3): ").strip()
            
            if post_choice == "1":
                continue  # Return to main menu
            elif post_choice == "2":
                import subprocess
                subprocess.Popen(f'explorer "{STAGING_BASE}"')
                print(f"\nOpened: {STAGING_BASE}")
                input("\nPress Enter to continue...")
            elif post_choice == "3":
                break
    
    print("\nThank you for using Style Baseline Explorer!")
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
