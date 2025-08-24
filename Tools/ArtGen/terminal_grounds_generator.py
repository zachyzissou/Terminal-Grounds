#!/usr/bin/env python3
"""
Terminal Grounds Asset Generator v0.9 - Enhanced Production System
Evolved from 92% technical success to enhanced lore accuracy and visual quality

Built on proven heun/normal/CFG 3.2 breakthrough parameters
Enhanced with Terminal Grounds-specific lore integration
Version 0.9: Production deployment with enhanced prompts and quality assurance
"""
import json
import urllib.request
import time
import uuid
import random
import itertools
import argparse
import subprocess
from pathlib import Path

# Perfect parameters from today's successful first generation
PERFECT_PARAMS = {
    "seed": 94887,
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.2,
    "steps": 25,
    "width": 1536,
    "height": 864
}

def get_lore_prompt(region_id, faction_id=None, lens="50mm lens, eye-level", composition="deep perspective vanishing point"):
    """Use existing Build-LorePrompt.ps1 to generate lore-accurate prompts"""
    ps_script = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/Build-LorePrompt.ps1")
    
    if not ps_script.exists():
        return None
        
    cmd = [
        "powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script),
        "-RegionId", region_id,
        "-Lens", lens,
        "-Composition", composition,
        "-IncludeStyleCapsule"
    ]
    
    if faction_id:
        cmd.extend(["-FactionId", faction_id])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error calling Build-LorePrompt.ps1: {e}")
    
    return None

def create_workflow(location, style, seed_offset, angle="Wide", lighting="Ambient", use_lore_system=False):
    """Create workflow with dynamic variations while keeping proven structure"""
    
    # Map locations to lore region IDs
    lore_mapping = {
        "Metro_Maintenance_Corridor": "REG_METRO_A",
        "IEZ_Facility_Interior": "REG_IEZ",
        "Tech_Wastes_Exterior": "REG_TECH_WASTES",
        "Corporate_Lobby_Interior": None,  # Not in lore system
        "Underground_Bunker": None,  # Not in lore system
        "Security_Checkpoint": None  # Not in lore system
    }
    
    # Try to use lore system if requested and available
    if use_lore_system and location in lore_mapping and lore_mapping[location]:
        lore_prompt = get_lore_prompt(lore_mapping[location])
        if lore_prompt:
            positive_prompt = lore_prompt
            # Add our variations to the lore prompt
            angle_modifier = camera_angles.get(angle, "")
            lighting_modifier = lighting_moods.get(lighting, "")
            positive_prompt += angle_modifier + lighting_modifier
        else:
            use_lore_system = False  # Fallback to manual prompts
    
    # If not using lore system, use manual prompts
    if not use_lore_system:
        # Enhanced location prompts with Terminal Grounds lore integration (v0.9)
        location_prompts = {
        "Metro_Maintenance_Corridor": "Terminal Grounds Metro_Maintenance_Corridor, underground maintenance tunnel system, Warden toll territory neutral ground, arched platforms, service alcoves, grated vents, hazard chevrons, weathered concrete, flaked paint, oily puddles, conduit bundles, warm practicals, cool fill, shafted dust through vents, post-cascade world, 6 months after IEZ disaster",
        
        "IEZ_Facility_Interior": "Terminal Grounds IEZ_Facility_Interior, Interdiction Exclusion Zone outer ring facility, post-cascade damage visible, phase-sheared surfaces, EMP damage scorch patterns, tilted structural elements, alien tech influence, charged haze, reality distortion effects, unstable lighting, slagged steel, cracked surfaces, blue-ash dust contamination, dangerous facility showing cascade effects",
        
        "Tech_Wastes_Exterior": "Terminal Grounds Tech_Wastes_Exterior, de-industrial wasteland with stuttering automated factories, autolines, robot arms, cable trellises, coolant plumes, abandoned conveyor systems, industrial fog, warning strobes through haze, toxic environment, oxidized alloys, stained polymer panels, glass dust, rusted machinery, post-industrial decay",
        
        "Corporate_Lobby_Interior": "Terminal Grounds Corporate_Lobby_Interior, abandoned corporate facility interior, post-cascade corporate decay, shattered glass walls, damaged reception areas, emergency power lighting, corporate debris, emergency lighting, dust motes, abandoned corporate authority, cracked marble floors, broken glass panels, emergency lighting systems, resource scarcity markers",
        
        "Underground_Bunker": "Terminal Grounds Underground_Bunker, military fortification, Directorate or abandoned military installation, reinforced blast doors, military stenciling, emergency systems, defensive positions, emergency lighting, military discipline, fortified security, reinforced concrete, heavy steel doors, military-grade equipment",
        
        "Security_Checkpoint": "Terminal Grounds Security_Checkpoint, faction security installation, access control facility, scanning equipment, guard posts, security barriers, faction identification systems, institutional authority, surveillance equipment, controlled access, security scanners, reinforced barriers, identification systems"
    }
    
    # Enhanced style modifiers with Terminal Grounds context (v0.9)
    style_modifiers = {
        "Clean_SciFi": ", clean sci-fi industrial aesthetic, functional design, military precision, well-maintained equipment, operational status, clean surfaces, structured industrial lighting, practical illumination systems, precision engineering, sleek panels, minimal wear patterns",
        "Gritty_Realism": ", gritty post-apocalyptic realism, scavenger repairs, survival adaptation, weathered surfaces, believable aging, natural wear patterns, scavenged components, harsh practical lighting, emergency power systems, makeshift illumination, visible repairs, improvised modifications, resource scarcity indicators"
    }
    
    # Camera angle variations
    camera_angles = {
        "Wide": ", wide angle shot, establishing shot, full environment view",
        "Detail": ", detailed close-up view, architectural details, surface textures",
        "Perspective": ", dramatic perspective, dynamic angle, cinematic composition",
        "Overhead": ", overhead view, bird's eye perspective, layout view"
    }
    
    # Lighting variations
    lighting_moods = {
        "Ambient": ", ambient lighting, soft natural illumination",
        "Dramatic": ", dramatic lighting, strong shadows, high contrast",
        "Emergency": ", emergency lighting, red alert, warning systems",
        "Atmospheric": ", atmospheric lighting, volumetric fog, moody atmosphere"
    }
    
    # Build enhanced prompt with lore integration (v0.9)
    base_prompt = location_prompts.get(location, f"Terminal Grounds {location}, professional game environment")
    style_modifier = style_modifiers.get(style, "")
    angle_modifier = camera_angles.get(angle, "")
    lighting_modifier = lighting_moods.get(lighting, "")
    
    # Add universal Terminal Grounds context
    tg_context = ", post-cascade world, 6 months after IEZ disaster, resource scarcity, professional game art concept, high detail environmental design, sharp focus crisp edges, fine surface textures, balanced exposure, architectural visualization quality"
    
    positive_prompt = base_prompt + style_modifier + angle_modifier + lighting_modifier + tg_context
    
    # Enhanced negative prompt to prevent common issues (v0.9)
    negative_prompt = "text, words, letters, numbers, UI elements, interface, HUD, overlays, logos, signs, typography, screen text, digital displays, blurry, soft focus, low quality, abstract, gradient, overexposed, blown highlights, washed out, watermark, signature, modern cars, contemporary clothing, smartphones, modern technology, fantasy elements, magic, supernatural, cartoon, anime, illustration"
    
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
                "width": PERFECT_PARAMS["width"],
                "height": PERFECT_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": PERFECT_PARAMS["seed"] + seed_offset,
                "steps": PERFECT_PARAMS["steps"],
                "cfg": PERFECT_PARAMS["cfg"],
                "sampler_name": PERFECT_PARAMS["sampler"],
                "scheduler": PERFECT_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_PERFECT_{location}_{style}_{angle}_{lighting}"
            }
        }
    }
    
    return workflow

