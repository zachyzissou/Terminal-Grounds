#!/usr/bin/env python3
"""
Final attempt to fix the generation issue
Try different environment settings and approaches
"""
import os
import json
import urllib.request
import subprocess
import time

def check_comfyui_environment():
    """Check ComfyUI environment and suggest fixes"""
    print("=== ComfyUI Environment Check ===")
    
    # Check if ComfyUI is running
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/system_stats", timeout=5) as resp:
            stats = json.loads(resp.read())
            print(f"✓ ComfyUI running - System: {stats.get('system', {})}")
    except:
        print("✗ ComfyUI not responding")
        return False
    
    # Check Python environment
    print(f"Python path: {subprocess.check_output(['where', 'python'], shell=True).decode().strip()}")
    
    # Check environment variables that might affect tqdm
    env_vars = ['PYTHONIOENCODING', 'TERM', 'PYTHONUNBUFFERED', 'TQDM_DISABLE']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    return True

def create_batch_restart_script():
    """Create a comprehensive restart script"""
    script_content = '''@echo off
title ComfyUI Restart with Environment Fix
echo ================================================
echo  FIXING COMFYUI TQDM ERROR
echo  Terminal Grounds Asset Generation
echo ================================================
echo.

echo Step 1: Killing existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im python3.exe >nul 2>&1

echo Step 2: Waiting for cleanup...
timeout /t 5 >nul

echo Step 3: Setting environment variables...
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
set TQDM_DISABLE=0
set TERM=

echo Step 4: Starting ComfyUI with fixes...
cd /d "C:\\Users\\Zachg\\Documents\\ComfyUI"

echo Starting ComfyUI (will open in new window)...
start "ComfyUI-Fixed" cmd /k "python main.py --listen 127.0.0.1 --port 8000 --disable-auto-launch"

echo.
echo ================================================
echo ComfyUI is starting with environment fixes
echo Wait 30 seconds then test generation
echo ================================================
echo.
echo Press any key when ComfyUI is ready...
pause >nul

echo Testing connection...
curl -s http://127.0.0.1:8000/system_stats >nul
if %errorlevel%==0 (
    echo ✓ ComfyUI is responding
) else (
    echo ✗ ComfyUI not responding yet
)

echo.
echo Ready to test generation!
pause
'''
    
    with open("C:\\Users\\Zachg\\Terminal-Grounds\\FIX_COMFYUI.bat", "w") as f:
        f.write(script_content)
    
    print("Created comprehensive restart script: FIX_COMFYUI.bat")

def test_minimal_generation():
    """One final minimal test"""
    # Absolutely minimal workflow
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "FLUX1\\flux1-dev-fp8.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "test", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "KSamplerAdvanced", "inputs": {"add_noise": "enable", "noise_seed": 1, "steps": 1, "cfg": 1, "sampler_name": "ddim", "scheduler": "normal", "start_at_step": 0, "end_at_step": 1, "return_with_leftover_noise": "disable", "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "test"}}
    }
    
    print("\n=== Final Minimal Test ===")
    try:
        data = json.dumps({"prompt": workflow}).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:8000/prompt", data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            prompt_id = result.get('prompt_id')
            print(f"Queued: {prompt_id}")
            
        # Quick check
        time.sleep(3)
        url = f"http://127.0.0.1:8000/history/{prompt_id}"
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            
        if prompt_id in data:
            status = data[prompt_id].get("status", {}).get("status_str", "unknown")
            if status == "success":
                print("SUCCESS! The issue is resolved!")
                return True
            else:
                print(f"Failed with status: {status}")
                
    except Exception as e:
        print(f"Test failed: {e}")
        
    return False

def main():
    print("=== ComfyUI Generation Issue Diagnostic & Fix ===")
    
    if not check_comfyui_environment():
        return
    
    # Try one more minimal test
    if test_minimal_generation():
        print("\n🎉 SUCCESS! Generation is working!")
        return
    
    # Create comprehensive fix
    create_batch_restart_script()
    
    print("""
=== SOLUTION ===
The issue is a Windows environment problem with tqdm progress bars.

Next steps:
1. Run: FIX_COMFYUI.bat (in project root)
2. Wait for ComfyUI to start with environment fixes
3. Test generation with: python working_flux_generator.py

This should resolve the '[Errno 22] Invalid argument' error.
""")

if __name__ == "__main__":
    main()