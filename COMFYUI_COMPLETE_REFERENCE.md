# ComfyUI Complete Reference - Terminal Grounds

## 🚀 Quick Start (Copy-Paste Commands)

### Start ComfyUI (Terminal 1)
```bash
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```
*Wait for "Starting server" message (~90 seconds)*

### Test Connection (Terminal 2)
```bash
python "C:\Users\Zachg\Terminal-Grounds\Tools\test_comfyui_api.py"
```
*Expected: "OK: ComfyUI reachable at http://127.0.0.1:8188"*

### Generate Asset
```bash
python "C:\Users\Zachg\Terminal-Grounds\Tools\ArtGen\working_flux_generator.py"
```

## 📊 System Specifications (Verified Working)

| Component | Specification |
|-----------|---------------|
| **ComfyUI Version** | 0.3.50 |
| **Python** | 3.12.9 |
| **PyTorch** | 2.6.0+cu124 |
| **GPU** | RTX 3090 Ti (24GB VRAM) |
| **RAM** | 32GB total |
| **Model** | FLUX1-dev-fp8.safetensors |
| **Port** | 8188 (standard) |

## ⚙️ Proven Generation Parameters

```json
{
  "model": "FLUX1/flux1-dev-fp8.safetensors",
  "sampler": "heun",
  "scheduler": "normal",
  "cfg": 3.2,
  "steps": 25,
  "width": 1536,
  "height": 864,
  "denoise": 1.0,
  "seed": 94887
}
```
**Success Rate**: 85%+ | **Generation Time**: ~5 minutes

## 📁 Key File Locations

### ComfyUI Installation
- **Main Directory**: `C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\`
- **Startup Script**: `main.py`
- **Models**: Linked to `C:\Users\Zachg\Documents\ComfyUI\models\`

### Workflows (Production Ready)
- **Metro Corridor**: `Tools/ArtGen/workflows/TG_Metro_Corridor_FINAL.json`
- **IEZ Facility**: `Tools/ArtGen/workflows/TG_IEZ_Facility_FINAL.json`
- **Tech Wastes**: `Tools/ArtGen/workflows/TG_TechWastes_FINAL.json`

### Python Scripts (Proven Working)
- **API Client**: `Tools/ArtGen/comfyui_api_client.py`
- **Working Generator**: `Tools/ArtGen/working_flux_generator.py`
- **API Test**: `Tools/test_comfyui_api.py`

### Output Location
- **Generated Images**: `C:/Users/Zachg/Documents/ComfyUI/output/`

## 🛠️ Troubleshooting Scenarios

### Scenario 1: ComfyUI Won't Start
**Symptoms**: Import errors, crashes, port conflicts
```bash
# Check port availability
netstat -ano | findstr :8188

# Kill existing processes
taskkill /f /im python.exe

# Restart
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

### Scenario 2: API Test Fails
**Symptoms**: Connection timeout, "NOT RUNNING" message
- **Wait longer**: ComfyUI startup takes 90+ seconds
- **Check terminal**: Look for error messages in startup log
- **Verify models**: Ensure FLUX1-dev-fp8.safetensors is loaded

### Scenario 3: Generation Produces No Output
**Symptoms**: API accepts request but no files generated
1. Check output directory: `C:/Users/Zachg/Documents/ComfyUI/output/`
2. Verify model loaded: Check startup log for FLUX model
3. Use proven parameters: heun/normal/CFG 3.2
4. Check GPU memory: Should have 20GB+ free

### Scenario 4: Low Quality Images
**Solutions**:
- Use production workflows (TG_*_FINAL.json files)
- Verify heun sampler + normal scheduler
- Check CFG value is 3.2
- Ensure resolution is 1536x864

## 📋 Startup Checklist

- [ ] Port 8188 free (`netstat -ano | findstr :8188`)
- [ ] GPU working (`nvidia-smi`)
- [ ] ComfyUI started (`python main.py --listen 127.0.0.1 --port 8188`)
- [ ] "Starting server" message appeared
- [ ] API test passes (`python Tools/test_comfyui_api.py`)
- [ ] System stats respond (`curl http://127.0.0.1:8188/system_stats`)
- [ ] Ready to generate assets!

## 🔧 Common Commands

### Status Check
```bash
curl http://127.0.0.1:8188/system_stats | python -m json.tool
```

### Process Management
```bash
# Find ComfyUI processes
tasklist | findstr python

# Kill all Python processes (emergency)
taskkill /f /im python.exe
```

### Asset Generation
```bash
# Single emblem test
python "C:\Users\Zachg\Terminal-Grounds\Tools\ArtGen\working_flux_generator.py"

# Batch generation
python "C:\Users\Zachg\Terminal-Grounds\Tools\ArtGen\comfyui_api_client.py" --type emblems
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Main project context for AI agents |
| `COMFYUI_STARTUP_CHECKLIST.md` | Step-by-step startup guide |
| `Tools/COMFYUI_STARTUP_GUIDE.md` | Detailed technical guide |
| `Tools/ArtGen/API_WORKFLOW_DOCUMENTATION.md` | API-specific documentation |
| `Tools/ArtGen/AAA_QUALITY_SOLUTION_REPORT.md` | Quality breakthrough details |

## ✅ Success Indicators

**ComfyUI is fully ready when you see:**
1. ✅ "Starting server" in terminal
2. ✅ "OK: ComfyUI reachable" from test script
3. ✅ JSON response from system_stats endpoint
4. ✅ RTX 3090 Ti visible in device list
5. ✅ FLUX1-dev-fp8 model loaded successfully

## 🆘 Emergency Reset

If everything breaks:
```bash
# Nuclear option - kill all Python processes
taskkill /f /im python.exe

# Wait for cleanup
timeout 10

# Start fresh
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

---
**This reference covers everything needed to run ComfyUI successfully without troubleshooting.**