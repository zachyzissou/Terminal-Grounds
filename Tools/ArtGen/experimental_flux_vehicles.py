#!/usr/bin/env python3
"""
Experimental FLUX Vehicle Generator
Based on proven Terminal Grounds parameters and documentation
Uses FLUX1-dev-fp8.safetensors with perfected parameters
"""

import json
import urllib.request
import time
import uuid

# PROVEN PARAMETERS from terminal_grounds_generator.py
PERFECT_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.2,
    "steps": 25,
    "width": 1536,
    "height": 864
}

def create_flux_vehicle_workflow(faction_name, vehicle_desc, style, seed):
    """Create FLUX vehicle concept with proven parameters"""
    
    # Enhanced prompts based on lore and faction characteristics
    faction_styles = {
        "Directorate": "military precision, corporate blue-grey color scheme, angular geometric design, polished tactical surfaces",
        "Free77": "mercenary modifications, red accents, practical field repairs, battle-worn appearance",
        "CivicWardens": "law enforcement aesthetic, community protection focus, utilitarian design, civic authority markings",
        "NomadClans": "convoy modifications, tribal weathering patterns, survival equipment, rugged overland capability",
        "IronScavengers": "scavenged components, welded armor plating, improvised weapons mounts, post-apocalyptic functionality",
        "CorporateHegemony": "executive transport, luxurious military design, high-tech integration, pristine condition",
        "ArchiveKeepers": "reconnaissance focus, sensor arrays, stealth capabilities, archival data protection"
    }
    
    # Style variations for experimental generation
    style_modifiers = {
        "gritty_realism": "weathered, battle-damaged, realistic wear patterns, mud and rust",
        "clean_scifi": "pristine condition, advanced technology integration, sleek surfaces",
        "industrial": "heavy armor plating, mechanical components exposed, utilitarian function"
    }
    
    faction_style = faction_styles.get(faction_name, "military vehicle")
    style_mod = style_modifiers.get(style, "realistic military design")
    
    positive_prompt = f"concept art of {vehicle_desc}, {faction_style}, {style_mod}, Terminal Grounds faction vehicle, post-apocalyptic military transport, detailed mechanical design, orthographic technical view, game concept art, professional vehicle design"
    
    # Comprehensive negative prompts to prevent issues
    negative_prompt = "text, letters, writing, insignia, numbers, symbols, logos, readable text, gibberish text, unreadable markings, flying vehicle, hover technology, impossible physics, cartoon style, anime, fantasy elements, magic, glowing energy effects"
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
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
                "width": PERFECT_PARAMS["width"],
                "height": PERFECT_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": PERFECT_PARAMS["steps"],
                "cfg": PERFECT_PARAMS["cfg"],
                "sampler_name": PERFECT_PARAMS["sampler"],
                "scheduler": PERFECT_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_EXPERIMENTAL_Vehicle_{faction_name}_{style}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_experimental_vehicles():
    """Generate experimental vehicles using FLUX and proven parameters"""
    
    # Experimental vehicle concepts for different factions
    experimental_vehicles = [
        ("Directorate", "stealth reconnaissance drone vehicle", "clean_scifi"),
        ("Free77", "armored mercenary transport", "gritty_realism"),
        ("CivicWardens", "urban patrol vehicle", "industrial"),
        ("NomadClans", "convoy supply truck", "gritty_realism"),
        ("IronScavengers", "technical assault vehicle", "industrial"),
    ]
    
    base_seed = 142857  # Using a different seed pattern for experimental generation
    
    print("EXPERIMENTAL FLUX VEHICLE GENERATION")
    print("Using FLUX1-dev-fp8 with proven parameters")
    print("=" * 60)
    
    for i, (faction, vehicle_desc, style) in enumerate(experimental_vehicles):
        seed = base_seed + (i * 1000)  # Larger seed spacing for variety
        
        print(f"Generating {faction} {vehicle_desc} ({style}) - seed: {seed}")
        
        workflow = create_flux_vehicle_workflow(faction, vehicle_desc, style, seed)
        
        try:
            # Submit to ComfyUI
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            prompt_id = result.get('prompt_id', 'unknown')
            print(f"  -> Submitted successfully (ID: {prompt_id})")
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            
        # Proper spacing between submissions (documented requirement)
        time.sleep(0.5)
    
    print("=" * 60)
    print("EXPERIMENTAL VEHICLE GENERATION COMPLETE")
    print("Using FLUX1-dev-fp8.safetensors with proven parameters:")
    print(f"  Sampler: {PERFECT_PARAMS['sampler']}")
    print(f"  Scheduler: {PERFECT_PARAMS['scheduler']}")
    print(f"  CFG: {PERFECT_PARAMS['cfg']}")
    print(f"  Steps: {PERFECT_PARAMS['steps']}")
    print(f"  Resolution: {PERFECT_PARAMS['width']}x{PERFECT_PARAMS['height']}")
    print()
    print("Check output directory: C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/")
    print("Look for files starting with: TG_EXPERIMENTAL_Vehicle_")

if __name__ == "__main__":
    generate_experimental_vehicles()