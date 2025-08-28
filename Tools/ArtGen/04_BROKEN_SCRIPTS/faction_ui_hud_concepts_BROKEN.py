#!/usr/bin/env python3
"""
Faction UI/HUD Interface Concept Generator
Each faction's psychology expressed through interface design
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
    "width": 1920,  # Wide for UI layouts
    "height": 1080
}

def create_ui_workflow(faction_name, ui_desc, seed):
    """Create UI/HUD concept showing faction interface psychology"""
    
    positive_prompt = f"tactical HUD interface design, {ui_desc}, Terminal Grounds faction UI system, military interface design, game HUD concept art, tactical display elements, faction-specific interface design, detailed UI mockup"
    
    negative_prompt = "fantasy interface, magical elements, bright neon colors, clean modern UI, minimalist design, cartoon style, consumer interface, smartphone UI"
    
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
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": f"TG_UI_{faction_name}"
            }
        }
    }
    return workflow

def submit_workflow(workflow):
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
    print("FACTION UI/HUD CONCEPT GENERATOR")
    print("Interface Psychology Matching Faction Identity")
    print("=" * 60)
    print()
    
    ui_concepts = [
        # Iron Scavengers - Hacked systems
        ("IronScavengers_HUD", "jury-rigged HUD with multiple incompatible systems hacked together, different fonts and colors from various faction interfaces, warning messages in three languages, some elements upside down from wrong installation, constant compatibility errors ignored"),
        
        # Corporate Hegemony - Brand integrated
        ("Corporate_HUD", "sleek corporate interface with terms of service popups during combat, ammunition counter showing cost per shot, health bar sponsored by medical division, crosshairs form corporate logo when aimed, stock prices scrolling in peripheral vision"),
        
        # Directorate - Military brutalism  
        ("Directorate_HUD", "harsh green monochrome interface with hand-stamped serial numbers, regulation font from 1980s, authorization codes required for advanced functions, damage reports filed automatically, kill counter with batch numbers"),
        
        # Free77 - Professional contractor
        ("Free77_HUD", "modular interface with employer color schemes that change per contract, QR codes linking to service rates, ammunition cost calculator, contract completion percentage, invoice generation in real-time"),
        
        # Nomad Clans - Improvised survival
        ("NomadClans_HUD", "patched together interface with hand-carved icons, fuel and water prominently displayed, route planning with hazard markers, family communications channel, repair status for all equipment"),
        
        # Archive Keepers - Data overload
        ("ArchiveKeepers_HUD", "information-dense interface with scrolling data streams, target personal history displays, ammunition that shows virus upload status, QR codes for knowledge database access, kill statistics with detailed analytics"),
        
        # Civic Wardens - Community watch
        ("CivicWardens_HUD", "neighborhood watch interface with spray-painted styling, community radio channels, local area maps with civilian safe zones, ammunition shared counter, volunteer roster status")
    ]
    
    queued = 0
    seed_base = 98111
    
    for i, (ui_name, description) in enumerate(ui_concepts):
        seed = seed_base + (i * 159)
        print(f"Generating {ui_name}...")
        print(f"  Interface: {description[:50]}...")
        
        workflow = create_ui_workflow(ui_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"UI/HUD GENERATION COMPLETE: {queued}/7 interface concepts")
    print("Each interface reflects faction psychology through design")

if __name__ == "__main__":
    main()