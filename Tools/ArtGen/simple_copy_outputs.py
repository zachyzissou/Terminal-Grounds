#!/usr/bin/env python3
"""
Simple ComfyUI Output Copier
Copy recent ComfyUI outputs to staging folder for analysis
"""

import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
COMFYUI_OUTPUT = Path(r"C:\Users\Zachg\Documents\ComfyUI\output")
STAGING_ROOT = Path(r"C:\Users\Zachg\Terminal-Grounds\Style_Staging")

def copy_recent_outputs(hours_back=2):
    """Copy outputs from the last N hours"""
    
    if not COMFYUI_OUTPUT.exists():
        print(f"ComfyUI output folder not found: {COMFYUI_OUTPUT}")
        return 0
        
    analysis_folder = STAGING_ROOT / "_Recent_Generations"
    analysis_folder.mkdir(parents=True, exist_ok=True)
    
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    copied_count = 0
    
    print(f"Copying outputs from last {hours_back} hours...")
    
    for file_path in COMFYUI_OUTPUT.glob("*.png"):
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        if file_time > cutoff_time:
            dest_path = analysis_folder / file_path.name
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
                copied_count += 1
                print(f"  Copied: {file_path.name}")
    
    print(f"Copied {copied_count} recent files")
    return copied_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Copy recent ComfyUI outputs")
    parser.add_argument("--hours", type=int, default=2,
                       help="Copy files from last N hours")
    
    args = parser.parse_args()
    copy_recent_outputs(args.hours)