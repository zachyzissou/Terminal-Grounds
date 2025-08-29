# Unreal MCP Setup Guide - Terminal Grounds

## 🎯 Overview

You have successfully installed the **Unreal MCP (Model Context Protocol)** integration for your Terminal Grounds project. This allows AI assistants like GitHub Copilot, Cursor, and Claude Desktop to control Unreal Engine through natural language commands.

## ✅ Installation Status

- ✅ **Python Environment**: 3.12.9 installed
- ✅ **UV Package Manager**: Installed and configured
- ✅ **Virtual Environment**: Created at `unreal-mcp/Python/.venv`
- ✅ **Dependencies**: All required packages installed
- ✅ **UnrealMCP Plugin**: Integrated into Terminal Grounds project
- ✅ **MCP Configuration**: Set up for Cursor and Claude Desktop

## 🚀 Quick Start

### 1. Launch Unreal Engine

```powershell
# Open Terminal Grounds project
& "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor.exe" "C:\Users\Zachg\Terminal-Grounds\TerminalGrounds.uproject"
```

### 2. Start MCP Server

```powershell
cd "C:\Users\Zachg\Terminal-Grounds\unreal-mcp\Python"
.venv\Scripts\activate
uv run unreal_mcp_server.py
```

### 3. Use with AI Assistant

Once both Unreal Engine and the MCP server are running, you can use natural language commands like:

- *"Create a red cube at position 0,0,0"*
- *"Add a point light above the cube"*
- *"Create a new Blueprint class called MyCharacter"*
- *"Focus the viewport on the cube"*

## 🛠️ Available Tools

### Actor Management

- **Create Actors**: Cubes, spheres, lights, cameras, etc.
- **Transform Control**: Position, rotation, scale manipulation
- **Property Queries**: Get actor properties and find by name
- **Actor Listing**: View all actors in current level

### Blueprint Development

- **Class Creation**: New Blueprint classes with components
- **Component Management**: Add mesh, camera, light, physics
- **Property Configuration**: Set component properties
- **Blueprint Compilation**: Compile and spawn Blueprint actors
- **Input Mapping**: Create player controls

### Blueprint Node Graph

- **Event Nodes**: BeginPlay, Tick, custom events
- **Function Calls**: Create and connect function nodes
- **Variables**: Add typed variables with default values
- **References**: Component and self references
- **Node Management**: Find and organize nodes

### Editor Control

- **Viewport Focus**: Focus on specific actors/locations
- **Camera Control**: Orientation and distance adjustment

## 📁 Project Structure

```
Terminal-Grounds/
├── unreal-mcp/                    # MCP integration
│   ├── MCPGameProject/           # Sample UE project
│   ├── Python/                   # Python MCP server
│   │   ├── .venv/               # Virtual environment
│   │   ├── tools/               # Tool modules
│   │   └── unreal_mcp_server.py # Main server
│   └── Docs/                    # Documentation
├── Plugins/
│   └── UnrealMCP/               # UE plugin (integrated)
├── .cursor/
│   └── mcp.json                 # Cursor configuration
└── .config/claude-desktop/
    └── mcp.json                 # Claude Desktop config
```

## 🔧 Configuration Files

### Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\Zachg\\Terminal-Grounds\\unreal-mcp\\Python",
        "run",
        "unreal_mcp_server.py"
      ]
    }
  }
}
```

### Claude Desktop (`.config/claude-desktop/mcp.json`)

```json
{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\Zachg\\Terminal-Grounds\\unreal-mcp\\Python",
        "run",
        "unreal_mcp_server.py"
      ]
    }
  }
}
```

## 🎮 Usage Examples

### Basic Actor Creation

- "Create a blue sphere at position 100, 0, 50"
- "Add a directional light pointing down"
- "Spawn a camera and focus viewport on it"

### Blueprint Development

- "Create a new Blueprint class called PlayerController"
- "Add a static mesh component to the Blueprint"
- "Create a BeginPlay event that prints 'Hello World'"
- "Add a float variable called Health with default 100"

### Level Design

- "Create 5 red cubes in a circle around the origin"
- "Add collision to all actors in the level"
- "Set all lights to cast shadows"

## 🐛 Troubleshooting

### Server Won't Start

1. Ensure Unreal Engine is running
2. Check if port 55557 is available
3. Verify virtual environment is activated
4. Check `unreal_mcp.log` for error details

### Plugin Not Loading

1. Verify plugin is in `Plugins/UnrealMCP/`
2. Check Unreal Engine version (requires 5.5+)
3. Enable plugin in Edit → Plugins
4. Restart Unreal Engine

### Connection Issues

1. Confirm MCP server is running
2. Check firewall settings for port 55557
3. Verify MCP client configuration paths
4. Restart both Unreal Engine and MCP server

## 📚 Resources

- **Documentation**: `unreal-mcp/Docs/README.md`
- **API Reference**: `unreal-mcp/Python/tools/`
- **Examples**: `unreal-mcp/Python/scripts/`
- **GitHub**: https://github.com/chongdashu/unreal-mcp

## 🎯 Next Steps

1. **Test Basic Commands**: Start with simple actor creation
2. **Explore Tools**: Try Blueprint and editor control features
3. **Integrate Workflow**: Use with your Terminal Grounds development
4. **Contribute**: Report issues or suggest improvements

---

**Status**: ✅ Fully configured and ready to use!
**Unreal Engine Version**: 5.6 (Compatible)
**Python Version**: 3.12.9 (Compatible)
**MCP Server**: Ready for natural language Unreal Engine control
