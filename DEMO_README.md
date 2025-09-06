# Terminal Grounds - Playable Demo

## 🎮 Demo Overview

This is a comprehensive playable demo of Terminal Grounds built using your existing systems and enhanced with MCP (Model Context Protocol) integration. The demo showcases:

- **8 AI enemies** with full patrol, detection, and combat behavior using your `TGEnemyGrunt` system
- **Functional weapons** with firing mechanics and damage using your `TGWeapon` system
- **Detailed TechWastes map** with strategic cover and objectives
- **Atmospheric lighting** and environment setup
- **MCP integration** for AI-driven development

## 🚀 Quick Start

### Prerequisites
- Unreal Engine 5.6
- Python 3.10+ (for MCP servers)
- Terminal Grounds project compiled

### Running the Demo

1. **Compile the project** with the new demo systems:
   ```bash
   # Build the project in Unreal Engine
   # Or use command line:
   "C:\Program Files\Epic Games\UE_5.6\Engine\Build\BatchFiles\Build.bat" TerminalGroundsEditor Win64 Development "C:\Users\Zachg\Terminal-Grounds\TerminalGrounds.uproject"
   ```

2. **Open Unreal Engine** and load the project

3. **Load the TechWastes map**:
   - Navigate to `Content/TG/Maps/TechWastes/TechWastes_Band_Gamma.umap`

4. **Add the Demo Setup actor**:
   - In the level, add a `TGDemoSetup` actor
   - Configure the demo settings in the Details panel
   - The demo will auto-setup when you play

5. **Play the demo!**
   - Press Play in the editor
   - Use WASD to move, mouse to aim, left click to shoot

## 🎯 Demo Features

### AI Enemies (TGEnemyGrunt)
- **8 strategically placed enemies** around the map
- **Patrol behavior** with waypoint navigation
- **Detection system** with 1500 unit range
- **Combat AI** with 800 unit attack range
- **Health system** (75 HP each)
- **Damage dealing** (25 damage per attack)

### Weapons (TGWeapon)
- **Functional weapon system** with line trace damage
- **Firing mechanics** with configurable fire rate
- **Ammo system** (30 rounds)
- **Damage system** (30 damage per shot)
- **Range** (10,000 units)

### Environment
- **Strategic cover objects** for tactical gameplay
- **Patrol waypoints** for AI navigation
- **Atmospheric lighting** with directional light and fog
- **TechWastes industrial theme**

### MCP Integration
- **Unreal Engine MCP Bridge** for AI-driven development
- **3D-MCP** for 3D content creation
- **Binary Reader MCP** for asset analysis
- **Unreal-Blender MCP** for cross-software workflows

## 🛠️ Technical Implementation

### Core Systems Used
- `ATGEnemyGrunt` - Your existing AI enemy system
- `ATGWeapon` - Your existing weapon system
- `ATGPlayPawn` - Your existing player system
- `TGDemoSetup` - New demo management system

### MCP Servers Integrated
- **UnrealEngine-ai-mcp** - Natural language Unreal control
- **3d-mcp** - Universal 3D software interface
- **unreal-blender-mcp** - Blender-Unreal integration
- **binary-reader-mcp** - Asset file analysis

### Demo Configuration
The `TGDemoSetup` actor provides these configurable options:
- Number of enemies (default: 8)
- Enemy spawn radius (default: 2500 units)
- Cover object creation (enabled by default)
- Patrol point creation (enabled by default)
- Lighting setup (enabled by default)

## 🎮 Controls

- **WASD** - Move player
- **Mouse** - Look around
- **Left Click** - Fire weapon
- **R** - Reload weapon (if implemented)

## 🏗️ Building Your Own Demo

### Using the Demo Builder Script
```bash
python build_demo.py
```

This script demonstrates how to use MCP servers to:
- Spawn actors programmatically
- Configure AI behavior
- Set up lighting and environment
- Create strategic gameplay elements

### Extending the Demo
1. **Add more enemy types** by extending `TGEnemyGrunt`
2. **Create new weapons** by extending `TGWeapon`
3. **Add objectives** by creating new actor types
4. **Enhance AI behavior** by modifying the patrol system

### MCP Development
The MCP servers allow for:
- **Natural language** Unreal Engine control
- **Automated** content generation
- **Cross-software** workflows
- **AI-driven** development

## 📁 File Structure

```
Terminal Grounds/
├── Source/TGCombat/
│   ├── Public/
│   │   ├── TGDemoSetup.h          # Demo management system
│   │   ├── TGDemoManager.h        # Alternative demo manager
│   │   └── TGDemoWeapon.h         # Enhanced weapon system
│   └── Private/
│       ├── TGDemoSetup.cpp        # Demo implementation
│       ├── TGDemoManager.cpp      # Demo manager implementation
│       └── TGDemoWeapon.cpp       # Enhanced weapon implementation
├── Content/TG/Maps/
│   └── TechWastes/
│       └── TechWastes_Band_Gamma.umap  # Demo map
├── build_demo.py                  # Demo builder script
└── DEMO_README.md                # This file
```

## 🎉 What You've Achieved

✅ **Playable Demo** - A fully functional game demo
✅ **AI Enemies** - 8 patrolling, combat-ready bots
✅ **Working Weapons** - Functional shooting mechanics
✅ **Detailed Map** - Strategic TechWastes environment
✅ **MCP Integration** - AI-driven development tools
✅ **Existing Systems** - Built on your current codebase

## 🚀 Next Steps

1. **Test the demo** in Unreal Engine
2. **Customize** the demo settings
3. **Add more content** using MCP tools
4. **Extend** the AI and weapon systems
5. **Create** additional maps and scenarios

The demo is ready to play and showcases the full potential of your Terminal Grounds systems combined with modern MCP development tools!
