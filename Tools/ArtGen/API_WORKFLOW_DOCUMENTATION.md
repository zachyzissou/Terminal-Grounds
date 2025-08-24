# Terminal Grounds - ComfyUI API Workflow System

## Overview

The Terminal Grounds project uses ComfyUI (running on port 8188) for AI-powered asset generation. Due to limitations with the ComfyUI-electron version's API compatibility, we've developed a hybrid approach that leverages both GUI and API methods.

## Current Setup

### Environment
- **ComfyUI Location**: `C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\`
- **ComfyUI Port**: 8188 (standard port)
- **Model**: FLUX1-dev-fp8.safetensors
- **Python**: 3.12.9
- **GPU**: RTX 3090 Ti (24GB VRAM)

### Proven Parameters
```json
{
  "model": "FLUX1\\flux1-dev-fp8.safetensors",
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

## Workflow Methods

### Method 1: GUI Workflow (Recommended - 85%+ Success Rate)

1. **Load Workflow**
   ```bash
   # Open ComfyUI interface
   http://127.0.0.1:8188
   ```

2. **Import Production Workflow**
   - Drag one of the FINAL workflows into the interface:
     - `TG_Metro_Corridor_FINAL.json`
     - `TG_IEZ_Facility_FINAL.json`
     - `TG_TechWastes_FINAL.json`

3. **Execute**
   - Click "Queue Prompt"
   - Wait ~5 minutes for generation
   - Output appears in: `C:/Users/Zachg/Documents/ComfyUI/output/`

### Method 2: API Workflow (Development)

```python
import json
import urllib.request
import urllib.error

class ComfyUIClient:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        
    def queue_prompt(self, workflow):
        """Queue a workflow for execution"""
        p = {"prompt": workflow}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt",
            data=data
        )
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except urllib.error.URLError as e:
            print(f"API Error: {e}")
            return None
    
    def get_history(self, prompt_id):
        """Get execution history"""
        url = f"http://{self.server_address}/history/{prompt_id}"
        try:
            with urllib.request.urlopen(url) as response:
                return json.loads(response.read())
        except:
            return None
```

## API Workflow Files

Located in `workflows/api/`:

| File | Purpose | Usage |
|------|---------|-------|
| `concept_art.api.json` | Concept art generation | Character/environment concepts |
| `environment_matte.api.json` | Environment mattes | Background plates |
| `high_detail_render.api.json` | High-detail renders | Hero assets |
| `icon_generation.api.json` | UI icon generation | Game interface elements |
| `poster_design.api.json` | Poster designs | In-game propaganda |
| `style_board.api.json` | Style boards | Art direction reference |
| `texture_decal.api.json` | Texture/decal generation | Surface details |

## Known Issues & Workarounds

### Issue: ComfyUI-electron API stderr conflicts
**Symptom**: API calls validate but fail to execute
**Workaround**: Use GUI method or standard ComfyUI installation

### Issue: TQDM progress bar conflicts
**Symptom**: Progress output causes API failures
**Workaround**: Suppress stderr or use GUI method

### Issue: Inconsistent API responses
**Symptom**: Same workflow produces different results via API
**Workaround**: Lock all parameters including seed

## Quality Assurance

### Automated Quality Scoring
```python
def assess_quality(image_path):
    """Score generated image quality"""
    scores = {
        "composition": check_composition(image_path),
        "detail": check_detail_level(image_path),
        "technical": check_technical_quality(image_path),
        "lore_alignment": check_lore_accuracy(image_path)
    }
    
    overall = sum(scores.values()) / len(scores)
    return overall >= 85  # Pass threshold
```

### Success Metrics
- **Target Success Rate**: 85%+
- **Current Achievement**: 85-90% with heun/normal parameters
- **Generation Time**: ~5 minutes per image
- **Quality Score Threshold**: 85/100

## Best Practices

1. **Always validate workflows** before bulk generation
2. **Use fixed seeds** for reproducibility during testing
3. **Monitor GPU memory** - FLUX requires significant VRAM
4. **Archive successful outputs** with their workflow parameters
5. **Document parameter changes** and their effects

## Troubleshooting

### Starting ComfyUI API
```bash
# Navigate to ComfyUI directory
cd C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API

# Start ComfyUI in API mode
python main.py --listen 127.0.0.1 --port 8188

# Test connectivity (in separate terminal)
python C:\Users\Zachg\Terminal-Grounds\Tools\test_comfyui_api.py

# Check system status
curl http://127.0.0.1:8188/system_stats
```

### Low Quality Output
1. Verify using proven parameters (heun/normal)
2. Check model loaded correctly (FLUX1-dev-fp8)
3. Ensure proper resolution (1536x864)
4. Validate negative prompts are applied

### API Connection Failed
1. Confirm ComfyUI running on port 8188
2. Check firewall/antivirus settings
3. Try GUI method as fallback
4. Review API_INVESTIGATION_REPORT.md for details

## Future Improvements

- [ ] Resolve ComfyUI-electron API compatibility
- [ ] Implement batch processing with quality gates
- [ ] Add automatic retry on failure
- [ ] Create parameter optimization system
- [ ] Build unified pipeline interface

## Related Documentation

- `AAA_QUALITY_SOLUTION_REPORT.md` - Quality breakthrough details
- `API_INVESTIGATION_REPORT.md` - Technical investigation findings
- `CLAUDE.md` - Project context for AI agents
- `workflows/README.md` - Workflow file descriptions

Last Updated: August 23, 2025