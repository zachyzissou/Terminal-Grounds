# Terminal Grounds Generation Rules - MANDATORY

**READ THIS BEFORE ANY ASSET GENERATION**

## ⚠️ CRITICAL RULE: ALWAYS USE LORE SYSTEM ⚠️

**NEVER generate assets without the lore system. ComfyUI does NOT understand faction names without context.**

## ✅ CORRECT METHOD - Use Existing Lore Integration

```bash
# For ANY Terminal Grounds asset generation, use:
cd "C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API"
.\Test-Generate.ps1 -UseLorePrompt -RegionId [REGION] -FactionId [FACTION] -Subject [DESCRIPTION] -Action [ACTION]
```

## ❌ WRONG METHODS - These Will Fail

- Using generic faction names: "IronScavengers faction vehicle" 
- Custom Python scripts without lore integration
- Raw prompts without Terminal Grounds world-building context
- Any generation that doesn't use the existing lore system

## 📋 Valid Faction IDs (Use These ONLY)

- `FCT_VUL` - Iron Vultures
- `FCT_DIR` - Sky Bastion Directorate  
- `FCT_CCB` - Trivector Combine
- `FCT_VAR` - Obsidian Archive
- `FCT_F77` - The Seventy-Seven
- `FCT_NOM` - Roadborn Clans
- `FCT_CWD` - Truce Wardens

## 📋 Valid Region IDs (Use These ONLY)

- `REG_CRIMSON_DOCKS` - Crimson Freeport
- `REG_SKY_BASTION` - Sky Bastion
- `REG_BLACK_VAULT` - The Deep Vault
- `REG_TECH_WASTES` - Machine Grave
- `REG_METRO_A` - Metro Maintenance A
- `REG_IEZ` - Interdiction Exclusion Zone

## 🎯 Proven Working Examples

```bash
# Iron Vultures vehicle
.\Test-Generate.ps1 -UseLorePrompt -RegionId 'REG_CRIMSON_DOCKS' -FactionId 'FCT_VUL' -Subject 'technical vehicle' -Action 'convoy transport'

# Directorate weapon  
.\Test-Generate.ps1 -UseLorePrompt -RegionId 'REG_SKY_BASTION' -FactionId 'FCT_DIR' -Subject 'squad automatic weapon' -Action 'field maintenance'

# Obsidian Archive character
.\Test-Generate.ps1 -UseLorePrompt -RegionId 'REG_BLACK_VAULT' -FactionId 'FCT_VAR' -Subject 'research specialist' -Action 'studying artifacts'
```

## 🚨 PREVENTION CHECKLIST

Before ANY generation:

1. ✅ Am I using `Test-Generate.ps1 -UseLorePrompt`?
2. ✅ Am I using valid RegionId from the list above?
3. ✅ Am I using valid FactionId from the list above?
4. ✅ Will ComfyUI understand the rich context this provides?

If ANY answer is NO - STOP and use the lore system.

## 📚 Reference Files

- **Lore Data**: `Tools/Comfy/ComfyUI-API/lore_prompts.json`
- **Lore Builder**: `Tools/Comfy/ComfyUI-API/Build-LorePrompt.ps1`
- **Generation Script**: `Tools/Comfy/ComfyUI-API/Test-Generate.ps1`
- **Lore Bible**: `docs/Lore/LORE_BIBLE.md`

## 🎯 THE SOLUTION

The problem was NEVER technical. We have a complete lore integration system that:

- Builds rich prompts with faction signatures
- Includes regional atmosphere and materials
- Provides world context ComfyUI understands
- Works with proven generation parameters

**USE IT. ALWAYS.**

---

*This document prevents the weeks of confusion we had trying to make ComfyUI understand "IronScavengers" without proper Terminal Grounds context.*