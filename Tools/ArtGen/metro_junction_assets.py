#!/usr/bin/env python3
"""
Metro Junction Asset Generator - Terminal Grounds Map Creation
Generates subway platforms, metro stations, and faction-specific areas for Metro Junction map.

Based on proven PERFECT_PARAMS from terminal_grounds_generator.py (92% success rate)
"""
import json
import urllib.request
import time
import uuid
import random
import os
import sys
from pathlib import Path

# Fix Windows Unicode encoding issues
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

# PROVEN PARAMETERS from terminal_grounds_generator.py
PERFECT_PARAMS = {
    "seed": 94887,
    "sampler": "heun", 
    "scheduler": "normal",
    "cfg": 3.2,
    "steps": 25,
    "width": 1536,
    "height": 864
}

# ComfyUI API settings
COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")

def create_workflow(prompt_text, negative_prompt, seed_offset=0):
    """Create 7-node workflow structure (proven from terminal_grounds_generator.py)"""
    
    workflow = {
        "1": {
            "inputs": {
                "text": prompt_text,
                "clip": ["4", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "2": {
            "inputs": {
                "text": negative_prompt,
                "clip": ["4", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {
                "seed": PERFECT_PARAMS["seed"] + seed_offset,
                "steps": PERFECT_PARAMS["steps"],
                "cfg": PERFECT_PARAMS["cfg"],
                "sampler_name": PERFECT_PARAMS["sampler"],
                "scheduler": PERFECT_PARAMS["scheduler"],
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["1", 0],
                "negative": ["2", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "FLUX1/flux1-dev-fp8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": PERFECT_PARAMS["width"],
                "height": PERFECT_PARAMS["height"],
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {
                "filename_prefix": "TG_MetroJunction",
                "images": ["6", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    return workflow

# Metro Junction specific prompts
METRO_JUNCTION_PROMPTS = {
    "subway_platform_directorate": {
        "positive": "Underground metro subway platform, blue corporate lighting, Directorate military checkpoints, security barriers, clean futuristic design, curved archway ceiling, train tracks visible, professional corporate aesthetics, authoritarian atmosphere, digital display boards, security cameras, 50mm lens, eye-level perspective",
        "negative": "gibberish text, scrambled letters, unreadable signage, blurry, low quality, amateur, cartoon, anime, oversaturated, people, trains in motion"
    },
    "subway_platform_free77": {
        "positive": "Underground metro subway platform, red resistance lighting, Free77 graffiti and propaganda posters, makeshift barriers, weathered industrial design, curved concrete ceiling, abandoned train tracks, rebel encampment aesthetic, resistance atmosphere, improvised equipment, 50mm lens, eye-level perspective",
        "negative": "gibberish text, scrambled letters, unreadable signage, blurry, low quality, amateur, cartoon, anime, oversaturated, people, active trains"
    },
    "metro_junction_central": {
        "positive": "Large underground metro junction hub, multiple track convergence, central platform area, mixed corporate and resistance elements, contested territory aesthetic, dramatic lighting from above, curved tunnel entrances, industrial architecture, territorial control point, strategic location, 50mm lens, elevated perspective",
        "negative": "gibberish text, scrambled letters, unreadable signage, blurry, low quality, amateur, cartoon, anime, oversaturated, people"
    },
    "metro_extraction_point": {
        "positive": "Metro platform extraction zone, territorial control interface, faction boundary markers, extraction equipment, secure departure area, dramatic atmospheric lighting, curved metro tunnel architecture, territorial influence visualization, strategic exit point, 50mm lens, wide perspective",
        "negative": "gibberish text, scrambled letters, unreadable signage, blurry, low quality, amateur, cartoon, anime, oversaturated, people, moving vehicles"
    }
}

def submit_workflow(workflow):
    """Submit workflow to ComfyUI API"""
    try:
        prompt_data = {"prompt": workflow, "client_id": str(uuid.uuid4())}
        data = json.dumps(prompt_data).encode('utf-8')
        
        req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        if 'prompt_id' in result:
            print(f"OK: Submitted workflow, prompt_id: {result['prompt_id']}")
            return True
        else:
            print(f"FAILED: No prompt_id in response: {result}")
            return False
            
    except Exception as e:
        print(f"FAILED: Workflow submission error: {e}")
        return False

def generate_metro_junction_assets():
    """Generate all Metro Junction assets using proven parameters"""
    
    print("=== Metro Junction Asset Generation ===")
    print(f"Parameters: {PERFECT_PARAMS}")
    print(f"Output Directory: {OUTPUT_DIR}")
    
    success_count = 0
    total_count = 0
    
    for asset_name, prompts in METRO_JUNCTION_PROMPTS.items():
        print(f"\nGenerating {asset_name}...")
        
        # Generate both Clean SciFi and Gritty Realism variants
        styles = ["Clean_SciFi", "Gritty_Realism"]
        
        for i, style in enumerate(styles):
            if style == "Clean_SciFi":
                style_modifier = ", clean futuristic aesthetic, bright professional lighting, pristine surfaces"
            else:
                style_modifier = ", gritty industrial atmosphere, weathered surfaces, dramatic shadows, worn materials"
            
            enhanced_positive = prompts["positive"] + style_modifier
            seed_offset = (total_count * len(styles)) + i
            
            workflow = create_workflow(enhanced_positive, prompts["negative"], seed_offset)
            
            if submit_workflow(workflow):
                success_count += 1
                print(f"  -> {asset_name}_{style}: SUCCESS")
            else:
                print(f"  -> {asset_name}_{style}: FAILED")
            
            total_count += 1
            time.sleep(0.5)  # Proven delay for stability
    
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    print(f"\n=== Generation Complete ===")
    print(f"Success Rate: {success_rate:.1f}% ({success_count}/{total_count})")
    print(f"Expected Success Rate: 92% (based on terminal_grounds_generator.py)")
    
    return success_count, total_count

def main():
    """Main execution function"""
    print("Metro Junction Asset Generator")
    print("Based on proven PERFECT_PARAMS (92% success rate)")
    
    # Verify ComfyUI is running
    try:
        response = urllib.request.urlopen(f"{COMFYUI_URL}/system_stats")
        print("OK: ComfyUI is running")
    except Exception as e:
        print(f"FAILED: ComfyUI not accessible at {COMFYUI_URL}: {e}")
        return False
    
    # Generate assets
    success_count, total_count = generate_metro_junction_assets()
    
    # Show results location
    print(f"\nCheck results in: {OUTPUT_DIR}")
    print("Look for files starting with 'TG_MetroJunction'")
    
    return success_count > 0

if __name__ == "__main__":
    main()