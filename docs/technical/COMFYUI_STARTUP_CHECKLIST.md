# ComfyUI Startup Checklist - Terminal Grounds

## Pre-Flight Check ✈️

Before starting ComfyUI, verify:
- [ ] No other ComfyUI processes running
- [ ] Port 8188 is available
- [ ] CUDA/GPU drivers are working

```bash
# Check if port 8188 is free
netstat -ano | findstr :8188
# Should return nothing if port is free

# Check GPU status  
nvidia-smi
# Should show RTX 3090 Ti
```

## Step 1: Start ComfyUI API 🚀

```bash
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

### Expected Startup Sequence:
1. **[0-10s]** Security scan, ComfyUI-Manager init
2. **[10-30s]** Platform detection, Python/PyTorch checks  
3. **[30-90s]** Loading 70+ custom nodes (lots of output)
4. **[90s+]** "Starting server" - ComfyUI is ready!

### Red Flags During Startup:
- ❌ Python version errors (need 3.12.9)
- ❌ CUDA not detected 
- ❌ Model files not found
- ❌ Port already in use

## Step 2: Verify API Ready ✅

**Open NEW terminal** and run:
```bash
python "C:\Users\Zachg\Terminal-Grounds\Tools\test_comfyui_api.py"
```

### Expected Output:
```
OK: ComfyUI reachable at http://127.0.0.1:8188
```

### If Failed:
- Wait longer (ComfyUI may still be loading)
- Check original terminal for error messages
- Verify port 8188 is listening: `netstat -ano | findstr :8188`

## Step 3: System Health Check 🏥

```bash
curl http://127.0.0.1:8188/system_stats
```

### Expected Response:
```json
{
  "system": {
    "comfyui_version": "0.3.50",
    "python_version": "3.12.9",
    "pytorch_version": "2.6.0+cu124"
  },
  "devices": [{
    "name": "cuda:0 NVIDIA GeForce RTX 3090 Ti",
    "vram_total": 25756696576,
    "vram_free": 24000000000
  }]
}
```

## Step 4: Test Asset Generation 🎨

### Quick Test - Single Emblem:
```bash
python "C:\Users\Zachg\Terminal-Grounds\Tools\ArtGen\working_flux_generator.py"
```

### Full Test - Batch Generation:
```bash
python "C:\Users\Zachg\Terminal-Grounds\Tools\ArtGen\comfyui_api_client.py" --type emblems
```

### Expected Results:
- Generation time: ~5 minutes per image
- Output location: `C:/Users/Zachg/Documents/ComfyUI/output/`
- Quality: Sharp, detailed images with no text artifacts

## Success Criteria ✨

**ComfyUI is fully ready when:**
- [x] API responds to system_stats
- [x] Test script reports "OK"
- [x] GPU shows in system stats with >20GB VRAM free
- [x] Sample generation completes successfully
- [x] Output files appear in expected location

## Emergency Restart 🆘

If anything goes wrong:
```bash
# Kill all ComfyUI processes
taskkill /f /im python.exe

# Wait 10 seconds
timeout 10

# Restart from Step 1
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

## Reference Files 📚

- `CLAUDE.md` - Complete project documentation
- `Tools/COMFYUI_STARTUP_GUIDE.md` - Detailed startup guide
- `Tools/ArtGen/API_WORKFLOW_DOCUMENTATION.md` - API specifics
- `Tools/test_comfyui_api.py` - Connection testing script

---
**This checklist ensures ComfyUI starts correctly every time without troubleshooting!**