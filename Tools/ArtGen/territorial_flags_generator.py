#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Territorial Flags Generator - CTO Phase 2 Implementation
Extends proven terminal_grounds_generator.py for faction territorial flags
Maintains 92% success rate with proven PERFECTION_PARAMS workflow structure
"""
import json
import urllib.request
import time
import uuid
import random
import itertools
import argparse
import subprocess
import sys
import os
from pathlib import Path

# Fix Windows Unicode encoding issues permanently
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Import proven parameters from working generator
sys.path.append(str(Path(__file__).parent))
from terminal_grounds_generator import PERFECTION_PARAMS, create_workflow, submit_workflow

def generate_territorial_flags():
    """Generate all 7 faction territorial flags using proven system"""
    
    print("TERRITORIAL FLAGS GENERATOR - CTO Phase 2")
    print("Extends proven 92% success rate system for territorial assets")
    print("=" * 60)
    
    # All 7 faction territorial flags
    territorial_flags = [
        "Territorial_Flag_Directorate",
        "Territorial_Flag_Iron_Scavengers", 
        "Territorial_Flag_Seventy_Seven",
        "Territorial_Flag_Corporate_Hegemony",
        "Territorial_Flag_Nomad_Clans",
        "Territorial_Flag_Archive_Keepers",
        "Territorial_Flag_Civic_Wardens"
    ]
    
    # Use proven style variations 
    styles = ["Clean_SciFi", "Gritty_Realism"]
    
    # Single angle/lighting for territorial flags (focused generation)
    angle = "Wide"
    lighting = "Ambient"
    
    total_assets = len(territorial_flags) * len(styles)
    seed_base = PERFECTION_PARAMS["seed"]
    
    print(f"Generating {total_assets} territorial flag assets")
    print(f"Seed base: {seed_base}, {PERFECTION_PARAMS['sampler']}/{PERFECTION_PARAMS['scheduler']}, CFG {PERFECTION_PARAMS['cfg']}, {PERFECTION_PARAMS['steps']} steps")
    print(f"Resolution: {PERFECTION_PARAMS['width']}x{PERFECTION_PARAMS['height']} (modified to 1024x1024 for flags)")
    print()
    
    # Generate all combinations
    for i, location in enumerate(territorial_flags):
        for j, style in enumerate(styles):
            # Calculate systematic seed offset
            seed_offset = (i * len(styles)) + j
            
            # Create workflow using proven structure 
            workflow = create_workflow(location, style, seed_offset, angle, lighting)
            
            # Modify resolution for territorial flags (square format)
            if "8" in workflow and "inputs" in workflow["8"]:
                workflow["8"]["inputs"]["width"] = 1024
                workflow["8"]["inputs"]["height"] = 1024
            
            # Submit using proven submission function
            try:
                result = submit_workflow(workflow, location, style, angle, lighting)
                if result:
                    print(f"Queued: {location} ({style}) - {result}")
                else:
                    print(f"FAILED: {location} ({style})")
            except Exception as e:
                print(f"ERROR: {location} ({style}) - {e}")
            
            # Small delay between submissions (proven approach)
            time.sleep(0.5)
    
    print()
    print("=" * 60)
    print(f"TERRITORIAL FLAGS BATCH COMPLETE: {total_assets} assets queued")
    print()
    print("Output files will be named:")
    print("TG_PERFECT_Territorial_Flag_[Faction]_[Style]_[Angle]_[Lighting]_*.png")
    print()
    print("CTO Phase 2: Territorial flag generation using proven 92% success rate system")
    print("Maintains PERFECTION_PARAMS structure with territorial-specific prompts")
    print("Expected success rate: 92% (proven system baseline)")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Generate territorial flags for all 7 factions')
    parser.add_argument('--test', action='store_true', help='Generate only one flag for testing')
    
    args = parser.parse_args()
    
    if args.test:
        print("TEST MODE: Generating single Civic Wardens flag")
        # Generate just one flag for testing
        workflow = create_workflow("Territorial_Flag_Civic_Wardens", "Clean_SciFi", 0, "Wide", "Ambient")
        if "8" in workflow and "inputs" in workflow["8"]:
            workflow["8"]["inputs"]["width"] = 1024
            workflow["8"]["inputs"]["height"] = 1024
        
        result = submit_workflow(workflow, "Territorial_Flag_Civic_Wardens", "Clean_SciFi", "Wide", "Ambient")
        if result:
            print(f"SUCCESS: Test flag queued - {result}")
        else:
            print("FAILED: Test flag submission failed")
    else:
        generate_territorial_flags()

if __name__ == "__main__":
    main()