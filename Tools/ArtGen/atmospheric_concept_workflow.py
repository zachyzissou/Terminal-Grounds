#!/usr/bin/env python3
"""
Terminal Grounds - Atmospheric Concept Art Generator
==================================================
Based on successful generation parameters:
- Model: FLUX1/flux1-dev-fp8.safetensors
- Seed: 94887 (and variations)
- Resolution: 3840x2160
- Simple but effective prompts focused on atmosphere
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from comfyui_api_client import ComfyUIAPIClient, STAGING_ROOT

def create_atmospheric_concept_workflow(
    prompt: str,
    seed: int = 94887,
    width: int = 3840,
    height: int = 2160,
    steps: int = 30,
    cfg: float = 4.0,
    sampler_name: str = "euler",
    scheduler: str = "normal",
    filename_prefix: str = "PROD_CONCEPT_ART",
    negative_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Create workflow for atmospheric concept art generation"""

    # Resolve checkpoint name with optional env override
    ckpt_name = os.getenv("TG_CKPT", "FLUX1\\flux1-dev-fp8.safetensors")

    # Treat incoming prompt as authoritative content; just append quality descriptors
    full_prompt = f"{prompt}, concept art, detailed illustration, professional game art, high detail, cinematic lighting, atmospheric"

    negative = negative_text or "low quality, amateur, poor composition, bad lighting, text, watermark"

    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": ckpt_name}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": full_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1}
        },
    "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
        "sampler_name": sampler_name,
        "scheduler": scheduler,
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
        "filename_prefix": filename_prefix
            }
        }
    }

def generate_terminal_grounds_concepts():
    """Generate atmospheric concept art for various Terminal Grounds locations"""

    client = ComfyUIAPIClient()

    if not client.check_server():
        print("ComfyUI server not running. Please start ComfyUI first.")
        return

    # Concept prompts that should work well with the proven formula
    concepts = [
        {
            "name": "Metro_Maintenance_Corridor",
            "prompt": "underground metro corridor, industrial lighting, wet concrete, atmospheric depth",
            "seed": 94887
        },
        {
            "name": "IEZ_Facility_Interior",
            "prompt": "abandoned industrial facility, emergency lighting, hazard stripes, noir atmosphere",
            "seed": 94888
        },
        {
            "name": "Black_Vault_Entrance",
            "prompt": "mysterious vault entrance, eerie lighting, ancient technology, foreboding atmosphere",
            "seed": 94889
        },
        {
            "name": "Tech_Wastes_Corridor",
            "prompt": "maintenance tunnel, flickering lights, pipes and cables, post-industrial decay",
            "seed": 94890
        },
        {
            "name": "Crimson_Docks_Interior",
            "prompt": "industrial warehouse, red emergency lighting, cargo containers, atmospheric fog",
            "seed": 94891
        }
    ]

    print("Generating Terminal Grounds Atmospheric Concepts")
    print("=" * 50)

    for concept in concepts:
        print(f"Generating: {concept['name']}...")

        # Create workflow
        workflow = create_atmospheric_concept_workflow(
            prompt=concept['prompt'],
            seed=concept['seed']
        )

        # Queue generation
        prompt_id = client.queue_prompt(workflow)

        if not prompt_id:
            print(f"  [FAILED] Could not queue {concept['name']}")
            continue

        print(f"  [QUEUED] ID: {prompt_id}")

        # Wait for completion
        images = client.wait_for_completion(prompt_id, timeout=120)

        if images:
            # Copy to staging for analysis
            for img_filename in images:
                client.copy_to_staging(img_filename)

            print(f"  [SUCCESS] Generated: {len(images)} images")
        else:
            print("  [FAILED] Generation failed or timed out")

        print()

def generate_seed_variations(base_prompt: str, base_seed: int = 94887, count: int = 5):
    """Generate variations of a successful prompt with different seeds"""

    client = ComfyUIAPIClient()

    if not client.check_server():
        print("ComfyUI server not running. Please start ComfyUI first.")
        return

    print(f"Generating {count} seed variations of: {base_prompt}")
    print("-" * 50)

    for i in range(count):
        seed = base_seed + i
        print(f"Variation {i+1}/5 (seed {seed})...")

        workflow = create_atmospheric_concept_workflow(
            prompt=base_prompt,
            seed=seed
        )

        prompt_id = client.queue_prompt(workflow)

        if prompt_id:
            images = client.wait_for_completion(prompt_id, timeout=120)
            if images:
                for img_filename in images:
                    client.copy_to_staging(img_filename)
                print("  ✓ Generated")
            else:
                print("  ✗ Failed")
        else:
            print("  ✗ Queue failed")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate atmospheric Terminal Grounds concept art")
    parser.add_argument("--concepts", action="store_true", default=True,
                       help="Generate preset concept locations")
    parser.add_argument("--variations", type=str,
                       help="Generate seed variations of a custom prompt")
    parser.add_argument("--count", type=int, default=5,
                       help="Number of variations to generate")

    args = parser.parse_args()

    if args.variations:
        generate_seed_variations(args.variations, count=args.count)
    elif args.concepts:
        generate_terminal_grounds_concepts()
