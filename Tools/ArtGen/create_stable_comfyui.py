#!/usr/bin/env python3
"""
Create Stable ComfyUI Configuration - Terminal Grounds
Disables problematic nodes that cause crashes while preserving essential functionality
"""
import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def disable_crash_causing_nodes():
    """Disable nodes that cause segmentation faults and crashes"""
    base_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes")
    disabled_dir = base_path / "disabled_nodes"
    disabled_dir.mkdir(exist_ok=True)
    
    # Nodes that are causing crashes due to xFormers/DLL compatibility
    problematic_nodes = [
        "aiia",  # Unicode issues (already moved)
        "ComfyUI-nunchaku",  # Missing nunchaku package, xFormers DLL errors
        "comfyui-layerdiffuse",  # xFormers DLL compatibility issues
    ]
    
    disabled_count = 0
    
    for node_name in problematic_nodes:
        node_path = base_path / node_name
        disabled_path = base_path / f"{node_name}.disabled"
        
        # Check if node exists and isn't already disabled
        if node_path.exists() and not disabled_path.exists():
            try:
                shutil.move(str(node_path), str(disabled_path))
                logger.info(f"✓ Disabled {node_name} (crash prevention)")
                disabled_count += 1
            except Exception as e:
                logger.warning(f"Failed to disable {node_name}: {e}")
        elif disabled_path.exists():
            logger.info(f"• {node_name} already disabled")
        else:
            logger.info(f"• {node_name} not found")
    
    return disabled_count

def verify_essential_nodes():
    """Verify that essential nodes are still available"""
    base_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes")
    
    essential_nodes = [
        "ComfyUI-RizzNodes",  # Should work now with trimesh installed
        "ComfyUI-Manager",
        "efficiency-nodes-comfyui", 
        "comfyui_controlnet_aux",
        "ComfyUI-Impact-Pack",
        "comfyui-bawknodes",  # FLUX workflow suite
        "cg-use-everywhere",
        "ComfyUI-Crystools",
    ]
    
    working_count = 0
    
    logger.info("Essential nodes status:")
    for node in essential_nodes:
        node_path = base_path / node
        if node_path.exists():
            logger.info(f"✓ {node} - Available")
            working_count += 1
        else:
            logger.warning(f"✗ {node} - Missing")
    
    return working_count, len(essential_nodes)

def create_stable_startup_script():
    """Create the final stable startup script"""
    startup_script = """@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ==========================================
echo  ComfyUI - Terminal Grounds (STABLE)
echo ==========================================
echo.
echo Status: Problematic nodes disabled
echo Encoding: UTF-8 
echo Port: 8188
echo.
echo Starting ComfyUI...
echo Wait for "Starting server" message
echo.

cd /d "C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API"

python main.py --listen 127.0.0.1 --port 8188

echo.
echo ComfyUI stopped.
pause
"""
    
    script_path = Path("C:/Users/Zachg/Terminal-Grounds/START_COMFYUI_STABLE.bat")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    logger.info(f"✓ Created stable startup script: {script_path}")

def main():
    """Main function to create stable configuration"""
    logger.info("Creating Stable ComfyUI Configuration...")
    logger.info("Prioritizing: No crashes > Feature completeness")
    
    # Disable crash-causing nodes
    disabled = disable_crash_causing_nodes()
    
    # Verify essential nodes
    working, total = verify_essential_nodes()
    
    # Create stable startup script
    create_stable_startup_script()
    
    logger.info("\n" + "="*50)
    logger.info("STABLE CONFIGURATION COMPLETE")
    logger.info("="*50)
    
    logger.info(f"✓ Disabled {disabled} problematic nodes")
    logger.info(f"✓ {working}/{total} essential nodes available")
    logger.info("✓ Stable startup script created")
    
    logger.info("\nSTABILITY MEASURES:")
    logger.info("• AIIA disabled (Unicode crashes)")
    logger.info("• nunchaku disabled (missing dependencies)")  
    logger.info("• layerdiffuse disabled (xFormers DLL issues)")
    logger.info("• RizzNodes kept (trimesh installed)")
    logger.info("• All FLUX workflow nodes preserved")
    
    logger.info("\nNEXT STEPS:")
    logger.info("1. Use START_COMFYUI_STABLE.bat")
    logger.info("2. Verify startup reaches 'Starting server'")
    logger.info("3. Test asset generation workflows")
    
    logger.info("\n🎯 Configuration optimized for stability!")

if __name__ == "__main__":
    main()