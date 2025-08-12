# Terminal Grounds Content Pipeline Agent

A comprehensive content pipeline agent for Terminal Grounds UE5.6 that automates asset audit, generation, and integration.

## Overview

The Terminal Grounds Content Pipeline Agent is a complete automation system that:

1. **Audits** existing assets to identify placeholders and missing content
2. **Generates** high-quality replacements using Hugging Face AI models
3. **Integrates** assets into Unreal Engine 5.6 with proper settings
4. **Maintains** Terminal Grounds art direction and lore consistency

## Features

### 🔍 Asset Audit System
- Recursive scanning of all image content folders
- Intelligent placeholder and watermark detection
- Asset categorization (concept art, logos, posters, UI icons)
- Priority-based flagging for replacement
- Comprehensive audit reporting

### 🎨 AI-Powered Asset Generation
- Hugging Face model integration (Flux 1 Schnell)
- Terminal Grounds-specific prompt templates
- Faction-aware generation with art bible compliance
- Multi-resolution support (512×512 to 2048×2048+)
- Quality levels: draft, standard, high, premium

### 🏗️ Unreal Engine 5.6 Integration
- Automated import with correct naming conventions
- Proper texture groups and compression settings
- Material instance creation from M_TG_Decal_Master
- GameplayTags application for UI assets
- Python script generation for UE5 automation

### 🔧 Workflow Automation
- Complete pipeline orchestration
- Continuous monitoring mode
- Quality assurance validation
- Comprehensive logging and reporting
- Non-placeholder asset protection

## Supported Asset Categories

| Category | Resolution | Output Location | Material Creation |
|----------|------------|-----------------|-------------------|
| Faction Logos | 1024×1024 | `Content/TG/Decals/Factions/` | ✅ Decal Material |
| Propaganda Posters | 1024×2048 | `Content/TG/Decals/Posters/` | ✅ Decal Material |
| UI Icons | 512×512 | `Content/TG/Icons/` | ❌ Direct Texture |
| Weapon Concepts | 2048×1024 | `Content/TG/ConceptArt/Weapons/` | ❌ Direct Texture |
| Vehicle Concepts | 2048×1024 | `Content/TG/ConceptArt/Vehicles/` | ❌ Direct Texture |
| Biome Concepts | 2048×1024 | `Content/TG/ConceptArt/Biomes/` | ❌ Direct Texture |
| General Concept Art | 2048×2048 | `Content/TG/ConceptArt/` | ❌ Direct Texture |

## Installation & Setup

### Prerequisites
- Python 3.8+
- Unreal Engine 5.6
- Access to Hugging Face models (for generation)

### Required Python Packages
```bash
pip install requests pillow
```

### Setup
1. Clone the Terminal Grounds repository
2. Ensure all pipeline scripts are in `Tools/` directory
3. Verify content structure matches expected paths

## Usage

### Quick Start
```bash
# Run complete pipeline
python Tools/TG_ContentPipelineMain.py

# Run specific phases
python Tools/TG_ContentPipelineMain.py --audit-only
python Tools/TG_ContentPipelineMain.py --generate-only
python Tools/TG_ContentPipelineMain.py --integrate-only

# Continuous monitoring
python Tools/TG_ContentPipelineMain.py --continuous
```

### Individual Components
```bash
# Asset audit only
python Tools/TG_ContentPipelineAgent.py audit

# Generate specific asset types
python Tools/TG_HuggingFaceGenerator.py logos
python Tools/TG_HuggingFaceGenerator.py posters
python Tools/TG_HuggingFaceGenerator.py icons

# Create UE integration templates
python Tools/TG_UnrealEngineIntegrator.py create-templates
```

### Demo and Testing
```bash
# Run complete demonstration
python Tools/test_pipeline_demo.py
```

## Faction Integration

The pipeline supports all 7 Terminal Grounds factions with unique visual styles:

| Faction | Style | Primary Colors | Keywords |
|---------|--------|----------------|----------|
| **Directorate** | Military Precision | Navy Blue, Gunmetal, White | Disciplined, Tactical, Steel |
| **Vultures Union** | Salvage Industrial | Rust Red, Gray, Yellow | Scrap, Warning Stripes, Oil |
| **Free 77** | Contractor Practical | Desert Tan, Olive, Black | Mercenary, Desert, Tactical |
| **Corporate Combine** | Corporate Clean | Blue, Chrome, Purple | Professional, Energy, Tech |
| **Nomad Clans** | Convoy Rugged | Brown, Orange, Tan | Road-worn, Convoy, Banners |
| **Vaulted Archivists** | Alien Mystical | Dark Green, Gold, Cyan | Eye Symbols, Archive, Coils |
| **Civic Wardens** | Defensive Militia | Navy, Orange, Green | Bastion, Sandbags, Neighborhood |

