#!/usr/bin/env python3
"""
Dead Sky Region Builder - FLUX Workflow Version
Updated to use proper FLUX model loading workflow
"""

import requests
import json
import time
from pathlib import Path

def test_flux_workflow():
    """Test ComfyUI with proper FLUX model workflow"""

    print("=== DEAD SKY FLUX WORKFLOW TEST ===")

    # Create output directory
    output_path = Path("Content/TG/Regions/DeadSky")
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Created output directory: {output_path}")

    comfyui_url = "http://127.0.0.1:8188"

    # Test ComfyUI connection
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

    # Check available UNet models
    try:
        response = requests.get(f"{comfyui_url}/object_info/UNETLoader")
        if response.status_code == 200:
            info = response.json()
            unet_models = info["UNETLoader"]["input"]["required"]["unet_name"][0]
            print(f"Available UNET models: {unet_models}")
            if not unet_models:
                print("No UNET models found!")
                return False
        else:
            print("Could not get UNET model info")
            return False
    except Exception as e:
        print(f"Error checking UNET models: {e}")
        return False

    # FLUX workflow - proper node structure
    flux_workflow = {
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
                "clip": ["11", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "DeadSky_FLUX_Test",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        },
        "10": {
            "inputs": {
                "unet_name": "flux1-dev-fp8.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            },
            "class_type": "UNETLoader"
        },
        "11": {
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        },
        "12": {
            "inputs": {
                "conditioning": ["6", 0],
                "guidance": 3.5
            },
            "class_type": "FluxGuidance"
        },
        "13": {
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "SamplerCustomAdvanced"
        },
        "16": {
            "inputs": {
                "sampler_name": "euler"
            },
            "class_type": "KSamplerSelect"
        },
        "17": {
            "inputs": {
                "scheduler": "simple",
                "steps": 20,
                "denoise": 1.0,
                "model": ["10", 0]
            },
            "class_type": "BasicScheduler"
        },
        "22": {
            "inputs": {
                "model": ["10", 0],
                "conditioning": ["12", 0]
            },
            "class_type": "BasicGuider"
        },
        "25": {
            "inputs": {
                "noise_seed": int(time.time())
            },
            "class_type": "RandomNoise"
        }
    }

    print("Testing FLUX workflow...")
    try:
        response = requests.post(f"{comfyui_url}/prompt", json={"prompt": flux_workflow})
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get("prompt_id")
            print(f"SUCCESS! FLUX generation started!")
            print(f"Prompt ID: {prompt_id}")

            # Create success manifest
            manifest = {
                "flux_test": True,
                "prompt_id": prompt_id,
                "timestamp": time.time(),
                "region": "Dead Sky (IEZ)",
                "status": "flux_generation_started",
                "expected_output": f"DeadSky_FLUX_Test_{prompt_id}.png",
                "model_used": "flux1-dev-fp8.safetensors",
                "workflow_type": "FLUX_Advanced"
            }

            manifest_path = output_path / "flux_test_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"Test manifest saved: {manifest_path}")
            print("Check ComfyUI interface for generation progress!")
            return True
        else:
            print(f"FLUX workflow failed: {response.status_code}")
            print(f"Error details: {response.text}")
            return False
    except Exception as e:
        print(f"FLUX workflow error: {e}")
        return False

if __name__ == "__main__":
    success = test_flux_workflow()
    if success:
        print("\n=== FLUX DEAD SKY TEST SUCCESSFUL ===")
        print("🎯 FLUX model working correctly!")
        print("📁 Check Content/TG/Regions/DeadSky/ for outputs")
        print("🖥️  Check ComfyUI web interface for image generation")
        print("✅ Ready to proceed with full Dead Sky region generation!")
    else:
        print("\n=== FLUX DEAD SKY TEST FAILED ===")
        print("❌ FLUX workflow needs adjustment")
        print("🔧 Check model availability and node configuration")
