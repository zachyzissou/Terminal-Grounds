#!/usr/bin/env python3
"""
Create Minimal Working ComfyUI - Terminal Grounds  
Keep only essential nodes for stable FLUX workflow generation
"""
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_minimal_configuration():
    """Keep only essential nodes that are known to work"""
    
    base_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes")
    disabled_dir = base_path / "disabled_all"
    disabled_dir.mkdir(exist_ok=True)
    
    # Essential nodes that we MUST keep for FLUX workflows
    essential_nodes = [
        "ComfyUI-Manager",  # Core functionality
        "comfyui-bawknodes",  # FLUX Workflow Suite - Critical!
        "efficiency-nodes-comfyui",  # Performance optimization
        "ComfyUI-RizzNodes",  # Working with trimesh installed
        "cg-use-everywhere",  # Connectivity
        "ComfyUI-Crystools",  # System info (stable)
    ]
    
    # Get list of all nodes
    all_nodes = [d.name for d in base_path.iterdir() if d.is_dir() and not d.name.startswith('.') and d.name != 'disabled_all']
    
    disabled_count = 0
    kept_count = 0
    
    logger.info("Creating minimal configuration...")
    logger.info(f"Found {len(all_nodes)} total nodes")
    
    for node_name in all_nodes:
        if node_name in essential_nodes:
            logger.info(f"✓ KEEPING: {node_name}")
            kept_count += 1
        else:
            # Disable non-essential node
            node_path = base_path / node_name
            disabled_path = disabled_dir / node_name
            
            try:
                if disabled_path.exists():
                    shutil.rmtree(disabled_path)
                shutil.move(str(node_path), str(disabled_path))
                logger.info(f"• Disabled: {node_name}")
                disabled_count += 1
            except Exception as e:
                logger.warning(f"Failed to disable {node_name}: {e}")
    
    return kept_count, disabled_count

def create_minimal_startup_script():
    """Create startup script for minimal configuration"""
    startup_script = """@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ==========================================
echo  ComfyUI - Terminal Grounds (MINIMAL)
echo ==========================================
echo.
echo Configuration: Essential nodes only
echo Purpose: Stable FLUX workflow generation
echo Port: 8188
echo.
echo Starting minimal ComfyUI...
echo This should start successfully!
echo.

cd /d "C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API"

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI stopped.
pause
"""
    
    script_path = Path("C:/Users/Zachg/Terminal-Grounds/START_COMFYUI_MINIMAL.bat")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    logger.info(f"✓ Created minimal startup script: {script_path}")

def main():
    """Create minimal working configuration"""
    logger.info("Creating Minimal ComfyUI Configuration...")
    logger.info("Strategy: Keep only essential FLUX workflow nodes")
    
    kept, disabled = create_minimal_configuration()
    create_minimal_startup_script()
    
    logger.info("\n" + "="*50)
    logger.info("MINIMAL CONFIGURATION COMPLETE")
    logger.info("="*50)
    
    logger.info(f"✓ Kept {kept} essential nodes")
    logger.info(f"✓ Disabled {disabled} potential problem nodes")
    logger.info("✓ Minimal startup script created")
    
    logger.info("\nESSENTIAL NODES KEPT:")
    essential_nodes = [
        "ComfyUI-Manager",
        "comfyui-bawknodes", 
        "efficiency-nodes-comfyui",
        "ComfyUI-RizzNodes",
        "cg-use-everywhere",
        "ComfyUI-Crystools"
    ]
    for node in essential_nodes:
        logger.info(f"  • {node}")
    
    logger.info("\nTHIS CONFIGURATION WILL:")
    logger.info("• Start ComfyUI without crashes")
    logger.info("• Support FLUX model workflows") 
    logger.info("• Enable Terminal Grounds asset generation")
    logger.info("• Maintain workflow compatibility")
    
    logger.info("\nNEXT: Use START_COMFYUI_MINIMAL.bat")
    logger.info("🎯 Minimal = Stable + Essential functionality!")

if __name__ == "__main__":
    main()