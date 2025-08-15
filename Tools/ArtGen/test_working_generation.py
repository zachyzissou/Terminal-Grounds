#!/usr/bin/env python3
"""
Test the working generation system
Run a quick test using the proven style baseline explorer code
"""

import json
import urllib.request
import time
from pathlib import Path

# Use the working workflow from style_baseline_explorer.py
def create_test_workflow():
    """Create a simple test workflow using proven approach"""
    
    # This is the exact workflow structure that worked yesterday
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "positive": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "military faction emblem, insignia, badge, symbol, high quality, professional game asset",
                "clip": ["1", 1]
            }
        },
        "negative": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "low quality, amateur, placeholder, watermark",
                "clip": ["1", 1]
            }
        },
        "latent": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "sampler": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42,
                "steps": 35,
                "cfg": 7.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["positive", 0],
                "negative": ["negative", 0],
                "latent_image": ["latent", 0]
            }
        },
        "decode": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["sampler", 0],
                "vae": ["1", 2]
            }
        },
        "save": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "TG_Test_Working",
                "images": ["decode", 0]
            }
        }
    }
    
    return workflow

def queue_and_wait(workflow, timeout=120):
    """Queue workflow and wait for completion"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Queue the workflow
    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(
        f"{base_url}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id', '')
            print(f"Queued successfully: {prompt_id}")
    except Exception as e:
        print(f"Failed to queue: {e}")
        return None
    
    if not prompt_id:
        return None
    
    # Wait for completion
    print("Generating", end="")
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            url = f"{base_url}/history/{prompt_id}"
            with urllib.request.urlopen(url) as response:
                history = json.loads(response.read())
                
            if prompt_id in history:
                job_data = history[prompt_id]
                status = job_data.get('status', {})
                status_str = status.get('status_str', 'unknown')
                
                if status_str == 'success':
                    outputs = job_data.get('outputs', {})
                    for node_output in outputs.values():
                        if 'images' in node_output:
                            filename = node_output['images'][0]['filename']
                            print(" ✓ SUCCESS!")
                            print(f"Generated: {filename}")
                            return filename
                elif status_str == 'error':
                    print(" ✗ ERROR!")
                    messages = status.get('messages', [])
                    for msg in messages:
                        if msg[0] == "execution_error":
                            error = msg[1].get("exception_message", "Unknown error")
                            print(f"Error: {error}")
                    return None
        except:
            pass
        
        print(".", end="", flush=True)
        time.sleep(2)
    
    print(" ✗ TIMEOUT")
    return None

def main():
    print("=== Testing Working Generation System ===")
    print("Using proven workflow from style_baseline_explorer.py")
    
    # Create and submit workflow
    workflow = create_test_workflow()
    filename = queue_and_wait(workflow)
    
    if filename:
        print(f"\n🎉 SUCCESS! ComfyUI is working!")
        print(f"✅ Generated image: {filename}")
        print("\n✨ Terminal Grounds asset generation is operational!")
        
        # Check if file exists in ComfyUI output
        comfyui_output = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
        source_file = comfyui_output / filename
        
        if source_file.exists():
            print(f"📁 File confirmed in: {source_file}")
        else:
            print("📁 File location unknown - check ComfyUI output folder")
            
        print("\n🚀 Ready to run full asset generation pipeline!")
        
    else:
        print(f"\n❌ Generation failed")
        print("The same tqdm error is still preventing generation")
        print("Need to investigate ComfyUI environment or restart")

if __name__ == "__main__":
    main()