# ComfyUI API Startup Guide - Terminal Grounds

## Quick Start

### 1. Start ComfyUI API
```bash
cd C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API
python main.py --listen 127.0.0.1 --port 8188
```

### 2. Test Connection
```bash
# In a separate terminal:
python C:\Users\Zachg\Terminal-Grounds\Tools\test_comfyui_api.py
```

### 3. Verify System Status
```bash
curl http://127.0.0.1:8188/system_stats
```

## Expected Startup Process

### Phase 1: Initial Loading (0-30 seconds)
- Security scan
- ComfyUI-Manager initialization
- Platform detection
- Python/PyTorch version check

### Phase 2: Node Loading (30-90 seconds)
- Custom nodes import (70+ nodes)
- Model cache initialization
- Extension loading
- Dependency verification

### Phase 3: Server Ready (90+ seconds)
- Look for: `"Starting server"`
- Server accessible at: `http://127.0.0.1:8188`
- System stats endpoint available

## Troubleshooting

### Startup Takes Long Time
**Normal**: ComfyUI loads 70+ custom nodes and caches models
**Wait**: 90+ seconds for full startup
**Sign of completion**: "Starting server" message

### Import Errors During Startup
**Normal**: Some optional nodes may fail to import
**Impact**: Most features still work
**Action**: Only investigate if core functionality fails

### Port Already in Use
```bash
# Find process using port 8188
netstat -ano | findstr :8188

# Kill process if needed (replace PID)
taskkill /PID <process_id> /F
```

### API Not Responding After Startup
```bash
# Check if server actually started
curl http://127.0.0.1:8188/system_stats

# If no response, check terminal output for errors
# Look for "Starting server" message
```

## Production Usage

### Using Existing API Client
```bash
# Generate emblems
python Tools/ArtGen/comfyui_api_client.py --type emblems

# Generate all assets
python Tools/ArtGen/comfyui_api_client.py --all
```

### Direct API Workflow Submission
```python
import json
import urllib.request

# Load workflow
with open('Tools/ArtGen/workflows/TG_Metro_Corridor_FINAL.json', 'r') as f:
    workflow = json.load(f)

# Submit to API
data = json.dumps({"prompt": workflow}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
with urllib.request.urlopen(req) as response:
    result = json.loads(response.read())
    print(f"Queued: {result['prompt_id']}")
```

## System Requirements Verified

- **Python**: 3.12.9
- **PyTorch**: 2.6.0+cu124
- **GPU**: RTX 3090 Ti (24GB VRAM)
- **RAM**: 32GB total
- **Models**: FLUX1-dev-fp8.safetensors loaded correctly

## Related Files

- `Tools/test_comfyui_api.py` - Connection testing
- `Tools/ArtGen/comfyui_api_client.py` - Production client
- `Tools/ArtGen/API_WORKFLOW_DOCUMENTATION.md` - Full API docs
- `CLAUDE.md` - Updated with correct startup commands

Last Updated: August 23, 2025