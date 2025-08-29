#!/usr/bin/env python3
"""
SHARP Experimental FLUX Vehicle Generator
FIXED: Addresses blurriness issues with enhanced sharpness parameters
Based on successful TG_Weapon_Sharp generation parameters
"""

import json
import urllib.request
import time
import uuid

# SHARP PARAMETERS - Based on successful sharp weapon generation
SHARP_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.5,        # Higher CFG for stronger prompt adherence and sharpness
    "steps": 30,       # More steps for enhanced detail
    "width": 1536,
    "height": 864
}

def create_sharp_vehicle_workflow(faction_name, vehicle_desc, style, seed):
    """Create ultra-sharp FLUX vehicle concept"""
    
    # Enhanced faction characteristics for vehicles
    faction_styles = {
        "Directorate": "military precision engineering, corporate blue-grey armor plating, angular geometric design, polished tactical surfaces",
        "Free77": "mercenary field modifications, red accent stripes, practical armor reinforcement, battle-tested reliability",
        "CivicWardens": "law enforcement tactical vehicle, community protection equipment, utilitarian armor design, civic authority specification",
        "NomadClans": "convoy survival modifications, tribal weathering patterns, overland expedition equipment, rugged territorial capability",
        "IronScavengers": "scavenged armor welding, improvised weapon systems, post-apocalyptic functionality, trophy modifications"
    }
    
    style_modifiers = {
        "gritty_realism": "realistic battle damage, authentic weathering patterns, operational wear, field maintenance modifications",
        "clean_scifi": "pristine military condition, advanced technological integration, factory specification surfaces",
        "industrial": "heavy duty construction, exposed mechanical systems, utilitarian battlefield functionality"
    }
    
    faction_style = faction_styles.get(faction_name, "military vehicle design")
    style_mod = style_modifiers.get(style, "realistic military specification")
    
    # ULTRA-SHARP positive prompt based on successful weapon generation
    positive_prompt = f"ultra sharp professional vehicle concept art, {vehicle_desc}, {faction_style}, {style_mod}, Terminal Grounds faction vehicle, crisp detailed game asset concept, razor sharp orthographic technical view, crystal clear mechanical details, pin-sharp armor plating, high definition technical drawing, professional concept art quality, detailed vehicle engineering"
    
    # ENHANCED negative prompt against blur - based on sharp weapon success
    negative_prompt = "blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, jpeg artifacts, text, letters, writing, insignia, numbers, symbols, logos, readable text, flying vehicle, hover technology, impossible physics, cartoon style, anime, fantasy elements"
    
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
                "width": SHARP_PARAMS["width"],
                "height": SHARP_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": SHARP_PARAMS["steps"],
                "cfg": SHARP_PARAMS["cfg"],
                "sampler_name": SHARP_PARAMS["sampler"],
                "scheduler": SHARP_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_SHARP_Vehicle_{faction_name}_{style}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_sharp_vehicles():
    """Generate ultra-sharp vehicles using enhanced parameters"""
    
    # Focused experimental vehicle concepts
    sharp_vehicles = [
        ("Directorate", "stealth reconnaissance ATV", "clean_scifi"),
        ("Free77", "armored mercenary truck", "gritty_realism"),
        ("IronScavengers", "technical combat vehicle", "industrial"),
    ]
    
    base_seed = 187234  # New seed range for sharp generation
    
    print("SHARP EXPERIMENTAL VEHICLE GENERATION")
    print("ENHANCED PARAMETERS: CFG 3.5, Steps 30, Anti-blur controls")
    print("=" * 60)
    
    for i, (faction, vehicle_desc, style) in enumerate(sharp_vehicles):
        seed = base_seed + (i * 500)  # Good seed spacing
        
        print(f"Generating SHARP {faction} {vehicle_desc} ({style}) - seed: {seed}")
        
        workflow = create_sharp_vehicle_workflow(faction, vehicle_desc, style, seed)
        
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
            
        # Proper spacing between submissions
        time.sleep(0.5)
    
    print("=" * 60)
    print("SHARP VEHICLE GENERATION PARAMETERS:")
    print(f"  Sampler: {SHARP_PARAMS['sampler']}")
    print(f"  Scheduler: {SHARP_PARAMS['scheduler']}")
    print(f"  CFG: {SHARP_PARAMS['cfg']} (enhanced from 3.2)")
    print(f"  Steps: {SHARP_PARAMS['steps']} (enhanced from 25)")
    print(f"  Resolution: {SHARP_PARAMS['width']}x{SHARP_PARAMS['height']}")
    print()
    print("Enhanced Features:")
    print("  - Ultra-sharp positive prompts")
    print("  - Strong anti-blur negative prompts")
    print("  - Higher CFG for better prompt adherence")
    print("  - More steps for enhanced detail")
    print()
    print("Check output directory for: TG_SHARP_Vehicle_*")

if __name__ == "__main__":
    generate_sharp_vehicles()