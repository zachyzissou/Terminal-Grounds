#!/usr/bin/env python3
"""
Working FLUX Generator using the exact metadata from yesterday's success
"""
import json
import urllib.request
import time

def create_working_flux_workflow():
    """Create workflow based on working metadata"""
    # Using the exact structure that worked yesterday
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode", 
            "inputs": {
                "text": "Terminal Grounds faction emblem, military insignia, clean vector art, professional logo design",
                "clip": ["1", 1]
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "text, words, letters, blurry, low quality, watermark",
                "clip": ["1", 1]  
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024, 
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 94887,  # From working metadata
                "steps": 40,    # From working metadata
                "cfg": 4.5,     # From working metadata
                "sampler_name": "euler",
                "scheduler": "simple",  # From working metadata
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
                "filename_prefix": "TG_Working_Test"
            }
        }
    }
    return workflow

def submit_workflow():
    """Submit the working workflow"""
    workflow = create_working_flux_workflow()
    
    print("=== Testing Working FLUX Workflow ===")
    print("Using exact parameters from yesterday's successful generation")
    print(f"Seed: {workflow['5']['inputs']['seed']}")
    print(f"Steps: {workflow['5']['inputs']['steps']}")
    print(f"CFG: {workflow['5']['inputs']['cfg']}")
    print(f"Scheduler: {workflow['5']['inputs']['scheduler']}")
    
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
            print(f"\nQueued successfully: {prompt_id}")
            return prompt_id
    except Exception as e:
        print(f"Failed to queue: {e}")
        return None

def monitor_job(prompt_id, timeout=120):
    """Monitor job execution"""
    if not prompt_id:
        return False
        
    print(f"\nMonitoring job {prompt_id}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            url = f"http://127.0.0.1:8000/history/{prompt_id}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                
            if prompt_id in data:
                job_data = data[prompt_id]
                status = job_data.get("status", {})
                status_str = status.get("status_str", "unknown")
                completed = status.get("completed", False)
                
                print(f"Status: {status_str}, Completed: {completed}")
                
                if status_str == "success" and completed:
                    print("\n*** SUCCESS! Image generated! ***")
                    
                    # Check outputs
                    outputs = job_data.get("outputs", {})
                    if outputs:
                        print("Output files:")
                        for node_id, output in outputs.items():
                            if "images" in output:
                                for img in output["images"]:
                                    filename = img.get("filename", "unknown")
                                    print(f"  - {filename}")
                    return True
                    
                elif status_str == "error":
                    print("\n*** ERROR ***")
                    messages = status.get("messages", [])
                    for msg in messages:
                        if msg[0] == "execution_error":
                            error_msg = msg[1].get("exception_message", "Unknown")
                            node_id = msg[1].get("node_id", "unknown")
                            print(f"Node {node_id}: {error_msg}")
                    return False
                    
        except Exception as e:
            print(f"Error checking status: {e}")
            
        time.sleep(5)
    
    print("Timeout waiting for job completion")
    return False

def main():
    print("=== Attempting Terminal Grounds Asset Generation ===")
    print("Using proven workflow structure from working image metadata")
    
    prompt_id = submit_workflow()
    if prompt_id:
        success = monitor_job(prompt_id)
        if success:
            print("\n🎉 SUCCESS! ComfyUI is working!")
            print("✅ We can generate Terminal Grounds assets!")
            print("\nNext: Run the full asset generation pipeline")
        else:
            print("\n❌ Job failed with the same tqdm error")
            print("Need to investigate ComfyUI environment issue")
    else:
        print("\n❌ Could not queue job")
        print("Check ComfyUI server status")

if __name__ == "__main__":
    main()