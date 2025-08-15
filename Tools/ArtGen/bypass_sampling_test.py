#!/usr/bin/env python3
"""
Try to bypass the sampling issue by using different node combinations
"""
import json
import urllib.request
import time

def test_checkpoint_preview():
    """Use CheckpointLoaderSimple -> PreviewImage to avoid sampling"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "simple test image", "clip": ["1", 1]}
        },
        "3": {
            "class_type": "EmptyLatentImage", 
            "inputs": {"width": 512, "height": 512, "batch_size": 1}
        },
        "4": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["1", 2]}
        },
        "5": {
            "class_type": "SaveImage",
            "inputs": {"images": ["4", 0], "filename_prefix": "TG_NoSampling"}
        }
    }
    return workflow

def test_flux_schnell():
    """Try with FLUX Schnell which might work differently"""
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "FLUX1\\flux1-schnell-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "terminal grounds test", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 12345,
                "steps": 4,  # Schnell uses fewer steps
                "cfg": 1.0,  # Schnell uses lower CFG
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "TG_Schnell"}}
    }
    return workflow

def submit_and_check(workflow, name):
    """Submit workflow and check results"""
    print(f"\n=== {name} ===")
    
    # Submit workflow
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/prompt", 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            prompt_id = result.get('prompt_id')
            print(f"Queued: {prompt_id}")
    except Exception as e:
        print(f"Failed to queue: {e}")
        return False
        
    # Wait and check result
    time.sleep(3)
    
    try:
        url = f"http://127.0.0.1:8000/history/{prompt_id}"
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            
        if prompt_id in data:
            status = data[prompt_id].get("status", {})
            if status.get("status_str") == "success":
                print("SUCCESS! Generated image")
                return True
            elif status.get("status_str") == "error":
                messages = status.get("messages", [])
                for msg in messages:
                    if msg[0] == "execution_error":
                        error = msg[1].get("exception_message", "")
                        print(f"Error: {error}")
                return False
    except Exception as e:
        print(f"Could not check status: {e}")
        
    return False

def main():
    print("=== Attempting to Bypass Sampling Issues ===")
    
    # First check what FLUX models are available
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/object_info/CheckpointLoaderSimple") as resp:
            data = json.loads(resp.read())
            models = data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            flux_models = [m for m in models if "flux" in m.lower()]
            print(f"Available FLUX models: {flux_models}")
    except Exception as e:
        print(f"Could not check models: {e}")
    
    # Test approaches
    tests = [
        (test_checkpoint_preview(), "Direct VAE Decode (No Sampling)"),
        (test_flux_schnell(), "FLUX Schnell (4 steps)")
    ]
    
    for workflow, name in tests:
        success = submit_and_check(workflow, name)
        if success:
            print(f"\n*** {name} WORKS! ***")
            print("This approach can generate images!")
            return
    
    print("\nAll approaches failed. The issue requires ComfyUI restart or environment fix.")

if __name__ == "__main__":
    main()