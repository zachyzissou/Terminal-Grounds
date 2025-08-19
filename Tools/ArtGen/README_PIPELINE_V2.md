# Terminal Grounds Asset Generation Pipeline v2.0

A complete overhaul of the Terminal Grounds asset generation system, providing a professional, AAA-quality pipeline for creating game assets using ComfyUI and AI generation.

## 🚀 Key Features

### **Unified Control System**
- Single entry point for all asset generation
- Consistent interface across all operations
- Professional command-line and interactive modes

### **Smart Workflow Selection**
- Automatically chooses optimal ComfyUI workflows based on asset type
- Supports concept art, high-detail renders, icons, posters, and more
- Extensible workflow system

### **Faction-Aware Generation**
- Deep integration with Terminal Grounds' 7 factions
- Automatic prompt enhancement based on faction aesthetics
- LoRA-based style application

### **Quality Assurance**
- Automated quality validation and scoring
- Smart upscaling and enhancement
- Quality gate enforcement
- Image analysis and composition checking

### **Asset Management**
- Intelligent file organization and naming
- Comprehensive metadata tracking
- Version control and asset registry
- Search and discovery capabilities

### **Batch Processing**
- Efficient queue management with priority support
- CSV import (e.g., from Weapons.csv)
- Faction batch generation
- Progress tracking and retry logic

### **UE5 Integration**
- Seamless import into Unreal Engine 5
- Automatic material instance creation
- Metadata tagging and organization
- Both Python API and command-line support

## 📁 Architecture Overview

```
Tools/ArtGen/pipeline/
├── core/                      # Core pipeline components
│   ├── pipeline_controller.py # Master orchestrator
│   ├── asset_spec.py          # Asset specification system
│   ├── workflow_manager.py    # ComfyUI workflow management
│   ├── quality_assurance.py   # Quality validation & enhancement
│   ├── batch_processor.py     # Batch processing with queues
│   └── asset_manager.py       # File organization & metadata
├── comfyui/                   # ComfyUI integration
│   └── enhanced_client.py     # Robust ComfyUI client
├── integrations/              # External integrations
│   └── ue5_connector.py       # Unreal Engine 5 integration
├── utils/                     # Utilities
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging utilities
│   ├── validation.py          # Validation functions
│   ├── file_utils.py          # File operations
│   ├── image_analysis.py      # Image quality analysis
│   └── upscaling.py           # AI upscaling support
└── workflows/                 # ComfyUI workflow templates
    ├── concept_art.api.json
    ├── high_detail_render.api.json
    ├── icon_generation.api.json
    ├── poster_design.api.json
    ├── style_board.api.json
    ├── texture_decal.api.json
    └── environment_matte.api.json
```

## 🚀 Quick Start

### 1. Installation
```bash
# No additional dependencies required - uses existing ComfyUI setup
cd Tools/ArtGen
```

### 2. Configuration
Edit `config.json` to match your setup:
```json
{
  "comfyui_url": "http://127.0.0.1:8188",
  "base_output_dir": "../../Docs/Generated",
  "ue5_integration_enabled": false
}
```

### 3. Basic Usage

#### Generate a Single Asset
```bash
python terminal_grounds_pipeline.py generate weapon "Plasma Rifle" --faction directorate
```

#### Generate from CSV (like Weapons.csv)
```bash
python terminal_grounds_pipeline.py batch-csv Data/Tables/Weapons.csv --type weapon
```

#### Generate Faction Asset Set
```bash
python terminal_grounds_pipeline.py faction-assets directorate --types weapon,vehicle --count 5
```

#### Validate Pipeline
```bash
python terminal_grounds_pipeline.py validate
```

#### Interactive Mode
```bash
python terminal_grounds_pipeline.py interactive
```

## 📊 Advanced Usage

### Custom Asset Specifications
```python
from pipeline import AssetSpecification, PipelineController

# Create detailed specification
spec = AssetSpecification(
    name="Advanced Plasma Rifle",
    asset_type="weapon",
    faction="directorate",
    category="energy_weapons",
    primary_prompt="sleek military plasma rifle, directorate aesthetics",
    render_settings=RenderSettings(
        width=1024,
        height=1024,
        steps=30,
        cfg=7.0,
        seed=12345
    ),
    quality_settings=QualitySettings(
        auto_upscale=True,
        enhance_details=True
    ),
    auto_import_ue5=True
)

# Generate
controller = PipelineController()
result = controller.generate_single_asset(spec)
```

### Batch Processing with Progress
```python
def progress_callback(progress_info):
    percent = progress_info["progress_percent"]
    print(f"Progress: {percent:.1f}%")

result = controller.process_csv_batch(
    "Data/Tables/Weapons.csv",
    template_spec,
    progress_callback
)
```

### Quality Assurance Integration
```python
# Automatic quality validation
qa_result = quality_assurance.validate_output(generation_result, spec)

if qa_result.needs_upscaling:
    upscaled_result = quality_assurance.upscale_asset(generation_result, spec)

if qa_result.needs_enhancement:
    enhanced_result = quality_assurance.enhance_asset(generation_result, spec)
```

## 🔧 Configuration Options

