# Terminal Grounds Asset Generation Pipeline
## Current Production System + v2.0 Roadmap

⚠️ **STATUS**: This document describes both the **current working pipeline** and the **planned v2.0 system**. 

📍 **For production today, use the "Current Pipeline" section below.**

---

## 🚀 Current Pipeline (Ready Now)

### Configuration (ComfyUI Already Running)
```bash
# ComfyUI auto-detection (your scripts probe 8000 then 8188)
# Or set specific server: set COMFYUI_SERVER=127.0.0.1:8188

# Set default model environment variable  
set TG_CKPT=FLUX1\flux1-dev-fp8.safetensors

# Check current config
python -c "import json; print(json.load(open('artgen_config.json')))"
```

### Current Working Tools

#### 1. High-Quality Batch Generation
```bash
cd Tools/ArtGen

# Generate with HQ pipeline (primary production tool)
python pipeline_hq_batch.py --prompt "directorate plasma rifle, corporate military design" --negative "blurry, low quality" --dump-workflow --dump-history

# Batch run from planning file
python artgen_run_batch.py --plan outputs/batch_2025-08-12A.plan.json
```

#### 2. Concept Art Generation  
```bash
# Atmospheric environments
python atmospheric_concept_workflow.py --style "industrial cyberpunk" --faction directorate

# Working FLUX generator
python working_flux_generator.py --prompt "terminal grounds corridor concept"
```

#### 3. Enhancement & Post-Processing
```bash
# Refine and sharpen existing images
python refine_sharpen_pass.py --input "Style_Staging/_Recent_Generations/image.png" --refine-steps 20 --refine-denoise 0.35

# Upscale with your 4x-UltraSharp model
python upscale_image_once.py --input "path/to/image.png" --model "4x-UltraSharp.pth"
```

#### 4. Testing & Validation
```bash
# Quick generation test
python quick_test_generation.py

# Style baseline exploration  
python style_baseline_explorer.py --faction directorate --iterations 5
```

### Import to UE5 (Current Method)
```bash
# Use VS Code task or run directly
# Task: "UE5.6: Import ArtGen Outputs"
python ue_import/tools_import_artgen_outputs.py C:\Path\to\Generations
```

### View Generated Assets
- **Output Location**: `Style_Staging/_Recent_Generations/`
- **Browse**: Open `Style_Staging/_Recent_Generations/index.html`
- **Metadata**: Each image has accompanying `.json` sidecar files

### Current Workflow Files
- **Templates**: `Tools/ArtGen/workflows/*.api.json` (template workflows for client scripts)
- **Config**: `artgen_config.json` (server settings and model paths)
- **Output**: `Style_Staging/_Recent_Generations/` with `index.html` browser
- **Models**: FLUX via environment variable `TG_CKPT=FLUX1\flux1-dev-fp8.safetensors`

### Current Limitations (Addressed in v2.0)
- Multiple script entry points (no unified interface)
- Manual workflow selection
- Basic quality control (manual review)
- Manual UE5 import process
- No automated batch CSV processing

---

## 🚀 Planned v2.0 Architecture (Future)

> ⚠️ **Note**: The commands below are planned for v2.0 and don't exist yet. Use the "Current Pipeline" section above for production work.

### v2.0 Command Mapping (Planned)
| **Planned v2.0 Command** | **Current Equivalent** |
|--------------------------|-------------------------|
| `terminal_grounds_pipeline.py generate weapon "Rifle"` | `pipeline_hq_batch.py --prompt "rifle"` |
| `terminal_grounds_pipeline.py batch-csv weapons.csv` | Manual process with `artgen_run_batch.py` |
| `terminal_grounds_pipeline.py faction-assets directorate` | Multiple runs with faction prompts |
| `terminal_grounds_pipeline.py interactive` | **Not available** (planned feature) |
| `terminal_grounds_pipeline.py validate` | Manual ComfyUI server check |
| `terminal_grounds_pipeline.py enhance image.png` | `refine_sharpen_pass.py --input image.png` |

### v2.0 Vision
- **Unified Entry Point**: Single `terminal_grounds_pipeline.py` script
- **Smart Workflow Selection**: Automatically choose optimal ComfyUI workflows
- **Quality Gates**: Automated scoring and enhancement
- **CSV Batch Processing**: Direct import from your data tables
- **Seamless UE5 Integration**: One-command generation and import

---

## 🎯 Getting Started Today

### Quick Production Workflow
```bash
cd Tools/ArtGen

# 1. Test your setup
python quick_test_generation.py

# 2. Generate concept art
python pipeline_hq_batch.py --prompt "directorate weapon design, corporate military aesthetic" --negative "blurry, low quality" --dump-workflow

# 3. Enhance if needed
python refine_sharpen_pass.py --input "Style_Staging/_Recent_Generations/latest_image.png"

# 4. Import to UE5 via VS Code task: "UE5.6: Import ArtGen Outputs"
```

