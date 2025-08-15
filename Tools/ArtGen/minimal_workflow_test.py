#!/usr/bin/env python3
"""
Ultra-minimal ComfyUI workflow test
Bypasses sampling issues by using different approaches
"""
import json
import urllib.request
import urllib.error

def test_checkpoint_only():
    """Test just loading the checkpoint"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        }
    }
    return workflow

def test_text_encoding():
    """Test checkpoint + text encoding only"""
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple", 
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "simple test", "clip": ["1", 1]}
        }
    }
    return workflow

def test_alternative_sampler():
    """Test with different sampler that might not use tqdm"""
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "terminal grounds test", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 12345,
                "steps": 1,  # Minimal steps
                "cfg": 1.0,  # Minimal CFG
                "sampler_name": "ddim",  # Different sampler
                "scheduler": "simple",  # Different scheduler
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "TG_Minimal"}}
    }
    return workflow

def submit_workflow(workflow, name):
    """Submit workflow and get result"""
    print(f"\n=== Testing {name} ===")
    
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/prompt", 
        data=data, 
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            result = json.loads(body)
            print(f"OK Queued: {result.get('prompt_id', 'unknown')}")
            return result.get('prompt_id')
    except urllib.error.HTTPError as e:
        print(f"X HTTP Error {e.code}")
        try:
            error_body = e.read().decode("utf-8", errors="ignore")
            print(f"Error: {error_body}")
        except:
            pass
        return None
    except Exception as e:
        print(f"X Error: {e}")
        return None

def check_job_status(prompt_id):
    """Check if job completed successfully"""
    if not prompt_id:
        return False
        
    try:
        url = f"http://127.0.0.1:8000/history/{prompt_id}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            
        if prompt_id in data:
            status = data[prompt_id].get("status", {})
            status_str = status.get("status_str", "unknown")
            completed = status.get("completed", False)
            
            print(f"  Status: {status_str}, Completed: {completed}")
            
            if status_str == "error":
                messages = status.get("messages", [])
                for msg in messages:
                    if msg[0] == "execution_error":
                        error = msg[1].get("exception_message", "Unknown error")
                        print(f"  Error: {error}")
                        return False
            elif status_str == "success" and completed:
                print("  OK SUCCESS!")
                return True
            
    except Exception as e:
        print(f"  Could not check status: {e}")
        
    return False

def main():
    print("=== ComfyUI Workflow Troubleshooting ===")
    
    tests = [
        (test_checkpoint_only(), "Checkpoint Loading Only"),
        (test_text_encoding(), "Checkpoint + Text Encoding"),  
        (test_alternative_sampler(), "Alternative Sampler (DDIM, 1 step)")
    ]
    
    for workflow, name in tests:
        prompt_id = submit_workflow(workflow, name)
        if prompt_id:
            import time
            time.sleep(2)  # Give it time to process
            success = check_job_status(prompt_id)
            if success:
                print(f"OK {name} WORKS!")
                break
            else:
                print(f"X {name} failed")
        else:
            print(f"X {name} couldn't queue")
    
    print("\n=== Next Steps ===")
    print("If any test succeeded, we found a working path.")
    print("If all failed, the issue is deeper in ComfyUI setup.")

if __name__ == "__main__":
    main()