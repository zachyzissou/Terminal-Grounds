#!/usr/bin/env python3
"""
Restore specific nodes needed for advanced Terminal Grounds workflows
"""
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def restore_workflow_specific_nodes():
    """Restore nodes needed for advanced workflows while maintaining stability"""
    
    base_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes")
    disabled_dir = base_path / "disabled_all"
    
    # Nodes needed for advanced Terminal Grounds workflows
    workflow_nodes = [
        "comfyui_ultimatesdupscale",  # For UltimateSDUpscale
        "ComfyUI-Impact-Pack",  # Has ImageSharpen and other utilities
        "comfyui_controlnet_aux",  # For advanced control
    ]
    
    restored = []
    
    for node_name in workflow_nodes:
        disabled_path = disabled_dir / node_name
        active_path = base_path / node_name
        
        if disabled_path.exists() and not active_path.exists():
            try:
                shutil.move(str(disabled_path), str(active_path))
                logger.info(f"✓ Restored: {node_name}")
                restored.append(node_name)
            except Exception as e:
                logger.warning(f"Failed to restore {node_name}: {e}")
    
    return restored

def main():
    """Restore nodes for advanced workflows"""
    logger.info("Restoring nodes for advanced Terminal Grounds workflows...")
    
    restored = restore_workflow_specific_nodes()
    
    if restored:
        logger.info(f"\n✅ Restored {len(restored)} nodes for advanced workflows")
        logger.info("Advanced workflow features now available:")
        for node in restored:
            logger.info(f"  • {node}")
        
        logger.info("\n⚠️  RESTART REQUIRED:")
        logger.info("Use START_COMFYUI_MINIMAL.bat to restart with new nodes")
    else:
        logger.info("No additional nodes needed to restore")

if __name__ == "__main__":
    main()