"""
Documentation-Accurate Terminal Grounds Workflow
Uses official faction documentation for maximum authenticity
"""

import json
import urllib.request
from datetime import datetime
from lore_accurate_prompts import TerminalGroundsPromptMaster

def build_documentation_emblem_workflow(faction_code: str, seed: int = 12345):
    """
    Build emblem workflow using official documentation prompts
    """
    
    prompt_master = TerminalGroundsPromptMaster()
    faction_prompt = prompt_master.build_emblem_prompt(faction_code)
    
    # Extract faction data for metadata
    faction_data = faction_prompt["faction_data"]
    
    workflow = {
        # FLUX checkpoint (proven working)
        "checkpoint": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"
            }
        },
        
        # Documentation-accurate prompts
        "positive_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": faction_prompt["positive"],
                "clip": ["checkpoint", 1]
            }
        },
        
        "negative_prompt": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": faction_prompt["negative"],
                "clip": ["checkpoint", 1]
            }
        },
        
        # High resolution generation (as per asset implementation notes)
        "latent": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1536,   # High base resolution for vector clarity
                "height": 1536,
                "batch_size": 1
            }
        },
        
        # Optimized FLUX sampling for emblems
        "sampler": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 35,      # Quality steps for detailed emblems
                "cfg": 4.0,       # FLUX-optimized CFG
                "sampler_name": "euler",
                "scheduler": "simple",  # FLUX-optimized scheduler
                "denoise": 1.0,
                "model": ["checkpoint", 0],
                "positive": ["positive_prompt", 0],
                "negative": ["negative_prompt", 0],
                "latent_image": ["latent", 0]
            }
        },
        
        # VAE decode
        "decoded": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["sampler", 0],
                "vae": ["checkpoint", 2]
            }
        },
        
        # Final resize to Terminal Grounds standard (2048x2048 per documentation)
        "final_emblem": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["decoded", 0],
                "upscale_method": "lanczos",  # Preserves vector sharpness
                "width": 2048,
                "height": 2048,
                "crop": "center"
            }
        },
        
        # Save with documentation-compliant naming
        "save": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["final_emblem", 0],
                "filename_prefix": f"TG_LORE_{faction_code}_{faction_data['name']}_Emblem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
    }
    
    return workflow, faction_data

def test_documentation_accuracy():
    """
    Test documentation-accurate emblem generation
    """
    
    print("=== TESTING DOCUMENTATION-ACCURATE WORKFLOW ===")
    
    # Test with Directorate (most detailed documentation)
    workflow, faction_data = build_documentation_emblem_workflow("DIR", seed=88888)
    
    print(f"Faction: {faction_data['name']}")
    print(f"Identity: {faction_data['identity']}")
    print(f"Visual Philosophy: {faction_data['visual_philosophy']}")
    print(f"Primary Color: {faction_data['colors']['primary']}")
    print(f"Emblem Core: {faction_data['emblem_core']}")
    print(f"Material Authenticity: {faction_data['materials'][:100]}...")
    
    # Send to ComfyUI
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
            print(f"\\nDocumentation workflow queued: {prompt_id}")
            print("\\nDocumentation compliance:")
            print("- Official faction identity from art bible")
            print("- Exact color codes from style guide")  
            print("- Material descriptions from documentation")
            print("- Aesthetic keywords from visual philosophy")
            print("- Forbidden elements excluded per guidelines")
            print("- Asset naming per UE5 implementation notes")
            print("\\nThis should produce the most Terminal Grounds-accurate emblem yet!")
            return prompt_id
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_all_documented_factions():
    """
    Generate emblems for all documented factions
    """
    
    prompt_master = TerminalGroundsPromptMaster()
    faction_codes = ["DIR", "VLT", "CCB"]  # Documented factions
    
    print(f"\\n=== GENERATING ALL DOCUMENTED FACTIONS ===")
    
    for i, faction_code in enumerate(faction_codes):
        print(f"\\nGenerating {faction_code}...")
        
        workflow, faction_data = build_documentation_emblem_workflow(faction_code, seed=90000 + i)
        
        # Send to ComfyUI
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
                print(f"  {faction_data['name']}: {prompt_id}")
        except Exception as e:
            print(f"  {faction_code}: Error - {e}")

if __name__ == "__main__":
    test_documentation_accuracy()