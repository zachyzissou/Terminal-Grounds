#!/usr/bin/env python3
"""
VISUAL ENHANCEMENT EXPERIMENT - Terminal Grounds
Enhanced detail and faction-specific weathering using proven parameters as foundation
Safe incremental improvements to CFG/steps within tested ranges
"""

import json
import urllib.request
import time
import uuid

# ENHANCED PARAMETERS - Safe improvements within tested ranges
ENHANCED_PARAMS = {
    "sampler": "heun",        # Proven reliable - never change
    "scheduler": "normal",    # Proven reliable - never change
    "cfg": 3.5,              # Enhanced from proven 3.2 (based on sharp weapon success)
    "steps": 30,             # Enhanced from proven 25 (based on sharp weapon success)
    "width": 1536,
    "height": 864
}

def create_visual_enhancement_workflow(asset_type, faction, description, seed):
    """Enhanced visual quality using proven sharp weapon parameters"""
    
    # FACTION-SPECIFIC VISUAL ENHANCEMENT
    faction_enhancements = {
        "Directorate": "corporate precision engineering, regulation blue-grey surfaces, standardized military specification, angular geometric panels",
        "Free77": "professional mercenary modifications, tactical red accent colors, contractor-grade equipment, field-tested reliability",
        "IronScavengers": "scavenged component integration, trophy warfare modifications, improvised repairs, functional ugliness aesthetic",
        "CivicWardens": "civilian equipment militarization, community protection modifications, neighborhood watch aesthetics",
        "NomadClans": "convoy survival adaptations, tribal weathering patterns, overland expedition equipment"
    }
    
    enhancement = faction_enhancements.get(faction, "military specification")
    
    # ENHANCED POSITIVE PROMPT - Detailed material focus
    positive_prompt = f"ultra sharp professional {asset_type} concept art, {description}, {enhancement}, Terminal Grounds faction aesthetic, crystal clear mechanical engineering, pin-sharp technical details, high definition material textures, realistic metal surfaces, authentic weathering patterns, detailed component assembly, professional game asset quality"
    
    # PROVEN NEGATIVE PROMPT - From successful sharp weapon generation
    negative_prompt = "blurry, out of focus, soft focus, low resolution, pixelated, low quality, fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, gaussian blur, soft edges, poor focus, low detail, compressed artifacts, jpeg artifacts, cartoon, anime, fantasy, clean pristine condition, text, letters, writing, readable text"
    
    # PROVEN 7-NODE WORKFLOW STRUCTURE
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": ENHANCED_PARAMS["width"],
                "height": ENHANCED_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": ENHANCED_PARAMS["steps"],
                "cfg": ENHANCED_PARAMS["cfg"],
                "sampler_name": ENHANCED_PARAMS["sampler"],
                "scheduler": ENHANCED_PARAMS["scheduler"],
                "denoise": 1.0,
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
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"TG_VISUAL_ENHANCED_{asset_type}_{faction}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def run_visual_enhancement_experiment():
    """Test enhanced visual quality on diverse asset types"""
    
    # DIVERSE TEST ASSETS - One per faction for visual comparison
    test_assets = [
        ("weapon", "Directorate", "precision machine gun with corporate engineering"),
        ("vehicle", "IronScavengers", "combat technical with salvaged armor plating"),
        ("equipment", "NomadClans", "survival gear with tribal modifications")
    ]
    
    base_seed = 320000  # New seed range for clean comparison
    
    print("VISUAL ENHANCEMENT EXPERIMENT - Terminal Grounds")
    print("Enhanced detail quality using proven sharp weapon parameters")
    print("=" * 70)
    print()
    print("EXPERIMENT PARAMETERS:")
    print(f"  Base Model: FLUX1-dev-fp8.safetensors")
    print(f"  Enhanced CFG: {ENHANCED_PARAMS['cfg']} (up from proven 3.2)")
    print(f"  Enhanced Steps: {ENHANCED_PARAMS['steps']} (up from proven 25)")
    print(f"  Proven Sampler: {ENHANCED_PARAMS['sampler']}/{ENHANCED_PARAMS['scheduler']}")
    print(f"  Enhanced Feature: Faction-specific visual language")
    print()
    
    success_count = 0
    
    for i, (asset_type, faction, description) in enumerate(test_assets):
        seed = base_seed + (i * 500)  # Proven seed spacing
        
        print(f"Test {i+1}: {asset_type.upper()} - {faction}")
        print(f"  Description: {description}")
        print(f"  Enhancement: Faction-specific visual language")
        print(f"  Seed: {seed}")
        
        workflow = create_visual_enhancement_workflow(asset_type, faction, description, seed)
        
        try:
            # Submit to ComfyUI using proven method
            data = json.dumps({"prompt": workflow}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt",
                                       data=data,
                                       headers={'Content-Type': 'application/json'})
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            prompt_id = result.get('prompt_id', 'unknown')
            print(f"  -> Submitted successfully (ID: {prompt_id})")
            success_count += 1
            
        except Exception as e:
            print(f"  -> ERROR: {e}")
            
        print()
        
        # PROVEN 0.5 second delay
        time.sleep(0.5)
    
    print("=" * 70)
    print("VISUAL ENHANCEMENT EXPERIMENT QUEUED")
    print(f"Success Rate: {success_count}/{len(test_assets)} submissions")
    print()
    print("VALIDATION CRITERIA:")
    print("  1. Enhanced mechanical detail compared to baseline")
    print("  2. Accurate faction-specific visual language")
    print("  3. Improved material textures and weathering")
    print("  4. Maintained sharpness with no blur artifacts")
    print()
    print("COMPARISON TARGETS:")
    print("  - Compare detail level against existing TG_LORE_* assets")
    print("  - Validate faction visual accuracy against lore bible")
    print("  - Measure material quality improvement")
    print()
    print("Output files: TG_VISUAL_ENHANCED_*")

if __name__ == "__main__":
    run_visual_enhancement_experiment()