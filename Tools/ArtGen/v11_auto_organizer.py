#!/usr/bin/env python3
"""
v1.1 PERFECTION GRADE Auto-Organizer
Automatically organizes v1.1 results for quality comparison and analysis
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

def organize_v11_batch():
    """Automatically organize v1.1 PERFECTION GRADE results"""
    output_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
    v11_batch_dir = output_dir / "environments" / "batch_v11_2025-08-24"
    
    # Create v1.1 batch directory
    v11_batch_dir.mkdir(parents=True, exist_ok=True)
    
    # Find new TG_PERFECT files with 00003_ pattern (v1.1 indicators)
    main_env_dir = output_dir / "environments"
    
    moved_files = []
    for png_file in main_env_dir.glob("TG_PERFECT_*00003_*.png"):
        target_path = v11_batch_dir / png_file.name
        shutil.move(str(png_file), str(target_path))
        moved_files.append(png_file.name)
        print(f"[v1.1] Moved {png_file.name} to v1.1 batch")
    
    print(f"\n[SUCCESS] Organized {len(moved_files)} v1.1 PERFECTION GRADE assets")
    return moved_files

if __name__ == "__main__":
    organize_v11_batch()