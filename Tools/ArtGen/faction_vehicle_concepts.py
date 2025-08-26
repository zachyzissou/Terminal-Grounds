#!/usr/bin/env python3
"""
Faction Vehicle Concept Generator
Implementing Chief Art Director Vehicle Philosophy per Faction
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

def create_vehicle_workflow(faction_name, vehicle_desc, seed):
    """Create vehicle concept based on faction philosophy"""
    
    positive_prompt = f"military vehicle concept art, {vehicle_desc}, Terminal Grounds faction vehicle, post-apocalyptic combat transport, weathered armored vehicle with authentic military markings and readable faction insignia, technical details visible, clear unit numbers and tactical symbols, professional military stenciling, orthographic concept view, game asset design, industrial mechanical detail, sharp lettering on armor plating"
    
    negative_prompt = "flying vehicle, hover car, sci-fi spaceship, clean pristine, factory new, fantasy, magical, glowing energy, impossible physics, cartoon proportions, gibberish text, scrambled letters, unreadable markings, nonsense symbols, corrupted signage"
    
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
    print("FACTION VEHICLE CONCEPT GENERATOR")
    print("Vehicle Philosophy Implementation")
    print("=" * 60)
    print()
    
    # Vehicle concepts from faction visual bible
    vehicles = [
        # Iron Scavengers - Frankenstein assemblies
        ("IronScavengers_Technical", "pickup truck with mismatched armor panels from three different military vehicles, scavenger orange paint over original camouflage showing through, trophy rack displaying defeated faction emblems, engine parts from different vehicles visible, no two wheels match"),
        
        # Corporate Hegemony - Brand warfare mobility
        ("Corporate_APC", "white polymer armored personnel carrier with blue LED strips, holographic corporate logos projecting from hull, self-cleaning surfaces staying pristine, tinted windows showing internal displays, QR codes on armor panels"),
        
        # Directorate - Brutalist authority
        ("Directorate_Tank", "30-year-old main battle tank with hand-painted unit numbers, armor welded over armor in layers, searchlights as psychological weapons, treads designed to leave Directorate symbols, olive drab paint worn to bare metal"),
        
        # Free77 - Modular mercenary
        ("Free77_MRAP", "mine-resistant vehicle with magnetic faction panels for current employer, desert tan base with removable employer color accents, 'For Hire' stenciling visible under paint, kill counter that's also invoice tally"),
        
        # Nomad Clans - Mobile home fortress
        ("NomadClans_Convoy", "converted bus that's also living quarters, exterior covered in tool mounting points, solar panels and water collectors on roof, tires from four different manufacturers, road dust paint mixed with motor oil"),
        
        # Archive Keepers - Data warfare platform
        ("ArchiveKeepers_Recon", "surveillance vehicle covered in antenna arrays and sensors, purple and gold color scheme, QR codes on every panel, satellite dishes and data storage banks visible, holographic displays in windows"),
        
        # Civic Wardens - Improvised protection
        ("CivicWardens_Riot", "converted delivery van with welded steel plates, 'Protected by Neighborhood Watch' signs as armor, different color panels from community donations, CB radio antennas, improvised ram made from shopping carts")
    ]
    
    queued = 0
    seed_base = 95555
    
    for i, (vehicle_name, description) in enumerate(vehicles):
        seed = seed_base + (i * 123)
        print(f"Generating {vehicle_name}...")
        print(f"  Philosophy: {description[:50]}...")
        
        workflow = create_vehicle_workflow(vehicle_name, description, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60) 
    print(f"VEHICLE GENERATION COMPLETE: {queued}/7 faction vehicles")
    print("Each demonstrates faction mobility philosophy")

if __name__ == "__main__":
    main()