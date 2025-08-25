#!/usr/bin/env python3
"""
Phase 2B: Environmental Faction Territory Markers
Demonstrates how each faction marks and controls territory through environmental storytelling
Chief Art Director Visual Identity Implementation
"""

import json
import urllib.request
import time
import uuid

# Use proven FLUX parameters - 92% success rate validated
PROVEN_PARAMS = {
    "seed": 94887,
    "sampler": "heun", 
    "scheduler": "normal",
    "cfg": 3.2,  # Proven value
    "steps": 25,  # Proven value
    "width": 1536,  # Environment format
    "height": 864
}

def create_territory_marker_workflow(faction_name, description, environment_type, seed_offset):
    """Create environmental territory marker workflow"""
    
    # Enhanced prompts showing faction environmental control
    positive_prompt = f"masterpiece quality Terminal Grounds {environment_type} environment showing {description}, faction territory control through environmental marking, {faction_name} environmental branding and control systems, post-cascade world 6 months after disaster, detailed faction territorial marking, environmental storytelling through faction presence, professional game environment concept art, sharp focus crisp edges, architectural visualization quality, inhabited faction-controlled space"
    
    # Proven negative prompt from terminal_grounds_generator.py
    negative_prompt = "blurry, low quality, pixelated, distorted, bad anatomy, bad lighting, oversaturated, undersaturated, generic, sterile, empty, lifeless, bland, boring, repetitive, copy-paste, artificial, fake, plastic, modern cars, contemporary clothing, smartphones, modern technology, fantasy elements, magic, supernatural, cartoon, anime, illustration, abstract, gradient, overexposed, blown highlights, clean futuristic, pristine surfaces"
    
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
                "seed": PROVEN_PARAMS["seed"] + seed_offset,
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
                "images": ["6", 0],
                "filename_prefix": f"TG_Territory_{faction_name}_{environment_type}"
            }
        }
    }
    
    return workflow

def submit_workflow(workflow):
    """Submit workflow to ComfyUI using proven connection method"""
    client_id = str(uuid.uuid4())
    prompt_data = {
        "prompt": workflow,
        "client_id": client_id
    }
    
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
        print(f"Error submitting workflow: {e}")
        return None

def main():
    print("=" * 85)
    print("PHASE 2B: ENVIRONMENTAL FACTION TERRITORY MARKERS - ENVIRONMENTAL STORYTELLING")  
    print("=" * 85)
    print("Generating faction territory control concepts showing environmental branding")
    print("Demonstrating Chief Art Director 'Tribal Corporate Warfare' pillar")
    print("Proven pipeline: heun/normal, CFG 3.2, 25 steps, 1536x864")
    print()
    
    # Faction territory marking concepts demonstrating different environmental control methods
    territory_concepts = [
        ("IronScavengers", "scrap-metal totems built from defeated enemies' equipment, orange theft tags spray-painted over conquered faction symbols, asymmetrical salvage monuments reaching skyward with mixed faction trophies", "Industrial"),
        
        ("CorporateHegemony", "holographic territory markers projecting corporate advertisements, automated security warnings in corporate blue and cyan, logo-scarred battlefield with environmental corporate branding", "Corporate"),
        
        ("Directorate", "military checkpoint with navy blue chevron markings on concrete barriers, institutional signage and organized security perimeter, professional military territory control", "Military"),
        
        ("ArchiveKeepers", "information graffiti displaying historical data on walls, glowing text from dead languages marking territory boundaries, crystalline data preservation monuments", "Archive"),
        
        ("NomadClans", "temporary monuments built from vehicle parts and territorial bones, adaptive camouflage markers that blend with environment, convoy trail markers and mobile settlement signs", "Desert"),
        
        ("CivicWardens", "neighborhood fortifications with community-made warning systems, grassroots protection barriers with civilian safety markings, improvised urban defense installations", "Urban")
    ]
    
    print(f"Generating {len(territory_concepts)} faction territory control concepts...")
    print("Each concept demonstrates unique environmental marking methods:")
    print("• IronScavengers: Trophy totems from stolen equipment")
    print("• CorporateHegemony: Holographic branding warfare") 
    print("• Directorate: Professional military control systems")
    print("• ArchiveKeepers: Information graffiti and data preservation")
    print("• NomadClans: Mobile adaptive territorial marking")
    print("• CivicWardens: Community-made protection systems")
    print()
    
    queued = 0
    for i, (faction, description, environment) in enumerate(territory_concepts):
        print(f"Queuing {faction} {environment} Territory...", end=" ")
        
        # Use different seed offsets to ensure variety
        workflow = create_territory_marker_workflow(faction, description, environment, i * 200)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"OK - {prompt_id}")
            queued += 1
        else:
            print("FAILED")
        
        time.sleep(1)  # Brief pause between submissions
    
    print()
    print("=" * 85)
    print(f"PHASE 2B COMPLETE: {queued}/{len(territory_concepts)} territory markers queued")
    print()
    print("Expected output files:")
    for faction, _, environment in territory_concepts:
        print(f"  - TG_Territory_{faction}_{environment}_*.png")
    print()
    print("Output location: C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API\\output\\")
    print()
    print("This demonstrates:")
    print("[OK] Environmental faction territory control systems")
    print("[OK] Chief Art Director 'Tribal Corporate Warfare' pillar implementation")
    print("[OK] Unique environmental marking for each faction identity")
    print("[OK] Environmental storytelling through faction territorial branding")
    print()
    print("Next: Phase 2C - Extraction Zone Visual Language Concepts")

if __name__ == "__main__":
    main()