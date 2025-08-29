#!/usr/bin/env python3
"""
Clean Concept Art Generator - Terminal Grounds
Simple fix for branded overlay/UI template issues
Focus on pure concept art without game UI elements
"""

import json
import urllib.request
import time
import uuid

# SHARP PARAMETERS - From successful sharp weapon generation
CLEAN_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.5,              # Enhanced for sharpness (from sharp weapon success)
    "steps": 30,             # Enhanced for detail (from sharp weapon success)
    "width": 1536,
    "height": 864
}

def create_clean_concept_workflow(asset_type, faction, description, seed):
    """Generate clean concept art without branded overlays"""
    
    # SIMPLE POSITIVE PROMPT - Focus on concept art, not game UI
    positive_prompt = f"concept art of {description}, {faction} faction aesthetic, Terminal Grounds style, military equipment design, technical illustration, orthographic view, detailed mechanical components, realistic materials, professional concept art"
    
    # ENHANCED NEGATIVE PROMPT - Block branded elements, UI, AND blur
    negative_prompt = "branded overlays, game UI, user interface, watermarks, logos, Terminal Grounds branding, Mission Briefing text, branded templates, UI elements, interface overlays, game HUD, menu elements, branded graphics, corporate logos, publisher watermarks, game franchise branding, licensed content, trademark symbols, copyright notices, text overlays, digital interface, game menus, branded layouts, template designs, professional game UI, blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, cartoon"
    
    # PROVEN 7-NODE WORKFLOW
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
            "inputs": {
                "width": CLEAN_PARAMS["width"],
                "height": CLEAN_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": CLEAN_PARAMS["steps"],
                "cfg": CLEAN_PARAMS["cfg"],
                "sampler_name": CLEAN_PARAMS["sampler"],
                "scheduler": CLEAN_PARAMS["scheduler"],
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
            "inputs": {
                "filename_prefix": f"TG_CLEAN_CONCEPT_{asset_type}_{faction}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_clean_concept_test():
    """Test SHARP clean concept art generation without branded elements"""
    
    # Simple test cases
    test_assets = [
        ("weapon", "Directorate", "military carbine rifle with blue accents"),
        ("vehicle", "Free77", "armored personnel carrier with red markings"),
    ]
    
    base_seed = 360000  # New seed range for sharp clean test
    
    print("SHARP CLEAN CONCEPT ART TEST - Terminal Grounds")
    print("Removing branded overlays + Enhanced sharpness (CFG 3.5, 30 steps)")
    print("=" * 60)
    print()
    print("FIXED PARAMETERS:")
    print(f"  CFG: {CLEAN_PARAMS['cfg']} (enhanced for sharpness)")
    print(f"  Steps: {CLEAN_PARAMS['steps']} (enhanced for detail)")
    print(f"  Anti-blur: Enhanced negative prompts")
    print()
    
    for i, (asset_type, faction, description) in enumerate(test_assets):
        seed = base_seed + (i * 500)
        
        print(f"Test {i+1}: {asset_type.upper()} - {faction}")
        print(f"  Focus: Clean concept art without UI overlays")
        print(f"  Seed: {seed}")
        
        workflow = create_clean_concept_workflow(asset_type, faction, description, seed)
        
        try:
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            prompt_id = result.get('prompt_id', 'unknown')
            print(f"  -> Submitted (ID: {prompt_id})")
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            
        print()
        time.sleep(0.5)
    
    print("=" * 50)
    print("CLEAN CONCEPT ART TEST QUEUED")
    print()
    print("Expected Results:")
    print("  - No branded overlays or UI elements")  
    print("  - Clean concept art focus")
    print("  - No 'Terminal Grounds' branding")
    print("  - No 'Mission Briefing' watermarks")
    print()
    print("Output files: TG_CLEAN_CONCEPT_*")

if __name__ == "__main__":
    generate_clean_concept_test()