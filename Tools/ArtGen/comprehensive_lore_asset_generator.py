#!/usr/bin/env python3
"""
Comprehensive Lore-Integrated Asset Generator
Applies proven sharp parameters with deep lore integration for Terminal Grounds
Generates diverse assets across all project categories with canonical accuracy
"""

import json
import urllib.request
import time
import uuid
import random

# PROVEN SHARP PARAMETERS - Based on successful TG_Weapon_Sharp generation
SHARP_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.5,        # Enhanced for sharpness and lore adherence
    "steps": 30,       # Enhanced for detail resolution
    "width": 1536,
    "height": 864
}

# COMPREHENSIVE FACTION LORE INTEGRATION
FACTION_LORE = {
    "Directorate": {
        "psychology": "military precision, corporate authority, regulation-obsessed bureaucracy",
        "visual_language": "angular geometric design, blue-grey corporate colors, standardized equipment with regulation markings",
        "condition": "well-maintained, regulation specification, proper military maintenance",
        "details": "stamped serial numbers, regulation modifications, prescribed weathering patterns, authorized equipment only"
    },
    
    "Free77": {
        "psychology": "mercenary professionalism, contractor pragmatism, employer-neutral reliability",
        "visual_language": "modular swappable components, red accent colors, professional field modifications",
        "condition": "battle-tested reliability, professional maintenance, field-proven durability",
        "details": "employer logo panels, contractor identification, invoice tallies, rate schedules, professional scope markings"
    },
    
    "IronScavengers": {
        "psychology": "trophy warfare, theft pride, functional ugliness philosophy",
        "visual_language": "mismatched stolen components, trophy mounting, layered modifications, crude but effective repairs",
        "condition": "salvaged equipment, improvised repairs, welded trophy elements, scavenged parts",
        "details": "defeated enemy insignia welded on, visible serial numbers from multiple origins, duct tape modifications, trophy dog tags"
    },
    
    "CivicWardens": {
        "psychology": "community protection, civilian authority, neighborhood watch mentality",
        "visual_language": "civilian equipment militarized, community protection markings, utilitarian modifications",
        "condition": "improvised armor additions, community workshop repairs, neighborhood identification",
        "details": "community watch stickers, spray-painted unit numbers, zip-tied attachments, donated equipment mix"
    },
    
    "NomadClans": {
        "psychology": "convoy survival, tribal identity, overland expedition heritage",
        "visual_language": "tribal weathering patterns, convoy modifications, survival equipment integration",
        "condition": "road-worn durability, convoy maintenance, tribal customization, survival adaptations",
        "details": "tribal markings, convoy discipline indicators, survival equipment, road captain insignia, blessed components"
    }
}

# COMPREHENSIVE ASSET CATEGORIES WITH LORE INTEGRATION
ASSET_CATEGORIES = {
    "weapons": {
        "types": ["assault_rifle", "sniper_rifle", "submachine_gun", "shotgun", "machine_gun", "sidearm"],
        "prompt_base": "professional weapon concept art, detailed mechanical design, game asset quality",
        "lore_focus": "weapon customization, faction modifications, combat wear patterns"
    },
    
    "vehicles": {
        "types": ["combat_vehicle", "transport_truck", "reconnaissance_ATV", "armored_personnel_carrier", "technical_vehicle"],
        "prompt_base": "military vehicle concept art, detailed mechanical engineering, orthographic technical view",
        "lore_focus": "faction modifications, combat adaptations, survival equipment"
    },
    
    "equipment": {
        "types": ["combat_armor", "field_gear", "communication_device", "tactical_equipment", "survival_kit"],
        "prompt_base": "tactical equipment concept art, detailed functional design, field-tested appearance",
        "lore_focus": "field modifications, faction customization, practical wear patterns"
    },
    
    "architecture": {
        "types": ["fortified_outpost", "supply_depot", "command_bunker", "checkpoint_facility", "territorial_marker"],
        "prompt_base": "military architecture concept art, defensive design, environmental integration",
        "lore_focus": "faction territorial control, defensive modifications, strategic positioning"
    },
    
    "environments": {
        "types": ["battlefield_terrain", "urban_combat_zone", "industrial_facility", "wasteland_outpost", "underground_complex"],
        "prompt_base": "environment concept art, atmospheric lighting, tactical positioning considerations",
        "lore_focus": "territorial control, faction influence, strategic value, environmental storytelling"
    }
}

