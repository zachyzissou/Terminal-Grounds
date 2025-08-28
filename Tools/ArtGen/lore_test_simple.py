#!/usr/bin/env python3
"""
Simple Lore Integration Test
Test lore-enhanced prompts with known working parameters
"""

import json
import urllib.request
import uuid
import subprocess
import os

# Use EXACT parameters from successful ultra-res vehicle generation
PROVEN_PARAMS = {
    "sampler": "heun",
    "scheduler": "normal", 
    "cfg": 3.1,
    "steps": 30,
    "width": 2048,
    "height": 1536,
    "denoise": 1.0
}

def build_lore_prompt(region_id, faction_id, subject, action):
    """Build authentic Terminal Grounds prompt using lore system"""
    try:
        script_dir = "C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API"
        script_path = os.path.join(script_dir, "Build-LorePrompt.ps1")
        
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", script_path,
            "-RegionId", region_id,
            "-FactionId", faction_id, 
            "-Subject", subject,
            "-Action", action,
            "-IncludeStyleCapsule",
            "-IncludeWorld"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Lore prompt failed: {result.stderr}")
            return f"{subject}, {action}, Terminal Grounds concept art"
    except Exception as e:
        print(f"Error building lore prompt: {e}")
        return f"{subject}, {action}, Terminal Grounds concept art"

def create_simple_workflow(positive_prompt, seed):
    """Create simple workflow using proven parameters"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode", 
            "inputs": {"text": "blurry, soft focus, out of focus, motion blur, low resolution, low quality", "clip": ["1", 1]}
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
                "filename_prefix": "TG_LORE_TEST"
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
        print(f"Error submitting workflow: {e}")
        return None

def main():
    print("LORE INTEGRATION TEST")
    print("Using proven ultra-res parameters with lore-enhanced prompts")
    print()
    
    # Test lore prompt generation
    print("Building lore prompt...")
    lore_prompt = build_lore_prompt(
        "REG_CRIMSON_DOCKS",
        "FCT_VUL", 
        "Iron Vultures technical vehicle",
        "parked at salvage refit quay"
    )
    
    print(f"Generated prompt ({len(lore_prompt)} chars):")
    print(f"  {lore_prompt[:100]}...")
    print()
    
    # Create and submit workflow
    print("Creating workflow with proven parameters...")
    workflow = create_simple_workflow(lore_prompt, 88888)
    
    print("Submitting to ComfyUI...")
    prompt_id = submit_workflow(workflow)
    
    if prompt_id:
        print(f"SUCCESS: Queued as {prompt_id}")
        print("This tests lore integration with proven generation parameters")
    else:
        print("FAILED: Could not queue lore-enhanced generation")
    print()

if __name__ == "__main__":
    main()