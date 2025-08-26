#!/usr/bin/env python3
"""
Faction Character/Operator Concept Generator
Character designs that embody faction psychology through visual storytelling
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
    "width": 1024,
    "height": 1536  # Portrait for characters
}

def create_character_workflow(faction_name, char_desc, seed):
    """Create character concept based on faction identity"""
    
    positive_prompt = f"tactical operator character concept art, {char_desc}, Terminal Grounds faction soldier, post-apocalyptic military gear, weathered combat equipment, professional game character design, detailed tactical gear, faction-specific modifications, atmospheric portrait lighting, character sheet style"
    
    negative_prompt = "clean pristine uniform, factory new equipment, fantasy armor, sci-fi energy weapons, glowing effects, cartoon proportions, anime style, superhero costume, bright colors, undamaged gear, civilian clothing"
    
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
                "filename_prefix": f"TG_Character_{faction_name}"
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
    print("FACTION CHARACTER CONCEPT GENERATOR")
    print("Operator Psychology Through Visual Design")
    print("=" * 60)
    print()
    
    characters = [
        # Iron Scavengers - Trophy collector
        ("IronScavengers_Raider", "scavenger wearing mismatched armor pieces from defeated enemies, trophy dog tags hanging from tactical vest, weapons holstered in wrong holsters that were modified to fit, face paint using motor oil and rust, equipment pouches clearly from different factions"),
        
        # Corporate Hegemony - Brand enforcer
        ("Corporate_Enforcer", "corporate security operator with armor displaying stock prices on OLED panels, corporate pin that glows blue, weapons won't unlock without biometric corporate ID, face mask with corporate smile printed on, clothing changes color based on corporate alert level"),
        
        # Directorate - Institution soldier
        ("Directorate_Trooper", "institutional military operator wearing boots older than himself, helmet with kill marks scratched inside only, dog tags from multiple deployment zones, patches sewn over patches never removed, face paint in regulation patterns from 1980s manual"),
        
        # Free77 - Contract mercenary
        ("Free77_Contractor", "professional mercenary with modular gear showing magnetic faction panels for current employer, desert tan base with changeable color accents, QR code on chest linking to contractor rate card, ammunition sorted by cost effectiveness"),
        
        # Nomad Clans - Road survivor
        ("NomadClans_Outrider", "nomad road warrior with gear wrapped in various animal leathers, tactical vest made from repurposed vehicle materials, weapons blessed with road salt, equipment showing repairs from multiple generations, solar panel charging pack"),
        
        # Archive Keepers - Data archaeologist
        ("ArchiveKeepers_Archivist", "information warfare specialist with scrolling text displays on armor showing data statistics, purple and gold color scheme, QR codes etched on equipment, face mask with holographic display, ammunition that uploads data on impact"),
        
        # Civic Wardens - Community defender
        ("CivicWardens_Guardian", "neighborhood watch volunteer with improvised tactical gear, zip-tied flashlight on weapon, spray-painted unit number still dripping, mismatched equipment from community donations, 'Protected by Neighborhood Watch' patch")
    ]
    
    queued = 0
    seed_base = 96777
    
    for i, (char_name, description) in enumerate(characters):
        seed = seed_base + (i * 135)
        print(f"Generating {char_name}...")
        print(f"  Identity: {description[:55]}...")
        
        workflow = create_character_workflow(char_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"CHARACTER GENERATION COMPLETE: {queued}/7 faction operators")
    print("Each embodies faction psychology through gear and appearance")

if __name__ == "__main__":
    main()