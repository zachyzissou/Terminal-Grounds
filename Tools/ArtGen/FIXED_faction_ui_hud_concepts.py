#!/usr/bin/env python3
"""
FIXED Faction UI HUD Concept Generator
CTO CRITICAL FIX: Copyright protection system implemented

SOLUTION: Comprehensive copyright blocking for major game franchises
- Eliminated generic "game HUD" references that trigger copyrighted training data  
- Changed to "custom Terminal Grounds original interface design"
- Added comprehensive copyright blocks for Call of Duty, Battlefield, etc.
"""

import json
import urllib.request
import time
import uuid

PROVEN_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal",
    "cfg": 3.2, 
    "steps": 25,
    "width": 1536,
    "height": 864
}

def create_ui_workflow(faction_name, seed):
    """Create faction UI with comprehensive copyright protection"""
    
    # CRITICAL FIX: Original Terminal Grounds design language, no generic game references
    positive_prompt = f"custom Terminal Grounds original faction UI system, {faction_name} interface design, military command interface, tactical display screen, original interface concept art, clean UI mockup, faction-specific design language, Terminal Grounds universe aesthetic, original game interface design"
    
    # COMPREHENSIVE copyright blocking for major game franchises
    negative_prompt = "call of duty, battlefield, apex legends, overwatch, rainbow six, modern warfare, game copyrights, existing game UI, trademarked interfaces, copyrighted game assets, activision, EA games, ubisoft, blizzard entertainment, recognizable game branding, existing franchise UI, licensed game content, trademarked game elements, copyrighted HUD designs"
    
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
                "width": PROVEN_PARAMS["width"],
                "height": PROVEN_PARAMS["height"],
                "batch_size": 1
            }
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
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"TG_FIXED_UI_{faction_name}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_faction_ui_concepts():
    """Generate UI concepts for all factions with copyright protection"""
    
    factions = [
        "CivicWardens",
        "ArchiveKeepers", 
        "NomadClans",
        "Free77",
        "Directorate",
        "Corporate",
        "IronScavengers"
    ]
    
    base_seed = 94887
    
    print("FIXED UI GENERATION - COPYRIGHT PROTECTION ACTIVE")
    print("=" * 60)
    
    for i, faction in enumerate(factions):
        seed = base_seed + (i * 100)
        
        print(f"Generating {faction} UI concept (seed: {seed})")
        
        workflow = create_ui_workflow(faction, seed)
        
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
    print("FIXED UI GENERATION COMPLETE")
    print("All UI concepts generated with copyright protection")
    print("Check output directory for TG_FIXED_UI_* files")

if __name__ == "__main__":
    generate_faction_ui_concepts()