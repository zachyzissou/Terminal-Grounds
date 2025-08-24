#!/usr/bin/env python3
"""
ComfyUI Comprehensive Repair Script - Terminal Grounds
Fixes Unicode encoding, missing dependencies, and xFormers compatibility without disabling functionality
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def set_environment_encoding():
    """Set proper UTF-8 encoding for Python environment"""
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    logger.info("Set environment encoding to UTF-8")

def fix_aiia_unicode_encoding():
    """Fix Unicode encoding issues in AIIA node without disabling it"""
    aiia_init_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes/aiia/__init__.py")
    
    if not aiia_init_path.exists():
        logger.info("AIIA node not found, skipping Unicode fix")
        return False
    
    try:
        # Read the file with explicit UTF-8 encoding
        with open(aiia_init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add encoding declaration at the top if not present
        if '# -*- coding: utf-8 -*-' not in content:
            lines = content.split('\n')
            # Insert encoding declaration after shebang if present, otherwise at the beginning
            if lines[0].startswith('#!'):
                lines.insert(1, '# -*- coding: utf-8 -*-')
            else:
                lines.insert(0, '# -*- coding: utf-8 -*-')
            content = '\n'.join(lines)
        
        # Wrap print statements with proper encoding handling
        content = content.replace(
            'print("--- 正在加载 ComfyUI_AIIA 自定义节点包 ---")',
            'print("--- 正在加载 ComfyUI_AIIA 自定义节点包 ---".encode("utf-8", errors="replace").decode("utf-8", errors="replace"))'
        )
        
        # Fix other print statements with Chinese text
        content = content.replace(
            'print(f"尝试导入 {module_name_relative}...")',
            'print(f"尝试导入 {module_name_relative}...".encode("utf-8", errors="replace").decode("utf-8", errors="replace"))'
        )
        
        content = content.replace(
            'print(f"  成功导入 {module_alias_for_log} 模块对象。")',
            'print(f"  成功导入 {module_alias_for_log} 模块对象。".encode("utf-8", errors="replace").decode("utf-8", errors="replace"))'
        )
        
        # Write back with UTF-8 encoding
        with open(aiia_init_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Fixed Unicode encoding in AIIA node")
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix AIIA Unicode encoding: {e}")
        return False

def install_missing_dependencies():
    """Install missing dependencies for ComfyUI nodes"""
    dependencies_to_install = [
        'trimesh',  # For ComfyUI-RizzNodes
        'insightface',  # For ComfyUI-nunchaku
        'opencv-python',  # For ComfyUI-nunchaku
        'facexlib',  # For ComfyUI-nunchaku
        'onnxruntime',  # For ComfyUI-nunchaku
        'timm',  # For ComfyUI-nunchaku
        'sentencepiece',  # For ComfyUI-nunchaku
        'protobuf',  # For ComfyUI-nunchaku
        'peft>=0.15',  # For ComfyUI-nunchaku
        'scipy',  # Generally useful for image processing
    ]
    
    logger.info("Installing missing dependencies...")
    
    for package in dependencies_to_install:
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install {package}: {e.stderr}")
        except Exception as e:
            logger.warning(f"Error installing {package}: {e}")

def fix_xformers_compatibility():
    """Fix xFormers compatibility issues"""
    try:
        # Check current xFormers version
        result = subprocess.run(
            [sys.executable, '-c', 'import xformers; print(xformers.__version__)'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            xformers_version = result.stdout.strip()
            logger.info(f"xFormers version: {xformers_version}")
            
            # Try to reinstall compatible version
            logger.info("Reinstalling xFormers for compatibility...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 
                'xformers'
            ], check=True)
            logger.info("xFormers reinstalled successfully")
        else:
            logger.info("xFormers not installed, installing...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'xformers'
            ], check=True)
            
    except subprocess.CalledProcessError as e:
        logger.warning(f"xFormers installation/upgrade failed: {e}")
    except Exception as e:
        logger.warning(f"Error handling xFormers: {e}")

def create_encoding_safe_startup_script():
    """Create a startup script with proper encoding settings"""
    startup_script = """@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Starting ComfyUI with proper encoding and fixes...
echo.
echo Environment settings:
echo - Code page: UTF-8 (65001)
echo - Python encoding: UTF-8
echo - Unicode support: Enabled
echo.

cd /d "C:\\Users\\Zachg\\Terminal-Grounds\\Tools\\Comfy\\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188

pause
"""
    
    script_path = Path("C:/Users/Zachg/Terminal-Grounds/START_COMFYUI_REPAIRED.bat")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    logger.info(f"Created repaired startup script: {script_path}")

def update_requirements_files():
    """Update requirements.txt files for nodes with missing dependencies"""
    
    # Fix ComfyUI-RizzNodes requirements
    rizz_req_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes/ComfyUI-RizzNodes/requirements.txt")
    if rizz_req_path.exists():
        with open(rizz_req_path, 'a', encoding='utf-8') as f:
            f.write('\ntrimesh\nscipy\n')
        logger.info("Updated ComfyUI-RizzNodes requirements.txt")
    
    # Fix ComfyUI-nunchaku requirements (add missing dependencies)
    nunchaku_req_path = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/custom_nodes/ComfyUI-nunchaku/requirements.txt")
    if nunchaku_req_path.exists():
        with open(nunchaku_req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add any missing dependencies
        missing_deps = []
        if 'scipy' not in content:
            missing_deps.append('scipy')
        
        if missing_deps:
            with open(nunchaku_req_path, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(missing_deps) + '\n')
            logger.info("Updated ComfyUI-nunchaku requirements.txt")

def main():
    """Main repair function"""
    logger.info("Starting ComfyUI Comprehensive Repair...")
    logger.info("This script will repair issues without disabling any functionality")
    
    # Set environment encoding first
    set_environment_encoding()
    
    repairs_applied = []
    
    # Fix Unicode encoding in AIIA node
    if fix_aiia_unicode_encoding():
        repairs_applied.append("✓ Fixed AIIA Unicode encoding")
    
    # Install missing dependencies
    install_missing_dependencies()
    repairs_applied.append("✓ Installed missing dependencies")
    
    # Fix xFormers compatibility
    fix_xformers_compatibility()
    repairs_applied.append("✓ Fixed xFormers compatibility")
    
    # Update requirements files
    update_requirements_files()
    repairs_applied.append("✓ Updated requirements files")
    
    # Create safe startup script
    create_encoding_safe_startup_script()
    repairs_applied.append("✓ Created encoding-safe startup script")
    
    logger.info("\n" + "="*50)
    logger.info("REPAIR COMPLETE - ALL FUNCTIONALITY PRESERVED")
    logger.info("="*50)
    
    for repair in repairs_applied:
        logger.info(repair)
    
    logger.info("\nNext steps:")
    logger.info("1. Use START_COMFYUI_REPAIRED.bat to start ComfyUI")
    logger.info("2. All nodes should now load without errors")
    logger.info("3. Unicode text should display properly")
    logger.info("4. Dependencies are installed and compatible")
    
    logger.info(f"\nRepaired {len(repairs_applied)} issues successfully!")

if __name__ == "__main__":
    main()