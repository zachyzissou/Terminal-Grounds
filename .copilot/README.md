# GitHub Copilot Modes Setup Guide

This guide shows how to configure GitHub Copilot modes to emulate your Claude agent functionality.

## 🎯 Overview

Your Claude agents have been converted into GitHub Copilot mode configurations that provide similar specialized behavior and response structures.

## 📁 File Structure

```
.copilot/
├── modes.json                    # Main configuration and mode definitions
└── modes/
    ├── cto-architect.json       # Technical architecture guidance
    ├── chief-art-director.json  # Visual direction and art pillars
    ├── chief-design-officer.json # Game design systems
    ├── chief-security-officer.json # Security architecture
    ├── data-scientist.json      # Analytics and data processing
    ├── devops-engineer.json     # Infrastructure automation
    ├── performance-engineer.json # System optimization
    ├── comfyui-concept-designer.json # AI asset generation
    ├── map-designer.json        # Level design
    └── document-control-specialist.json # Documentation governance
```

## ⚙️ VS Code Configuration

### Step 1: Open VS Code Settings

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Preferences: Open User Settings (JSON)"
3. Click on the option to open `settings.json`

### Step 2: Add Mode Configurations

Add the following to your `settings.json`:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Reference the Terminal Grounds project context from CLAUDE.md and use appropriate specialized modes when discussing technical, creative, or operational topics."
    }
  ]
}
```

### Step 3: Mode-Specific Instructions

For each mode, you can add specific instructions. For example:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "When discussing technical architecture, use CTO ARCHITECT mode: Structure responses as Analysis → Recommendations → Architecture Sketches → Next Steps. Provide Safe/Bold/Experimental options."
    },
    {
      "text": "When discussing visual design, use CHIEF ART DIRECTOR mode: Structure responses as Visual Analysis → Art Pillar Recommendations → Detailed Style Guides → Retcon Notes → Implementation Roadmap."
    }
  ]
}
```

## 🚀 Usage

### Activating Modes

Use these prompts to activate specific modes:

- **CTO ARCHITECT MODE:** `[your technical question]`
- **CHIEF ART DIRECTOR MODE:** `[your visual design question]`
- **CHIEF DESIGN OFFICER MODE:** `[your game design question]`
- **And so on...**

### Response Structures

Each mode follows its specialized response structure:

- **CTO Architect:** Analysis → Recommendations → Architecture Sketches → Next Steps
- **Chief Art Director:** Visual Analysis → Art Pillar Recommendations → Detailed Style Guides → Retcon Notes → Implementation Roadmap
- **Chief Design Officer:** Analysis → Recommendations → System Details → Retcon Notes → Next Steps
- **Document Control Specialist:** Documentation Analysis → Issue Identification → Governance Strategy → Implementation Plan

### Three-Option Framework

Most modes provide three options for recommendations:

- **Safe:** Industry best practices, proven solutions
- **Bold:** Forward-leaning approaches with higher potential
- **Experimental:** Bleeding-edge solutions with higher risk

## 🎨 Mode Colors & Themes

Each mode has an associated color for easy identification:

- CTO Architect: Cyan
- Chief Art Director: Yellow
- Chief Design Officer: Pink
- Chief Security Officer: Red
- Data Scientist: Green
- DevOps Engineer: Blue
- Performance Engineer: Orange
- ComfyUI Concept Designer: Purple
- Map Designer: Brown
- Document Control Specialist: Gray

## 🔧 Advanced Configuration

### Custom Instructions per Mode

You can create mode-specific instruction files and reference them in your VS Code settings:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".copilot/modes/cto-architect.json"
    }
  ]
}
```

### Context Integration

The modes automatically reference your Terminal Grounds context from `CLAUDE.md` and project documentation.

## 📋 Quick Reference

| Mode | Trigger | Focus Area |
|------|---------|------------|
| CTO Architect | `CTO ARCHITECT MODE:` | Technical architecture |
| Chief Art Director | `CHIEF ART DIRECTOR MODE:` | Visual design |
| Chief Design Officer | `CHIEF DESIGN OFFICER MODE:` | Game design |
| Chief Security Officer | `CHIEF SECURITY OFFICER MODE:` | Security |
| Data Scientist | `DATA SCIENTIST MODE:` | Analytics |
| DevOps Engineer | `DEVOPS ENGINEER MODE:` | Infrastructure |
| Performance Engineer | `PERFORMANCE ENGINEER MODE:` | Optimization |
| ComfyUI Concept Designer | `COMFYUI CONCEPT DESIGNER MODE:` | AI assets |
| Map Designer | `MAP DESIGNER MODE:` | Level design |
| Document Control Specialist | `DOCUMENT CONTROL SPECIALIST MODE:` | Documentation |

## 🎯 Next Steps

1. Configure your VS Code settings as described above
2. Test each mode with sample questions
3. Customize the instructions based on your preferences
4. Consider creating mode-specific keyboard shortcuts

This setup gives you Claude-like agent functionality within GitHub Copilot!
