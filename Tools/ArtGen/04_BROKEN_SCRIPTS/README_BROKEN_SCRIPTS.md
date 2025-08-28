# BROKEN SCRIPTS ARCHIVE

**⚠️ WARNING: DO NOT USE THESE SCRIPTS ⚠️**

This directory contains scripts that have been identified as broken and removed from production use.

## Scripts in this Archive

### `faction_vehicle_concepts_BROKEN.py` 
- **Issue:** Severe text corruption in all generated vehicles
- **Root Cause:** Conflicting positive/negative prompts for text elements
- **Evidence:** Generated vehicles with scrambled, unreadable text covering surfaces
- **Replacement:** `faction_vehicle_concepts.py` (fixed version)

### `faction_ui_hud_concepts_BROKEN.py`
- **Issue:** Generated copyrighted content (Call of Duty UI elements)
- **Root Cause:** Generic "game HUD" prompts without copyright blocking
- **Legal Risk:** HIGH - immediate copyright violation exposure
- **Replacement:** `faction_ui_hud_concepts.py` (copyright-safe version)

## Why These Scripts Failed

Both scripts suffered from **prompt engineering failures**:

1. **Text Corruption:** FLUX model cannot handle complex text requests without generating corrupted text
2. **Copyright Exposure:** Generic prompts trigger copyrighted content generation from training data

## Fixed Replacements Available

The working directory now contains production-ready replacements:
- `faction_vehicle_concepts.py` - Text-free vehicle generation
- `faction_ui_hud_concepts.py` - Copyright-safe UI generation

## Post-Mortem Reference

For full technical analysis, see: `Assets_PostMortem_Report_2025-08-28.md`

---
**Archive Date:** August 28, 2025  
**Reason:** Production-blocking issues resolved  
**Status:** NEVER USE - Reference only