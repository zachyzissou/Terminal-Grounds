#!/usr/bin/env python3
"""
Faction Architectural Damage Pattern Generator  
Environmental storytelling through faction-specific territorial modifications
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

def create_architecture_workflow(faction_name, arch_desc, seed):
    """Create architectural pattern showing faction territorial control"""
    
    positive_prompt = f"architectural detail concept art, {arch_desc}, Terminal Grounds faction territory control, environmental storytelling, weathered infrastructure modifications, post-apocalyptic territorial marking, detailed architectural damage patterns, faction-specific building modifications"
    
    negative_prompt = "pristine buildings, new construction, undamaged architecture, clean surfaces, fantasy elements, sci-fi technology, bright lighting, cartoon style"
    
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
                "filename_prefix": f"TG_Architecture_{faction_name}"
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
    print("FACTION ARCHITECTURAL PATTERN GENERATOR")
    print("Environmental Storytelling Through Territory Control")
    print("=" * 60)
    print()
    
    architecture_patterns = [
        # Iron Scavengers - Scrap trophy totems
        ("IronScavengers_Territory", "building entrance with scrap metal totems constructed from defeated enemies' equipment, mismatched doors stolen from different buildings, power cables jury-rigged from three different infrastructure systems, graffiti showing equipment serial numbers tracking stolen items"),
        
        # Corporate Hegemony - Brand scarred spaces  
        ("Corporate_Facility", "corporate building with holographic logos projected onto walls, glass surfaces showing advertisements to enemies and tactical data to employees, elevators requiring corporate ID for access, anti-homeless architecture used as defensive positions"),
        
        # Directorate - Brutalist fortification
        ("Directorate_Bunker", "concrete bunker with five layers of different-era reinforcement, every doorway weighs 500 pounds, windows converted to gun slits, barbed wire from three decades layered together, fading 'AUTHORIZED PERSONNEL' signs"),
        
        # Free77 - Contract workspace
        ("Free77_Outpost", "modular facility with magnetic faction panels showing current employer, 'For Hire' stenciling visible under current paint, QR codes linking to contractor services, ammunition cost displays on walls"),
        
        # Nomad Clans - Mobile architecture
        ("NomadClans_Camp", "portable structures that break down for travel, solar panels and water collectors mounted on every surface, tool mounting points covering exterior walls, generational repairs visible in patchwork materials"),
        
        # Archive Keepers - Data archaeology site
        ("ArchiveKeepers_Archive", "building walls covered in QR codes storing knowledge, windows displaying different data to each viewer, floors with embedded fiber optic patterns, doors that quiz visitors before opening"),
        
        # Civic Wardens - Community fortress
        ("CivicWardens_Checkpoint", "converted civilian building with welded steel barriers, 'Neighborhood Watch' signs used as armor plating, different color materials from community donations, improvised defensive positions using shopping carts")
    ]
    
    queued = 0
    seed_base = 97333
    
    for i, (arch_name, description) in enumerate(architecture_patterns):
        seed = seed_base + (i * 147)
        print(f"Generating {arch_name}...")
        print(f"  Pattern: {description[:50]}...")
        
        workflow = create_architecture_workflow(arch_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"ARCHITECTURE GENERATION COMPLETE: {queued}/7 patterns")
    print("Each shows faction territorial psychology through modifications")

if __name__ == "__main__":
    main()