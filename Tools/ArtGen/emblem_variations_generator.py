#!/usr/bin/env python3
"""
Generate 3 variations of each faction emblem for website showcase
Uses proven parameters with different seed bases for variety
"""

import json
import urllib.request
import time
import uuid

# Proven parameters for 100% success rate
PROVEN_PARAMS = {
    "sampler": "heun", 
    "scheduler": "normal",
    "cfg": 3.2,
    "steps": 25,
    "width": 1024,
    "height": 1024
}

# Three different seed bases for variation
SEED_BASES = [94887, 95555, 96333]  # Proven base plus variations

def create_emblem_workflow(faction_name, description, seed):
    """Create emblem workflow with specific seed"""
    
    positive_prompt = f"masterpiece quality {description}, Terminal Grounds faction emblem, military insignia, professional game asset, iconic symbol design, institutional graphic design, centered composition, clean background, high contrast detail, sharp crisp edges, balanced composition, official faction military identity, corporate quality standards, recognizable silhouette, faction authority symbol, clean typography if text present, readable lettering, military stencil precision"
    
    negative_prompt = "blurry, low quality, pixelated, distorted, bad anatomy, bad lighting, oversaturated, undersaturated, generic, sterile, empty, lifeless, bland, boring, repetitive, copy-paste, artificial, fake, plastic, watermark, signature, modern cars, contemporary clothing, smartphones, modern technology, fantasy elements, magic, supernatural, cartoon, anime, illustration, abstract, gradient, overexposed, blown highlights, soft edges, unclear details, amateur design, low resolution, gibberish text, scrambled letters, unreadable text, corrupted characters, malformed letters, text artifacts"
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": PROVEN_PARAMS["width"], "height": PROVEN_PARAMS["height"], "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": PROVEN_PARAMS["steps"],
                "cfg": PROVEN_PARAMS["cfg"],
                "sampler_name": PROVEN_PARAMS["sampler"],
                "scheduler": PROVEN_PARAMS["scheduler"],
                "denoise": 1.0,
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
            "inputs": {"images": ["6", 0], "filename_prefix": f"TG_Emblem_Var_{faction_name}"}
        }
    }
    
    return workflow

def submit_workflow(workflow):
    """Submit workflow to ComfyUI"""
    client_id = str(uuid.uuid4())
    prompt_data = {"prompt": workflow, "client_id": client_id}
    
    data = json.dumps(prompt_data).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:8188/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get('prompt_id')
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 60)
    print("FACTION EMBLEM VARIATIONS GENERATOR")
    print("=" * 60)
    print("Generating 3 variations of each faction emblem")
    print("Using proven parameters: heun/normal/CFG 3.2/25 steps")
    print()
    
    # Complete faction set with enhanced descriptions
    factions = [
        ("Directorate", "military chevron insignia in angular shield formation, navy blue and gunmetal gray with crisp white accents, authoritative geometric design"),
        ("IronScavengers", "asymmetrical scrap-metal claw grasping mixed faction symbols as victory trophies, scavenger orange paint over gunmetal field"),
        ("Free77", "professional stenciled number 77 with crossed rifles beneath, desert tan and olive drab with contractor black accents"),
        ("CorporateHegemony", "interlocked hexagonal corporate shields with holographic enhancement, corporate blue field with hologram cyan highlights"),
        ("NomadClans", "hand-painted convoy culture wheel with adaptive camouflage elements, sun-bleached orange and weathered leather brown"),
        ("ArchiveKeepers", "geometric data preservation patterns with glowing text elements, ancient purple and data gold with crystalline tech patterns"),
        ("CivicWardens", "community-made urban militia stencil with mesh barrier elements, safety green and warden teal with community protection markers")
    ]
    
    total_queued = 0
    
    for variation in range(3):
        print(f"\n--- VARIATION {variation + 1} ---")
        seed_base = SEED_BASES[variation]
        
        for i, (name, description) in enumerate(factions):
            seed = seed_base + (i * 100)  # Spread seeds for variety
            print(f"Queuing {name} (var {variation + 1}, seed {seed})...", end=" ")
            
            workflow = create_emblem_workflow(name, description, seed)
            prompt_id = submit_workflow(workflow)
            
            if prompt_id:
                print(f"OK - {prompt_id}")
                total_queued += 1
            else:
                print("FAILED")
            
            time.sleep(0.5)  # Brief pause
    
    print()
    print("=" * 60)
    print(f"COMPLETE: {total_queued}/21 emblem variations queued")
    print("Expected files: TG_Emblem_Var_[FactionName]_*.png")
    print("Output: C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API\\output\\")

if __name__ == "__main__":
    main()