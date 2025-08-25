# Terminal Grounds Asset Pipeline Implementation Guide

## 🎯 Overview

This document outlines the complete asset generation and replacement pipeline for Terminal Grounds, integrating HF/MCP image generation with UE5.6.

## 📊 Current Status (2025-01-29)

### Assets Generated Today

✅ **Faction Logos (7/7)**

- Sky Bastion Directorate - Navy blue military shield with wings
- Iron Vultures - Scavenger skull with industrial elements  
- The Seventy-Seven - Mercenary badge with Highway 77 motif
- Trivector Combine - High-tech hexagonal circuit design
- Roadborn Clans - Convoy compass with road elements
- Obsidian Archive - Knowledge key with arcane geometry
- Truce Wardens - Emergency services shield with medical cross

✅ **UI Icons (2/8)**

- Ballistic damage indicator
- Ion damage indicator

### Placeholder Status

- **Total Placeholders Identified**: 73
- **Replaced So Far**: 9
- **Remaining**: 64

## 🔧 Pipeline Components

### 1. Asset Generation System

- **Tool**: Hugging Face MCP with FLUX.1 Schnell
- **Resolution**: 512x512 to 2048x2048
- **Formats**: PNG with transparency support
- **Style Consistency**: Enforced through Art Bible parameters

### 2. Directory Structure

```text
Terminal-Grounds/
├── Content/TG/
│   ├── Icons/
│   │   └── Factions/        # Faction logos
│   ├── Concepts/
│   │   └── Weapons/         # Weapon concept art
│   ├── Decals/
│   │   └── Posters/         # POI posters
│   └── UI/                  # HUD elements
├── Tools/ArtGen/
│   └── outputs/
│       ├── Logos/           # Generated logos
│       └── Biomes/          # Biome concepts
└── Docs/
    └── Assets/
        ├── Manifest.md      # Asset tracking
        └── validation_report.md
```

### 3. Automation Script

The Python pipeline script (`tg-asset-pipeline`) provides:

- Placeholder detection and categorization
- Asset manifest generation
- UE5 import script creation
- Art/Lore Bible compliance validation
- Performance metrics tracking

## 📋 Next Steps

### Immediate Actions (Priority 1)

1. **Complete UI Icon Set**
   - Generate remaining 6 UI icons at 512x512
   - Icons needed: extract_marker, map_ping, rarity variants, status_charge

2. **Weapon Concepts Generation**
   - 20+ weapon concepts identified in placeholder report
   - Focus on tier differentiation (Field/Splice/Monolith)
   - Resolution: 2048x1024

3. **Run Pipeline Script**

   ```powershell
   python Tools/ArtGen/tg-asset-pipeline.py
   ```

### Short-term Goals (Priority 2)

1. **Biome Concept Art**
      - IEZ Alpha/Beta Districts
      - Machine Grave Gamma Band
      - North Bastion views
      - The Deep Vault interiors

2. **Vehicle Concepts**
   - 8 vehicles in placeholder report
   - Include faction-specific variants

3. **POI Posters & Decals**
   - Environmental storytelling elements
   - Faction propaganda posters
   - Warning signs and markers

### Integration Tasks

1. **UE5.6 Import**
   - Run generated import script in UE5 Python console
   - Apply material instances with faction colors
   - Set up GameplayTags for all assets

2. **Version Control**
   - Commit assets with structured messages
   - Tag releases with asset manifest version

3. **CI/CD Pipeline**
   - Set up automated validation checks
   - Implement placeholder detection in build process

## 🎨 Generation Prompts Template

### Faction Assets

```text
{faction_name} faction {asset_type}, {primary_colors}, {thematic_elements}, 
{art_style}, PBR ready, high contrast, vector style, {resolution} resolution
```

### UI Elements

```text
Game UI {element_type}, {function_description}, {color_scheme}, 
clean minimalist design, high readability, transparent background, {size}px
```

### Concept Art

```text
{category} concept art, Terminal Grounds style, {tech_tier} technology, 
{faction_influence}, post-apocalyptic sci-fi, weathered textures, 
atmospheric lighting, {resolution} resolution
```

## 📈 Quality Metrics

### Resolution Requirements

- **Faction Logos**: 2048x2048 (currently 1024x1024 - needs upscale)
- **UI Icons**: 512x512 minimum
- **Weapon Concepts**: 2048x1024
- **Biome Concepts**: 3840x2160
- **Decals/Posters**: 1024x1024

### Performance Targets

- **Texture Memory**: < 16MB per asset
- **Total Package**: < 2GB for all visual assets
- **LOD Generation**: Required for all in-game assets

## 🔄 Iteration Process

1. **Generate** → Create variants (3+ per asset)
2. **Review** → Check Art Bible compliance
3. **Select** → Choose best variant
4. **Polish** → Adjust colors/details if needed
5. **Import** → Bring into UE5.6
6. **Validate** → Test in-game appearance
7. **Document** → Update manifest

## 🚀 Commands Reference

### Generate Assets

```python
# Use HF MCP tools as shown in examples
hugging mcp:gr1_flux1_schnell_infer
```

### Run Pipeline

```powershell
cd C:\Users\Zachg\Terminal-Grounds
python Tools/ArtGen/tg-asset-pipeline.py
```

### Import to UE5

```python
# In UE5 Python console
exec(open('Tools/ArtGen/ue5_import.py').read())
```

## 📝 Notes

- All generated assets must align with Art Bible color palettes
- Faction identity must be consistent with Lore Bible descriptions
- Maintain clear version control with v1, v2, v3 naming
- Document any deviations from original specifications
- Keep placeholder audit updated after each generation batch

## 🎯 Success Criteria

✅ All 73 placeholders replaced with production-ready assets
✅ Consistent visual language across all factions
✅ Performance targets met (90 FPS on target hardware)
✅ Full UE5.6 integration with proper tags and materials
✅ Complete documentation and version control

---

**Last Updated**: 2025-01-29 14:45
**Pipeline Version**: 1.0.0
**Next Review**: After 20 more assets generated