def submit_workflow(workflow, location, style, angle="Wide", lighting="Ambient"):
    """Submit workflow to ComfyUI with variation info"""
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
            prompt_id = result.get('prompt_id')
            return prompt_id
    except Exception as e:
        print(f"Error submitting {location}: {e}")
        return None

def generate_terminal_grounds_assets():
    """Generate Terminal Grounds assets with enhanced lore accuracy (v0.9)"""
    print("TERMINAL GROUNDS ASSET GENERATOR v0.9 - ENHANCED PRODUCTION SYSTEM")
    print("=" * 70)
    print("Enhanced with Terminal Grounds lore integration and quality improvements")
    print()
    
    # All validated locations - now with enhanced lore prompts
    locations = [
        "Metro_Maintenance_Corridor",        # Enhanced: Warden toll territory, arched platforms
        "IEZ_Facility_Interior",            # Enhanced: Post-cascade damage, alien tech influence  
        "Tech_Wastes_Exterior",             # Enhanced: Autolines, robot arms, cable trellises
        "Corporate_Lobby_Interior",         # Enhanced: Post-cascade decay, emergency lighting
        "Underground_Bunker",               # Enhanced: Military stenciling, Directorate installation
        "Security_Checkpoint"               # Enhanced: Faction security, surveillance equipment
    ]
    
    styles = ["Clean_SciFi", "Gritty_Realism"]
    
    # Select variations for dynamic generation
    angles = ["Wide", "Detail", "Perspective"]  # Skip Overhead for now
    lightings = ["Ambient", "Dramatic", "Atmospheric"]  # Skip Emergency for now
    
    # Calculate totals
    queued = 0
    # For full matrix: locations × styles × angles × lightings  
    # For manageable batch: locations × styles × 1 angle × 1 lighting
    total = len(locations) * len(styles) * 1 * 1  # Start simple
    
    print(f"Generating {total} enhanced lore environments with variations...")
    print("Seed base: 94887, heun/normal, CFG 3.2, 25 steps, 1536x864")
    print("Enhanced features: Terminal Grounds lore integration, post-cascade context")
    print("Variations: Multiple angles and lighting moods")
    print()
    
    for i, location in enumerate(locations):
        for j, style in enumerate(styles):
            # Use different angle/lighting per location for variety
            angle = angles[i % len(angles)]
            lighting = lightings[i % len(lightings)]
            
            seed_offset = (i * len(styles)) + j
            
            workflow = create_workflow(location, style, seed_offset, angle, lighting)
            prompt_id = submit_workflow(workflow, location, style, angle, lighting)
            
            if prompt_id:
                print(f"Queued: {location} ({style}) - {prompt_id}")
                queued += 1
            else:
                print(f"Failed: {location} ({style})")
            
            time.sleep(0.5)  # Brief pause
    
    print()
    print("=" * 55)
    print(f"BATCH COMPLETE: {queued}/{total} assets queued")
    print()
    print("Output files will be named:")
    print("TG_PERFECT_[Location]_[Style]_[Angle]_[Lighting]_*.png")
    print()
    print("v0.9 Enhanced Features:")
    print("✓ Terminal Grounds lore integration")
    print("✓ Post-cascade environmental context") 
    print("✓ Location-specific atmospheric details")
    print("✓ Enhanced style differentiation")
    print("✓ Improved negative prompt filtering")
    print("✓ Same proven technical parameters (heun/normal/CFG 3.2)")

if __name__ == "__main__":
    generate_terminal_grounds_assets()