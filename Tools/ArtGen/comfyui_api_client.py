#!/usr/bin/env python3
"""
Terminal Grounds - ComfyUI API Client
======================================
Reliable asset generation without desktop automation.
This replaces the clunky mouse/keyboard control approach.

Usage:
    python comfyui_api_client.py --type emblems
    python comfyui_api_client.py --type icons
    python comfyui_api_client.py --all
"""

import json
import urllib.request
import urllib.error
import time
import argparse
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configuration
# Auto-detect ComfyUI server:
# 1) COMFYUI_SERVER env var if set (e.g., 127.0.0.1:8188)
# 2) Probe 127.0.0.1:8000 then 127.0.0.1:8188
# 3) Fallback to 127.0.0.1:8188

def _probe_server(hostport: str) -> bool:
    try:
        with urllib.request.urlopen(f"http://{hostport}/system_stats", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def _detect_server() -> str:
    env = os.getenv("COMFYUI_SERVER")
    if env:
        return env
    for hp in ("127.0.0.1:8000", "127.0.0.1:8188"):
        if _probe_server(hp):
            return hp
    return "127.0.0.1:8188"

COMFYUI_SERVER = _detect_server()
PROJECT_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds")
COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
STAGING_ROOT = PROJECT_ROOT / "Style_Staging"

class ComfyUIAPIClient:
    """Simple, reliable API client for ComfyUI"""

    def __init__(self, server: Optional[str] = None):
        self.server = server or COMFYUI_SERVER
        self.base_url = f"http://{self.server}"
        # Set up staging folder for automatic copying
        self.staging_folder = STAGING_ROOT / "_Recent_Generations"
        self.staging_folder.mkdir(parents=True, exist_ok=True)

    def check_server(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/system_stats")
            return response.status == 200
        except:
            return False

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue a workflow and return prompt ID"""
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
            print(f"Error queueing prompt: {e}")
            return ""

    def get_image(self, filename: str) -> bytes:
        """Download generated image"""
        url = f"{self.base_url}/view?filename={filename}"
        try:
            with urllib.request.urlopen(url) as response:
                return response.read()
        except Exception as e:
            print(f"Error downloading image: {e}")
            return b""

    def copy_to_staging(self, filename: str):
        """Copy ComfyUI output to staging folder for analysis"""
        try:
            source_path = COMFYUI_OUTPUT / filename
            if source_path.exists():
                # Create timestamped copy
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_name = f"{timestamp}_{filename}"
                dest_path = self.staging_folder / dest_name

                shutil.copy2(source_path, dest_path)

                # Also keep original name for easy access
                latest_path = self.staging_folder / filename
                shutil.copy2(source_path, latest_path)

                print(f"✓ Copied to staging: {filename}")
                return True
        except Exception as e:
            print(f"✗ Failed to copy {filename} to staging: {e}")
        return False

    def wait_for_completion(self, prompt_id: str, timeout: int = 60) -> List[str]:
        """Wait for generation to complete"""
        start = time.time()

        while time.time() - start < timeout:
            try:
                url = f"{self.base_url}/history/{prompt_id}"
                with urllib.request.urlopen(url) as response:
                    history = json.loads(response.read())

                if prompt_id in history:
                    outputs = history[prompt_id].get('outputs', {})
                    images = []

                    for node_output in outputs.values():
                        if 'images' in node_output:
                            for img in node_output['images']:
                                images.append(img['filename'])

                    if images:
                        return images

            except Exception as e:
                print(f"Error checking status: {e}")

            time.sleep(1)

        return []

def create_emblem_workflow(faction_name: str, description: str) -> Dict[str, Any]:
    """Create workflow for faction emblem generation"""

    prompt = f"{description}, military faction emblem, game asset, iconic symbol, high contrast, centered"
    negative = "text, words, watermark, low quality, blurry"

    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 2048, "height": 2048, "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": abs(hash(faction_name)) % 1000000,
                "steps": 25,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": f"TG_Emblem_{faction_name}"
            }
        }
    }

def generate_faction_emblems(client: ComfyUIAPIClient):
    """Generate all faction emblems"""

    factions = [
        ("Directorate", "military chevron, steel gray and blue, authoritative"),
        ("VulturesUnion", "scavenger bird, black and yellow, industrial"),
        ("Free77", "mercenary 77 stencil, tactical brown, practical"),
        ("CorporateCombine", "hexagonal shield, blue and silver, high-tech"),
        ("NomadClans", "tribal banner with wheel, orange and brown, weathered"),
        ("VaultedArchivists", "mystical eye with coil, gold and green, ancient"),
        ("CivicWardens", "fortress block, orange and navy, defensive")
    ]

    output_dir = PROJECT_ROOT / "Content" / "TG" / "Decals" / "Factions"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nGenerating Faction Emblems")
    print("-" * 40)

    for name, description in factions:
        print(f"  Generating: {name}...", end=" ")

        # Create and queue workflow
        workflow = create_emblem_workflow(name, description)
        prompt_id = client.queue_prompt(workflow)

        if not prompt_id:
            print("FAILED (couldn't queue)")
            continue

        # Wait for completion
        images = client.wait_for_completion(prompt_id)

        if images:
            # Download and save first image
            image_data = client.get_image(images[0])
            if image_data:
                output_path = output_dir / f"{name}_2K.png"
                output_path.write_bytes(image_data)
                print(f"OK -> {output_path.name}")
            else:
                print("FAILED (download error)")
        else:
            print("FAILED (generation timeout)")

def main():
    parser = argparse.ArgumentParser(description="Terminal Grounds Asset Generator")
    parser.add_argument("--type", choices=["emblems", "icons", "posters"],
                       help="Asset type to generate")
    parser.add_argument("--all", action="store_true",
                       help="Generate all asset types")
    args = parser.parse_args()

    # Initialize client
    client = ComfyUIAPIClient()

    # Check server
    print("Checking ComfyUI server...", end=" ")
    if not client.check_server():
        print("NOT RUNNING!")
        print("\nPlease start ComfyUI in API mode:")
        print("  Run: C:\\ComfyUI\\run_comfyui_api.bat")
        return 1
    print("OK")

    # Generate based on arguments
    if args.all or args.type == "emblems":
        generate_faction_emblems(client)

    if args.all or args.type == "icons":
        print("\nUI Icons generation not yet implemented")
        # TODO: Add icon generation

    if args.all or args.type == "posters":
        print("\nPropaganda Posters generation not yet implemented")
        # TODO: Add poster generation

    print("\n" + "=" * 40)
    print("Generation complete!")
    print("Check: Content/TG/Decals/Factions/")

    return 0

if __name__ == "__main__":
    exit(main())
