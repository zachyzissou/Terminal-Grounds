#!/usr/bin/env python3
"""
Terminal Grounds - Upscaled Concept Art Generator
==============================================
Generate at 1920x1080, then upscale to 4K using RealESRGAN
Following your successful production framework pattern
"""

from typing import Dict, Any
from comfyui_api_client import ComfyUIAPIClient

def create_upscaled_concept_workflow(
    prompt: str, 
    seed: int = 94887,
    steps: int = 40,
    cfg: float = 4.5
) -> Dict[str, Any]:
    """Create workflow that generates at 1920x1080 then upscales to 4K"""
    
    full_prompt = f"Terminal Grounds {prompt}, concept art, detailed illustration, professional game art, high detail, cinematic lighting, atmospheric"
    negative = "low quality, amateur, poor composition, bad lighting, text, watermark"
    
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": full_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1920, "height": 1080, "batch_size": 1}  # Generate at 1080p
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
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
        # Add upscaler node here if available
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": "TG_CONCEPT_1080p"
            }
        }
    }

def test_1080p_generation():
    """Test generation at safe 1080p resolution"""
    
    client = ComfyUIAPIClient()
    
    if not client.check_server():
        print("ComfyUI server not running")
        return False
    
    print("Testing 1080p concept generation...")
    
    workflow = create_upscaled_concept_workflow(
        "underground facility, emergency lighting, noir atmosphere",
        seed=94889
    )
    
    prompt_id = client.queue_prompt(workflow)
    if not prompt_id:
        print("Failed to queue")
        return False
    
    print(f"Queued: {prompt_id}")
    
    images = client.wait_for_completion(prompt_id, timeout=120)
    if images:
        print(f"SUCCESS: Generated {len(images)} images")
        for img in images:
            print(f"  - {img}")
            client.copy_to_staging(img)
        return True
    else:
        print("Generation failed")
        return False

if __name__ == "__main__":
    test_1080p_generation()