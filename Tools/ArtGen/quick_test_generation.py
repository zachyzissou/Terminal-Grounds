#!/usr/bin/env python3
"""
Quick test generation using your proven parameters
"""

import json
import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from comfyui_api_client import ComfyUIAPIClient

def create_test_workflow():
    """Create a simple test workflow using your proven parameters"""
    
    prompt = "Terminal Grounds underground facility, emergency lighting, concept art, detailed illustration, professional game art, high detail, cinematic lighting, atmospheric"
    negative = "low quality, amateur, poor composition, bad lighting, text, watermark"
    
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 3840, "height": 2160, "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 94888,
                "steps": 40,
                "cfg": 4.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
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
                "filename_prefix": "TG_TEST_ATMOSPHERIC"
            }
        }
    }

def main():
    print("Testing ComfyUI generation with proven parameters...")
    
    client = ComfyUIAPIClient()
    
    if not client.check_server():
        print("ERROR: ComfyUI server not running")
        return False
    
    print("Server OK, queueing generation...")
    
    workflow = create_test_workflow()
    prompt_id = client.queue_prompt(workflow)
    
    if not prompt_id:
        print("ERROR: Failed to queue prompt")
        return False
    
    print(f"Queued with ID: {prompt_id}")
    print("Waiting for completion (timeout 120s)...")
    
    images = client.wait_for_completion(prompt_id, timeout=120)
    
    if images:
        print(f"SUCCESS: Generated {len(images)} images")
        for img in images:
            print(f"  - {img}")
            client.copy_to_staging(img)
        return True
    else:
        print("ERROR: Generation failed or timed out")
        return False

if __name__ == "__main__":
    main()