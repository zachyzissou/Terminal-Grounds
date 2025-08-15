# Terminal Grounds - Advanced Asset Generation System

## Overview

This is the new and improved asset generation pipeline for Terminal Grounds, designed to work with ComfyUI and your RTX 3090 Ti. It addresses the two main issues you were having:

1. **Better Workflows**: Optimized ComfyUI workflows specifically for Terminal Grounds assets
2. **Output Monitoring**: Real-time watching and review system for generated assets

## Components

### 1. Main Generator (`TERMINAL_GROUNDS_GENERATOR.bat`)
- Complete asset generation pipeline
- Interactive menu system
- Integrated output monitoring
- Support for all faction emblems and propaganda posters

### 2. Output Monitor (`OUTPUT_MONITOR.bat`)
- Standalone monitoring tool
- Watches ComfyUI output folder
- Auto-organizes assets by type
- Web-based review dashboard

### 3. Python Scripts
- `terminal_grounds_generator.py`: Main generation pipeline
- `output_monitor.py`: Standalone output watcher

## Setup

1. **Ensure ComfyUI is running in API mode**:
   - Start ComfyUI on port 8000
   - Make sure FLUX models are loaded

2. **Update paths if needed**:
   - Edit `COMFYUI_OUTPUT` in the Python scripts if your ComfyUI output folder is different
   - Default: `C:\Users\Zachg\Documents\ComfyUI\output`

## How to Use

### Option 1: Full Pipeline
1. Run `TERMINAL_GROUNDS_GENERATOR.bat`
2. Choose from the menu:
   - Generate all faction emblems
   - Generate propaganda posters
   - Generate specific faction assets
   - Open review dashboard
   - Process approved assets

### Option 2: Just Monitor Output
1. Run `OUTPUT_MONITOR.bat`
2. It will watch for new files and create a web dashboard
3. Review assets in your browser (auto-opens)

## Workflow Improvements

### Faction Emblems
- 2048x2048 resolution for high quality
- Optimized prompts for each faction's aesthetic
- Proper negative prompts to avoid text/watermarks
- Uses dpmpp_2m sampler with karras scheduler

### Propaganda Posters
- 1536x2048 resolution (3:4 ratio)
- Four themes: recruitment, victory, warning, unity
- Faction-specific color schemes and styles
- Higher CFG and steps for detailed results

## Asset Organization

```
Tools/ArtGen/outputs/
├── review/           # New assets for review
│   ├── Emblems/
│   ├── Posters/
│   ├── Icons/
│   └── Misc/
└── approved/         # Assets ready for import
    ├── Emblems/
    ├── Posters/
    ├── Icons/
    └── Misc/
```

## Review Dashboard

The web dashboard (`review/dashboard.html`) provides:
- Visual grid of all generated assets
- Category organization
- Approve/Reject buttons for each asset
- Generation statistics
- Auto-refresh every 5 seconds

## Factions Configured

1. **Directorate (DIR)** - Military chevron, steel gray/blue
2. **Vultures Union (VLT)** - Scavenger bird, black/yellow
3. **Free 77 (F77)** - Mercenary stencil, tactical brown
4. **Corporate Combine (CCB)** - Hexagonal shield, corporate blue
5. **Nomad Clans (NMD)** - Tribal wheel, desert orange
6. **Vaulted Archivists (VAC)** - Mystic eye, gold/green
7. **Civic Wardens (CWD)** - Fortress block, orange/navy

## Tips

- **Start small**: Generate one faction's assets first to test
- **Check the dashboard**: Open it in a browser to review assets visually
- **Batch processing**: Queue multiple generations, then review all at once
- **LoRA support**: The system detects and uses LoRAs if available

## Troubleshooting

**ComfyUI not detected:**
- Make sure ComfyUI is running on port 8000
- Check firewall settings

**No files appearing in review:**
- Verify COMFYUI_OUTPUT path is correct
- Check that files start with "TG_" prefix

**Dashboard not updating:**
- Refresh browser manually (F5)
- Check that output_monitor.py is running

## Next Steps

Once you approve assets, they're ready to be imported into Unreal Engine:
- Emblems → Content/TG/Decals/Factions/
- Posters → Content/TG/Decals/Posters/
- Icons → Content/TG/Icons/UI/

The system is designed to integrate with your existing Unreal import pipeline.
