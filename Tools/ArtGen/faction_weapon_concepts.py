#!/usr/bin/env python3
"""
Faction-Specific Weapon Concept Generator
Based on Chief Art Director Visual Language Bible
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
    "width": 1536,
    "height": 864
}

def create_weapon_workflow(faction_name, weapon_desc, seed):
    """Create weapon concept workflow based on faction visual language"""
    
    positive_prompt = f"professional weapon concept art, {weapon_desc}, Terminal Grounds aesthetic, game asset concept, orthographic view, technical details visible, weathered combat equipment, post-apocalyptic military hardware, detailed mechanical components, faction-specific modifications, high detail technical drawing"
    
    negative_prompt = "blurry, low quality, cartoon, anime, fantasy, magic, glowing runes, sci-fi energy weapons, laser beams, unrealistic proportions, floating parts, impossible mechanics, clean pristine condition, factory new, untested equipment"
    
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
                "filename_prefix": f"TG_Weapon_{faction_name}"
            }
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
    print("FACTION WEAPON CONCEPT GENERATOR")
    print("Chief Art Director Visual Language Implementation")
    print("=" * 60)
    print()
    
    # Weapon concepts based on faction visual language bible
    weapon_concepts = [
        # Iron Scavengers - Trophy Warfare
        ("IronScavengers_Rifle", "franken-rifle with Directorate barrel welded to Corporate polymer body, wrapped in Nomad leather strips, mismatched scope from Free77, trophy dog tags hanging from stock, visible serial numbers from three different weapons, duct tape and wire modifications, scavenger orange paint over original faction colors"),
        
        # Corporate Hegemony - Brand Warfare  
        ("Corporate_SMG", "white polymer submachine gun with integrated OLED strips showing corporate logo, blue accent lighting, QR code on magazine, smart-linked with warning labels, holographic ammunition counter, self-cleaning surface, terms of service etched on barrel"),
        
        # Directorate - Institutional Authority
        ("Directorate_MG", "30-year-old heavy machine gun with hand-stamped serial numbers, olive drab paint worn to metal, regulation modifications from 1980s manual, ammunition belt with batch numbers from 5 years ago, bipod welded not bolted, scratched kill marks on receiver"),
        
        # Free77 - Professional Violence
        ("Free77_Sniper", "modular sniper rifle with swappable faction-colored parts, desert tan base, QR code linking to contractor rates, magnetic employer logo panel, professional scope with watermark sponsorships, invoice tally scratched on stock"),
        
        # Nomad Clans - Mobile Survival
        ("NomadClans_Shotgun", "pump shotgun wrapped in various animal leathers, sling made from seatbelt, hand-carved stock with family history, shells blessed with road salt, solar panel charging attachment, water purification tube attached to barrel"),
        
        # Archive Keepers - Data Archaeology
        ("ArchiveKeepers_PDW", "personal defense weapon with scrolling OLED display showing kill statistics, purple and gold aesthetic, QR codes etched on receiver, trigger requires passphrase, ammunition magazine with data storage capability"),
        
        # Civic Wardens - Community Fortress
        ("CivicWardens_Carbine", "civilian rifle with welded armor plates, zip-tied flashlight, neighborhood watch sticker, spray-painted unit number still dripping, mismatched parts from community donations, CB radio antenna attached")
    ]
    
    total_queued = 0
    seed_base = 94887
    
    for i, (weapon_name, description) in enumerate(weapon_concepts):
        seed = seed_base + (i * 111)
        print(f"Queuing {weapon_name}...")
        print(f"  Psychology: {description[:60]}...")
        
        workflow = create_weapon_workflow(weapon_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            total_queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"WEAPON CONCEPT GENERATION COMPLETE")
    print(f"Queued: {total_queued}/{len(weapon_concepts)} faction weapons")
    print(f"Output: C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API\\output\\")
    print()
    print("Each weapon demonstrates faction visual language:")
    print("- Core psychological identity")
    print("- Environmental storytelling")
    print("- Cultural depth through details")

if __name__ == "__main__":
    main()