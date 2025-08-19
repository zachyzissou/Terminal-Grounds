# Terminal Grounds Asset Pipeline - Current Status

## 📍 What's Available Right Now

### ✅ Production-Ready Tools
- **`pipeline_hq_batch.py`** - Primary asset generation with FLUX models
- **`atmospheric_concept_workflow.py`** - Environment concept generation  
- **`refine_sharpen_pass.py`** - Post-processing and enhancement
- **`upscale_image_once.py`** - 4x-UltraSharp upscaling
- **`artgen_run_batch.py`** - Batch processing from JSON plans
- **`quick_test_generation.py`** - Setup validation

### ✅ Working Configuration  
- **ComfyUI Auto-Detection**: Scripts probe ports 8000 then 8188
- **FLUX Models**: Set via `TG_CKPT=FLUX1\flux1-dev-fp8.safetensors`
- **Config File**: `artgen_config.json` (not pipeline_config.json)
- **Output**: `Style_Staging/_Recent_Generations/` with HTML browser

### ✅ Current Workflows
- **Templates**: `Tools/ArtGen/workflows/*.api.json` (client templates)
- **Models**: Your excellent FLUX + 200+ LoRA collection
- **Enhancement**: 4x-UltraSharp.pth upscaler working
- **UE5 Import**: Via VS Code task "UE5.6: Import ArtGen Outputs"

---

## 🚧 v2.0 Roadmap (Planned Features)

### Missing Components (Future)
- ❌ `terminal_grounds_pipeline.py` - Unified entry point  
- ❌ Quality scoring/gates automation
- ❌ CSV batch processing system
- ❌ Interactive mode interface
- ❌ Automated workflow selection
- ❌ Asset registry/search system

### Command Mapping (Planned → Current)
| **Future v2.0** | **Use Today** |
|------------------|---------------|
| `generate weapon "Rifle"` | `pipeline_hq_batch.py --prompt "rifle"` |
| `batch-csv weapons.csv` | Manual with `artgen_run_batch.py` |
| `validate` | Manual ComfyUI server check |
| `enhance image.png` | `refine_sharpen_pass.py --input image.png` |

---

## 🎯 Immediate Next Steps

### For Production Today
```bash
cd Tools/ArtGen

# 1. Test your setup  
python quick_test_generation.py

# 2. Generate assets
python pipeline_hq_batch.py --prompt "directorate weapon design" --dump-workflow

# 3. Enhance if needed
python refine_sharpen_pass.py --input "Style_Staging/_Recent_Generations/latest.png"
```

### For v2.0 Development
1. **Build unified entry point** (`terminal_grounds_pipeline.py`)
2. **Implement quality scoring** system  
3. **Create CSV batch processor**
4. **Add automated workflow selection**
5. **Build asset registry/search**

---

## 📋 Documentation Fixes Applied

### ✅ Corrected Issues
- **Status Banner**: Clear separation of current vs planned features
- **Port Configuration**: Uses existing auto-detection (8000/8188)
- **Model Paths**: Correct FLUX environment variable format
- **File Paths**: Match actual workflow templates and config files
- **Command Examples**: All use existing, working scripts
- **Server References**: Fixed ComfyUI connection patterns

### ✅ Realistic Expectations  
- Current tools section with working examples
- Clear "planned feature" warnings for v2.0 commands  
- Command mapping table (future → current equivalents)
- Accurate file locations and naming conventions

---

## 🚀 Bottom Line

**Current Status**: Excellent ComfyUI setup with professional-grade models and working automation scripts

**Next Phase**: Build the unified v2.0 pipeline on top of this solid foundation  

**Recommendation**: Use current tools for production, develop v2.0 incrementally without breaking existing workflow