def create_lore_integrated_workflow(category, asset_type, faction, seed, variant_name):
    """Create workflow with deep lore integration and sharp parameters"""
    
    faction_data = FACTION_LORE[faction]
    category_data = ASSET_CATEGORIES[category]
    
    # Build comprehensive lore-integrated prompt
    base_prompt = category_data["prompt_base"]
    psychology = faction_data["psychology"]
    visual_language = faction_data["visual_language"]
    condition = faction_data["condition"]
    details = faction_data["details"]
    lore_focus = category_data["lore_focus"]
    
    # Comprehensive positive prompt with lore integration
    positive_prompt = f"ultra sharp {base_prompt}, {asset_type} showing {psychology}, {visual_language}, {condition}, {lore_focus}, {details}, Terminal Grounds faction aesthetic, crisp detailed game asset concept, razor sharp orthographic view, crystal clear technical details, professional concept art quality, realistic military specification"
    
    # Enhanced negative prompt for sharp, lore-accurate results
    negative_prompt = "blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, generic military equipment, cartoon style, anime, fantasy elements, clean factory condition, unrealistic wear, impossible technology"
    
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
                "width": SHARP_PARAMS["width"],
                "height": SHARP_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": SHARP_PARAMS["steps"],
                "cfg": SHARP_PARAMS["cfg"],
                "sampler_name": SHARP_PARAMS["sampler"],
                "scheduler": SHARP_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_LORE_{category.upper()}_{faction}_{variant_name}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_comprehensive_assets():
    """Generate 10 diverse assets across project categories with full lore integration"""
    
    # Carefully selected asset mix for comprehensive coverage
    asset_queue = [
        ("weapons", "assault_rifle", "Directorate", "RegulationCarbine"),
        ("weapons", "sniper_rifle", "Free77", "ContractorRifle"),  
        ("vehicles", "combat_vehicle", "IronScavengers", "TrophyTechnical"),
        ("vehicles", "transport_truck", "NomadClans", "ConvoyHauler"),
        ("equipment", "combat_armor", "CivicWardens", "CommunityProtection"),
        ("equipment", "tactical_equipment", "Directorate", "RegulationKit"),
        ("architecture", "fortified_outpost", "IronScavengers", "ScavengerStronghold"),
        ("architecture", "supply_depot", "Free77", "ContractorBase"),
        ("environments", "urban_combat_zone", "CivicWardens", "NeighborhoodBattle"),
        ("environments", "industrial_facility", "NomadClans", "RefugeeFacility")
    ]
    
    base_seed = 200000  # New seed range for lore-integrated generation
    
    print("COMPREHENSIVE LORE-INTEGRATED ASSET GENERATION")
    print("Enhanced Parameters + Deep Faction Integration")
    print("=" * 70)
    print()
    
    for i, (category, asset_type, faction, variant_name) in enumerate(asset_queue):
        seed = base_seed + (i * 1000)  # Good seed spacing for variety
        
        print(f"{i+1:2d}. {category.upper()}: {faction} {variant_name}")
        print(f"    Type: {asset_type}")
        print(f"    Lore: {FACTION_LORE[faction]['psychology']}")
        print(f"    Seed: {seed}")
        
        workflow = create_lore_integrated_workflow(category, asset_type, faction, seed, variant_name)
        
        try:
            # Submit to ComfyUI
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            prompt_id = result.get('prompt_id', 'unknown')
            print(f"    -> Submitted successfully (ID: {prompt_id})")
            
        except Exception as e:
            print(f"    -> ERROR: {e}")
            
        print()
        
        # Proper spacing between submissions
        time.sleep(0.5)
    
    print("=" * 70)
    print("COMPREHENSIVE ASSET GENERATION COMPLETE")
    print("ENHANCED PARAMETERS:")
    print(f"  Sampler: {SHARP_PARAMS['sampler']}")
    print(f"  Scheduler: {SHARP_PARAMS['scheduler']}")
    print(f"  CFG: {SHARP_PARAMS['cfg']} (enhanced for sharpness)")
    print(f"  Steps: {SHARP_PARAMS['steps']} (enhanced for detail)")
    print(f"  Resolution: {SHARP_PARAMS['width']}x{SHARP_PARAMS['height']}")
    print()
    print("LORE INTEGRATION FEATURES:")
    print("  - Faction-specific psychology integration")
    print("  - Visual language consistency")
    print("  - Canonical condition and wear patterns")
    print("  - Authentic faction modification details")
    print()
    print("ASSET DIVERSITY:")
    print("  - 2x Weapons (Directorate Carbine, Free77 Sniper)")
    print("  - 2x Vehicles (Scavenger Technical, Nomad Hauler)")
    print("  - 2x Equipment (Warden Armor, Directorate Kit)")
    print("  - 2x Architecture (Scavenger Outpost, Free77 Base)")
    print("  - 2x Environments (Warden Urban, Nomad Industrial)")
    print()
    print("Check output directory for: TG_LORE_*")

if __name__ == "__main__":
    generate_comprehensive_assets()