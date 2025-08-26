#!/usr/bin/env python3
"""
FIXED: Faction Weapon Concepts - Enhanced Sharpness
Addressing blur issues with stronger negative prompts and sharpness emphasis
"""

import json
import urllib.request
import time
import uuid

# Proven parameters with potential sharpness tweaks
PROVEN_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.5,  # Slightly higher for more prompt adherence
    "steps": 30,  # More steps for detail
    "width": 1536,
    "height": 864
}

def create_sharp_weapon_workflow(faction_name, weapon_desc, seed):
    """Create weapon workflow with enhanced sharpness controls"""
    
    # Enhanced positive prompt with sharpness emphasis
    positive_prompt = f"ultra sharp professional weapon concept art, {weapon_desc}, Terminal Grounds aesthetic, crisp detailed game asset concept, razor sharp orthographic view, crystal clear technical details, pin-sharp mechanical components, high definition technical drawing, professional concept art quality, detailed weapon design"
    
    # Stronger negative prompt against blur
    negative_prompt = "blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, jpeg artifacts, cartoon, anime, fantasy, clean pristine condition"
    
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
                "filename_prefix": f"TG_Weapon_Sharp_{faction_name}"
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
    print("SHARP WEAPON CONCEPT REGENERATION")
    print("Enhanced sharpness controls for professional quality")
    print("=" * 60)
    print()
    
    # Same weapon concepts with enhanced quality
    weapon_concepts = [
        ("IronScavengers_Rifle", "franken-rifle with Directorate barrel welded to Corporate polymer body, wrapped in Nomad leather strips, mismatched scope from Free77, trophy dog tags hanging from stock, visible serial numbers from three different weapons, duct tape and wire modifications, scavenger orange paint over original faction colors"),
        
        ("Corporate_SMG", "white polymer submachine gun with integrated OLED strips showing corporate logo, blue accent lighting, QR code on magazine, smart-linked with warning labels, holographic ammunition counter, self-cleaning surface, terms of service etched on barrel"),
        
        ("Directorate_MG", "30-year-old heavy machine gun with hand-stamped serial numbers, olive drab paint worn to metal, regulation modifications from 1980s manual, ammunition belt with batch numbers from 5 years ago, bipod welded not bolted, scratched kill marks on receiver"),
        
        ("Free77_Sniper", "modular sniper rifle with swappable faction-colored parts, desert tan base, QR code linking to contractor rates, magnetic employer logo panel, professional scope with watermark sponsorships, invoice tally scratched on stock"),
        
        ("NomadClans_Shotgun", "pump shotgun wrapped in various animal leathers, sling made from seatbelt, hand-carved stock with family history, shells blessed with road salt, solar panel charging attachment, water purification tube attached to barrel"),
        
        ("ArchiveKeepers_PDW", "personal defense weapon with scrolling OLED display showing kill statistics, purple and gold aesthetic, QR codes etched on receiver, trigger requires passphrase, ammunition magazine with data storage capability"),
        
        ("CivicWardens_Carbine", "civilian rifle with welded armor plates, zip-tied flashlight, neighborhood watch sticker, spray-painted unit number still dripping, mismatched parts from community donations, CB radio antenna attached")
    ]
    
    queued = 0
    seed_base = 99887  # Different seed base
    
    for i, (weapon_name, description) in enumerate(weapon_concepts):
        seed = seed_base + (i * 111)
        print(f"Regenerating {weapon_name} (SHARP)...")
        print(f"  Enhanced: {description[:45]}...")
        
        workflow = create_sharp_weapon_workflow(weapon_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"SHARP WEAPON REGENERATION: {queued}/7 weapons")
    print("Enhanced parameters: CFG 3.5, Steps 30, Strong anti-blur")

if __name__ == "__main__":
    main()