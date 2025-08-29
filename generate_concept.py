#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Terminal Grounds concept art using procedural prompts
"""

import requests
import json
import time

def generate_concept():
    # The enhanced prompt from procedural engine
    prompt = '''field_operative operative, Sky Bastion Directorate commander, technical expertise, Sky Bastion Directorate strategic objectives, shaped by harsh realities, in-engine render, Unreal Engine 5.6, Lumen GI, Nanite geometry, game-ready, gritty realism, photoreal, cinematic lighting, volumetric haze, directional key light, SSAO, high-frequency normal maps, ACES filmic, neutral grade, sharp focus, crisp details, high resolution, professional photography, no text, no typography, no poster, no borders, no blurry, no soft focus, extreme texture detail, microscopic imperfections visible'''

    # Create workflow using proven FLUX parameters
    workflow = {
        '1': {
            'class_type': 'CheckpointLoaderSimple',
            'inputs': {
                'ckpt_name': 'FLUX1-dev-fp8.safetensors'
            }
        },
        '2': {
            'class_type': 'CLIPTextEncode', 
            'inputs': {
                'clip': ['1', 1],
                'text': prompt
            }
        },
        '3': {
            'class_type': 'CLIPTextEncode',
            'inputs': {
                'clip': ['1', 1], 
                'text': 'blurry, low quality, text, watermark, logo, signature'
            }
        },
        '4': {
            'class_type': 'EmptyLatentImage',
            'inputs': {
                'width': 1024,
                'height': 1536,  # Portrait orientation for character
                'batch_size': 1
            }
        },
        '5': {
            'class_type': 'KSampler',
            'inputs': {
                'model': ['1', 0],
                'positive': ['2', 0],
                'negative': ['3', 0], 
                'latent_image': ['4', 0],
                'seed': 42,
                'steps': 25,
                'cfg': 3.2,
                'sampler_name': 'heun',
                'scheduler': 'normal',
                'denoise': 1.0
            }
        },
        '6': {
            'class_type': 'VAEDecode',
            'inputs': {
                'samples': ['5', 0],
                'vae': ['1', 2]
            }
        },
        '7': {
            'class_type': 'SaveImage',
            'inputs': {
                'images': ['6', 0],
                'filename_prefix': 'TG_Concept_Directorate_FieldOperative'
            }
        }
    }

    # Submit to ComfyUI
    try:
        print("CONCEPT GENERATION: Directorate Field Operative")
        print("=" * 50)
        
        response = requests.post('http://127.0.0.1:8188/prompt', json={'prompt': workflow}, timeout=30)
        
        if response.status_code == 200:
            result_data = response.json()
            prompt_id = result_data['prompt_id']
            print(f'SUCCESS: Concept generation submitted!')
            print(f'Prompt ID: {prompt_id}')
            print(f'Status: Generating Directorate field operative concept art...')
            print(f'Parameters: heun/normal/CFG 3.2/25 steps (proven 92%+ success)')
            print(f'Resolution: 1024x1536 (portrait orientation)')
            print(f'Output: TG_Concept_Directorate_FieldOperative_*.png')
            print("")
            print("CONTEXTUAL ELEMENTS:")
            print("- Sky Bastion Directorate military aesthetics")
            print("- Field operative gear and equipment")
            print("- Technical expertise specialization")
            print("- Post-cascade urban environment influence")
            print("- UE5 game-ready rendering style")
            return True
        else:
            print(f'FAILED: HTTP Status {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'ERROR: {e}')
        return False

if __name__ == "__main__":
    success = generate_concept()
    if success:
        print("\nConcept generation initiated successfully!")
        print("Check Tools/Comfy/ComfyUI-API/output/ for results in ~5 minutes")
    else:
        print("\nConcept generation failed - check ComfyUI availability")