### ComfyUI Settings
- `comfyui_url`: ComfyUI server URL
- `generation_timeout`: Max generation time
- `default_model`: Default AI model

### Processing Settings
- `max_concurrent_jobs`: Parallel generation limit
- `retry_failed_jobs`: Auto-retry on failure
- `quality_gate_enabled`: Enable quality validation

### Output Settings
- `base_output_dir`: Base output directory
- `auto_enhance_assets`: Auto-enhance low quality assets
- `auto_upscale_assets`: Auto-upscale when needed

### UE5 Integration
- `ue5_integration_enabled`: Enable UE5 import
- `ue5_project_path`: Path to UE5 project
- `use_ue5_python_api`: Use Python API vs command-line

## 🎨 Asset Types Supported

- **Weapons**: High-detail renders with faction styling
- **Vehicles**: Concept art and technical illustrations  
- **Gear**: Equipment and armor visualization
- **Buildings**: Environmental structures and architecture
- **Characters**: Character concepts and portraits
- **Environments**: Landscape and environment mattes
- **UI Icons**: Game interface elements
- **Posters**: In-game propaganda and signage
- **Textures**: Material textures and decals
- **Concepts**: General concept art

## 🏷️ Faction Integration

The pipeline deeply integrates with Terminal Grounds' faction system:

### Directorate
- Military aesthetics with clean lines
- Parkerized steel and serial-stamped equipment
- Disciplined formations and standardized gear

### Free77
- Contractor/mercenary styling
- Modular gear and utilitarian design
- Pragmatic team-based equipment

### Vultures Union  
- Salvaged and patched aesthetics
- Opportunistic scavenged equipment
- Rusted rivets and weathered surfaces

### + 4 More Factions
Each with unique LoRAs, color palettes, and style guides.

## 📈 Quality Assurance

### Automatic Validation
- Resolution scoring
- Detail analysis
- Composition assessment
- Color harmony evaluation
- Faction alignment checking

### Enhancement Pipeline
- Smart upscaling with AI models
- Detail enhancement filters
- Color correction and grading
- Format optimization

### Quality Gates
- Configurable quality thresholds
- Automatic retry for failed assets
- Quality reporting and analytics

## 🔗 UE5 Integration

### Automatic Import
- Direct import into content browser
- Proper texture compression settings
- Material instance creation
- Metadata tagging

### Organization
- Faction-based folder structure
- Asset type categorization
- Search and filtering support

## 🛠️ Extending the Pipeline

### Adding New Workflows
1. Create new ComfyUI workflow JSON
2. Place in `workflows/` directory
3. Add workflow type to `asset_spec.py`
4. Update workflow selection rules

### Custom Quality Metrics
```python
class CustomQualityAssurance(QualityAssurance):
    def _calculate_custom_score(self, image, spec):
        # Custom quality analysis
        return score
```

### New Asset Types
```python
class AssetType(Enum):
    CUSTOM_TYPE = "custom_type"
```

## 📊 Performance Optimizations

### RTX 3090 Ti Optimized
- Batch size optimization
- Memory management
- Concurrent processing limits
- Model caching strategies

### Efficiency Features
- Smart caching of LoRAs and models
- Workflow reuse and optimization
- Progressive quality enhancement
- Resource monitoring

## 🐛 Troubleshooting

### Common Issues

#### ComfyUI Connection Failed
```bash
# Check ComfyUI is running
python terminal_grounds_pipeline.py validate
```

#### Generation Timeout
```json
// Increase timeout in config.json
"generation_timeout": 1200.0
```

#### Quality Gate Failures
```json
// Adjust quality thresholds
"min_quality_score": 60.0
```

### Debug Mode
```bash
python terminal_grounds_pipeline.py --verbose --log-file debug.log generate weapon "Test"
```

## 📚 Migration from v1

### Script Mapping
| Old Script | New Command |
|------------|-------------|
| `generate_concepts.py` | `terminal_grounds_pipeline.py batch-csv` |
| `artgen_run_batch.py` | `terminal_grounds_pipeline.py faction-assets` |
| `working_flux_generator.py` | `terminal_grounds_pipeline.py generate` |

### Configuration Migration
1. Review existing `artgen_config.json`
2. Update `config.json` with your settings
3. Test with `validate` command

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black pipeline/
```

### Adding Features
1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit pull request

## 📄 License

This pipeline is part of the Terminal Grounds project and follows the same licensing terms.

---

## 🎯 Summary

The Terminal Grounds Asset Generation Pipeline v2.0 represents a complete overhaul that transforms a collection of scattered scripts into a professional, production-ready asset generation system. It provides:

- **Unified Control**: Single entry point for all operations
- **Smart Automation**: Intelligent workflow selection and processing  
- **Quality Assurance**: Automated validation and enhancement
- **Scalable Architecture**: Handles everything from single assets to large batches
- **Professional Integration**: Seamless UE5 import and organization
- **Faction Awareness**: Deep integration with Terminal Grounds lore and aesthetics

This system is designed to scale with your project, from rapid prototyping to final production assets, while maintaining the highest quality standards and efficient resource utilization of your RTX 3090 Ti setup.