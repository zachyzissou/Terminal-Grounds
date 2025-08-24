# HeunPP2 Parameters for FLUX Models

## Key Findings from Research

### Critical Discovery: FLUX Parameter Requirements
Your current parameters are likely **completely wrong** for FLUX models:

| Parameter | Your Current | FLUX Recommended | Issue |
|-----------|-------------|------------------|-------|
| **Steps** | 25-30 | **1-4 steps** | 🔴 10x too high |
| **CFG** | 3.2 | **1.0** | 🔴 3x too high |
| **Scheduler** | normal | **sgm_uniform** or **simple** | 🔴 Wrong type |

### Why HeunPP2 Failed
1. **Massive step overshoot**: 30 steps vs recommended 1-4 for FLUX
2. **CFG incompatibility**: FLUX doesn't use traditional CFG like SDXL
3. **Wrong scheduler**: Normal scheduler not optimal for FLUX architecture

## Corrected Parameters for FLUX + HeunPP2

### Test Configuration 1: Conservative
```
Sampler: heunpp2
Steps: 4
CFG: 1.0
Scheduler: simple
Denoise: 1.0
```

### Test Configuration 2: FLUX-Optimized
```
Sampler: heunpp2
Steps: 1
CFG: 1.0
Scheduler: sgm_uniform
Denoise: 0.20
```

### Test Configuration 3: Middle Ground
```
Sampler: heunpp2
Steps: 2
CFG: 1.0
Scheduler: simple
Denoise: 1.0
```

## Why Your Heun Works vs HeunPP2 Doesn't

### Heun Tolerance
- Standard heun sampler may be more **tolerant** of incorrect parameters
- Can function even with suboptimal FLUX settings
- Produces "good enough" results despite parameter mismatch

### HeunPP2 Precision
- More **mathematically precise** and sensitive to correct parameters
- Fails completely when parameters are wrong for the model architecture
- Requires exact FLUX-specific settings to function

## Recommended Test Sequence

### Test 1: Minimal FLUX Parameters
```powershell
./Test-Generate.ps1 -Prompt "simple industrial corridor test" 
  -Prefix TG_HeunPP_FLUX_Test1 -Width 1920 -Height 1080 
  -Steps 4 -CFG 1.0 -Sampler heunpp2 -Scheduler simple -Seed 12345
```

### Test 2: Ultra-Minimal (Schnell Style)
```powershell
./Test-Generate.ps1 -Prompt "simple industrial corridor test"
  -Prefix TG_HeunPP_FLUX_Test2 -Width 1920 -Height 1080
  -Steps 1 -CFG 1.0 -Sampler heunpp2 -Scheduler sgm_uniform -Seed 12345
```

### Test 3: Your Existing Heun for Comparison
```powershell
./Test-Generate.ps1 -Prompt "simple industrial corridor test"
  -Prefix TG_Heun_Comparison -Width 1920 -Height 1080
  -Steps 25 -CFG 3.2 -Sampler heun -Scheduler normal -Seed 12345
```

## Expected Outcomes

### If HeunPP2 with FLUX Parameters Works:
- Should produce clear, detailed images
- Generation time: 30-60 seconds (vs 5-7 minutes)
- Quality may exceed your current heun results
- **Revolutionary speed improvement**

### If Still Fails:
- HeunPP2 may have fundamental FLUX incompatibility
- Stick with proven heun approach
- Consider testing other samplers (euler, dpmpp_2m) with FLUX parameters

## Critical Insight

**Your current "successful" heun generations may be suboptimal for FLUX!**

If FLUX really wants 1-4 steps and CFG 1.0, then your 25-step CFG 3.2 approach might be:
- Working despite wrong parameters (heun tolerance)
- Taking 10x longer than necessary
- Potentially producing lower quality than possible

Testing both heunpp2 AND heun with proper FLUX parameters could revolutionize your entire pipeline speed and quality.