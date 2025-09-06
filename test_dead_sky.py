#!/usr/bin/env python3
"""
Dead Sky Region Builder - Test Version
Quick test to verify ComfyUI connection and generate one asset
"""

import requests
import json
import time
from pathlib import Path

def test_comfyui_generation():
    """Test ComfyUI with a simple Dead Sky asset generation"""

    print("=== DEAD SKY REGION BUILDER TEST ===")

    # Create output directory
    output_path = Path("Content/TG/Regions/DeadSky")
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Created output directory: {output_path}")

    # Test ComfyUI connection
    comfyui_url = "http://127.0.0.1:8188"
    try:
        response = requests.get(f"{comfyui_url}/system_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"ComfyUI connected: {stats['system']['comfyui_version']}")
            print(f"GPU: {stats['devices'][0]['name']}")
        else:
            print("ComfyUI connection failed")
            return False
    except Exception as e:
        print(f"ComfyUI error: {e}")
        return False

    # Simple test workflow - Dead Sky concept art
    workflow = {
        "3": {
            "inputs": {
                "seed": int(time.time()),
                "steps": 20,
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
                "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "Dead Sky region concept art, Terminal Grounds game, post-apocalyptic irradiated wasteland, three concentric danger zones, atmospheric sci-fi environment",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, people, text, logos",
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
                "filename_prefix": "DeadSky_Test_Concept",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

    # Submit to ComfyUI
    try:
        print("Submitting Dead Sky concept generation to ComfyUI...")
        response = requests.post(f"{comfyui_url}/prompt", json={"prompt": workflow})
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"Generation started! Prompt ID: {prompt_id}")

            # Create test manifest
            manifest = {
                "test_run": True,
                "prompt_id": prompt_id,
                "timestamp": time.time(),
                "region": "Dead Sky (IEZ)",
                "status": "generation_started",
                "expected_output": f"DeadSky_Test_Concept_{prompt_id}.png"
            }

            manifest_path = output_path / "test_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"Test manifest saved: {manifest_path}")
            print("Check ComfyUI interface for generation progress!")
            return True
        else:
            print(f"ComfyUI request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"ComfyUI generation error: {e}")
        return False

if __name__ == "__main__":
    success = test_comfyui_generation()
    if success:
        print("\n=== DEAD SKY TEST SUCCESSFUL ===")
        print("Check Content/TG/Regions/DeadSky/ for outputs")
        print("Check ComfyUI web interface for image generation")
    else:
        print("\n=== DEAD SKY TEST FAILED ===")
        print("Check ComfyUI status and connection")