### Configuration Check
```bash
# Verify ComfyUI connection (uses auto-detection)
python -c "
import sys; sys.path.append('.')
from comfyui_api_client import _detect_server
import urllib.request
server = _detect_server()
print(f'ComfyUI detected at: {server}')
with urllib.request.urlopen(f'http://{server}/system_stats') as r:
    print(f'Status: {r.status}')
"

# Check your model setup  
echo %TG_CKPT%
```

---

## 📋 Current Asset Types

### Primary Assets
- **Weapons** - Firearms, melee, futuristic armaments
- **Vehicles** - Ground, air, space craft
- **Emblems** - Faction insignia and logos
- **Posters** - Propaganda and informational
- **Icons** - UI elements and symbols
- **Concepts** - Environment and character art

### Faction Integration
- **Directorate** (DIR) - Corporate military aesthetics
- **Free77** (F77) - Guerrilla resistance styling  
- **Vultures Union** (VLT) - Scavenger industrial look
- **Corporate Combine** - Clean corporate branding
- **Nomad Clans** - Tribal and mobile themes
- **Vaulted Archivists** - Academic and preservation
- **Civic Wardens** - Public safety and order

---

## 🎨 Workflow System

### Automatic Workflow Selection
The system intelligently chooses ComfyUI workflows based on asset type:

```python
weapon → high_detail_render_workflow.json     # Maximum detail for close-ups
vehicle → environment_integration.json        # Context-aware vehicle rendering
emblem → logo_design_workflow.json           # Vector-style clean emblems
poster → propaganda_design.json              # Cinematic poster layouts
icon → ui_element_workflow.json              # Clean, scalable icons
concept → artistic_concept.json              # Painterly concept art
```

### Quality Enhancement Pipeline
1. **Generation** - Primary ComfyUI workflow
2. **Quality Assessment** - Automated scoring (0-100)
3. **Enhancement** - Upscaling if quality < 85
4. **Validation** - Faction alignment check
5. **Post-Processing** - Final polish and metadata

---

## 📊 Quality Assurance System

### Automated Quality Scoring
- **Resolution Score** (0-30): Pixel density and sharpness
- **Detail Score** (0-30): Feature richness and complexity  
- **Composition Score** (0-25): Visual balance and framing
- **Faction Alignment** (0-15): Style consistency with faction

### Quality Gates
- **< 60**: Regeneration required
- **60-75**: Basic enhancement applied
- **75-85**: Standard upscaling
- **85+**: Production ready

### Enhancement Options
- **4x-UltraSharp.pth** - Your installed upscaler
- **Detail enhancement** - Fine detail restoration
- **Color correction** - Faction palette alignment
- **Metadata tagging** - Comprehensive asset information

---

## 🚀 Batch Processing

### CSV Import (Works with Your Data)
Your existing `Weapons.csv` and other data tables work directly:

```csv
Name,Faction,Type,Description
Plasma Rifle,Directorate,Energy,High-energy directed weapon
Scavenger Shotgun,Vultures,Ballistic,Makeshift close-combat weapon
```

### Batch Commands
```bash
# Process entire CSV with UE5 import
python terminal_grounds_pipeline.py batch-csv Data/Tables/Weapons.csv --import-ue5

# Generate faction-specific assets
python terminal_grounds_pipeline.py faction-assets directorate --count 20

# Bulk concept art generation
python terminal_grounds_pipeline.py bulk-concepts --themes industrial,cyberpunk --count 50
```

### Progress Tracking
- Real-time progress bars
- Estimated completion times
- Error handling with retry logic
- Comprehensive logging

---

## 🎮 UE5 Integration

### Automatic Import
```bash
# Generate and import to UE5 in one command
python terminal_grounds_pipeline.py generate weapon "Rail Gun" --faction directorate --import-ue5
```

### Asset Organization in UE5
```
/Game/Generated/
├── Weapons/
│   ├── Directorate/
│   │   ├── T_RailGun_Albedo
│   │   ├── T_RailGun_Normal  
│   │   └── MI_RailGun
│   └── Free77/
├── Vehicles/
└── Concepts/
```

### Material Instance Creation
- Automatic material instance setup
- Faction-specific material parameters
- Proper texture assignments
- Metadata preservation

---

## 🔧 Configuration

### pipeline_config.json
```json
{
  "comfyui": {
    "server": "127.0.0.1:8000",
    "timeout": 300,
    "max_concurrent": 2
  },
  "quality": {
    "min_score": 60,
    "target_score": 85,
    "enhancement_threshold": 75
  },
  "paths": {
    "output_base": "Docs/Generated",
    "ue5_content": "Content/TG",
    "staging": "Style_Staging"
  },
  "factions": {
    "enabled": ["directorate", "free77", "vultures", "combine", "nomads", "archivists", "wardens"]
  }
}
```

