#!/usr/bin/env python3
"""
Parameter Test Generator - Terminal Grounds
Test different CFG/step combinations to find optimal sharpness
Based on your observation that current settings may be causing blur
"""

import json
import urllib.request
import time
import uuid

def create_parameter_test_workflow(cfg, steps, seed, test_name):
    """Test different parameter combinations"""
    
    # Simple test prompt to isolate parameter effects
    positive_prompt = "ultra sharp concept art of military assault rifle, detailed mechanical components, crisp technical illustration, professional game asset quality"
    
    # Clean negative prompt focused on blur elimination
    negative_prompt = "blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, branded overlays, game UI, watermarks"
    
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
                "width": 1536,
                "height": 864,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
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
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"TG_PARAM_TEST_{test_name}_CFG{cfg}_STEPS{steps}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def run_parameter_tests():
    """Test different parameter combinations to find optimal sharpness"""
    
    # Parameter combinations to test
    test_combinations = [
        (3.2, 25, "EnvProven"),      # Environment generator proven parameters
        (3.5, 30, "WeaponSharp"),    # Weapon sharp parameters  
        (3.0, 20, "Lower"),          # Lower values
        (4.0, 35, "Higher"),         # Higher values
        (3.2, 30, "MidCFG_HighStep") # Mix: proven CFG with more steps
    ]
    
    base_seed = 400000
    
    print("PARAMETER OPTIMIZATION TEST - Terminal Grounds")
    print("Testing different CFG/step combinations for optimal sharpness")
    print("=" * 70)
    print()
    
    for i, (cfg, steps, name) in enumerate(test_combinations):
        seed = base_seed + (i * 100)  # Different seeds for each test
        
        print(f"Test {i+1}: {name}")
        print(f"  CFG: {cfg}, Steps: {steps}")
        print(f"  Seed: {seed}")
        
        workflow = create_parameter_test_workflow(cfg, steps, seed, name)
        
        try:
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            prompt_id = result.get('prompt_id', 'unknown')
            print(f"  -> Submitted (ID: {prompt_id})")
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            
        print()
        time.sleep(0.5)
    
    print("=" * 70)
    print("PARAMETER TESTS QUEUED")
    print()
    print("COMPARISON TARGETS:")
    print("  1. EnvProven (CFG 3.2, 25 steps) - 92% success baseline")
    print("  2. WeaponSharp (CFG 3.5, 30 steps) - Sharp weapon success")
    print("  3. Lower values - Test if less is more")
    print("  4. Higher values - Test if more processing helps")  
    print("  5. Mixed approach - Proven CFG with enhanced steps")
    print()
    print("ANALYSIS CRITERIA:")
    print("  - Overall sharpness and detail")
    print("  - Edge clarity and definition")
    print("  - Material texture quality")
    print("  - No blur artifacts")
    print()
    print("Output files: TG_PARAM_TEST_*")

if __name__ == "__main__":
    run_parameter_tests()