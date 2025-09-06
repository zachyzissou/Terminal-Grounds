#!/usr/bin/env python3
"""
Dead Sky Region Builder - Debug Version
Test ComfyUI workflow and debug any issues
"""

import requests
import json
import time
from pathlib import Path

def debug_comfyui():
    """Debug ComfyUI workflow issues"""

    print("=== DEAD SKY COMFYUI DEBUG ===")

    comfyui_url = "http://127.0.0.1:8188"

    # Check available models
    try:
        print("Checking available models...")
        response = requests.get(f"{comfyui_url}/object_info")
        if response.status_code == 200:
            info = response.json()
            checkpoints = info.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])
            if isinstance(checkpoints, list) and len(checkpoints) > 0:
                available_models = checkpoints[0]  # First item is usually the list of options
                print(f"Available models: {available_models[:3]}...")  # Show first 3
            else:
                print("Could not determine available models")
        else:
            print(f"Failed to get object info: {response.status_code}")
    except Exception as e:
        print(f"Error checking models: {e}")

    # Test queue status
    try:
        print("Checking queue status...")
        response = requests.get(f"{comfyui_url}/queue")
        if response.status_code == 200:
            queue = response.json()
            print(f"Queue running: {len(queue.get('queue_running', []))}")
            print(f"Queue pending: {len(queue.get('queue_pending', []))}")
        else:
            print(f"Failed to check queue: {response.status_code}")
    except Exception as e:
        print(f"Error checking queue: {e}")

    # Simplified workflow test
    simple_workflow = {
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 10,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "flux1-dev-fp8.safetensors"  # Try without FLUX1\ prefix
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "a simple test image",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "bad quality",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "test_output",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

    print("Testing simplified workflow...")
    try:
        response = requests.post(f"{comfyui_url}/prompt", json={"prompt": simple_workflow})
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"Success! Prompt ID: {result.get('prompt_id')}")
            return True
        else:
            print("Workflow failed")
            return False
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    debug_comfyui()
