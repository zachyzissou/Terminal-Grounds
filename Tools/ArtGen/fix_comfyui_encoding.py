#!/usr/bin/env python3
"""
Fix ComfyUI encoding issues and problematic nodes
"""
import os
import shutil
from pathlib import Path

def fix_encoding_issues():
    """Fix Unicode encoding issues in ComfyUI nodes"""
    
    comfyui_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API")
    custom_nodes = comfyui_path / "custom_nodes"
    
    # Create disabled nodes directory
    disabled_dir = custom_nodes / "disabled"
    disabled_dir.mkdir(exist_ok=True)
    
    # List of problematic nodes to disable temporarily
    problematic_nodes = [
        "aiia",  # Chinese text causing Unicode errors
        "ComfyUI-nunchaku",  # Missing nunchaku dependency
        "ComfyUI-RizzNodes",  # Missing trimesh dependency  
        "comfyui-layerdiffuse",  # xFormers DLL issues
        "ComfyUI-WanVideoWrapper",  # Potential issues
    ]
    
    disabled_count = 0
    
    for node_name in problematic_nodes:
        node_path = custom_nodes / node_name
        if node_path.exists():
            disabled_path = disabled_dir / node_name
            print(f"Disabling problematic node: {node_name}")
            if disabled_path.exists():
                shutil.rmtree(disabled_path)
            shutil.move(str(node_path), str(disabled_path))
            disabled_count += 1
    
    print(f"Disabled {disabled_count} problematic nodes")
    return disabled_count

def fix_logger_encoding():
    """Fix logger encoding in ComfyUI"""
    logger_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/app/logger.py")
    
    if logger_path.exists():
        # Read current content
        with open(logger_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already fixed
        if 'errors="replace"' in content:
            print("Logger encoding already fixed")
            return False
        
        # Fix encoding issue
        content = content.replace(
            'super().write(data)',
            'super().write(data.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))'
        )
        
        # Write back
        with open(logger_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed logger encoding")
        return True
    
    return False

def create_startup_script():
    """Create a startup script with proper encoding"""
    startup_script = """@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo Starting ComfyUI with proper encoding...
cd /d "C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
"""
    
    with open("C:/Users/Zachg/Terminal-Grounds/START_COMFYUI_FIXED.bat", 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("Created fixed startup script: START_COMFYUI_FIXED.bat")

if __name__ == "__main__":
    print("Fixing ComfyUI encoding and stability issues...")
    
    disabled = fix_encoding_issues()
    logger_fixed = fix_logger_encoding() 
    create_startup_script()
    
    print("\nFixes applied:")
    print(f"- Disabled {disabled} problematic nodes")
    print(f"- Logger encoding {'fixed' if logger_fixed else 'already ok'}")
    print("- Created fixed startup script")
    print("\nUse START_COMFYUI_FIXED.bat to start ComfyUI")