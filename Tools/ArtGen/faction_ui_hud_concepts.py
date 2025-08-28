#!/usr/bin/env python3
"""
ENHANCED Faction UI/HUD Interface Concept Generator
Improved: Professional game development approach with original design focus
Terminal Grounds authentic faction interface psychology
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

def create_ui_workflow(faction_name, ui_desc, design_philosophy, seed):
    """Create UI/HUD concept with ENHANCED professional game development approach"""
    
    # ENHANCED: Professional game UI development with faction authenticity
    positive_prompt = f"professional tactical interface design for Terminal Grounds, {ui_desc}, {design_philosophy}, military-inspired user interface, faction-branded interface elements, clean readable typography, authentic tactical display design, professional game UI development, original interface concept art, custom game interface design, detailed UI mockup with faction personality"
    
    # TARGETED: Block only problematic sources while allowing professional inspiration
    negative_prompt = "call of duty screenshots, battlefield interface copies, apex legends UI, overwatch interface, existing game screenshots, copyrighted game assets, trademarked UI elements, placeholder lorem ipsum text, unfinished mockups, amateur interface design, generic mobile app UI, consumer software interface, cartoon UI elements"
    
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
    print("ENHANCED FACTION UI/HUD GENERATOR")
    print("Professional Game Development with Faction Authenticity")
    print("=" * 60)
    print()
    
    # ENHANCED: Professional UI concepts with faction-specific design philosophy
    ui_concepts = [
        # Iron Scavengers - Resourceful improvisation
        ("IronScavengers_HUD", 
         "adaptive interface combining salvaged systems from multiple sources, different UI elements in various colors and fonts representing scavenged components, warning systems in multiple languages, some display elements rotated from improper installation, functionality over form design philosophy",
         "improvised tech aesthetic inspired by real-world field modifications and emergency systems"),
        
        # Corporate - Professional brand integration
        ("Corporate_HUD", 
         "sleek professional interface with integrated corporate branding elements, cost-tracking displays for ammunition and resources, health monitoring with medical division logos, corporate efficiency metrics, stock market integration in peripheral displays",
         "modern enterprise software design language with military tactical overlays"),
        
        # Directorate - Military authority
        ("Directorate_HUD", 
         "harsh military command interface in regulation green monochrome, official authorization codes required for advanced functions, automatic damage and casualty reporting systems, kill tracking with unit identification, regulation military stencil typography throughout",
         "authentic military command and control system design inspired by real defense interfaces"),
        
        # Free77 - Modular professionalism
        ("Free77_HUD", 
         "modular contractor interface with client-customizable color schemes, QR code integration for service rates and contracts, real-time cost calculation for ammunition and equipment, contract completion tracking, invoice generation systems",
         "professional freelancer software meets tactical interface design"),
        
        # Nomad Clans - Survival community
        ("NomadClans_HUD", 
         "community-focused interface with hand-carved icon aesthetics, fuel and water resource tracking prominently displayed, family communications channels, route planning with community hazard markers, equipment repair status for survival",
         "survival community software with handmade aesthetic touches and family-oriented design"),
        
        # Archive Keepers - Information warfare
        ("ArchiveKeepers_HUD", 
         "information-dense interface with scrolling data streams, target personal history and threat assessment displays, ammunition tracking with data virus payload status, knowledge database access with security clearance levels, detailed analytics on all interactions",
         "advanced information warfare interface inspired by intelligence analysis software"),
        
        # Civic Wardens - Neighborhood protection  
        ("CivicWardens_HUD",
         "community watch interface with neighborhood spray-paint styling, local radio communication channels, civilian safe zone mapping, shared resource tracking for community ammunition, volunteer status and local area patrol assignments",
         "community volunteer software with neighborhood watch and emergency response design elements")
    ]
    
    queued = 0
    seed_base = 98333  # Different seed base for enhanced version
    
    for i, (ui_name, description, design_philosophy) in enumerate(ui_concepts):
        seed = seed_base + (i * 173)
        print(f"Generating ENHANCED {ui_name}...")
        print(f"  Interface: {description[:50]}...")
        print(f"  Philosophy: {design_philosophy[:40]}...")
        
        workflow = create_ui_workflow(ui_name, description, design_philosophy, seed)
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK - {prompt_id}")
            queued += 1
        else:
            print("  FAILED")
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"ENHANCED UI GENERATION COMPLETE: {queued}/7")
    print("Professional game development with authentic faction identity")

if __name__ == "__main__":
    main()