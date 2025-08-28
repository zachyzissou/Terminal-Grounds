#!/usr/bin/env python3
"""
Proven Quality Generator
Uses EXACT parameters from the successful ultra-high resolution vehicle generation
"""

import json
import urllib.request
import time
import uuid

# PROVEN SUCCESSFUL PARAMETERS - Exact copy from working generation
PROVEN_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.1,  # Exact CFG from successful generation
    "steps": 30,  # Exact steps from successful generation
    "width": 2048,   # Exact resolution from successful generation
    "height": 1536,  # Exact resolution from successful generation
    "denoise": 1.0
}

def create_workflow(asset_name, positive_prompt, negative_prompt, seed):
    """Create workflow with proven successful parameters"""
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}  # Same path that worked
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
                "denoise": PROVEN_PARAMS["denoise"],
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
                "filename_prefix": f"TG_PROVEN_{asset_name}"
            }
        }
    }
    return workflow

def submit_workflow(workflow):
    """Submit workflow to ComfyUI"""
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
    print("=" * 70)
    print("PROVEN QUALITY GENERATOR")
    print("Using Exact Parameters from Successful Ultra-High Resolution Vehicle")
    print("=" * 70)
    print()
    
    # Test assets using PROVEN successful parameters
    test_assets = [
        # Sharp weapon using proven ultra-res params
        {
            "name": "Weapon_Directorate_MG_UltraRes",
            "positive": "ultra-detailed military machine gun, Directorate faction heavy squad weapon, razor-sharp mechanical detail, regulation military stenciling with perfect readability, official unit identification markings clearly visible, command authority symbols, olive drab military paint with authentic wear patterns, professional weapon photography, studio lighting, technical blueprint precision, authentic military small arms engineering, weathered but maintained condition, regulation military fonts and numbering, white background, maximum detail, ultra-high resolution",
            "negative": "blurry, soft focus, out of focus, motion blur, low resolution, pixelated, compressed, low quality, amateur photography, poor lighting, dark shadows, black background, handwritten text, decorative fonts, civilian weapons, toy appearance, cartoon style",
            "seed": 88888
        },
        
        # Corporate character using proven params  
        {
            "name": "Character_Corporate_Enforcer_UltraRes",
            "positive": "ultra-detailed corporate security operator, Corporate faction enforcer, clean tactical gear with corporate branding elements, professional corporate color scheme with blue accents, clean sans-serif identification numbers, corporate logo placement on equipment, pristine equipment maintenance, professional military contractor aesthetic, tactical portrait photography, detailed character concept art, authentic corporate security uniforms, professional game character design, studio lighting, maximum detail, ultra-high resolution",
            "negative": "blurry, soft focus, dirty equipment, improvised gear, civilian clothing, amateur photography, cartoon style, anime aesthetics, fantasy elements, low quality, dark lighting, poor composition",
            "seed": 77777
        }
    ]
    
    queued = 0
    for i, asset in enumerate(test_assets, 1):
        print(f"[{i}/2] Generating PROVEN {asset['name']}...")
        print(f"  Resolution: {PROVEN_PARAMS['width']}x{PROVEN_PARAMS['height']} @ {PROVEN_PARAMS['steps']} steps")
        print(f"  CFG: {PROVEN_PARAMS['cfg']} (exact match to successful generation)")
        print(f"  Concept: {asset['positive'][:60]}...")
        print()
        
        workflow = create_workflow(
            asset['name'],
            asset['positive'],
            asset['negative'],
            asset['seed']
        )
        
        prompt_id = submit_workflow(workflow)
        
        if prompt_id:
            print(f"  OK QUEUED: {prompt_id}")
            queued += 1
        else:
            print(f"  FAILED: Could not queue generation")
        
        print()
        time.sleep(1.0)
    
    print("=" * 70)
    print(f"PROVEN QUALITY TEST: {queued}/2 queued")
    print("Using exact parameters from successful ultra-res vehicle generation")
    print("Expected generation time: ~15-20 minutes each")
    print("=" * 70)

if __name__ == "__main__":
    main()