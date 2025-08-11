# Terminal Grounds Modding SDK

## Overview
The Terminal Grounds Modding Kit (TGModKit) provides tools and templates for creating data-driven modifications to Terminal Grounds. The modding system supports hot-loadable content packs without requiring C++ compilation.

## Supported Mod Types

### Data Pack Mods
- **Weapons**: Add new weapons with custom stats, attachments, and visual/audio assets
- **Factions**: Create new factions with unique dialogue, equipment preferences, and AI behavior
- **Missions**: Design custom mission types and contract variations
- **Maps**: Add new POIs and modify existing map layouts (requires UE5 Editor)
- **Audio**: Custom weapon sounds, faction voice lines, and environmental audio

### Content Pack Structure
```
MyMod/
├── Data/
│   ├── Weapons.csv
│   ├── Factions.csv
│   ├── Missions.csv
│   └── Barks.csv
├── Content/
│   ├── Meshes/
│   ├── Textures/
│   ├── Audio/
│   └── Materials/
├── Config/
│   └── ModInfo.json
└── README.md
```

## Getting Started

### 1. Install TGModKit
Extract the TGModKit to your Terminal Grounds installation directory:
`TerminalGrounds/Mods/TGModKit/`

### 2. Create Your First Mod
Use the weapon template to create a custom weapon:

```bash
# Copy the weapon template
cp Templates/WeaponMod MyCustomWeapon
cd MyCustomWeapon

# Edit the weapon data
# Modify Data/Weapons.csv with your weapon stats
# Add your weapon mesh to Content/Meshes/
# Add weapon sounds to Content/Audio/
```

### 3. Test Your Mod
```bash
# Validate mod structure
python Tools/validate_mod.py MyCustomWeapon

# Install mod for testing
python Tools/install_mod.py MyCustomWeapon

# Launch Terminal Grounds with mods enabled
TerminalGrounds.exe -mods
```

## Data Schema Reference

### Weapons.csv Schema
```csv
Id,Tier,Family,Name,BaseDamage,FireRate,RPM,MaxRange,Hitscan,ProjectileSpeed,RecoilX,RecoilY,MagSize,ADS_ms,Reload_ms,PenClass,HeatCap,HeatPerShot,EMPVulnerability,WeaponConceptRef,FactionBias
```

### Required Fields
- **Id**: Unique identifier (prefix with mod name: "MyMod_WeaponName")
- **Tier**: Human/Hybrid/Alien
- **Family**: AR/DMR/LMG/SMG/SG/Pistol
- **Name**: Display name for the weapon
- **BaseDamage**: Base damage per shot (20-120 typical range)

### Optional Asset References
- **WeaponConceptRef**: Path to concept art image
- **MeshRef**: Path to weapon mesh (.uasset)
- **SoundRef**: Path to weapon audio (.uasset)

## Hot-Loading System

### Automatic Detection
Terminal Grounds automatically detects mod changes during gameplay:
- CSV file modifications reload immediately
- Asset changes require map reload (F5 in development mode)
- Config changes require game restart

### Development Commands
```
# In-game console commands (~ key)
TG.ReloadMods - Reload all mod data
TG.ListMods - Show active mods
TG.ToggleMod [ModName] - Enable/disable specific mod
TG.ValidateMods - Check for mod conflicts
```

## Asset Pipeline

### 3D Models
- **Format**: .fbx or .obj for import into UE5
- **Triangles**: <5000 for weapons, <15000 for vehicles
- **Textures**: 2048x2048 maximum, PBR materials preferred
- **LODs**: Provide 3 LOD levels for optimal performance

### Audio Assets
- **Format**: .wav, 48kHz, 16-bit minimum
- **Length**: <3 seconds for weapon sounds, <10 seconds for voice lines
- **Compression**: Vorbis compression applied automatically

### Concept Art
- **Format**: .png, .jpg supported
- **Resolution**: 1920x1080 recommended
- **Usage**: Displayed in weapon selection UI and documentation

## Mod Validation

### Automated Checks
The mod validator performs these checks:
- **Schema Compliance**: CSV files match expected column structure
- **Asset References**: All referenced files exist and are properly formatted
- **Balance Validation**: Weapon stats within acceptable ranges
- **Naming Conflicts**: No duplicate IDs across mods

### Performance Guidelines
- **Draw Calls**: <500 additional draw calls per mod
- **Memory**: <128MB additional RAM usage
- **Loading Time**: <5 seconds additional load time

## Publishing Mods

### Community Workshop (Planned)
Future releases will include Steam Workshop integration for easy mod sharing.

### Manual Distribution
1. Package your mod folder as a .zip file
2. Include installation instructions
3. Test on clean Terminal Grounds installation
4. Share via community forums or GitHub

## Mod Conflicts

### Automatic Resolution
- **Weapon IDs**: Must be unique across all mods
- **Asset Paths**: Use mod-specific folders to avoid conflicts
- **Load Order**: Alphabetical by mod folder name

### Manual Resolution
Edit `Config/ModLoadOrder.txt` to specify custom loading sequence:
```
CoreGameplay
MyWeaponPack
CommunityFactions
ExperimentalMissions
```

## Support and Documentation

### Community Resources
- **Forum**: terminalgrounds.com/modding
- **Discord**: #modding-support channel
- **GitHub**: github.com/zachyzissou/Terminal-Grounds-Mods

### Reporting Issues
When reporting mod-related bugs:
1. Include mod list and load order
2. Attach game logs (Logs/TerminalGrounds.log)
3. Provide steps to reproduce the issue
4. Test without mods to confirm mod-related

## Legal Notice

### Content Guidelines
- No copyrighted material without permission
- No offensive or inappropriate content
- Respect Terminal Grounds' art style and lore
- Credit original asset creators

### Licensing
Mods created with TGModKit may be distributed freely. Commercial use requires explicit permission from the Terminal Grounds development team.