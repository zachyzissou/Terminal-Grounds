# Terminal Grounds - Troubleshooting Guide

## ComfyUI Won't Start

**Symptom**: Import errors or crashes during startup
**Solution**:

```bash
# Check if port is occupied
netstat -ano | findstr :8188

# Kill existing process if needed
taskkill /PID <process_id> /F

# Restart ComfyUI
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
python main.py --listen 127.0.0.1 --port 8188
```

## API Not Responding

**Symptom**: Tools/test_comfyui_api.py shows timeout
**Solution**: Wait longer - ComfyUI takes 90+ seconds to fully load all nodes

## Generation Fails

**Symptom**: API accepts workflow but no output generated
**Check**:

1. FLUX1-dev-fp8.safetensors model is loaded
2. Use proven parameters: heun sampler, normal scheduler, CFG 3.2
3. Check `C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/` for results

## GPU Issues

**Expected**: RTX 3090 Ti with 24GB VRAM
**Check**: System stats should show CUDA device available

## Asset Generation Problems

### Text Corruption in Generated Assets
- **Cause**: FLUX model conflicts with text prompts
- **Solution**: Use `Tools/ArtGen/FIXED_faction_vehicle_concepts.py` for vehicles
- **Prevention**: Eliminate text references from prompts entirely

### Copyright Violations in UI Assets
- **Cause**: Generic "game HUD" prompts trigger copyrighted training data
- **Solution**: Use `Tools/ArtGen/FIXED_faction_ui_hud_concepts.py` with comprehensive blocking
- **Prevention**: Avoid generic gaming terminology in prompts

### Low Success Rates
- **Cause**: Incorrect sampler parameters or problematic prompts
- **Solution**: Use proven parameters (heun/normal/CFG 3.2/25 steps)
- **Validation**: Check `Tools/ArtGen/terminal_grounds_generator.py` for reference implementation

## WebSocket Connection Issues

**Symptom**: Server crashes with >100 concurrent connections
**Solution**: Use `Tools/TerritorialSystem/territorial_websocket_server.py` with max_connections parameter

## Directory Issues

**Wrong Output Directory Error**:
- **Problem**: Looking in `C:/Users/Zachg/Documents/ComfyUI/output/` (old location)
- **Solution**: Always use `C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/`
- **Prevention**: Update all scripts to use correct output path

## Windows Environment Issues

**Unicode Character Errors**:
- **Symptom**: 'charmap' codec errors in console output
- **Solution**: Use ASCII alternatives (-> instead of →, OK instead of ✓)
- **Prevention**: Add `# -*- coding: utf-8 -*-` header to all Python scripts

## Agent Discovery Issues

**Missing Pipeline v2.0**:
- **Problem**: Agents not finding primary asset generation system
- **Solution**: Always check `Tools/ArtGen/pipeline/` directory first
- **Prevention**: Follow AGENT DISCOVERY CHECKLIST before any work

## Quality Assessment Problems

**Low Lore Alignment Scores**:
- **Cause**: Generated assets don't match Terminal Grounds aesthetic
- **Solution**: Update prompts with faction-specific details from `Docs/Lore/LORE_BIBLE.md`
- **Prevention**: Run mandatory Lore QA pass after any lore changes

## Common Resolution Steps

1. **Restart Services**: ComfyUI, WebSocket server, Unreal Engine
2. **Clear Caches**: Delete temporary files in output directories
3. **Validate Paths**: Ensure all file paths use forward slashes
4. **Check Permissions**: Verify write access to output directories
5. **Update Dependencies**: Ensure all Python packages are current

## Emergency Contacts

- **Technical Issues**: Refer to `Tools/ArtGen/API_INVESTIGATION_REPORT.md`
- **Broken Scripts**: Check `Tools/ArtGen/04_BROKEN_SCRIPTS/README_BROKEN_SCRIPTS.md`
- **System Architecture**: See `Docs/Technical/SPECIFICATIONS.md`

Last Updated: September 6, 2025