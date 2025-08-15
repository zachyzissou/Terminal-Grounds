"""
Test production quality framework with real workflows
"""

import json
import urllib.request
from datetime import datetime
from production_quality_framework import QualityStandard, AssetCategory
from lore_accurate_prompts import TerminalGroundsPromptMaster

def test_asset_category(framework, asset_type, faction_code="DIR"):
    """Test a specific asset category with production settings"""
    
    print(f"\n=== TESTING {asset_type.value.upper()} PRODUCTION QUALITY ===")
    
    # Get optimal settings
    settings = framework.get_optimal_settings(asset_type)
    print(f"Target Resolution: {settings['target_resolution']}")
    print(f"Base Generation: {settings['base_generation']}")
    print(f"Upscale Method: {settings['upscale_method']}")
    print(f"Steps: {settings['steps']}, CFG: {settings['cfg']}")
    
    # Build production workflow
    prompt_master = TerminalGroundsPromptMaster()
    
    if asset_type == AssetCategory.LOGOS_INSIGNIAS:
        faction_prompt = prompt_master.build_emblem_prompt(faction_code)
        base_prompt = faction_prompt["positive"]
        base_negative = faction_prompt["negative"]
    else:
        # For other asset types, use basic faction prompt
        base_prompt = f"Terminal Grounds {faction_code} faction"
        base_negative = "low quality, blurry"
    
    # Enhance with quality keywords
    quality_prompt = base_prompt + ", " + ", ".join(settings["quality_keywords"])
    negative_prompt = base_negative + ", " + ", ".join(settings["negative_keywords"])
    
    print(f"Quality Prompt: {quality_prompt[:100]}...")
    
    # Build workflow
    base_width, base_height = settings["base_generation"]
    target_width, target_height = settings["target_resolution"]
    
    workflow = {
        "checkpoint": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "positive_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": quality_prompt,
                "clip": ["checkpoint", 1]
            }
        },
        "negative_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": ["checkpoint", 1]
            }
        },
        "latent": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": base_width,
                "height": base_height,
                "batch_size": 1
            }
        },
        "sampler": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 90000 + hash(asset_type.value) % 10000,
                "steps": settings["steps"],
                "cfg": settings["cfg"],
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
        }
    }
    
    # Handle different upscaling methods
    if settings["upscale_method"] == "none":
        workflow["save"] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["decoded", 0],
                "filename_prefix": f"PROD_{asset_type.value.upper()}_{datetime.now().strftime('%H%M%S')}"
            }
        }
    elif settings["upscale_method"] in ["nearest-exact", "bicubic", "bilinear", "lanczos"]:
        workflow["upscaled"] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["decoded", 0],
                "upscale_method": settings["upscale_method"],
                "width": target_width,
                "height": target_height,
                "crop": "center"
            }
        }
        workflow["save"] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["upscaled", 0],
                "filename_prefix": f"PROD_{asset_type.value.upper()}_{datetime.now().strftime('%H%M%S')}"
            }
        }
    else:
        # AI upscaling (like RealESRGAN, UltraSharp)
        workflow["upscale_model"] = {
            "class_type": "UpscaleModelLoader",
            "inputs": {"model_name": settings["upscale_method"]}
        }
        workflow["ai_upscaled"] = {
            "class_type": "ImageUpscaleWithModel",
            "inputs": {
                "upscale_model": ["upscale_model", 0],
                "image": ["decoded", 0]
            }
        }
        
        # Check if we need final resize to exact target
        workflow["final_resize"] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["ai_upscaled", 0],
                "upscale_method": "lanczos",
                "width": target_width,
                "height": target_height,
                "crop": "center"
            }
        }
        workflow["save"] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["final_resize", 0],
                "filename_prefix": f"PROD_{asset_type.value.upper()}_{datetime.now().strftime('%H%M%S')}"
            }
        }
    
    # Queue the workflow
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
            print(f"Queued: {prompt_id}")
            return prompt_id
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def run_production_tests():
    """Run production quality tests for key asset types"""
    
    print("=== TERMINAL GROUNDS PRODUCTION QUALITY TESTS ===")
    
    framework = QualityStandard()
    
    # Test the most critical asset types first
    test_categories = [
        AssetCategory.LOGOS_INSIGNIAS,  # Most critical - need perfect sharpness
        AssetCategory.CONCEPT_ART,      # Need cinematic quality
        AssetCategory.UI_ELEMENTS,      # Need crisp at small sizes
        AssetCategory.TEXTURES          # Need seamless tiling
    ]
    
    for category in test_categories:
        test_asset_category(framework, category)
    
    print("\n=== PRODUCTION TESTS COMPLETE ===")
    print("Check output directory for:")
    print("- PROD_LOGOS_INSIGNIAS_* (should be 4K, crystal sharp)")
    print("- PROD_CONCEPT_ART_* (should be 4K, detailed)")
    print("- PROD_UI_ELEMENTS_* (should be 512px, crisp)")
    print("- PROD_TEXTURES_* (should be 4K, seamless)")

if __name__ == "__main__":
    run_production_tests()