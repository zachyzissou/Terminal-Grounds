"""
Sharp Emblem Workflow - Fixes blur while maintaining vibrancy
"""

import json
import urllib.request
from datetime import datetime
from lore_accurate_prompts import TerminalGroundsPromptMaster

def build_sharp_emblem_workflow(faction_code: str, seed: int = 12345):
    """
    Build sharp, vibrant emblem workflow
    """
    
    prompt_master = TerminalGroundsPromptMaster()
    faction_prompt = prompt_master.build_emblem_prompt(faction_code)
    
    # Add sharpness keywords to positive prompt
    enhanced_positive = faction_prompt["positive"] + ", sharp edges, crisp lines, high definition, ultra sharp, crystal clear, perfect focus"
    
    # Remove blur-causing terms from negative prompt
    enhanced_negative = faction_prompt["negative"].replace("blurry, ", "").replace("pixelated, ", "") + ", soft focus, out of focus, motion blur, gaussian blur, unfocused"
    
    workflow = {
        "checkpoint": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
            }
        },
        
        "positive_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": enhanced_positive,
                "clip": ["checkpoint", 1]
            }
        },
        
        "negative_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": enhanced_negative,
                "clip": ["checkpoint", 1]
            }
        },
        
        # Generate at final resolution to avoid upscaling blur
        "latent": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 2048,   # Generate at final size
                "height": 2048,
                "batch_size": 1
            }
        },
        
        # Optimized for sharpness
        "sampler": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 25,      # Fewer steps to avoid over-processing
                "cfg": 3.5,       # Lower CFG to reduce blur
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["checkpoint", 0],
                "positive": ["positive_prompt", 0],
                "negative": ["negative_prompt", 0],
                "latent_image": ["latent", 0]
            }
        },
        
        "decoded": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["sampler", 0],
                "vae": ["checkpoint", 2]
            }
        },
        
        # NO upscaling - keep original sharpness
        "save": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["decoded", 0],
                "filename_prefix": f"TG_SHARP_{faction_code}_Emblem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
    }
    
    return workflow

def test_sharp_workflow():
    """Test sharp workflow"""
    
    workflow = build_sharp_emblem_workflow("DIR", seed=77777)
    
    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:8000/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            prompt_id = result.get('prompt_id', '')
            print(f"SHARP workflow queued: {prompt_id}")
            print("Sharpness optimizations:")
            print("- Generate at 2048x2048 (no upscaling blur)")
            print("- 25 steps (avoid over-processing)")
            print("- CFG 3.5 (prevent over-smoothing)")
            print("- Added sharpness keywords")
            print("- Removed blur-causing negatives")
            print("- NO post-processing upscaling")
            return prompt_id
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_sharp_workflow()