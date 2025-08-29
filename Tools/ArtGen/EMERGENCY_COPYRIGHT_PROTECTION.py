#!/usr/bin/env python3
"""
EMERGENCY COPYRIGHT PROTECTION SYSTEM
Terminal Grounds - Chief Security Officer

CRITICAL SECURITY IMPLEMENTATION:
- Maximum copyright violation prevention
- Comprehensive brand blocking 
- Legal liability elimination
- Production-safe negative prompts

VERSION: Emergency 1.0
DATE: 2025-08-29
SECURITY LEVEL: MAXIMUM PROTECTION
"""

import json
import urllib.request
import time

# MAXIMUM SECURITY COPYRIGHT BLOCKING
COMPREHENSIVE_COPYRIGHT_BLOCKS = [
    # MAJOR GAME PUBLISHERS - COMPLETE BLOCKING
    "Activision", "Electronic Arts", "EA Games", "Ubisoft", "Blizzard Entertainment",
    "Valve Corporation", "Epic Games", "Riot Games", "2K Games", "Take-Two Interactive",
    "Bethesda", "ZeniMax", "Square Enix", "Bandai Namco", "Capcom", "Konami",
    
    # MAJOR GAME FRANCHISES - ZERO TOLERANCE
    "Call of Duty", "Modern Warfare", "Black Ops", "Warzone", "Battlefield",
    "Counter-Strike", "CS:GO", "CS2", "Valorant", "Apex Legends", "Fortnite",
    "PUBG", "Rainbow Six", "Siege", "Overwatch", "Destiny", "Halo",
    "Tom Clancy", "Ghost Recon", "The Division", "Splinter Cell",
    
    # UI/INTERFACE PROTECTION
    "professional game interface", "branded HUD", "copyrighted UI", "licensed game elements",
    "watermarks", "branded overlays", "trademarked symbols", "existing game assets",
    "AAA game UI", "professional game templates", "military shooter UI", 
    "tactical FPS interface", "corporate game branding", "HUD template",
    
    # MILITARY/TACTICAL PROTECTION  
    "military simulation interfaces", "professional defense contractor UI",
    "government interface designs", "branded military graphics",
    "copyrighted military symbols", "licensed tactical imagery",
    "defense industry UI", "professional tactical displays",
    
    # WEAPON/EQUIPMENT PROTECTION
    "real weapon brands", "licensed weapon designs", "manufacturer logos",
    "military contractor branding", "defense company logos", 
    "weapon manufacturer marks", "branded tactical equipment",
    
    # GENERIC PROTECTION
    "existing video game", "copyrighted designs", "trademarked content",
    "licensed assets", "branded content", "watermarked imagery",
    "professional overlay templates", "corporate interface designs"
]

def get_maximum_copyright_protection():
    """Generate comprehensive copyright-blocking negative prompt"""
    return ", ".join(COMPREHENSIVE_COPYRIGHT_BLOCKS)

def create_copyright_safe_weapon_workflow(faction_name, weapon_type, seed):
    """Create weapon concept with maximum copyright protection"""
    
    # SAFE POSITIVE PROMPT - Original designs only
    positive_prompt = f"original {weapon_type} concept art, {faction_name} faction weapon, custom Terminal Grounds universe design, original sci-fi weapon concept, fictional military equipment, unique game asset design, concept art illustration, original weapon design, Terminal Grounds aesthetic"
    
    # MAXIMUM COPYRIGHT PROTECTION
    negative_prompt = get_maximum_copyright_protection()
    
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
                "width": 1536,
                "height": 864, 
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 3.2,
                "sampler_name": "heun",
                "scheduler": "normal",
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
                "filename_prefix": f"TG_COPYRIGHT_SAFE_{faction_name}_{weapon_type}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def create_copyright_safe_ui_workflow(faction_name, seed):
    """Create UI concept with maximum copyright protection"""
    
    # SAFE POSITIVE PROMPT - Original Terminal Grounds only
    positive_prompt = f"original Terminal Grounds faction interface, {faction_name} custom UI design, original game interface concept, fictional military command screen, Terminal Grounds universe aesthetic, original HUD mockup, concept art interface design, sci-fi command interface"
    
    # MAXIMUM COPYRIGHT PROTECTION
    negative_prompt = get_maximum_copyright_protection()
    
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
                "width": 1536,
                "height": 864,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 3.2,
                "sampler_name": "heun", 
                "scheduler": "normal",
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
                "filename_prefix": f"TG_COPYRIGHT_SAFE_UI_{faction_name}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def generate_test_safe_assets():
    """Generate test assets with maximum copyright protection"""
    
    print("EMERGENCY COPYRIGHT PROTECTION - MAXIMUM SECURITY")
    print("=" * 70)
    print(f"BLOCKING {len(COMPREHENSIVE_COPYRIGHT_BLOCKS)} COPYRIGHT TERMS")
    print("=" * 70)
    
    # Test one faction UI to verify safety
    test_faction = "Directorate"
    seed = 12345
    
    print(f"Generating copyright-safe test UI for {test_faction}")
    
    workflow = create_copyright_safe_ui_workflow(test_faction, seed)
    
    try:
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                   data=data,
                                   headers={'Content-Type': 'application/json'})
        
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"SUCCESS: Test asset submitted (ID: {result.get('prompt_id', 'unknown')})")
        print("Waiting for generation completion...")
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("=" * 70)
    print("COPYRIGHT PROTECTION TEST COMPLETE")
    print("Check output for TG_COPYRIGHT_SAFE_UI_Directorate_* file")
    print("VERIFY NO BRANDED/COPYRIGHTED ELEMENTS BEFORE PROCEEDING")

if __name__ == "__main__":
    generate_test_safe_assets()