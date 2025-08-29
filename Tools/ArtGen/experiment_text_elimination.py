#!/usr/bin/env python3
"""
TEXT ELIMINATION EXPERIMENT - Terminal Grounds
Precise refinement of proven patterns for enhanced text elimination
Based on successful FIXED_faction_vehicle_concepts.py foundation
"""

import json
import urllib.request
import time
import uuid

# PROVEN BASE PARAMETERS - Do not modify these (92% success rate foundation)
PROVEN_PARAMS = {
    "sampler": "heun",        # Proven reliable
    "scheduler": "normal",    # Proven reliable  
    "cfg": 3.2,              # Proven baseline - DO NOT CHANGE
    "steps": 25,             # Proven baseline - DO NOT CHANGE
    "width": 1536,
    "height": 864
}

def create_enhanced_text_elimination_workflow(asset_type, faction, description, seed):
    """Enhanced text elimination using proven 7-node structure"""
    
    # ENHANCED TEXT ELIMINATION NEGATIVE PROMPT - Built on proven foundation
    enhanced_negative = (
        "readable text, legible lettering, clear typography, sharp text, crisp letters, "
        "defined characters, product labels, serial numbers, model numbers, weapon markings, "
        "technical specifications, instructional text, warning labels, manufacturer text, "
        "stenciled text, etched text, raised lettering, engraved text, stamped markings, "
        "printed text, display screens, digital readouts, text overlays, alpha-numeric codes, "
        "writing, words, letters, symbols, numbers, inscriptions, signage, typography, "
        "character symbols, alphanumeric content, gibberish text, scrambled letters, "
        "unreadable markings, nonsense symbols, corrupted signage, "
        # Proven base negatives from successful scripts
        "blurry, out of focus, soft focus, low resolution, pixelated, low quality, "
        "fuzzy, hazy, unclear, indistinct, smudged, motion blur, depth of field blur, "
        "gaussian blur, soft edges, poor focus, low detail, compressed artifacts, "
        "cartoon, anime, fantasy, clean pristine condition"
    )
    
    # PROVEN POSITIVE PROMPT STRUCTURE - Enhanced for text-free assets
    positive_prompt = f"ultra sharp professional {asset_type} concept art, {description}, Terminal Grounds {faction} faction aesthetic, crisp detailed game asset concept, razor sharp orthographic view, crystal clear mechanical details, pin-sharp technical design, high definition concept art, professional game asset quality, detailed engineering, NO text, NO writing, NO labels"
    
    # PROVEN 7-NODE WORKFLOW STRUCTURE (never change this structure)
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
            "inputs": {"text": enhanced_negative, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": PROVEN_PARAMS["width"],
                "height": PROVEN_PARAMS["height"],
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": PROVEN_PARAMS["steps"],
                "cfg": PROVEN_PARAMS["cfg"],
                "sampler_name": PROVEN_PARAMS["sampler"],
                "scheduler": PROVEN_PARAMS["scheduler"],
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
                "filename_prefix": f"TG_TEXT_ELIMINATION_{asset_type}_{faction}",
                "images": ["6", 0]
            }
        }
    }
    
    return workflow

def run_text_elimination_experiment():
    """Test enhanced text elimination on proven problematic asset types"""
    
    # TEST ASSETS - Focus on historically text-prone categories
    test_assets = [
        ("weapon", "Directorate", "military assault rifle with clean surfaces"),
        ("vehicle", "Free77", "armored personnel carrier with tactical modifications"),
        ("equipment", "CivicWardens", "tactical armor vest with equipment attachments")
    ]
    
    base_seed = 300000  # New seed range for clean comparison
    
    print("TEXT ELIMINATION EXPERIMENT - Terminal Grounds")
    print("Enhanced text elimination using proven 92% success foundation")
    print("=" * 70)
    print()
    print("EXPERIMENT PARAMETERS:")
    print(f"  Base Model: FLUX1-dev-fp8.safetensors")
    print(f"  Proven CFG: {PROVEN_PARAMS['cfg']} (DO NOT MODIFY)")
    print(f"  Proven Steps: {PROVEN_PARAMS['steps']} (DO NOT MODIFY)")  
    print(f"  Proven Sampler: {PROVEN_PARAMS['sampler']}/{PROVEN_PARAMS['scheduler']}")
    print(f"  Enhanced Feature: Military-specific text elimination")
    print()
    
    success_count = 0
    
    for i, (asset_type, faction, description) in enumerate(test_assets):
        seed = base_seed + (i * 500)  # Proven seed spacing
        
        print(f"Test {i+1}: {asset_type.upper()} - {faction}")
        print(f"  Description: {description}")
        print(f"  Seed: {seed}")
        
        workflow = create_enhanced_text_elimination_workflow(asset_type, faction, description, seed)
        
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
        
        # PROVEN 0.5 second delay (critical for queue stability)
        time.sleep(0.5)
    
    print("=" * 70)
    print("TEXT ELIMINATION EXPERIMENT QUEUED")
    print(f"Success Rate: {success_count}/{len(test_assets)} submissions")
    print()
    print("VALIDATION CRITERIA:")
    print("  1. Zero readable text on any generated asset")
    print("  2. Maintained surface detail quality")
    print("  3. Clean industrial/military aesthetic preserved")
    print("  4. Compare against existing TG_LORE_WEAPONS_* for improvement")
    print()
    print("NEXT STEPS:")
    print("  1. Wait ~15 minutes for generation completion")
    print("  2. Examine each asset for text elimination success")
    print("  3. If successful, apply to full asset generation pipeline")
    print("  4. If unsuccessful, revert to proven FIXED_faction_vehicle baseline")
    print()
    print("Output files: TG_TEXT_ELIMINATION_*")

if __name__ == "__main__":
    run_text_elimination_experiment()