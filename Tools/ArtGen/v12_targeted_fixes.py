#!/usr/bin/env python3
"""
Terminal Grounds v1.2 - TARGETED 100% AAA FIXES
Focused regeneration of the 3 failing assets from v1.1 analysis

Based on v1.1 analysis:
- Corporate Plaza: Complete failure (0.64-0.66MB) - needs prompt redesign
- Security Checkpoint Clean_SciFi: Underperforming (0.69MB) - needs enhancement
- Target: Achieve 100% AAA quality (23/24 assets minimum)
"""
import json
import urllib.request
import time
import uuid
import sys
import os
from pathlib import Path

# Fix Windows Unicode encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# v1.2 ENHANCED parameters for problem assets
V12_ENHANCED_PARAMS = {
    "seed": 94887,
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 4.0,        # Increased from 3.8 for better detail
    "steps": 40,       # Increased from 32 for problem cases
    "width": 1792,
    "height": 1024
}

def create_v12_workflow(location, style, seed_offset):
    """Create v1.2 enhanced workflow for targeted fixes"""
    
    # v1.2 TARGETED FIXES - Redesigned prompts for failing assets
    location_prompts = {
        # REDESIGNED: Corporate Plaza → Corporate Lobby Interior (proven successful)
        "Corporate_Lobby_Interior_Enhanced": "masterpiece quality Terminal Grounds corporate lobby interior, post-cascade corporate decay with active survivor community, reception desk converted to well-organized supply distribution center with clear inventory labels and duty schedules, emergency lighting enhanced with practical work lamps and personal task lighting, executive offices transformed into inhabited sleeping quarters with personal belongings and daily use evidence, conference rooms repurposed as community meeting spaces with message boards and survivor communications, elevator banks converted to secure storage with visible organization systems, marble floors showing traffic patterns from daily community life, corporate furniture arranged for practical living with blankets and personal items, professional security barriers made from office materials, supply stockpiles organized for rationing with clear distribution schedules, evidence of established community leadership and daily survival routines, inhabited corporate transformation",
        
        # ENHANCED: Security Checkpoint with increased complexity
        "Security_Checkpoint_Enhanced": "masterpiece quality Terminal Grounds faction security checkpoint, heavily detailed active security installation with multiple guard stations showing personal belongings and shift rotation evidence, sophisticated scanning equipment with visible calibration certificates and maintenance logs, reinforced security barriers with faction identification systems actively processing travelers, surveillance monitors displaying live feeds with timestamp overlays, guard posts equipped with personal duty lockers containing shift supplies, advanced access control terminals with user interface displays and recent activity logs, weapon inspection stations with detailed procedural signage, visitor registration desks with completed forms and identification verification systems, security briefing areas with tactical maps and current threat assessments, evidence of continuous shift changes with coffee stations and personal items at each post, professional authority presence with inhabited command structure"
    }
    
    # Enhanced style modifiers for v1.2
    style_modifiers = {
        "Clean_SciFi": ", pristine professional functionality with complex technical details, well-maintained operational equipment showing daily professional use, organized workspace efficiency with personal customization touches, clean surfaces displaying active work patterns and professional modifications, precision engineering with user interface complexity, systematic organization with inhabited professional touches, technical readouts and professional monitoring systems",
        
        "Gritty_Realism": ", weathered professional functionality with complex survival adaptations, battle-tested equipment showing expert maintenance and modification, harsh environment adaptations with ingenious survival solutions, worn surfaces displaying extensive use patterns and survival modifications, rugged engineering with practical field modifications, organized scavenged materials showing resourceful adaptation, improvised monitoring systems and survival networking"
    }
    
    # Build enhanced prompt
    base_prompt = location_prompts.get(location, f"Terminal Grounds {location}")
    style_modifier = style_modifiers.get(style, "")
    
    # v1.2 universal enhancements
    v12_enhancements = ", ultra-high detail environmental complexity, crystal clear signage with readable text displays, professional lighting with authentic technical accuracy, masterpiece level environmental storytelling, photorealistic surface textures with comprehensive material detail, sharp focus with perfect exposure balance, AAA game environment quality with lived-in authenticity"
    
    positive_prompt = base_prompt + style_modifier + v12_enhancements
    
    # v1.2 ENHANCED negative prompts - more aggressive quality enforcement
    negative_prompt = "blurry, low quality, pixelated, distorted, bad anatomy, bad lighting, oversaturated, undersaturated, generic, sterile, empty, lifeless, bland, boring, repetitive, copy-paste, artificial, fake, plastic, clean room, laboratory sterile, no character, no personality, no human presence, no wear patterns, no use evidence, blurry text, illegible text, garbled text, nonsensical text, generic sci-fi text, placeholder text, lorem ipsum, corrupted text, fuzzy lettering, low resolution text, pixelated text, distorted signage, soft focus, washed out, watermark, signature, modern cars, contemporary clothing, smartphones, modern technology, fantasy elements, magic, supernatural, cartoon, anime, illustration, abstract, gradient, overexposed, blown highlights, underexposed, muddy shadows, low contrast, flat lighting, amateur photography, poor composition, tilted horizon, motion blur, depth of field issues, chromatic aberration, lens flare"
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "FLUX1\\\\flux1-dev-fp8.safetensors"
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
                "width": V12_ENHANCED_PARAMS["width"],
                "height": V12_ENHANCED_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": V12_ENHANCED_PARAMS["seed"] + seed_offset,
                "steps": V12_ENHANCED_PARAMS["steps"],
                "cfg": V12_ENHANCED_PARAMS["cfg"],
                "sampler_name": V12_ENHANCED_PARAMS["sampler"],
                "scheduler": V12_ENHANCED_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_V12_FIX_{location}_{style}"
            }
        }
    }
    
    return workflow

