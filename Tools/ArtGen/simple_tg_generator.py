#!/usr/bin/env python3
"""
Simple Terminal Grounds Asset Generator
"""
import json
import urllib.request
import time
import uuid

def generate_metro_corridor():
    """Generate a Metro Corridor asset using proven parameters"""
    
    print("TERMINAL GROUNDS - METRO CORRIDOR GENERATOR")
    print("=" * 50)
    
    # Simple workflow using proven heun/normal parameters
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
                "text": "Terminal Grounds Metro_Maintenance_Corridor, underground metro maintenance corridor, industrial architecture, clean sci-fi industrial, brushed metal panels, concrete surfaces, cable management, structured industrial lighting, practical illumination, professional game art concept, high detail environmental design, sharp focus crisp edges, fine surface textures, balanced exposure neutral lighting, architectural visualization quality",
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode", 
            "inputs": {
                "text": "text, words, letters, numbers, UI elements, interface, HUD, overlays, logos, signs, typography, screen text, digital displays, blurry, soft focus, low quality, abstract, gradient, overexposed, blown highlights, washed out, watermark, signature",
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
                "seed": 94887,
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
                "images": ["6", 0],
                "filename_prefix": "TG_Metro_Test"
            }
        }
    }
    
    # Submit to API
    print("Submitting generation request...")
    
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
            
        if prompt_id:
            print(f"Generation queued: {prompt_id}")
            print("Generating asset (takes ~5 minutes)...")
            print("Parameters: heun sampler, normal scheduler, CFG 3.2, 25 steps")
            print("Resolution: 1536x864")
            print("")
            print("Check output at: C:/Users/Zachg/Documents/ComfyUI/output/")
            print("Look for files starting with 'TG_Metro_Test'")
            return True
        else:
            print("Failed to queue generation")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    generate_metro_corridor()