---

## 📈 Performance Optimization

### RTX 3090 Ti Settings
- **Concurrent Jobs**: 2 (optimal for 24GB VRAM)
- **Batch Size**: 4 assets per batch
- **Memory Management**: Automatic cleanup
- **Model Caching**: Intelligent preloading

### Speed Improvements
- **Workflow Caching**: Reuse compiled workflows
- **Asset Pooling**: Batch similar requests
- **Progressive Enhancement**: Generate fast, enhance later
- **Priority Queues**: Critical assets first

---

## 🛠️ Advanced Features

### Custom Workflows
Add your own ComfyUI workflows:
```bash
python terminal_grounds_pipeline.py add-workflow custom_render.json --type weapon
```

### Asset Search & Discovery
```bash
# Find all Directorate weapons
python terminal_grounds_pipeline.py search --faction directorate --type weapon

# Quality-based search
python terminal_grounds_pipeline.py search --min-quality 90

# Date range search
python terminal_grounds_pipeline.py search --after 2025-08-01
```

### Version Control
```bash
# List asset versions
python terminal_grounds_pipeline.py versions "Plasma Rifle"

# Restore previous version
python terminal_grounds_pipeline.py restore "Plasma Rifle" --version 2
```

---

## 🔍 CLI Command Reference

### Generation Commands
```bash
generate <type> <name> [--faction] [--style] [--import-ue5]
batch-csv <file> [--type] [--import-ue5] 
faction-assets <faction> [--types] [--count]
bulk-concepts [--themes] [--count]
```

### Management Commands
```bash
validate                    # Check pipeline health
search [--filters]          # Find existing assets
versions <name>             # List asset versions
restore <name> --version N  # Restore previous version
cleanup [--dry-run]         # Remove temporary files
```

### Configuration Commands
```bash
config-set <key> <value>    # Update configuration
config-get <key>            # View configuration
add-workflow <file>         # Add custom workflow
list-workflows              # Show available workflows
```

---

## 🚨 Migration from V1

### Gradual Migration
1. **Keep existing scripts** - They continue to work
2. **Test new pipeline** - Use `--dry-run` flag
3. **Compare outputs** - Validate quality improvements
4. **Migrate workflows** - Move custom workflows to new system
5. **Update automation** - Replace batch scripts with new commands

### Compatibility Mode
```bash
# Run in V1 compatibility mode
python terminal_grounds_pipeline.py --v1-compat generate weapon "Test Gun"
```

---

## 📚 Examples & Tutorials

### Example 1: Generate Faction Weapon Pack
```bash
# Generate 10 Directorate weapons with automatic UE5 import
python terminal_grounds_pipeline.py faction-assets directorate \
  --types weapon \
  --count 10 \
  --quality-threshold 85 \
  --import-ue5 \
  --styles "corporate,military,high-tech"
```

### Example 2: Batch Process Equipment CSV
```bash
# Process your equipment database
python terminal_grounds_pipeline.py batch-csv Data/Tables/Equipment.csv \
  --type misc \
  --enhance-all \
  --import-ue5 \
  --parallel 2
```

### Example 3: Generate Environment Concepts
```bash
# Create industrial environment concepts
python terminal_grounds_pipeline.py bulk-concepts \
  --themes "industrial,cyberpunk,abandoned" \
  --faction-styles "directorate,vultures" \
  --count 25 \
  --resolution 2048x1152
```

---

## 🔧 Troubleshooting

### Common Issues
- **ComfyUI not responding**: Check server status with `validate`
- **Low quality outputs**: Adjust quality thresholds in config
- **UE5 import fails**: Verify UE5 Python API setup
- **Memory errors**: Reduce concurrent job count

### Debug Mode
```bash
python terminal_grounds_pipeline.py --debug generate weapon "Test"
```

### Log Analysis
```bash
# View recent logs
python terminal_grounds_pipeline.py logs --recent

# Search logs for errors
python terminal_grounds_pipeline.py logs --level error --since yesterday
```

---

## 🚀 What's Next

### Planned Features
- **Style Transfer**: Apply existing art styles to new assets
- **Collaborative Workflows**: Multi-user asset generation
- **Cloud Integration**: Distributed processing capabilities
- **ML Training**: Custom model training for Terminal Grounds
- **Version Control**: Git-like versioning for assets

### Getting Started Today
1. Run `python terminal_grounds_pipeline.py validate` to check setup
2. Try `python terminal_grounds_pipeline.py interactive` for guided experience
3. Process your first CSV: `python terminal_grounds_pipeline.py batch-csv Data/Tables/Weapons.csv`
4. Generate faction assets: `python terminal_grounds_pipeline.py faction-assets directorate`

---

**🎯 Result**: A professional, AAA-quality asset generation pipeline that transforms your scattered scripts into a unified, intelligent system that scales with Terminal Grounds from prototype to production.**