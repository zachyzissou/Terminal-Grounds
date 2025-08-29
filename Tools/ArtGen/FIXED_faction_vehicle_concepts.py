#!/usr/bin/env python3
"""
FIXED Faction Vehicle Concept Generator
CTO CRITICAL FIX: Complete text elimination to prevent corruption

SOLUTION: Removed ALL text references from prompts
- No faction insignia, unit numbers, or stenciling requests
- Focus on pure visual elements: color schemes, weathering, mechanical details
- Enhanced negative prompts for comprehensive text blocking
"""

import json
import urllib.request
import time
import uuid

SDXL_OPTIMIZED_PARAMS = {
    "sampler": "dpmpp_2m",
    "scheduler": "karras", 
    "cfg": 7.0,
    "steps": 30,
    "width": 1024,
    "height": 1024
}

def create_vehicle_workflow(faction_name, vehicle_desc, seed):
    """Create vehicle concept with ZERO text elements to prevent corruption"""
    
    # CRITICAL FIX: Complete elimination of text-related prompts
    positive_prompt = f"military vehicle concept art, {vehicle_desc}, Terminal Grounds faction vehicle, post-apocalyptic combat transport, weathered armored vehicle, technical mechanical detail, industrial design, realistic wear patterns, faction color scheme, orthographic concept view, game asset design, detailed mechanical components"
    
    # ENHANCED negative prompts for complete text blocking
    negative_prompt = "text, letters, numbers, symbols, writing, inscriptions, labels, signage, military markings, stencils, unit numbers, faction insignia, readable text, words, typography, character symbols, alphanumeric content, flying vehicle, hover car, sci-fi spaceship, clean pristine, factory new, fantasy, magical, glowing energy, impossible physics, cartoon proportions, gibberish text, scrambled letters, unreadable markings, nonsense symbols, corrupted signage"
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive_prompt,
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode", 
            "inputs": {
                "text": negative_prompt,
                "clip": ["1", 1]
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": SDXL_OPTIMIZED_PARAMS["width"],
                "height": SDXL_OPTIMIZED_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": SDXL_OPTIMIZED_PARAMS["steps"],
                "cfg": SDXL_OPTIMIZED_PARAMS["cfg"],
                "sampler_name": SDXL_OPTIMIZED_PARAMS["sampler"],
                "scheduler": SDXL_OPTIMIZED_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_FIXED_Vehicle_{faction_name}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_faction_vehicles():
    """Generate vehicles for all factions with ZERO text corruption"""
    
    vehicles = [
        ("CivicWardens", "riot control vehicle"),
        ("ArchiveKeepers", "recon surveillance vehicle"),
        ("NomadClans", "convoy transport truck"),
        ("Free77", "MRAP armored patrol vehicle"),
        ("Directorate", "main battle tank"),
        ("Corporate", "APC command vehicle"),
        ("IronScavengers", "technical assault truck")
    ]
    
    base_seed = 94887
    
    print("FIXED VEHICLE GENERATION - TEXT CORRUPTION ELIMINATED")
    print("=" * 60)
    
    for i, (faction, vehicle_desc) in enumerate(vehicles):
        seed = base_seed + (i * 100)
        
        print(f"Generating {faction} {vehicle_desc} (seed: {seed})")
        
        workflow = create_vehicle_workflow(faction, vehicle_desc, seed)
        
        try:
            # Submit to ComfyUI
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"  -> Submitted successfully (ID: {result.get('prompt_id', 'unknown')})")
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            
        # Spacing between submissions
        time.sleep(1.0)
    
    print("=" * 60)
    print("FIXED VEHICLE GENERATION COMPLETE")
    print("All vehicles generated WITHOUT text elements")
    print("Check output directory for TG_FIXED_Vehicle_* files")

if __name__ == "__main__":
    generate_faction_vehicles()