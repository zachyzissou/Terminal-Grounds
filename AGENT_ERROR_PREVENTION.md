# ⚠️ CRITICAL AGENT ERROR PREVENTION ⚠️

## THE MISTAKE THAT COST HOURS OF CONFUSION

**DATE**: August 24, 2025  
**PROBLEM**: Agent looked in WRONG output directory for generation analysis  
**IMPACT**: Completely missed 28 recent high-quality generations, provided false analysis  

---

## 🚫 NEVER DO THIS AGAIN 🚫

### WRONG OUTPUT DIRECTORY (DO NOT USE):
```
C:/Users/Zachg/Documents/ComfyUI/output/
```
**Contains**: Old files from August 19, 2025 and earlier  
**Status**: OBSOLETE, UNUSED, STALE DATA  

### ✅ CORRECT OUTPUT DIRECTORY (ALWAYS USE):
```
C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/
```
**Contains**: ACTIVE generation output, current work  
**Status**: LIVE, CURRENT, ACCURATE  

---

## MANDATORY CHECKS FOR GENERATION ANALYSIS

Before analyzing ANY Terminal Grounds generations:

1. **ALWAYS verify you're using the correct path**:
   ```
   C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/
   ```

2. **NEVER assume directory locations** - verify file paths explicitly

3. **Test file access first**:
   ```python
   from pathlib import Path
   correct_dir = Path("C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output")
   print(f"Directory exists: {correct_dir.exists()}")
   ```

---

## WHAT THE CORRECT DIRECTORY CONTAINS

As of August 24, 2025:
- **87 total generation images**
- **TG_PERFECT_* series**: 12 images (2-2.3MB each, highest quality)
- **TG_LORE_* series**: 16 images (complete lore branch)
- **TG_Emblem_* series**: 5 faction emblems
- **Generated**: August 23-24, 2025 (last night/early morning)

## WHAT THE WRONG DIRECTORY CONTAINS

- **105 total images** (misleading higher count)
- **Last generation**: August 19, 2025
- **Status**: STALE, HISTORICAL DATA ONLY
- **Result if used**: FALSE ANALYSIS, MISSED RECENT WORK

---

## AGENT PROTOCOL FOR GENERATION ANALYSIS

```python
# MANDATORY HEADER FOR ANY GENERATION ANALYSIS
CORRECT_OUTPUT_DIR = "C:/Users/Zachg/Terminal-Grounds/Tools/Comfy/ComfyUI-API/output/"
WRONG_OUTPUT_DIR = "C:/Users/Zachg/Documents/ComfyUI/output/"  # NEVER USE

# Always verify correct directory
assert Path(CORRECT_OUTPUT_DIR).exists(), f"Cannot find correct output directory: {CORRECT_OUTPUT_DIR}"

# Proceed with analysis using CORRECT_OUTPUT_DIR only
```

---

## SIGNATURE CONFIRMATION

**This error has been documented and directory paths corrected in CLAUDE.md**  
**Future agents: READ THIS FILE before any generation analysis**  
**No excuses for using wrong directory paths after this date**

---

---

## 🚫 NEVER CREATE NEW GENERATION SCRIPTS 🚫

**CRITICAL LESSON**: `terminal_grounds_generator.py` achieves 92% success rate
**NEVER**: Write new generation scripts from scratch
**ALWAYS**: Copy `terminal_grounds_generator.py` and modify only the prompts dictionary
**REASON**: Workflow structure, error handling, and API calls are proven - don't break what works

### Master Template Elements (NEVER CHANGE):
- 7-node workflow structure (numbered 1-7)
- PERFECT_PARAMS dictionary approach  
- try/catch error handling
- 0.5 second delays between submissions
- urllib.request API calls (not requests library)

### What TO Change:
- Prompt dictionary entries
- Resolution (for emblems: 1024x1024)
- Filename prefixes
- Location/style lists

**Bottom Line**: Refine existing scripts, never reinvent from scratch

---

**Created**: August 24, 2025  
**Reason**: Prevent costly directory confusion + stop creating redundant scripts
**Status**: MANDATORY REFERENCE for all generation work  