def submit_workflow(workflow, location, style):
    """Submit workflow to ComfyUI"""
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
        print(f"Error submitting {location} {style}: {e}")
        return None

def generate_v12_targeted_fixes():
    """Generate v1.2 targeted fixes for the 3 failing assets"""
    print("TERMINAL GROUNDS v1.2 - TARGETED 100% AAA FIXES")
    print("=" * 55)
    print("Fixing the 3 failing assets from v1.1 analysis:")
    print("1. Corporate Plaza → Corporate Lobby Interior Enhanced")  
    print("2. Security Checkpoint Clean_SciFi → Enhanced Detail")
    print("Enhanced Parameters: 40 steps, CFG 4.0, aggressive negative prompts")
    print()
    
    # Target the specific failing cases
    fix_targets = [
        ("Corporate_Lobby_Interior_Enhanced", "Clean_SciFi"),   # Replace Corporate Plaza Clean
        ("Corporate_Lobby_Interior_Enhanced", "Gritty_Realism"), # Replace Corporate Plaza Gritty
        ("Security_Checkpoint_Enhanced", "Clean_SciFi")          # Replace Security Clean base
    ]
    
    queued = 0
    for i, (location, style) in enumerate(fix_targets):
        seed_offset = 1000 + i  # Use different seed range for v1.2
        
        workflow = create_v12_workflow(location, style, seed_offset)
        prompt_id = submit_workflow(workflow, location, style)
        
        if prompt_id:
            print(f"✅ Queued: {location} ({style}) - {prompt_id}")
            queued += 1
        else:
            print(f"❌ Failed: {location} ({style})")
        
        time.sleep(0.5)
    
    print()
    print("=" * 55)
    print(f"v1.2 TARGETED FIXES: {queued}/3 queued successfully")
    print()
    print("v1.2 Enhanced Features:")
    print("[+] 40 steps (increased from 32) for maximum detail")
    print("[+] CFG 4.0 (increased from 3.8) for enhanced text clarity")
    print("[+] Redesigned Corporate Plaza → Corporate Lobby Interior")
    print("[+] Enhanced Security Checkpoint with complex details")
    print("[+] Aggressive negative prompts for quality enforcement")
    print("[+] Targeted fixes preserve successful v1.1 assets")
    print()
    print("Expected Outcome: 100% AAA Quality Achievement")
    print("Files will be named: TG_V12_FIX_[Location]_[Style]_*.png")

if __name__ == "__main__":
    generate_v12_targeted_fixes()