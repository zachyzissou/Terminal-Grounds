# Generation Analysis Reference Guide
## Windows File Analysis Commands for Terminal Grounds Assets

**Purpose**: Provide reliable, agent-accessible commands for analyzing ComfyUI generation results on Windows systems.

---

## 🎯 CRITICAL PATHS

### **Output Directory (ALWAYS USE THIS)**
```
✅ CORRECT: C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\
❌ WRONG:   C:\Users\Zachg\Documents\ComfyUI\output\ (legacy/unused)
```

### **File Naming Patterns**
- **Current Batch**: `TG_PERFECT_*Wide_Ambient*.png`, `TG_PERFECT_*Detail_Dramatic*.png`, `TG_PERFECT_*Perspective_Atmospheric*.png`  
- **Legacy Proven**: `TG_PERFECT_[Location]_[Style]_00001_.png`
- **Lore Series**: `TG_LORE_[Location]_[Style]_Perfect_00001_.png`

---

## 🔧 RELIABLE ANALYSIS COMMANDS

### **1. List Generation Results - USE LS TOOL**
```bash
# ALWAYS WORKS - Use this for complete directory analysis
LS path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output"

# Filter unwanted files (optional)
LS path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output" ignore=["*.txt", "*.log"]
```

### **2. Count Specific Generation Patterns**
```bash
# Count recent batch generations (use after LS output)
# Look for files with naming patterns:
# - TG_PERFECT_*_Wide_Ambient_*.png
# - TG_PERFECT_*_Detail_Dramatic_*.png  
# - TG_PERFECT_*_Perspective_Atmospheric_*.png
```

### **3. File Size Analysis**
```bash
# Get file sizes for quality assessment
Read file_path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\[SPECIFIC_FILENAME]"
# Note: Read tool shows file size in system reminders
```

### **4. Check ComfyUI Queue Status**
```bash
curl -s http://127.0.0.1:8188/queue | python -c "import json,sys; data=json.load(sys.stdin); print(f'Running: {len(data[\"queue_running\"])} | Pending: {len(data[\"queue_pending\"])}')"
```

---

## ⚠️ COMMANDS THAT FAIL ON WINDOWS

### **PowerShell Issues**
❌ **NEVER USE**: Complex PowerShell expressions with `$_` variables
❌ **NEVER USE**: `Where-Object` with shell escaping  
❌ **NEVER USE**: Calculated expressions in `Select-Object`

**Why**: Shell escaping and variable interpolation breaks consistently

### **Windows dir/findstr Issues**
❌ **PROBLEMATIC**: `dir | findstr` with complex patterns
❌ **PROBLEMATIC**: Nested quotes in cmd /c commands

**Why**: Quote escaping and pipe handling is unreliable

### **grep/find Issues**  
❌ **DOESN'T WORK**: Unix-style grep commands on Windows paths
❌ **DOESN'T WORK**: `find /c` for counting

**Why**: Mixed Unix/Windows command expectations

---

## 📊 QUALITY ASSESSMENT METRICS

### **File Size Indicators**
- **Masterpiece (2MB+)**: Underground Bunkers, complex environments
- **Excellent (1.2-2MB)**: Tech Wastes, detailed corridors
- **Production Ready (800KB-1.2MB)**: IEZ facilities, standard environments
- **Good (600-800KB)**: Security checkpoints, simple scenes
- **Failed (<500KB)**: Likely blank or corrupted generation

### **Success Rate Calculation**
```
Success Rate = (Files > 600KB) / (Total Files Generated) * 100
```

### **Naming Pattern Analysis**
- **Wide_Ambient**: Establishing shots, full environment views
- **Detail_Dramatic**: Close-up architectural details with high contrast
- **Perspective_Atmospheric**: Dynamic angles with volumetric lighting

---

## 🎮 BATCH ANALYSIS WORKFLOW

### **Step 1: Directory Scan**
```bash
LS path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output"
```

### **Step 2: Pattern Identification**
Count files matching each pattern:
- TG_PERFECT_*Wide_Ambient*.png
- TG_PERFECT_*Detail_Dramatic*.png  
- TG_PERFECT_*Perspective_Atmospheric*.png

### **Step 3: Quality Sampling**
Read 2-3 representative files to check sizes:
```bash
Read file_path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\[FILENAME]"
```

### **Step 4: Visual Quality Analysis - MANDATORY**
**CRITICAL**: File size and naming patterns only indicate technical completion, NOT quality!

```bash
# ALWAYS examine actual image content using Read tool
Read file_path="C:\Users\Zachg\Terminal-Grounds\Tools\Comfy\ComfyUI-API\output\[FILENAME.png]"
```

**Required Visual Assessment**:
1. **Lore Accuracy**: Does it match Terminal Grounds post-apocalyptic aesthetic?
2. **Style Consistency**: Clean SciFi vs Gritty Realism clearly differentiated?
3. **Content Quality**: Sharp details, proper composition, no artifacts?
4. **Thematic Correctness**: Captures the intended location/mood?

### **Step 5: Success Analysis**
- Calculate technical completion rate (files generated vs expected)
- Calculate visual quality rate (acceptable images vs total)
- Identify prompt refinement needs
- Document specific quality issues for future improvement

---

## 🚨 TROUBLESHOOTING

### **If LS Tool Shows No Recent Files**
1. Verify ComfyUI queue is empty: `curl -s http://127.0.0.1:8188/queue`
2. Check if output directory path is correct
3. Look for files with different naming patterns

### **If File Sizes Seem Wrong**
1. Use Read tool to double-check individual files
2. Compare with known good generations from previous sessions
3. Check for generation errors in ComfyUI logs

### **If PowerShell Commands Fail**
1. **DON'T DEBUG** - use LS tool instead
2. Reference this guide for reliable alternatives
3. Never use complex PowerShell expressions through Bash tool

---

## 📈 ANALYSIS TEMPLATES

### **Complete Batch Analysis Report Template**
```
## Batch Generation Analysis - [DATE]

**Technical Status**:
- Queue Status: Running: X | Pending: Y
- Total Files Generated: X/X requested
- Technical Success Rate: X% (files generated successfully)

**Visual Quality Assessment** (MANDATORY):
- Examined: X/X files using Read tool
- Visual Success Rate: X% (meet Terminal Grounds standards)

**Quality Distribution**:
- Excellent (8-10/10): X files - [list specific files]
- Good (6-8/10): X files - [list specific files]
- Acceptable (4-6/10): X files - [list specific files]
- Failed (<4/10): X files - [list specific files]

**By Variation Type**:
- Wide_Ambient: X files (X successful)
- Detail_Dramatic: X files (X successful)
- Perspective_Atmospheric: X files (X successful)

**Lore Accuracy Issues**:
- [List specific problems with Terminal Grounds aesthetic]
- [Note missing post-apocalyptic elements]
- [Identify style consistency problems]

**Recommended Actions**:
- [Prompt refinements needed]
- [Assets that should be regenerated]
- [Parameter adjustments to consider]
```

### **CRITICAL AGENT REMINDER**
❌ **NEVER** claim 100% success based only on file counts
✅ **ALWAYS** use Read tool to examine actual image content  
✅ **ALWAYS** assess lore accuracy and Terminal Grounds aesthetic fit
✅ **ALWAYS** provide honest visual quality ratings

---

**Last Updated**: August 24, 2025  
**Validation Status**: PRODUCTION READY  
**Next Review**: When analysis commands fail or new patterns emerge

---

*This reference eliminates the recurring problem of agents being unable to analyze generation results on Windows systems by providing tested, reliable command patterns.*