## Configuration

### Pipeline Configuration
Create a `config.json` file to customize pipeline behavior:

```json
{
  "audit": {
    "enabled": true,
    "placeholder_threshold": 0.5
  },
  "generation": {
    "enabled": true,
    "quality": "high",
    "max_assets_per_run": 50,
    "generation_delay": 2
  },
  "integration": {
    "enabled": true,
    "auto_import": false,
    "create_materials": true,
    "apply_tags": true
  },
  "continuous": {
    "enabled": false,
    "scan_interval": 3600
  }
}
```

## Unreal Engine Integration

### Material Setup
The pipeline requires a master material `M_TG_Decal_Master` with these parameters:
- **BaseColor** (Texture Parameter): Main decal texture
- **Opacity** (Scalar Parameter): Overall decal opacity
- **OpacityMask** (Texture Parameter): Optional opacity mask
- **Roughness** (Scalar Parameter): Surface roughness
- **Metallic** (Scalar Parameter): Metallic value

### Import Process
1. Pipeline generates Python import scripts
2. Open UE5 Python Console (Window > Developer Tools > Python Console)
3. Execute generated scripts:
   ```python
   exec(open(r'Tools/Unreal/python/import_batch_YYYYMMDD_HHMMSS.py').read())
   ```

### Asset Naming Conventions
- Textures: `T_AssetName`
- Materials: `M_AssetName` 
- Material Instances: `MI_AssetName`
- All assets follow `TG_Domain_Asset_Variant` pattern

## Logging and Monitoring

### Log Files
- `Docs/Phase4_Implementation_Log.md` - Implementation progress
- `Docs/Tech/pipeline_log.json` - Pipeline execution log
- `Docs/Tech/asset_audit_report.json` - Latest audit results
- `Docs/Tech/pipeline_results.json` - Complete pipeline results

### Monitoring
The pipeline provides detailed logging of:
- Asset scan results and flagged items
- Generation success/failure rates
- Import script creation
- Quality assurance checks
- Performance metrics

## Quality Assurance

### Style Compliance
- Terminal Grounds art bible alignment
- Faction color palette adherence
- Military sci-fi aesthetic consistency
- Post-apocalyptic mood requirements

### Technical Validation
- Proper naming conventions
- Correct file formats and resolutions
- UE5 compatibility
- Performance optimization

### Lore Alignment
- Faction identity accuracy
- Terminal Grounds universe consistency
- Military realism with sci-fi accents
- Environmental storytelling elements

## Troubleshooting

### Common Issues

**"No module named 'huggingface'"**
- Hugging Face functions are accessed through tool calls, not direct imports
- Pipeline will attempt to use available generation methods

**"Import failed" in UE5**
- Verify material templates exist (`M_TG_Decal_Master`)
- Check file paths and naming conventions
- Ensure UE5 Python API is enabled

**"No flagged assets found"**
- Existing assets are well-named and don't contain placeholder patterns
- Pipeline will generate sample assets for demonstration

### Debug Mode
Run with verbose output:
```bash
python Tools/TG_ContentPipelineMain.py --verbose
```

## Contributing

### Adding New Asset Categories
1. Update `AssetCategory` enum in `TG_ContentPipelineAgent.py`
2. Add category mapping in `categorize_asset()` method
3. Create prompt templates in `TG_HuggingFaceGenerator.py`
4. Add UE settings in `TG_UnrealEngineIntegrator.py`

### Adding New Factions
1. Update faction data in `_load_faction_data()` method
2. Add faction-specific prompt templates
3. Create faction color palettes and style guides
4. Update documentation

## Architecture

### Component Overview
```
TG_ContentPipelineMain.py      # Master orchestrator
├── TG_ContentPipelineAgent.py # Asset audit system
├── TG_HuggingFaceGenerator.py # AI asset generation
└── TG_UnrealEngineIntegrator.py # UE5 integration
```

### Data Flow
1. **Audit Phase**: Scan → Categorize → Flag → Report
2. **Generation Phase**: Template → Generate → Validate → Save
3. **Integration Phase**: Import → Configure → Material → Tag
4. **QA Phase**: Validate → Check → Report → Log

## Version History

### v1.0.0 - Initial Release
- Complete asset audit system
- Hugging Face integration with Flux 1 Schnell
- UE5.6 automated import system
- Material instance creation
- 7 faction support with art bible compliance
- Continuous monitoring capabilities
- Comprehensive logging and reporting

## License

This content pipeline agent is part of the Terminal Grounds project and follows the project's licensing terms.

## Support

For issues and questions:
1. Check troubleshooting section
2. Review log files for error details
3. Run demo script to verify installation
4. Submit issues through project channels