#!/usr/bin/env python3
"""
ENHANCED Faction Vehicle Concept Generator
Improved: Advanced text guidance for readable faction markings
Professional military vehicle aesthetics with clear identification
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

def create_vehicle_workflow(faction_name, vehicle_desc, text_guidance, seed):
    """Create vehicle concept with ENHANCED text handling for faction authenticity"""
    
    # ENHANCED: Specific, achievable text instructions
    positive_prompt = f"military vehicle concept art, {vehicle_desc}, Terminal Grounds faction vehicle, {text_guidance}, clean military stenciling with simple block lettering, faction identification markings on armor panels, weathered but readable unit numbers, professional military vehicle graphics, authentic military aesthetics, orthographic concept view, game asset design"
    
    # TARGETED: Specific text quality requirements while allowing good text
    negative_prompt = "handwritten text, cursive fonts, small illegible text, overlapping letters, blurred text, pixelated text, comic sans, decorative fonts, multiple conflicting fonts, text over complex backgrounds, gibberish text, scrambled letters, corrupted digital display text, unreadable graffiti, flying vehicle, hover car, sci-fi spaceship, fantasy elements"
    
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
                "filename_prefix": f"TG_Vehicle_{faction_name}"
            }
        }
    }
    return workflow

def submit_workflow(workflow):
    """Submit to ComfyUI"""
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
    print("ENHANCED FACTION VEHICLE GENERATOR")
    print("Advanced Text Guidance for Professional Military Aesthetics")
    print("=" * 60)
    print()
    
    # ENHANCED: Faction-specific visual identity with appropriate text guidance
    vehicles = [
        # Iron Scavengers - Makeshift but functional
        ("IronScavengers_Technical", 
         "pickup truck with mismatched armor panels welded from different sources, scavenger orange paint over various base colors, makeshift armor attachments, different wheel and tire combinations, battle-worn weathered appearance",
         "stenciled faction symbols, spray-painted unit markings, hand-painted warning signs"),
        
        # Corporate - Clean professional branding
        ("Corporate_APC", 
         "white polymer armored personnel carrier with blue accent strips, clean corporate design language, pristine self-cleaning surfaces, tinted windows, integrated LED status displays",
         "corporate logo placement, clean sans-serif identification numbers, professional vehicle branding"),
        
        # Directorate - Military authority
        ("Directorate_Tank", 
         "main battle tank with layered welded armor reinforcements, olive drab paint worn to bare metal in high-wear areas, searchlight and communications equipment, heavy tracked chassis, intimidating military profile",
         "official military stenciling, regulation unit numbers, command authority markings"),
        
        # Free77 - Modular professional
        ("Free77_MRAP", 
         "mine-resistant ambush protected vehicle with modular attachment points, desert tan base color with removable panel system, mercenary-grade modifications, professional contractor aesthetics",
         "contractor identification codes, modular faction panels, professional service markings"),
        
        # Nomad Clans - Mobile community
        ("NomadClans_Convoy", 
         "converted bus chassis with living quarter modifications, external tool and equipment mounting points, solar panels and water collection systems, mixed tire types, dust and oil weathering patterns",
         "clan family symbols, route markers, community identification signs"),
        
        # Archive Keepers - High-tech information
        ("ArchiveKeepers_Recon", 
         "surveillance and reconnaissance vehicle with antenna arrays and sensor equipment, purple and gold faction color scheme, visible electronic equipment and data storage systems, satellite communication gear",
         "data classification markings, archive identification codes, information security labels"),
        
        # Civic Wardens - Community protection
        ("CivicWardens_Riot", 
         "converted civilian delivery van with community-donated steel plate armor, mismatched colored panels representing different neighborhood contributions, CB radio antenna arrays, improvised but effective ram attachment",
         "neighborhood watch signs, community volunteer markings, local area identification")
    ]
    
    queued = 0
    seed_base = 97777  # Different seed base for enhanced version
    
    for i, (vehicle_name, description, text_guidance) in enumerate(vehicles):
        seed = seed_base + (i * 147)
        print(f"Generating ENHANCED {vehicle_name}...")
        print(f"  Vehicle: {description[:50]}...")
        print(f"  Text Style: {text_guidance[:40]}...")
        
        workflow = create_vehicle_workflow(vehicle_name, description, text_guidance, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"ENHANCED VEHICLE GENERATION COMPLETE: {queued}/7")
    print("Professional military aesthetics with faction-appropriate text")

if __name__ == "__main__":
    main()